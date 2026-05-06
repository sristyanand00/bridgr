#!/usr/bin/env python3
"""
Test the actual roadmap prompt with Groq to debug the issue
"""
from groq import Groq
import os
import json
from dotenv import load_dotenv
from services.llm_service import _clean_json

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Simplified roadmap prompt
prompt = """You are an expert teacher creating a personalised 90-day learning syllabus.

Student profile:
- Target role: Software Engineer
- Current match score: 25%
- Skills ALREADY HAVE: Python
- Skills MISSING: React, Node.js
- Available study time: 10 hours/week

Create a simple 2-phase syllabus.

Return ONLY valid JSON (no markdown, no extra text):
{
  "phases": [
    {
      "phase": 1,
      "label": "Foundation",
      "goal": "Build basic skills",
      "skills": ["React", "JavaScript"],
      "topics": [
        {
          "title": "React Basics",
          "days": "Days 1-30",
          "subtopics": ["Components", "Props", "State"],
          "mini_project": "Build a todo app",
          "resource": {
            "name": "React Tutorial",
            "url": "https://react.dev",
            "free": true
          }
        }
      ],
      "resources": [{"name": "React Docs", "url": "https://react.dev", "free": true}]
    }
  ],
  "total_weeks": 12,
  "total_days": 90,
  "summary": "Learn React and Node.js"
}"""

print('Testing roadmap prompt with Groq...')
try:
    response = client.chat.completions.create(
        model='llama-3.1-8b-instant',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.7,
        max_tokens=2048
    )
    content = response.choices[0].message.content
    print('Raw response:')
    print(content)
    print('\n' + '='*50 + '\n')
    
    # Try to clean and parse
    cleaned = _clean_json(content)
    print('Cleaned JSON:')
    print(cleaned)
    print('\n' + '='*50 + '\n')
    
    try:
        parsed = json.loads(cleaned)
        print('SUCCESS! Parsed JSON:')
        print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError as e:
        print('JSON parsing error:', e)
        
except Exception as e:
    print('Groq error:', e)
