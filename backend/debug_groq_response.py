#!/usr/bin/env python3
"""
Debug the exact Groq response to see the JSON issue
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def debug_groq_response():
    """Debug the exact Groq response"""
    
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = """You are an expert teacher creating a personalised 90-day learning syllabus.

Student profile:
- Target role: Aerospace Engineer
- Current match score: 1%
- Skills ALREADY HAVE: Python, Machine Learning
- Skills MISSING: C++, CAD, Computational Fluid Dynamics
- Available study time: 10 hours/week

Create a simple 3-phase syllabus. Return ONLY valid JSON:
{
  "phases": [
    {
      "phase": 1,
      "label": "Foundation",
      "day_range": "Days 1-30",
      "goal": "Build fundamental programming concepts",
      "skills": ["C++ Programming"],
      "topics": [
        {
          "title": "C++ Fundamentals",
          "days": "Days 1-15",
          "subtopics": ["Variables", "Control Flow", "Functions"],
          "mini_project": "Create a calculator program",
          "resource": {"name": "LearnCpp.com", "url": "https://www.learncpp.com/", "free": true}
        }
      ],
      "resources": [{"name": "LearnCpp.com", "url": "https://www.learncpp.com/", "free": true}]
    }
  ],
  "total_weeks": 12,
  "total_days": 90,
  "summary": "90-day plan to learn Aerospace Engineering skills"
}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048
        )
        
        content = response.choices[0].message.content
        print("🔍 Raw Groq Response:")
        print("=" * 50)
        print(content)
        print("=" * 50)
        
        # Try to parse the JSON
        try:
            # Clean the response first
            cleaned_content = content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            
            print("\n🧹 Cleaned JSON:")
            print("=" * 50)
            print(cleaned_content)
            print("=" * 50)
            
            # Try to parse
            parsed = json.loads(cleaned_content)
            print("\n✅ JSON Parsed Successfully!")
            print(f"Phases: {len(parsed.get('phases', []))}")
            
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON Parse Error: {e}")
            print(f"Error location: Line {e.lineno}, Column {e.colno}")
            
    except Exception as e:
        print(f"❌ Groq API failed: {e}")

if __name__ == "__main__":
    debug_groq_response()
