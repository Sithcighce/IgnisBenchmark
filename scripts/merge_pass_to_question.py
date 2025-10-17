#!/usr/bin/env python3
"""
Merge all pass.json files under a source directory (default: question_english)
into a single JSON array written to 验证/question.json (default). Existing
output will be backed up before writing.
"""
import json
import argparse
import shutil
import time
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description="Merge pass.json files into one question.json")
    parser.add_argument('--source', '-s', default='question_english', help='Source directory to search for pass.json')
    parser.add_argument('--out', '-o', default='验证/question.json', help='Output merged file path')
    args = parser.parse_args()

    src = Path(args.source)
    out = Path(args.out)

    if not src.exists():
        print(f"Source directory not found: {src}", file=sys.stderr)
        sys.exit(2)

    files = list(src.rglob('pass.json'))
    print(f"Found {len(files)} pass.json files under {src}")

    merged = []
    errors = []
    for f in sorted(files):
        try:
            text = f.read_text(encoding='utf-8')
            if not text.strip():
                print(f"Skipping empty file: {f}")
                continue
            data = json.loads(text)
        except Exception as e:
            errors.append((str(f), str(e)))
            print(f"Error reading/parsing {f}: {e}", file=sys.stderr)
            continue

        if isinstance(data, list):
            merged.extend(data)
        else:
            merged.append(data)

    out.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing output if present
    if out.exists():
        ts = int(time.time())
        bak_name = out.name + f'.bak_{ts}'
        bak_path = out.parent / bak_name
        shutil.copy2(out, bak_path)
        print(f"Backed up existing {out} -> {bak_path}")

    # Write merged JSON array
    try:
        out.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        print(f"Failed to write output {out}: {e}", file=sys.stderr)
        sys.exit(3)

    print(f"Wrote {len(merged)} items to {out}")
    if errors:
        print(f"Completed with {len(errors)} errors. See stderr for details.")


if __name__ == '__main__':
    main()
