#!/usr/bin/env python3
"""
Answer Verification Script using OpenRouter API (GPT-4o model)
Verifies answers in question.json using the judgment prompt
"""
import json
import os
import random
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_API_BASE = os.getenv('OPENROUTER_API_BASE', 'https://openrouter.ai/api/v1')

VERIFY_DIR = Path(__file__).parent
QUESTION_FILE = VERIFY_DIR / 'question.json'
PROMPT_FILE = VERIFY_DIR / '判题prompt'
RESULT_FILE = VERIFY_DIR / 'verification_results.json'
LOG_FILE = VERIFY_DIR / 'verification.log'


def load_prompt_template():
    """Load the judgment prompt template"""
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE}")
    return PROMPT_FILE.read_text(encoding='utf-8')


def load_questions(sample_size=None):
    """Load questions from question.json"""
    if not QUESTION_FILE.exists():
        raise FileNotFoundError(f"Question file not found: {QUESTION_FILE}")
    
    data = json.loads(QUESTION_FILE.read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise ValueError("Question file should contain a JSON array")
    
    # Sample if requested
    if sample_size and sample_size < len(data):
        data = random.sample(data, sample_size)
    
    return data


def format_original_text(original_text_dict):
    """Format the original_text dictionary into readable string"""
    if not original_text_dict:
        return "No original text provided"
    
    lines = []
    for key, value in sorted(original_text_dict.items(), key=lambda x: int(x[0])):
        lines.append(f"[{key}] {value}")
    return "\n".join(lines)


def call_openrouter_api(prompt, model="anthropic/claude-3.5-sonnet"):
    """Call OpenRouter API with the given prompt
    
    Available models that support CN region:
    - anthropic/claude-3.5-sonnet (recommended)
    - anthropic/claude-3-opus
    - google/gemini-pro-1.5-exp
    - meta-llama/llama-3.1-405b-instruct
    """
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
        "temperature": 0.1,  # Low temperature for consistent verification
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        # Print detailed error info if request fails
        if response.status_code != 200:
            print(f"\n⚠ API Error Details:")
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
        
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
        
    except requests.exceptions.RequestException as e:
        print(f"\n⚠ Request Exception: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response text: {e.response.text[:500]}")
        raise


def verify_question(question_item, prompt_template):
    """Verify a single question using the prompt"""
    # Extract fields
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
    
    # Add explicit JSON instruction
    filled_prompt += "\n\nIMPORTANT: Respond ONLY with the JSON object as specified in the Output Format section. Do not include any markdown code blocks or additional text."
    
    print(f"\nVerifying question: {question_id}")
    print(f"Question: {question_text[:100]}...")
    
    try:
        # Call API
        response_text = call_openrouter_api(filled_prompt)
        
        # Extract JSON from response (might be wrapped in markdown code blocks)
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif response_text.startswith('```'):
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Parse JSON response
        verification_result = json.loads(response_text)
        
        # Add metadata
        verification_result['question_id'] = question_id
        verification_result['verified_at'] = datetime.now().isoformat()
        
        print(f"✓ Correct: {verification_result.get('correct')}")
        print(f"  Verification Confidence: {verification_result.get('verification_confidence')}")
        
        return verification_result
        
    except Exception as e:
        print(f"✗ Error during verification: {e}")
        return {
            'question_id': question_id,
            'correct': None,
            'error': str(e),
            'verified_at': datetime.now().isoformat()
        }


def main():
    """Main verification workflow"""
    print("=" * 60)
    print("Answer Verification using OpenRouter API (Claude 3.5 Sonnet)")
    print("=" * 60)
    
    # Check API key
    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not found in .env file")
        return
    
    # Load prompt template
    print("\n1. Loading prompt template...")
    prompt_template = load_prompt_template()
    print(f"   Loaded from: {PROMPT_FILE}")
    
    # Load questions - sample 5 for testing
    print("\n2. Loading questions...")
    sample_size = 5  # Change this to verify more questions
    questions = load_questions(sample_size=sample_size)
    print(f"   Loaded {len(questions)} questions for verification")
    
    # Verify each question
    print(f"\n3. Starting verification (using model: anthropic/claude-3.5-sonnet)...")
    results = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i}/{len(questions)} ---")
        result = verify_question(question, prompt_template)
        results.append(result)
    
    # Save results
    print(f"\n4. Saving results...")
    RESULT_FILE.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"   Results saved to: {RESULT_FILE}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    correct_count = sum(1 for r in results if r.get('correct') is True)
    incorrect_count = sum(1 for r in results if r.get('correct') is False)
    error_count = sum(1 for r in results if r.get('correct') is None)
    
    print(f"Total verified: {len(results)}")
    print(f"  ✓ Correct: {correct_count}")
    print(f"  ✗ Incorrect: {incorrect_count}")
    print(f"  ⚠ Errors: {error_count}")
    
    # Show issues if any
    issues_found = [r for r in results if r.get('correct') is False or r.get('issues')]
    if issues_found:
        print(f"\n⚠ Questions with issues: {len(issues_found)}")
        for r in issues_found:
            print(f"\n  Question ID: {r.get('question_id')}")
            print(f"  Correct: {r.get('correct')}")
            if r.get('issues'):
                print(f"  Issues: {r.get('issues')}")
            print(f"  Reasoning: {r.get('reasoning', 'N/A')[:200]}...")
    
    print(f"\nFull results available in: {RESULT_FILE}")


if __name__ == '__main__':
    main()
