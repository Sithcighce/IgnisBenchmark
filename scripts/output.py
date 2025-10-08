#!/usr/bin/env python3
"""
将根目录 output.py 的功能移动并改进：
- 解析 data/benchmark_bank.jsonl
- 按分数升序输出 markdown 文件到 ./output

用法：
    python scripts/output.py

遵循项目开发准则，输出目标目录为 ./output
"""
from pathlib import Path
import json
import re


def safe_get(d, *keys):
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def extract_record(obj, index):
    qtext = None
    for k in ('question_text', 'question'):
        qtext = obj.get(k) or qtext
    if not qtext and isinstance(obj.get('question_data'), dict):
        qtext = obj['question_data'].get('question_text') or obj['question_data'].get('question')

    s_ans = obj.get('standard_answer')
    if not s_ans and isinstance(obj.get('question_data'), dict):
        s_ans = obj['question_data'].get('standard_answer')

    failed = obj.get('failed_attempt') or {}
    f_ans = failed.get('candidate_answer')

    score = None
    try:
        score = safe_get(obj, 'failed_attempt', 'grading_result', 'score')
    except Exception:
        score = None
    if score is None:
        score = safe_get(obj, 'grading_result', 'score')
    if isinstance(score, str):
        try:
            score = float(score)
        except Exception:
            score = None

    qid = None
    if isinstance(obj.get('question_data'), dict):
        qid = obj['question_data'].get('question_id')
    qid = qid or obj.get('question_id') or obj.get('id') or f"idx_{index}"

    evaluation = None
    evaluation = safe_get(obj, 'failed_attempt', 'grading_result', 'reasoning') or evaluation
    evaluation = safe_get(obj, 'failed_attempt', 'grading_result', 'reason') or evaluation
    evaluation = safe_get(obj, 'failed_attempt', 'grading_result', 'review') or evaluation
    evaluation = safe_get(obj, 'grading_result', 'reasoning') or evaluation
    evaluation = safe_get(obj, 'grading_result', 'reason') or evaluation
    evaluation = evaluation or 'N/A'

    return {
        'qid': qid,
        'question_text': qtext or 'N/A',
        'standard_answer': s_ans or 'N/A',
        'failed_answer': f_ans or 'N/A',
        'score': score,
        'evaluation': evaluation,
        'raw': obj,
    }


def normalize_fname(s: str) -> str:
    s = re.sub(r"[^0-9A-Za-z._-]", '_', s)
    return s[:80]


def main():
    root = Path(__file__).resolve().parent.parent
    src = root / 'data' / 'benchmark_bank.jsonl'
    if not src.exists():
        print(f"未找到文件: {src}. 请将 benchmark_bank.jsonl 放在 data/ 目录下。")
        return 2

    records = []
    with src.open('r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            rec = extract_record(obj, i)
            records.append(rec)

    with_score = [r for r in records if isinstance(r['score'], (int, float))]
    without_score = [r for r in records if not isinstance(r['score'], (int, float))]

    with_score.sort(key=lambda x: x['score'])
    chosen = with_score + without_score

    outdir = root / 'output' 
    outdir.mkdir(parents=True, exist_ok=True)
    for idx, rec in enumerate(chosen, start=1):
        qid = normalize_fname(str(rec['qid']))
        fname = outdir / f"{idx:04d}_{qid}.md"
        with fname.open('w', encoding='utf-8') as fh:
            fh.write(f"## 原题\n\n{rec['question_text']}\n\n")
            fh.write(f"## 答案\n\n{rec['standard_answer']}\n\n")
            fh.write(f"## 错误回答\n\n{rec['failed_answer']}\n\n")
            fh.write(f"## 评分\n\n{rec['score'] if rec['score'] is not None else 'N/A'}\n\n")
            fh.write(f"## 评价\n\n{rec.get('evaluation','N/A')}\n")

    print(f"已生成 {len(chosen)} 个 md 文件到: {outdir}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
