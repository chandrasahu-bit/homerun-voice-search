# HomeRun Voice Search — prototype

Voice → English keywords → Wizzy → products or collection redirect, for a
building-materials catalogue (plywood, plumbing, paint, power tools,
electrical, CCTV, bathroom fittings).

---

## Pipeline

```
mic
 │
 ▼
ASR  ─── primary: Sarvam saaras:v4 (streaming realtime)
     ─── fallback: Web Speech API (browser, Chrome only)
 │
 ▼
corrections.csv  ─── word-level ASR fixes (hot-reloaded, no restart)
                     e.g. "rough"→"roff", "bairoff"→"roff", "bosh"→"bosch"
 │
 ▼
catalog_spell_fix  ─── fuzzy match against catalogue title words
                       e.g. "showe"→"shower", "emulshion"→"emulsion"
 │
 ▼
rule router  ─── CATWORDS / TYPEWORDS bag match
             ─── fast path: confident match → skip LLM call
             ─── slow path: weak / unknown → escalate to LLM
 │
 ▼
LLM  ─── primary:  Sarvam sarvam-105b-conversations
     ─── fallback: Anthropic Claude
     ─── fallback: OpenAI
     ─── fallback: rule-based lexicon (lexicon.py)
 │        model receives:
 │          system: full prompt (brands, title bag, tags, L2 categories, match order, trade slang)
 │          user:   "Original (what customer said): <raw>"   ← only when corrected
 │                  "Corrected (use for catalogue matching): <fixed>"
 │                  or just the corrected transcript if unchanged
 │
 ▼
L2 normalization  ─── server-side, runs after LLM
                      snaps keyword to canonical L2 name when confidence ≥ 0.95
                      skipped if brand / color / size / material present (specific product)
 │
 ▼
/api/search  ─── Wizzy keyword search
             ─── collection redirect when keyword is an exact L2 name
```

Shopify is **never** called at query time. `sync_catalog.py` pulls active
products on a schedule into `data/catalog.json` + `data/vocab.json` +
`data/variant_specs.json`.

---

## Run

```bash
python3 sync_catalog.py     # refresh catalogue from Shopify (run hourly)
python3 server.py           # http://localhost:8787
```

---

## Catalogue data (`sync_catalog.py`)

Fetches active products via Shopify REST API, then fetches `spec.category-l2`
metafield values via GraphQL Admin API.

Builds three data files:

| File | Contents |
|---|---|
| `data/catalog.json` | 769 slim product records (id, title, type, l2, tags, variants, handle, price) |
| `data/vocab.json` | `brands` (93), `types` (264), `l2_categories` (85), `tags` (186) |
| `data/variant_specs.json` | real option values per product_type (used for spec validation) |

**Key vocab split:**

- `vocab["types"]` — from `product.product_type` → drives TYPEWORDS / catalogue bag matching (unchanged from product data)
- `vocab["l2_categories"]` — from `spec.category-l2` Shopify metafield → only used in the LLM prompt L2 section and server-side normalization. 85 values vs 264 product types — these map to actual Shopify collection pages.

---

## NLU: LLM match order

The model applies these steps in strict priority:

| Step | Condition | Action |
|---|---|---|
| 1 | **L2 category directly named** (original transcript) | `keywords` = exact L2 name, `product_type` = same, `confidence` 1.0 → Wizzy collection redirect |
| 2 | **Title bag word recognised** (corrected transcript) | Customer's words verbatim — do NOT add words they did not say |
| 3 | **Brand named** | Include in `keywords` + `brand` field |
| 4 | **Trade slang resolved** | Mapped English term as keywords |
| 5 | **No confident match** | Pass customer's own words through, `confidence` ≤ 0.4, `product_type` null |
| 6 | **Not in assortment** | `in_assortment` false, customer's words as keywords |

**`product_type` rule:** set to an L2 name **only** in step 1. Steps 2–6 must leave it null.

**Server-side confidence guard:** L2 normalization (keyword → canonical L2 name snap) only fires when `confidence ≥ 0.95`. This blocks inferred guesses from triggering collection redirects.

**Dual-transcript input:** when spell-fix or corrections change the transcript, the model receives both the original (for step 1 L2 check — spoken "and" = "&") and the corrected (for steps 2–4 catalogue matching). When unchanged, only one transcript is sent.

---

## Corrections (`data/corrections.csv`)

Word-level overrides for systematic ASR mis-hearings. Hot-reloaded on every
request — edit the file, no server restart needed.

```
heard,intended
rough,roff
ruff,roff
bairoff,roff
bosh,bosch
```

Use for words where fuzzy spell-fix can't reach (edit distance too large or
the wrong word wins).

---

## `lexicon.py` — the domain asset

Trade vernacular mapped to catalogue English:
`sunmica`→laminate, `kabza`→hinge, `nal`/`ಕೊಳಾಯಿ`→tap,
`safedi`→wall putty, `sariya`→TMT bar, `fuhara`/`jhirna`→shower.

Two rules encoded there that generic translation gets wrong:

- **Dimension vs. quantity.** `ek inch CPVC pipe` = 1-inch pipe (spec, stays in keywords). `do bag cement` = quantity 2 bag (leaves keywords).
- **`rang`/`banna` is ambiguous** — means both *paint* and *colour*. `kale rang ka sink` = black sink; `ಬಿಳಿ ಬಣ್ಣ` = white paint. Resolved by whether another product noun is present.

Indic terms match as substrings (not `\b`) — Kannada attaches case suffixes directly (`ಹೊರಗೋಡೆ` + `ಗೆ`).

---

## Wizzy

`POST https://api.wizzy.ai/v1/products/search`, headers `x-store-id` + `x-api-key`.

**Collection redirects** fire when the keyword exactly matches a configured redirect phrase in Wizzy. Step 1 L2 matches produce keywords that match these redirects (e.g. "Interior Emulsions", "Cameras", "CPVC Pipes & Hardware"). The UI renders a redirect as a collection result, not a product list.

---

## API endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/understand` | POST | Main NLU: transcript → keywords + intent |
| `/api/search` | POST | Keywords → Wizzy → products / redirect |
| `/api/compare` | POST | Run all NLU arms side-by-side on one utterance |
| `/api/transcribe` | POST | Sarvam STT: audio → transcript |
| `/api/status` | GET | Server health, vocab counts, provider flags |
| `/api/prompt` | GET | Current built system prompt (debug) |
| `/api/last_call` | GET | Last system + user message sent to LLM (debug) |

---

## Degradation

| Component | Primary | Fallback |
|---|---|---|
| STT | Sarvam saaras:v4 | Web Speech API (Chrome) |
| Intent / NLU | Sarvam sarvam-105b-conversations | Anthropic → OpenAI → rule lexicon |
| Search | Wizzy | Local index over `data/catalog.json` |

The prototype runs with no keys set — rule-based lexicon answers intent,
local catalog answers search. Add keys in `.env` to enable each layer.

---

## Known gaps

- **Sarvam STT quota**: 402 `Credits exhausted` → voice input fails immediately, falls back to Web Speech API. Monitor usage.
- **Multi-item utterances**: LLM parses multiple items correctly but only the first item is passed to Wizzy search.
- **Language detection (rule fallback)**: script-based, so romanised Hindi (`kale rang ka sink`) reports as `en`. The LLM layer reports `mixed` correctly.
- **"LED Bulbs" not an L2 category**: `spec.category-l2` metafield not set on bulb products → no collection redirect for "bulbs". Set the metafield in Shopify and re-run `sync_catalog.py` to enable.
