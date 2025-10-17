#!/usr/bin/env python3
"""
重新测试 API 失败(0分)的题目
使用 OpenAI API (不并发) + DeepSeek 判题
验证这些题目是否真的没有回答
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_BASE = "https://api.deepseek.com"

# Configuration
BASE_DIR = Path(r'c:\Users\13031\Desktop\workspace\distillation_generation\历史尝试归档\14_最终交付')
BENCHMARK_FILE = Path(r'c:\Users\13031\Desktop\workspace\distillation_generation\历史尝试归档\12_第十一次尝试_GPT5测试\data\benchmarkGPT5_recovered.json')
ZERO_SCORE_FILE = BASE_DIR / 'data' / 'gpt验证结果分类' / '4_API失败_零分' / 'api_failures_zero_score.json'
OUTPUT_FILE = BASE_DIR / 'data' / 'retest_zero_score_results.json'
LOG_FILE = BASE_DIR / 'retest_zero_score.log'

# Settings
REQUEST_TIMEOUT = 180
MAX_RETRIES = 3


def log_message(msg):
    """日志记录"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {msg}\n"
    
    print(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line)


def load_question_full_data(question_id):
    """从 benchmarkGPT5_recovered.json 加载完整题目数据"""
    with open(BENCHMARK_FILE, 'r', encoding='utf-8') as f:
        all_questions = json.load(f)
    
    for q in all_questions:
        if q['question_id'] == question_id:
            return q
    
    raise ValueError(f"Question {question_id} not found in benchmark file")


def format_original_text(original_text_dict):
    """格式化原文引用"""
    if not original_text_dict:
        return "No original text provided"
    
    lines = []
    for key, value in sorted(original_text_dict.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        lines.append(f"[Citation {key}]: {value}")
    return "\n".join(lines)


def call_gpt5_openai(question_text: str):
    """
    使用 OpenAI API 调用 GPT-5 回答题目
    注意: 使用 OpenAI 官方 API,模型为 gpt-5
    """
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # 完全相同的提示词
    prompt = f"""# ROLE
You are a senior expert in combustion science, heat transfer, fluid mechanics, CFD, and energy systems.

# TASK
Answer the following technical question with comprehensive detail and accuracy.

# REQUIREMENTS
- Provide a detailed, technically accurate answer
- Explain mechanisms, principles, and relationships
- Use precise scientific terminology
- Be comprehensive but concise
- Answer in English

# QUESTION
{question_text}

# YOUR ANSWER
Provide your detailed answer below:
"""
    
    payload = {
        "model": "gpt-5",  # 使用 OpenAI 的 GPT-5 模型
        "messages": [
            {
                "role": "system",
                "content": "You are a senior expert in combustion science, heat transfer, fluid mechanics, CFD, and energy systems. Provide detailed, accurate technical answers."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            log_message(f"  → Calling GPT-5 via OpenAI API (attempt {attempt + 1}/{MAX_RETRIES})...")
            response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content'].strip()
                log_message(f"  ✓ Got answer ({len(answer)} chars)")
                return answer
            
            # Handle rate limits
            if response.status_code == 429:
                wait_time = min(2 ** attempt * 2, 30)
                log_message(f"  ⚠ Rate limit, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            if attempt < MAX_RETRIES - 1:
                log_message(f"  ⚠ API Error {response.status_code}, retrying...")
                time.sleep(2 ** attempt)
                continue
            else:
                error_msg = f"API Error {response.status_code}: {response.text[:300]}"
                log_message(f"  ✗ {error_msg}")
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                log_message(f"  ⚠ Timeout, retry {attempt+1}/{MAX_RETRIES}")
                time.sleep(2 ** attempt)
            else:
                error_msg = "Request timeout after all retries"
                log_message(f"  ✗ {error_msg}")
                raise Exception(error_msg)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
            else:
                log_message(f"  ✗ Failed: {str(e)}")
                raise
    
    raise Exception(f"Failed after {MAX_RETRIES} retries")


def call_deepseek_to_grade(question_text: str, standard_answer: str, gpt_answer: str, 
                           original_text: str):
    """
    使用 DeepSeek API 判题
    使用与 benchmark_gpt5.py 完全相同的判题提示词
    """
    url = f"{DEEPSEEK_API_BASE}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # 完全相同的判题提示词
    prompt = f"""# ROLE
You are a strict technical answer grader in combustion science, heat transfer, fluid mechanics, CFD, and energy systems.

# TASK
Grade the given answer by comparing it with the standard answer and original text citations.

---

## QUESTION
{question_text}

---

## STANDARD ANSWER (Reference)
{standard_answer}

---

## ORIGINAL TEXT CITATIONS (Ground Truth)
{original_text}

---

## ANSWER TO GRADE (GPT-5's Response)
{gpt_answer}

---

## GRADING CRITERIA

### Check for Factual Errors
- Does the answer contain factually incorrect statements?
- Does it contradict the original text or standard answer?
- Are physical/chemical/thermodynamic principles stated correctly?

### Check for Logical Errors
- Is the reasoning process sound?
- Are cause-effect relationships correct?
- Are there logical contradictions?

### Scoring Guidelines
- **correct = true**: No factual or logical errors, core mechanisms correctly explained
- **correct = false**: Contains factual errors, logical flaws, or contradictions

**Note**: Do NOT penalize for:
- Different wording or phrasing (as long as factually correct)
- More detailed or more concise answers (if accurate)
- Different but equivalent explanations

**DO penalize for**:
- Wrong physical laws or principles
- Contradictions with original text
- Logical errors or flawed reasoning
- Missing critical mechanisms

### Score (0-100)
- **90-100**: Excellent - fully correct with comprehensive explanation
- **75-89**: Good - correct with minor omissions
- **60-74**: Acceptable - mostly correct but missing some details
- **40-59**: Poor - significant errors or omissions
- **0-39**: Incorrect - fundamental errors

---

## OUTPUT FORMAT (JSON ONLY)

```json
{{
  "correct": true/false,
  "score": 85,
  "issues": [
    "Description of any issues found (empty array if none)"
  ],
  "reasoning": "Brief explanation of the grade"
}}
```

**IMPORTANT**: Return ONLY the JSON object, no other text.
"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are a strict technical answer grader. Return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            log_message(f"  → Calling DeepSeek to grade (attempt {attempt + 1}/{MAX_RETRIES})...")
            response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                grading_text = result['choices'][0]['message']['content'].strip()
                
                # Parse JSON
                grading = json.loads(grading_text)
                log_message(f"  ✓ Grading complete: score={grading.get('score', 0)}, correct={grading.get('correct', False)}")
                return grading
            
            if attempt < MAX_RETRIES - 1:
                log_message(f"  ⚠ DeepSeek Error {response.status_code}, retrying...")
                time.sleep(2 ** attempt)
                continue
            else:
                error_msg = f"DeepSeek Error {response.status_code}: {response.text[:300]}"
                log_message(f"  ✗ {error_msg}")
                raise Exception(error_msg)
                
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
            else:
                log_message(f"  ✗ Grading failed: {str(e)}")
                raise
    
    raise Exception(f"Grading failed after {MAX_RETRIES} retries")


def test_single_question(question_id: str):
    """测试单个题目"""
    log_message(f"\n{'='*80}")
    log_message(f"Testing Question: {question_id}")
    log_message(f"{'='*80}")
    
    # Load full question data
    try:
        question_data = load_question_full_data(question_id)
    except Exception as e:
        log_message(f"✗ Failed to load question: {str(e)}")
        return None
    
    question_text = question_data['question_text']
    standard_answer = question_data['standard_answer']
    original_text = format_original_text(question_data.get('original_text', {}))
    
    log_message(f"Question preview: {question_text[:100]}...")
    
    # Step 1: Call GPT-5 (via OpenAI API)
    try:
        gpt_answer = call_gpt5_openai(question_text)
    except Exception as e:
        log_message(f"✗ GPT-5 API failed: {str(e)}")
        return {
            "question_id": question_id,
            "status": "api_error",
            "error": str(e),
            "gpt_answer": None,
            "grading": None
        }
    
    # Step 2: Grade with DeepSeek
    try:
        grading = call_deepseek_to_grade(question_text, standard_answer, gpt_answer, original_text)
    except Exception as e:
        log_message(f"✗ Grading failed: {str(e)}")
        return {
            "question_id": question_id,
            "status": "grading_error",
            "error": str(e),
            "gpt_answer": gpt_answer,
            "gpt_answer_length": len(gpt_answer),
            "grading": None
        }
    
    # Success
    result = {
        "question_id": question_id,
        "status": "success",
        "gpt_answer": gpt_answer,
        "gpt_answer_length": len(gpt_answer),
        "grading": grading,
        "score": grading.get('score', 0),
        "correct": grading.get('correct', False)
    }
    
    log_message(f"✓ Test complete: score={result['score']}, correct={result['correct']}, length={result['gpt_answer_length']}")
    
    return result


def main():
    """主函数"""
    log_message("=" * 80)
    log_message("重新测试 API 失败(0分)的题目")
    log_message("=" * 80)
    log_message(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message(f"使用 API: OpenAI (gpt-4o)")
    log_message(f"判题模型: DeepSeek-chat")
    log_message(f"测试模式: 顺序执行 (无并发)")
    log_message("")
    
    # Load zero score questions
    with open(ZERO_SCORE_FILE, 'r', encoding='utf-8') as f:
        zero_score_questions = json.load(f)
    
    question_ids = [q['question_id'] for q in zero_score_questions]
    total_questions = len(question_ids)
    
    log_message(f"待测试题目: {total_questions} 道")
    log_message("")
    
    # Test each question sequentially
    results = []
    for i, question_id in enumerate(question_ids, 1):
        log_message(f"\n[{i}/{total_questions}] Testing {question_id}")
        
        result = test_single_question(question_id)
        if result:
            results.append(result)
        
        # Save intermediate results
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Wait between requests (avoid rate limits)
        if i < total_questions:
            wait_time = 3
            log_message(f"  → Waiting {wait_time}s before next question...")
            time.sleep(wait_time)
    
    # Final statistics
    log_message(f"\n{'='*80}")
    log_message("测试完成")
    log_message(f"{'='*80}")
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    api_error_count = sum(1 for r in results if r['status'] == 'api_error')
    grading_error_count = sum(1 for r in results if r['status'] == 'grading_error')
    
    log_message(f"总题目数: {total_questions}")
    log_message(f"成功测试: {success_count}")
    log_message(f"API错误: {api_error_count}")
    log_message(f"判题错误: {grading_error_count}")
    
    if success_count > 0:
        successful_results = [r for r in results if r['status'] == 'success']
        avg_score = sum(r['score'] for r in successful_results) / len(successful_results)
        avg_length = sum(r['gpt_answer_length'] for r in successful_results) / len(successful_results)
        correct_count = sum(1 for r in successful_results if r['correct'])
        
        log_message(f"\n成功测试的题目统计:")
        log_message(f"  平均分数: {avg_score:.2f}")
        log_message(f"  平均回答长度: {avg_length:.0f} 字符")
        log_message(f"  正确数: {correct_count}/{success_count}")
        log_message(f"  正确率: {correct_count/success_count*100:.2f}%")
    
    log_message(f"\n结果已保存到: {OUTPUT_FILE}")
    log_message(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
