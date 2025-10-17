#!/usr/bin/env python3
"""
GPT-5 Benchmark Test
1. Extract questions with full consensus (all 3 models agree)
2. Use GPT-5 to answer questions
3. Use DeepSeek to grade answers
4. Generate benchmark report
"""
import json
import os
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import requests
from dotenv import load_dotenv
from collections import defaultdict

# Load environment
load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_BASE = "https://api.deepseek.com"

# Configuration
VERIFY_DIR = Path(__file__).parent
PASS_FILE = VERIFY_DIR / 'pass.json'
BEST_FILE = VERIFY_DIR / 'best.json'
BENCHMARK_FILE = VERIFY_DIR / 'benchmarkGPT5.json'
STATS_FILE = VERIFY_DIR / 'gpt5_benchmark_stats.json'
LOG_FILE = VERIFY_DIR / 'gpt5_benchmark.log'

# Settings
MAX_CONCURRENT = 50
REQUEST_TIMEOUT = 180

# Thread-safe counters
stats_lock = Lock()
global_stats = {
    "total_questions": 0,
    "completed": 0,
    "failed": 0,
    "correct_answers": 0,
    "incorrect_answers": 0,
    "total_score": 0.0,
    "errors": defaultdict(int)
}


def log_message(msg):
    """Thread-safe logging"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {msg}\n"
    
    with stats_lock:
        print(msg)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)


def extract_best_questions():
    """提取三模型一致认可的题目"""
    log_message("=" * 80)
    log_message("Step 1: Extracting questions with full consensus")
    log_message("=" * 80)
    
    with open(PASS_FILE, 'r', encoding='utf-8') as f:
        all_passed = json.load(f)
    
    # Filter: all_correct = True
    best_questions = [
        q for q in all_passed
        if q.get('verification', {}).get('consensus', {}).get('all_correct') is True
    ]
    
    log_message(f"Total passed questions: {len(all_passed)}")
    log_message(f"Full consensus questions: {len(best_questions)}")
    log_message(f"Consensus rate: {len(best_questions)/len(all_passed)*100:.2f}%")
    
    # Save best.json
    with open(BEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(best_questions, f, ensure_ascii=False, indent=2)
    
    log_message(f"✓ Saved to: {BEST_FILE}")
    
    return best_questions


def format_original_text(original_text_dict):
    """Format the original_text dictionary into readable string"""
    if not original_text_dict:
        return "No original text provided"
    
    lines = []
    for key, value in sorted(original_text_dict.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        lines.append(f"[Citation {key}]: {value}")
    return "\n".join(lines)


def call_gpt5_to_answer(question_text: str, max_retries=3):
    """Call GPT-5 via OpenRouter to answer the question"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Build prompt
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
        "model": "openai/gpt-5",
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
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            
            # Handle rate limits
            if response.status_code == 429:
                wait_time = min(2 ** attempt * 2, 30)
                log_message(f"⚠ Rate limit, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            with stats_lock:
                global_stats["errors"][f"gpt5_status_{response.status_code}"] += 1
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"API Error {response.status_code}: {response.text[:300]}")
                
        except requests.exceptions.Timeout:
            with stats_lock:
                global_stats["errors"]["gpt5_timeout"] += 1
            if attempt < max_retries - 1:
                log_message(f"⚠ Timeout, retry {attempt+1}/{max_retries}")
                time.sleep(2 ** attempt)
            else:
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
    
    raise Exception(f"Failed after {max_retries} retries")


def call_deepseek_to_grade(question_text: str, standard_answer: str, gpt5_answer: str, 
                           original_text: str, max_retries=3):
    """Call DeepSeek API to grade the GPT-5 answer"""
    url = f"{DEEPSEEK_API_BASE}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Build grading prompt
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
{gpt5_answer}

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
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                answer_text = result['choices'][0]['message']['content'].strip()
                
                # Parse JSON
                if answer_text.startswith('```json'):
                    answer_text = answer_text.split('```json')[1].split('```')[0].strip()
                elif answer_text.startswith('```'):
                    answer_text = answer_text.split('```')[1].split('```')[0].strip()
                
                return json.loads(answer_text)
            
            with stats_lock:
                global_stats["errors"][f"deepseek_status_{response.status_code}"] += 1
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"API Error {response.status_code}: {response.text[:300]}")
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
    
    raise Exception(f"Failed after {max_retries} retries")


def process_single_question(question_item, question_idx, total_questions):
    """Process a single question: GPT-5 answer + DeepSeek grading"""
    question_id = question_item.get('question_id', f'q_{question_idx}')
    question_text = question_item.get('question_text', '')
    standard_answer = question_item.get('standard_answer', '')
    original_text_dict = question_item.get('original_text', {})
    
    log_message(f"Processing [{question_idx}/{total_questions}] {question_id}")
    
    try:
        # Step 1: Get GPT-5 answer
        gpt5_answer = call_gpt5_to_answer(question_text)
        log_message(f"  ✓ GPT-5 answered (length: {len(gpt5_answer)} chars)")
        
        # Step 2: Grade with DeepSeek
        original_text = format_original_text(original_text_dict)
        grading_result = call_deepseek_to_grade(
            question_text, standard_answer, gpt5_answer, original_text
        )
        log_message(f"  ✓ Graded: {'CORRECT' if grading_result.get('correct') else 'INCORRECT'} (Score: {grading_result.get('score', 0)})")
        
        # Update stats
        with stats_lock:
            global_stats["completed"] += 1
            if grading_result.get('correct'):
                global_stats["correct_answers"] += 1
            else:
                global_stats["incorrect_answers"] += 1
            global_stats["total_score"] += grading_result.get('score', 0)
        
        # Build result
        result = {
            "question_id": question_id,
            "question_text": question_text,
            "standard_answer": standard_answer,
            "original_text": original_text_dict,
            "gpt5_answer": gpt5_answer,
            "grading": {
                "correct": grading_result.get('correct'),
                "score": grading_result.get('score'),
                "issues": grading_result.get('issues', []),
                "reasoning": grading_result.get('reasoning', ''),
                "graded_at": datetime.now().isoformat()
            },
            "metadata": question_item.get('metadata', {}),
            "type": question_item.get('type'),
            "difficulty": question_item.get('difficulty'),
            "topic": question_item.get('topic')
        }
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        log_message(f"  ✗ Error: {str(e)[:200]}")
        
        with stats_lock:
            global_stats["failed"] += 1
            global_stats["errors"]["processing_error"] += 1
        
        return {
            "success": False,
            "question_id": question_id,
            "error": str(e)
        }


def generate_statistics(benchmark_results):
    """Generate detailed statistics"""
    log_message("=" * 80)
    log_message("Generating statistics...")
    
    stats = {
        "generation_time": datetime.now().isoformat(),
        "model_tested": "openai/gpt-5",
        "grading_model": "deepseek-chat",
        "total_questions": global_stats["total_questions"],
        "completed": global_stats["completed"],
        "failed": global_stats["failed"],
        "results": {
            "correct": global_stats["correct_answers"],
            "incorrect": global_stats["incorrect_answers"],
            "accuracy": f"{global_stats['correct_answers']/max(1, global_stats['completed'])*100:.2f}%",
            "average_score": global_stats["total_score"] / max(1, global_stats["completed"])
        },
        "errors": dict(global_stats["errors"])
    }
    
    # Analyze by difficulty
    difficulty_stats = defaultdict(lambda: {"total": 0, "correct": 0, "scores": []})
    for item in benchmark_results:
        if item.get("success"):
            result = item["result"]
            diff = result.get("difficulty", "unknown")
            difficulty_stats[str(diff)]["total"] += 1
            if result.get("grading", {}).get("correct"):
                difficulty_stats[str(diff)]["correct"] += 1
            difficulty_stats[str(diff)]["scores"].append(result.get("grading", {}).get("score", 0))
    
    stats["by_difficulty"] = {}
    for diff, data in difficulty_stats.items():
        stats["by_difficulty"][diff] = {
            "total": data["total"],
            "correct": data["correct"],
            "accuracy": f"{data['correct']/max(1, data['total'])*100:.2f}%",
            "avg_score": sum(data["scores"]) / max(1, len(data["scores"]))
        }
    
    # Analyze by topic
    topic_stats = defaultdict(lambda: {"total": 0, "correct": 0, "scores": []})
    for item in benchmark_results:
        if item.get("success"):
            result = item["result"]
            topic = result.get("topic", "unknown")
            topic_stats[topic]["total"] += 1
            if result.get("grading", {}).get("correct"):
                topic_stats[topic]["correct"] += 1
            topic_stats[topic]["scores"].append(result.get("grading", {}).get("score", 0))
    
    stats["by_topic"] = {}
    for topic, data in sorted(topic_stats.items(), key=lambda x: x[1]["total"], reverse=True)[:10]:
        stats["by_topic"][topic] = {
            "total": data["total"],
            "correct": data["correct"],
            "accuracy": f"{data['correct']/max(1, data['total'])*100:.2f}%",
            "avg_score": sum(data["scores"]) / max(1, len(data["scores"]))
        }
    
    # Analyze by type
    type_stats = defaultdict(lambda: {"total": 0, "correct": 0, "scores": []})
    for item in benchmark_results:
        if item.get("success"):
            result = item["result"]
            qtype = result.get("type", "unknown")
            type_stats[qtype]["total"] += 1
            if result.get("grading", {}).get("correct"):
                type_stats[qtype]["correct"] += 1
            type_stats[qtype]["scores"].append(result.get("grading", {}).get("score", 0))
    
    stats["by_type"] = {}
    for qtype, data in type_stats.items():
        stats["by_type"][qtype] = {
            "total": data["total"],
            "correct": data["correct"],
            "accuracy": f"{data['correct']/max(1, data['total'])*100:.2f}%",
            "avg_score": sum(data["scores"]) / max(1, len(data["scores"]))
        }
    
    # Save statistics
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    log_message(f"✓ Statistics saved to {STATS_FILE}")
    
    return stats


def print_summary(stats):
    """Print beautiful summary"""
    print("\n" + "=" * 80)
    print("GPT-5 BENCHMARK TEST SUMMARY")
    print("=" * 80)
    print(f"\n📊 Overall Results:")
    print(f"   Total Questions: {stats['total_questions']}")
    print(f"   Completed: {stats['completed']}")
    print(f"   Failed: {stats['failed']}")
    print(f"\n✅ Performance:")
    print(f"   Correct Answers: {stats['results']['correct']}/{stats['completed']}")
    print(f"   Accuracy: {stats['results']['accuracy']}")
    print(f"   Average Score: {stats['results']['average_score']:.2f}/100")
    
    if "by_difficulty" in stats:
        print(f"\n📈 Performance by Difficulty:")
        for diff in sorted(stats['by_difficulty'].keys()):
            data = stats['by_difficulty'][diff]
            print(f"   Level {diff}: {data['correct']}/{data['total']} ({data['accuracy']}) - Avg Score: {data['avg_score']:.2f}")
    
    if "by_type" in stats:
        print(f"\n📝 Performance by Type:")
        for qtype, data in sorted(stats['by_type'].items(), key=lambda x: x[1]['total'], reverse=True):
            print(f"   {qtype}: {data['correct']}/{data['total']} ({data['accuracy']}) - Avg Score: {data['avg_score']:.2f}")
    
    if "by_topic" in stats:
        print(f"\n📚 Performance by Topic (Top 5):")
        for i, (topic, data) in enumerate(list(stats['by_topic'].items())[:5], 1):
            print(f"   {i}. {topic}: {data['correct']}/{data['total']} ({data['accuracy']}) - Avg Score: {data['avg_score']:.2f}")
    
    if stats['errors']:
        print(f"\n⚠️  Errors:")
        for error_type, count in stats['errors'].items():
            print(f"   {error_type}: {count}")
    
    print("\n" + "=" * 80)
    print(f"✅ Results saved to:")
    print(f"   Benchmark: {BENCHMARK_FILE}")
    print(f"   Statistics: {STATS_FILE}")
    print(f"   Log: {LOG_FILE}")
    print("=" * 80 + "\n")


def main():
    """Main execution"""
    print("=" * 80)
    print("GPT-5 BENCHMARK TEST")
    print("=" * 80)
    print(f"Answer Model: GPT-5 (via OpenRouter)")
    print(f"Grading Model: DeepSeek (official API)")
    print(f"Concurrency: {MAX_CONCURRENT}")
    print("=" * 80 + "\n")
    
    # Check API keys
    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not found")
        return
    if not DEEPSEEK_API_KEY:
        print("ERROR: DEEPSEEK_API_KEY not found")
        return
    
    # Step 1: Extract best questions
    best_questions = extract_best_questions()
    global_stats["total_questions"] = len(best_questions)
    
    # Step 2: Process all questions
    log_message("\n" + "=" * 80)
    log_message("Step 2: Running GPT-5 benchmark test")
    log_message("=" * 80)
    log_message(f"Starting parallel processing with {MAX_CONCURRENT} workers...")
    
    start_time = time.time()
    benchmark_results = []
    
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        futures = {
            executor.submit(process_single_question, q, i, len(best_questions)): i
            for i, q in enumerate(best_questions, 1)
        }
        
        completed_count = 0
        for future in as_completed(futures):
            completed_count += 1
            try:
                result = future.result()
                benchmark_results.append(result)
                
                if completed_count % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = completed_count / elapsed
                    eta = (len(best_questions) - completed_count) / rate if rate > 0 else 0
                    log_message(f"Progress: {completed_count}/{len(best_questions)} ({completed_count/len(best_questions)*100:.1f}%) - ETA: {eta/60:.1f}min")
            except Exception as e:
                log_message(f"✗ Error in future: {e}")
    
    elapsed = time.time() - start_time
    log_message(f"✓ All questions processed in {elapsed/60:.2f} minutes")
    
    # Step 3: Save results
    log_message("\n" + "=" * 80)
    log_message("Step 3: Saving results")
    log_message("=" * 80)
    
    # Save benchmark results
    successful_results = [r["result"] for r in benchmark_results if r.get("success")]
    with open(BENCHMARK_FILE, 'w', encoding='utf-8') as f:
        json.dump(successful_results, f, ensure_ascii=False, indent=2)
    log_message(f"✓ Saved {len(successful_results)} results to {BENCHMARK_FILE}")
    
    # Step 4: Generate statistics
    stats = generate_statistics(benchmark_results)
    
    # Print summary
    print_summary(stats)


if __name__ == '__main__':
    main()
