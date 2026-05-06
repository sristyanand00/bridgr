#!/usr/bin/env python3
"""
Test Groq API directly to debug JSON parsing issues
"""
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

print('Testing Groq directly...')
try:
    response = client.chat.completions.create(
        model='llama-3.1-8b-instant',
        messages=[{'role': 'user', 'content': 'Respond with just: {"status": "ok"}'}],
        temperature=0.7,
        max_tokens=100
    )
    content = response.choices[0].message.content
    print('Raw response:', repr(content))
    print('Content:', content)
    
    # Try to parse as JSON
    import json
    try:
        parsed = json.loads(content)
        print('Parsed JSON:', parsed)
    except json.JSONDecodeError as e:
        print('JSON parsing error:', e)
        
except Exception as e:
    print('Groq error:', e)
