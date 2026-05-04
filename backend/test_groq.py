#!/usr/bin/env python3
"""
Test script to debug Groq API directly
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def test_groq_direct():
    """Test Groq API directly for roadmap generation"""
    
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found in .env")
        return
    
    print("🔑 Testing Groq API directly...")
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Sample roadmap request
        prompt = """You are an expert teacher creating a personalised 90-day learning syllabus.

Student profile:
- Target role: Aerospace Engineer
- Current match score: 1%
- Skills ALREADY HAVE: Python, Machine Learning
- Skills MISSING: C++, CAD, Computational Fluid Dynamics
- Available study time: 10 hours/week

Create a 3-phase syllabus with topics, subtopics, and mini-projects.
Return ONLY valid JSON:
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

        print("📤 Sending request to Groq...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048
        )
        
        print("✅ Groq responded successfully!")
        print("📄 Response:")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"❌ Groq API failed: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_groq_direct()
