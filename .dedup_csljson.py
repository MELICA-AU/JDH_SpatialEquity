"""One-shot dedup of .melica_se.json by citation-key.

Keeps the entry with the most fields per key (tiebreak: first occurrence).
"""
import json
import sys
from pathlib import Path

src = Path(".melica_se.json")
data = json.loads(src.read_text(encoding="utf-8"))

if not isinstance(data, list):
    sys.exit(f"expected top-level array, got {type(data).__name__}")

by_key: dict[str, dict] = {}
order: list[str] = []
dup_counts: dict[str, int] = {}

for entry in data:
    key = entry.get("citation-key") or entry.get("id")
    if not key:
        continue
    dup_counts[key] = dup_counts.get(key, 0) + 1
    incumbent = by_key.get(key)
    if incumbent is None:
        by_key[key] = entry
        order.append(key)
    else:
        if len(entry) > len(incumbent):
            by_key[key] = entry

deduped = [by_key[k] for k in order]
duplicates = {k: c for k, c in dup_counts.items() if c > 1}

print(f"input entries:   {len(data)}")
print(f"unique keys:     {len(deduped)}")
print(f"removed:         {len(data) - len(deduped)}")
print(f"keys with dupes: {len(duplicates)}")
if duplicates:
    print("top offenders:")
    for k, c in sorted(duplicates.items(), key=lambda kv: -kv[1])[:10]:
        print(f"  {c}x  {k}")

src.write_text(json.dumps(deduped, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote {len(deduped)} entries back to {src}")
