#!/usr/bin/env python3
"""
Test script to debug Gemini roadmap generation specifically
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def test_gemini_direct():
    """Test Gemini API directly for roadmap generation"""
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not found in .env")
        return
    
    print("🔑 Testing Gemini API directly...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Sample roadmap request
    prompt = """You are an expert teacher creating a personalised 90-day learning syllabus.

Student profile:
- Target role: Aerospace Engineer
- Current match score: 1%
- Skills ALREADY HAVE (do NOT teach these): Python, Machine Learning, Problem Solving
- Skills MISSING (focus syllabus on these): C++, CAD, Computational Fluid Dynamics
- Available study time: 10 hours/week

Create a 3-phase syllabus split as:
  Phase 1: Days 1 30   (Foundation)
  Phase 2: Days 31 60 (Core Skills)
  Phase 3: Days 61 90 (Job Ready)

Rules:
- Each phase has 2-4 topics
- Each topic has a title, day range within the phase, 3-5 subtopics to learn, one mini project, and one specific FREE resource
- Resources must be real URLs: freeCodeCamp, Kaggle, fast.ai, official docs, YouTube, MDN, CS50, etc.
- Do NOT teach skills they already have
- Mini projects should be concrete and buildable

Return ONLY valid JSON (no markdown, no extra text):
{
  "phases": [
    {
      "phase": 1,
      "label": "Foundation",
      "day_range": "Days 1 30",
      "goal": "Build fundamental programming and engineering concepts",
      "skills": ["C++ Programming", "Engineering Mathematics"],
      "milestones": ["Built basic C++ programs", "Completed math refresher"],
      "topics": [
        {
          "title": "C++ Fundamentals",
          "days": "Days 1 15",
          "subtopics": [
            "Variables and data types",
            "Control flow and functions",
            "Object-oriented programming basics"
          ],
          "mini_project": "Create a simple calculator program",
          "resource": {
            "name": "LearnCpp.com",
            "url": "https://www.learncpp.com/",
            "free": true
          }
        }
      ],
      "resources": [
        {"name": "LearnCpp.com", "url": "https://www.learncpp.com/", "free": true}
      ]
    }
  ],
  "total_weeks": 12,
  "total_days": 90,
  "summary": "A comprehensive 90-day plan to transition into Aerospace Engineering"
}"""

    try:
        print("📤 Sending request to Gemini...")
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        print("✅ Gemini responded successfully!")
        print("📄 Response:")
        print(response.text)
        
    except Exception as e:
        print(f"❌ Gemini API failed: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_gemini_direct()
