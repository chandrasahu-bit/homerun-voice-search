#!/usr/bin/env python3
"""Sync active Shopify products -> data/catalog.json + data/vocab.json.

Run on a schedule (hourly is plenty). This is the ONLY time we touch Shopify;
the voice pipeline never calls Shopify at query time.

L2 categories come from the Shopify metafield spec.category-l2 (fetched via
GraphQL) rather than product.product_type, so vocab["types"] matches the
actual Wizzy/Shopify taxonomy.
"""
import json, os, re, urllib.request, collections, pathlib

ROOT = pathlib.Path(__file__).parent
def env(k, d=""):
    for line in (ROOT / ".env").read_text().splitlines():
        line = line.strip()
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip()
    return os.environ.get(k, d)

SHOP  = env("SHOPIFY_STORE_DOMAIN")
TOKEN = env("SHOPIFY_ADMIN_TOKEN")
VER   = env("SHOPIFY_REST_VERSION", "2024-01")

def fetch_all():
    url = f"https://{SHOP}/admin/api/{VER}/products.json?status=active&limit=250"
    out, page = [], 0
    while url and page < 40:
        page += 1
        req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read()); link = r.headers.get("Link", "")
        out.extend(data["products"])
        print(f"  page {page}: {len(data['products'])}")
        m = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = m.group(1) if m else None
    return out

_L2_QUERY = """
query($cursor: String) {
  products(first: 250, after: $cursor, query: "status:active") {
    edges {
      node {
        legacyResourceId
        metafield(namespace: "spec", key: "category-l2") {
          value
        }
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""

def fetch_l2_metafields():
    """Return {product_id (int): l2_value} from spec.category-l2 metafield."""
    endpoint = f"https://{SHOP}/admin/api/{VER}/graphql.json"
    l2map, cursor, page = {}, None, 0
    while page < 40:
        page += 1
        payload = json.dumps({"query": _L2_QUERY, "variables": {"cursor": cursor}}).encode()
        req = urllib.request.Request(
            endpoint, data=payload,
            headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        if "errors" in data:
            raise RuntimeError(f"GraphQL errors: {data['errors']}")
        products = data["data"]["products"]
        for edge in products["edges"]:
            node = edge["node"]
            mf = node.get("metafield")
            if mf and mf.get("value"):
                l2map[int(node["legacyResourceId"])] = mf["value"].strip()
        pi = products["pageInfo"]
        print(f"  l2 page {page}: {len(products['edges'])} products, {sum(1 for v in l2map.values() if v)} with l2")
        if not pi["hasNextPage"]:
            break
        cursor = pi["endCursor"]
    return l2map

def build(products, l2map=None):
    slim, tagc = [], collections.Counter()
    # type_specs: product_type -> option name -> set of real values seen on
    # any variant of that type. This is the grounding data R4's spec-
    # validation step checks a stated size/spec against - built here so the
    # sync job (which already talks to Shopify) is the only thing that reads
    # product.options / variant.option1-3, never the query-time path.
    type_specs = collections.defaultdict(lambda: collections.defaultdict(set))
    for p in products:
        tags = [t.strip() for t in p["tags"].split(",") if t.strip()]
        for t in tags: tagc[t] += 1
        ptype = p.get("product_type", "")
        l2 = (l2map or {}).get(p["id"], "")
        # Shopify names each option slot (1-3) per product, e.g. "Size",
        # "Colour" - option1/2/3 on a variant are only meaningful alongside
        # that name, so zip them together rather than keeping bare values.
        opt_names = [o.get("name", "") for o in p.get("options", [])]
        variants, prices = [], []
        for v in p.get("variants", []):
            t = (v.get("title") or "").strip()
            if t and t.lower() != "default title":
                variants.append({"title": t, "sku": v.get("sku"), "price": v.get("price")})
            if v.get("price"): prices.append(float(v["price"]))
            if ptype:
                for i, name in enumerate(opt_names, start=1):
                    val = (v.get(f"option{i}") or "").strip()
                    if name and val and val.lower() != "default title":
                        type_specs[ptype][name].add(val)
        slim.append({
            "id": p["id"], "title": p["title"], "type": ptype, "l2": l2,
            "tags": tags, "variants": variants, "handle": p["handle"],
            "price": min(prices) if prices else None,
            "image": (p.get("image") or {}).get("src", "") if p.get("image") else "",
        })
    titles = [p["title"].lower() for p in slim]
    brands = sorted({t for t in tagc if any(x.startswith(t.lower()) for x in titles)})
    # types: from product_type — drives TYPEWORDS/catalogue bags, unchanged.
    types = sorted({p["type"] for p in slim if p["type"]})
    # l2_categories: from spec.category-l2 metafield — used ONLY in the prompt's
    # L2 fallback section. Separate from types so catalogue bags are not affected.
    if l2map:
        l2_vals = sorted({p["l2"] for p in slim if p["l2"]})
        l2_categories = l2_vals if l2_vals else types
        print(f"  L2 source: spec.category-l2 metafield ({len(l2_vals)} unique values)")
    else:
        l2_categories = types
        print("  L2 source: product_type (metafield fetch skipped)")
    vocab = {"brands": brands, "types": types, "l2_categories": l2_categories,
             "tags": [t for t, n in tagc.most_common() if n >= 3]}
    specs = {ptype: {name: sorted(vals) for name, vals in names.items()}
             for ptype, names in type_specs.items()}
    return slim, vocab, specs

if __name__ == "__main__":
    print(f"Syncing active products from {SHOP} ...")
    prods = fetch_all()
    print("Fetching spec.category-l2 metafields via GraphQL ...")
    l2map = fetch_l2_metafields()
    slim, vocab, specs = build(prods, l2map)
    (ROOT / "data").mkdir(exist_ok=True)
    json.dump(slim,  open(ROOT / "data/catalog.json", "w"), ensure_ascii=False)
    json.dump(vocab, open(ROOT / "data/vocab.json",  "w"), ensure_ascii=False, indent=1)
    json.dump(specs, open(ROOT / "data/variant_specs.json", "w"), ensure_ascii=False, indent=1)
    n_specs = sum(len(v) for v in specs.values())
    print(f"\n{len(slim)} products | {len(vocab['brands'])} brands | {len(vocab['types'])} product types "
          f"| {len(vocab['l2_categories'])} L2 categories | {len(specs)} types with real variant specs ({n_specs} option lists)")
    print("wrote data/catalog.json, data/vocab.json, data/variant_specs.json")
