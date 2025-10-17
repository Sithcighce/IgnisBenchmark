#!/usr/bin/env python3
"""
Check duplicates in 验证/question.json
- exact object duplicates (canonicalized JSON)
- duplicates by 'id' field (if present)
- duplicates by 'question' or 'title' text (normalized)

Prints a concise summary and examples.
"""
import json
from pathlib import Path
from collections import defaultdict, Counter
import sys

OUT = Path('验证/question.json')

if not OUT.exists():
    print(f"File not found: {OUT}", file=sys.stderr)
    sys.exit(2)

data = json.loads(OUT.read_text(encoding='utf-8'))
if not isinstance(data, list):
    print(f"Expected a JSON array in {OUT}", file=sys.stderr)
    sys.exit(3)

n = len(data)
print(f"Total items: {n}")

# Exact object duplicates (canonicalized)
canon_map = defaultdict(list)
for idx, item in enumerate(data):
    try:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True)
    except Exception:
        # Fallback: use repr
        key = repr(item)
    canon_map[key].append(idx)

exact_dups = {k: v for k, v in canon_map.items() if len(v) > 1}
print(f"Exact-object duplicates groups: {len(exact_dups)} (total duplicate items: {sum(len(v) for v in exact_dups.values())})")
if exact_dups:
    print("Examples of exact duplicates (showing indices and item):")
    count = 0
    for k, idxs in list(exact_dups.items())[:5]:
        print(f"  indices: {idxs}")
        try:
            example = json.loads(k)
            print(f"    item sample keys: {list(example.keys())[:10]}")
        except Exception:
            print(f"    item repr: {k[:200]}")
        count += 1
    print()

# Duplicates by id
id_map = defaultdict(list)
for idx, item in enumerate(data):
    if isinstance(item, dict):
        for k in ('id', 'Id', 'ID'):
            if k in item and item[k] is not None:
                id_map[str(item[k])].append(idx)
                break

id_dups = {k: v for k, v in id_map.items() if len(v) > 1}
print(f"Duplicates by id-key groups: {len(id_dups)} (total duplicate items: {sum(len(v) for v in id_dups.values())})")
if id_dups:
    print("Examples of id duplicates:")
    for k, idxs in list(id_dups.items())[:5]:
        print(f"  id={k} indices={idxs}")
    print()

# Duplicates by question/title normalized
text_map = defaultdict(list)
for idx, item in enumerate(data):
    if isinstance(item, dict):
        text = None
        for k in ('question', 'Question', 'title', 'Title', 'q'):
            if k in item and isinstance(item[k], str):
                text = item[k].strip().lower()
                break
        if text:
            text_map[text].append(idx)

text_dups = {k: v for k, v in text_map.items() if len(v) > 1}
print(f"Duplicates by text (question/title) groups: {len(text_dups)} (total duplicate items: {sum(len(v) for v in text_dups.values())})")
if text_dups:
    print("Examples of text duplicates (showing a snippet and indices):")
    for k, idxs in list(text_dups.items())[:5]:
        print(f"  text_snippet={k[:80]!r} indices={idxs}")
    print()

# Summary: overlap between methods
# Compute sets of indices that are duplicates in any method
dup_indices = set()
for v in exact_dups.values():
    dup_indices.update(v)
for v in id_dups.values():
    dup_indices.update(v)
for v in text_dups.values():
    dup_indices.update(v)

print(f"Total unique items that appear in any duplicate group: {len(dup_indices)}")

# Quick per-file stats
print('\nTop 10 files with most items (by source path if available)')
# Try to extract source path from a field like 'source' or 'file' if present
source_map = defaultdict(int)
for item in data:
    if isinstance(item, dict):
        for k in ('source', 'file', 'path'):
            if k in item and isinstance(item[k], str):
                source_map[item[k]] += 1
                break

if source_map:
    for src, cnt in Counter(source_map).most_common(10):
        print(f"  {src}: {cnt}")
else:
    print("  No explicit source/path fields found in items.")

# Print suggestion if many duplicates
if len(dup_indices) == 0:
    print('\nNo duplicates detected by the three checks.')
else:
    print('\nSuggestion: if you want, run this script with --dedup to create 验证/question.dedup.json removing duplicates by chosen strategy.')

# Optionally implement --dedup? Not needed for now
