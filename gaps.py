#!/usr/bin/env python3
"""Weekly review: what are customers saying that we don't understand?

Reads data/queries.jsonl and ranks the words that matched NO bag.
Those words are the dictionary's to-do list.
"""
import json, collections, pathlib
LOG = pathlib.Path(__file__).parent / "data" / "queries.jsonl"
if not LOG.exists():
    raise SystemExit("no queries logged yet")

rows = [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]
words = collections.Counter()
examples = {}
for r in rows:
    for w in r.get("unknown_words") or []:
        words[w] += 1
        examples.setdefault(w, r["said"])

print(f"{len(rows)} queries logged\n")
print("WORDS CUSTOMERS SAY THAT NO BAG RECOGNISES")
print("(each one is a candidate dictionary entry)\n")
print(f"  {'count':>5}  {'word':16s} example")
for w, n in words.most_common(30):
    print(f"  {n:5d}  {w:16s} {examples[w][:44]!r}")

zero = [r for r in rows if r.get("hits") == 0]
if zero:
    print(f"\n{len(zero)} queries returned NOTHING — possible assortment gaps:")
    for r in zero[:10]:
        print(f"   {r['said'][:40]!r} -> searched {r['keywords']!r}")
