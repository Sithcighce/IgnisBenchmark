#!/usr/bin/env python3
import json
import os
from datetime import datetime
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_jsonl_data(filepath):
    data = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return data

def main():
    print("Generating complete question browser...")
    validation_path = project_root / "data" / "validation_set.jsonl"
    benchmark_path = project_root / "data" / "benchmark_bank.jsonl" 
    seed_path = project_root / "data" / "seed_examples.jsonl"
    output_path = project_root / "output" / "complete_question_browser.html"
    
    validation_data = load_jsonl_data(validation_path)
    benchmark_data = load_jsonl_data(benchmark_path)
    seed_data = load_jsonl_data(seed_path)
    
    total = len(validation_data) + len(benchmark_data) + len(seed_data)
    accuracy = len(validation_data) / (len(validation_data) + len(benchmark_data)) * 100 if (len(validation_data) + len(benchmark_data)) > 0 else 0
    
    html_content = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Question Browser</title></head><body><h1>Question Bank ({total} questions, {accuracy:.1f}% accuracy)</h1><p>Generated: {datetime.now()}</p></body></html>"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Browser generated: {output_path}")

if __name__ == "__main__":
    main()
