#!/usr/bin/env python3
"""
Test OpenRouter API connection
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_API_BASE = os.getenv('OPENROUTER_API_BASE', 'https://openrouter.ai/api/v1')

print(f"API Key (first 20 chars): {OPENROUTER_API_KEY[:20]}...")
print(f"API Base: {OPENROUTER_API_BASE}")

url = f"{OPENROUTER_API_BASE}/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": "openai/gpt-4o-mini",  # Use cheaper model for testing
    "messages": [
        {
            "role": "user",
            "content": "Say 'Hello, API is working!' in JSON format with a 'message' field."
        }
    ]
}

try:
    print("\nSending test request...")
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text[:1000]}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ Success!")
        print(f"Model used: {result.get('model')}")
        print(f"Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"\n✗ Error: {response.status_code}")
        
except Exception as e:
    print(f"\n✗ Exception: {e}")
