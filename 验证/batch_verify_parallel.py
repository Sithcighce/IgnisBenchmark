#!/usr/bin/env python3
"""
Parallel Batch Answer Verification Script
- Uses 3 models: Claude Sonnet 4.5, GPT-5, Gemini 2.5 Pro
- Processes 1200+ questions with 50 concurrent requests
- Saves pass/fail results separately
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
OPENROUTER_API_BASE = os.getenv('OPENROUTER_API_BASE', 'https://openrouter.ai/api/v1')

# Configuration
VERIFY_DIR = Path(__file__).parent
QUESTION_FILE = VERIFY_DIR / 'question.json'
PROMPT_FILE = VERIFY_DIR / '判题prompt'

# Output structure
OUTPUT_DIR = VERIFY_DIR / 'verification_output'
TEMP_DIR = OUTPUT_DIR / 'temp'
PASS_FILE = VERIFY_DIR / 'pass.json'
NOTPASS_FILE = VERIFY_DIR / 'notpass.json'
STATS_FILE = VERIFY_DIR / 'verification_stats.json'
LOG_FILE = VERIFY_DIR / 'batch_verification.log'

# Models to use
MODELS = [
    "anthropic/claude-sonnet-4.5",
    "openai/gpt-5", 
    "google/gemini-2.5-pro"
]

# Concurrency settings
MAX_CONCURRENT = 50
REQUEST_TIMEOUT = 180

# Thread-safe counters
stats_lock = Lock()
global_stats = {
    "total_questions": 0,
    "total_verifications": 0,
    "completed_verifications": 0,
    "failed_verifications": 0,
    "api_errors": defaultdict(int),
    "model_stats": {model: {"success": 0, "failed": 0} for model in MODELS}
}


def log_message(msg):
    """Thread-safe logging"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {msg}\n"
    
    with stats_lock:
        print(msg)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)


def load_prompt_template():
    """Load the judgment prompt template"""
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE}")
    return PROMPT_FILE.read_text(encoding='utf-8')


def format_original_text(original_text_dict):
    """Format the original_text dictionary into readable string"""
    if not original_text_dict:
        return "No original text provided"
    
    lines = []
    for key, value in sorted(original_text_dict.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        lines.append(f"[{key}] {value}")
    return "\n".join(lines)


def call_openrouter_api(prompt, model, max_retries=3):
    """Call OpenRouter API with retry logic"""
    url = f"{OPENROUTER_API_BASE}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert in combustion science and thermophysics. You must respond with valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            
            # Handle rate limits
            if response.status_code == 429:
                wait_time = min(2 ** attempt * 2, 30)  # Exponential backoff, max 30s
                log_message(f"⚠ Rate limit for {model}, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            # Log error details
            with stats_lock:
                global_stats["api_errors"][f"{model}_status_{response.status_code}"] += 1
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"API Error {response.status_code}: {response.text[:300]}")
                
        except requests.exceptions.Timeout:
            with stats_lock:
                global_stats["api_errors"][f"{model}_timeout"] += 1
            if attempt < max_retries - 1:
                log_message(f"⚠ Timeout for {model}, retry {attempt+1}/{max_retries}")
                time.sleep(2 ** attempt)
            else:
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
    
    raise Exception(f"Failed after {max_retries} retries")


def verify_with_model(question_item, prompt_template, model):
    """Verify a single question with a specific model"""
    question_text = question_item.get('question_text', '')
    standard_answer = question_item.get('standard_answer', '')
    original_text_dict = question_item.get('original_text', {})
    question_id = question_item.get('question_id', 'unknown')
    
    # Format original text
    original_text = format_original_text(original_text_dict)
    
    # Fill in the prompt template
    filled_prompt = prompt_template.replace('{question_text}', question_text)
    filled_prompt = filled_prompt.replace('{standard_answer}', standard_answer)
    filled_prompt = filled_prompt.replace('{original_text}', original_text)
    filled_prompt += "\n\nIMPORTANT: Respond ONLY with the JSON object as specified in the Output Format section. Do not include any markdown code blocks or additional text."
    
    try:
        # Call API
        response_text = call_openrouter_api(filled_prompt, model)
        
        # Extract JSON from response
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif response_text.startswith('```'):
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Parse JSON response
        verification_result = json.loads(response_text)
        
        # Add model info
        model_short = model.split('/')[-1]
        verification_result['model_name'] = model
        verification_result['model_short'] = model_short
        verification_result['verified_at'] = datetime.now().isoformat()
        
        with stats_lock:
            global_stats["completed_verifications"] += 1
            global_stats["model_stats"][model]["success"] += 1
        
        return {
            "success": True,
            "model": model,
            "result": verification_result
        }
        
    except Exception as e:
        with stats_lock:
            global_stats["failed_verifications"] += 1
            global_stats["model_stats"][model]["failed"] += 1
        
        log_message(f"✗ Error verifying {question_id} with {model}: {str(e)[:200]}")
        
        return {
            "success": False,
            "model": model,
            "error": str(e),
            "verified_at": datetime.now().isoformat()
        }


def process_single_question(question_item, prompt_template, question_idx, total_questions):
    """Process a single question with all 3 models"""
    question_id = question_item.get('question_id', f'q_{question_idx}')
    
    log_message(f"Processing [{question_idx}/{total_questions}] {question_id}")
    
    # Verify with all models
    verification_results = []
    for model in MODELS:
        result = verify_with_model(question_item, prompt_template, model)
        verification_results.append(result)
    
    # Aggregate results
    successful_verifications = [v["result"] for v in verification_results if v["success"]]
    failed_verifications = [v for v in verification_results if not v["success"]]
    
    # Determine consensus
    if len(successful_verifications) >= 2:  # At least 2 models succeeded
        correct_votes = sum(1 for v in successful_verifications if v.get("correct") is True)
        all_correct = all(v.get("correct") is True for v in successful_verifications)
        all_high_confidence = all(v.get("verification_confidence") == "high" for v in successful_verifications)
        
        consensus = {
            "all_correct": all_correct,
            "correct_votes": correct_votes,
            "total_votes": len(successful_verifications),
            "all_high_confidence": all_high_confidence,
            "disagreement_count": len(successful_verifications) - correct_votes if all_correct else correct_votes
        }
        
        # Determine status
        if all_correct and all_high_confidence:
            status = "approved"
        elif correct_votes >= 2:
            status = "approved"
        elif correct_votes == 0:
            status = "rejected"
        else:
            status = "needs_review"
    else:
        # Not enough successful verifications
        status = "needs_review"
        consensus = {
            "all_correct": False,
            "correct_votes": 0,
            "total_votes": len(successful_verifications),
            "all_high_confidence": False,
            "disagreement_count": 0,
            "note": f"Only {len(successful_verifications)} model(s) completed verification"
        }
    
    # Build final result
    result_item = question_item.copy()
    result_item["verification"] = {
        "status": status,
        "verifiers": successful_verifications,
        "failed_verifiers": failed_verifications if failed_verifications else [],
        "verified_at": datetime.now().isoformat(),
        "consensus": consensus
    }
    
    # Save to temp file (for parallel safety)
    temp_file = TEMP_DIR / f"{question_id}_{status}.json"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(result_item, f, ensure_ascii=False, indent=2)
    
    log_message(f"✓ Completed [{question_idx}/{total_questions}] {question_id} -> {status}")
    
    return {
        "question_id": question_id,
        "status": status,
        "temp_file": temp_file
    }


def merge_results():
    """Merge all temp files into pass.json and notpass.json"""
    log_message("=" * 80)
    log_message("Merging results...")
    
    pass_items = []
    notpass_items = []
    
    for temp_file in TEMP_DIR.glob("*.json"):
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                item = json.load(f)
            
            status = item.get("verification", {}).get("status", "needs_review")
            
            if status == "approved":
                pass_items.append(item)
            else:
                notpass_items.append(item)
                
        except Exception as e:
            log_message(f"⚠ Error reading {temp_file}: {e}")
    
    # Save results
    if pass_items:
        with open(PASS_FILE, 'w', encoding='utf-8') as f:
            json.dump(pass_items, f, ensure_ascii=False, indent=2)
        log_message(f"✓ Saved {len(pass_items)} approved questions to {PASS_FILE}")
    
    if notpass_items:
        with open(NOTPASS_FILE, 'w', encoding='utf-8') as f:
            json.dump(notpass_items, f, ensure_ascii=False, indent=2)
        log_message(f"✓ Saved {len(notpass_items)} not-approved questions to {NOTPASS_FILE}")
    
    return len(pass_items), len(notpass_items)


def generate_statistics(pass_count, notpass_count):
    """Generate detailed statistics"""
    log_message("=" * 80)
    log_message("Generating statistics...")
    
    stats = {
        "generation_time": datetime.now().isoformat(),
        "models_used": MODELS,
        "concurrency": MAX_CONCURRENT,
        "total_questions": global_stats["total_questions"],
        "total_verifications": global_stats["total_verifications"],
        "completed_verifications": global_stats["completed_verifications"],
        "failed_verifications": global_stats["failed_verifications"],
        "results": {
            "approved": pass_count,
            "not_approved": notpass_count,
            "approval_rate": f"{pass_count/max(1, global_stats['total_questions'])*100:.2f}%"
        },
        "model_performance": global_stats["model_stats"],
        "api_errors": dict(global_stats["api_errors"])
    }
    
    # Analyze pass.json for more details
    if PASS_FILE.exists():
        with open(PASS_FILE, 'r', encoding='utf-8') as f:
            pass_items = json.load(f)
        
        # Analyze consensus
        all_correct_count = sum(1 for item in pass_items 
                                if item.get("verification", {}).get("consensus", {}).get("all_correct") is True)
        all_high_conf_count = sum(1 for item in pass_items 
                                  if item.get("verification", {}).get("consensus", {}).get("all_high_confidence") is True)
        
        stats["pass_details"] = {
            "all_models_correct": all_correct_count,
            "all_high_confidence": all_high_conf_count,
            "unanimous_approval_rate": f"{all_correct_count/max(1, pass_count)*100:.2f}%"
        }
        
        # Analyze by difficulty
        difficulty_dist = defaultdict(int)
        for item in pass_items:
            diff = item.get("difficulty", "unknown")
            difficulty_dist[str(diff)] += 1
        stats["pass_by_difficulty"] = dict(difficulty_dist)
        
        # Analyze by topic
        topic_dist = defaultdict(int)
        for item in pass_items:
            topic = item.get("topic", "unknown")
            topic_dist[topic] += 1
        stats["pass_by_topic"] = dict(topic_dist)
    
    # Analyze notpass.json
    if NOTPASS_FILE.exists():
        with open(NOTPASS_FILE, 'r', encoding='utf-8') as f:
            notpass_items = json.load(f)
        
        # Count needs_review vs rejected
        needs_review = sum(1 for item in notpass_items 
                          if item.get("verification", {}).get("status") == "needs_review")
        rejected = sum(1 for item in notpass_items 
                      if item.get("verification", {}).get("status") == "rejected")
        
        stats["notpass_details"] = {
            "needs_review": needs_review,
            "rejected": rejected
        }
    
    # Save statistics
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    log_message(f"✓ Statistics saved to {STATS_FILE}")
    
    return stats


def print_summary(stats):
    """Print a beautiful summary"""
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"\n📊 Overall Results:")
    print(f"   Total Questions: {stats['total_questions']}")
    print(f"   Total Verifications: {stats['total_verifications']} (3 models × questions)")
    print(f"   Completed: {stats['completed_verifications']}")
    print(f"   Failed: {stats['failed_verifications']}")
    print(f"\n✅ Pass/Fail Distribution:")
    print(f"   Approved: {stats['results']['approved']} ({stats['results']['approval_rate']})")
    print(f"   Not Approved: {stats['results']['not_approved']}")
    
    if "pass_details" in stats:
        print(f"\n🎯 Pass Quality:")
        print(f"   All Models Agreed (Correct): {stats['pass_details']['all_models_correct']}")
        print(f"   All High Confidence: {stats['pass_details']['all_high_confidence']}")
        print(f"   Unanimous Approval Rate: {stats['pass_details']['unanimous_approval_rate']}")
    
    if "notpass_details" in stats:
        print(f"\n⚠️  Not Approved Breakdown:")
        print(f"   Needs Review: {stats['notpass_details']['needs_review']}")
        print(f"   Rejected: {stats['notpass_details']['rejected']}")
    
    print(f"\n🤖 Model Performance:")
    for model, perf in stats['model_performance'].items():
        model_short = model.split('/')[-1]
        total = perf['success'] + perf['failed']
        success_rate = perf['success'] / max(1, total) * 100
        print(f"   {model_short}: {perf['success']}/{total} ({success_rate:.1f}% success)")
    
    if "pass_by_difficulty" in stats:
        print(f"\n📈 Pass by Difficulty:")
        for diff, count in sorted(stats['pass_by_difficulty'].items()):
            print(f"   Level {diff}: {count} questions")
    
    if "pass_by_topic" in stats:
        print(f"\n📚 Pass by Topic (Top 5):")
        sorted_topics = sorted(stats['pass_by_topic'].items(), key=lambda x: x[1], reverse=True)[:5]
        for topic, count in sorted_topics:
            print(f"   {topic}: {count} questions")
    
    if stats['api_errors']:
        print(f"\n⚠️  API Errors:")
        for error_type, count in stats['api_errors'].items():
            print(f"   {error_type}: {count}")
    
    print("\n" + "=" * 80)
    print(f"✅ Results saved to:")
    print(f"   Pass: {PASS_FILE}")
    print(f"   Not Pass: {NOTPASS_FILE}")
    print(f"   Statistics: {STATS_FILE}")
    print(f"   Log: {LOG_FILE}")
    print("=" * 80 + "\n")


def main():
    """Main execution"""
    print("=" * 80)
    print("PARALLEL BATCH VERIFICATION")
    print("=" * 80)
    print(f"Models: {', '.join([m.split('/')[-1] for m in MODELS])}")
    print(f"Concurrency: {MAX_CONCURRENT}")
    print("=" * 80 + "\n")
    
    # Check API key
    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not found in .env file")
        return
    
    # Setup directories
    OUTPUT_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    
    # Clear old temp files
    for f in TEMP_DIR.glob("*.json"):
        f.unlink()
    
    # Load prompt template
    log_message("Loading prompt template...")
    prompt_template = load_prompt_template()
    
    # Load questions
    log_message("Loading questions...")
    with open(QUESTION_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    total_questions = len(questions)
    global_stats["total_questions"] = total_questions
    global_stats["total_verifications"] = total_questions * len(MODELS)
    
    log_message(f"Loaded {total_questions} questions")
    log_message(f"Total verifications to perform: {global_stats['total_verifications']}")
    log_message("=" * 80)
    
    # Process in parallel
    log_message(f"Starting parallel verification with {MAX_CONCURRENT} workers...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        futures = {
            executor.submit(process_single_question, q, prompt_template, i, total_questions): i
            for i, q in enumerate(questions, 1)
        }
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            try:
                result = future.result()
                if completed % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = completed / elapsed
                    eta = (total_questions - completed) / rate if rate > 0 else 0
                    log_message(f"Progress: {completed}/{total_questions} ({completed/total_questions*100:.1f}%) - ETA: {eta/60:.1f}min")
            except Exception as e:
                log_message(f"✗ Error in future: {e}")
    
    elapsed = time.time() - start_time
    log_message(f"✓ All questions processed in {elapsed/60:.2f} minutes")
    
    # Merge results
    pass_count, notpass_count = merge_results()
    
    # Generate statistics
    stats = generate_statistics(pass_count, notpass_count)
    
    # Print summary
    print_summary(stats)


if __name__ == '__main__':
    main()
