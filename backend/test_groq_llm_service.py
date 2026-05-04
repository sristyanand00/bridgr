#!/usr/bin/env python3
"""
Test the exact LLM service Groq call for roadmap generation
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv

# Import the exact functions from LLM service
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.llm_service import LLMService, _clean_json

load_dotenv()

def test_groq_llm_service():
    """Test the exact LLM service Groq call"""
    
    print("🔧 Testing LLM Service Groq integration...")
    
    # Create LLM service instance
    llm_service = LLMService()
    
    # Test the exact roadmap prompt
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
      "goal": "one sentence goal for this phase",
      "skills": ["skill1", "skill2"],
      "topics": [
        {
          "title": "Topic Name",
          "days": "Days 1 15",
          "subtopics": [
            "Specific thing to learn 1",
            "Specific thing to learn 2",
            "Specific thing to learn 3"
          ],
          "mini_project": "Concrete project description",
          "resource": {
            "name": "Exact Resource Name",
            "url": "https://real-url.com/...",
            "free": true
          }
        }
      ],
      "resources": [
        {"name": "Resource Name", "url": "https://...", "free": true}
      ]
    }
  ],
  "total_weeks": 12,
  "total_days": 90,
  "summary": "2-3 sentence personalised summary of the plan"
}"""

    try:
        print("📤 Calling LLM Service Groq method...")
        result = llm_service._try_groq(prompt, "roadmap for 'Aerospace Engineer' (90 days)")
        
        if result:
            print("✅ LLM Service Groq succeeded!")
            print(f"📊 Phases generated: {len(result.get('phases', []))}")
            print(f"📅 Total days: {result.get('total_days')}")
            print(f"📝 Summary: {result.get('summary', '')[:100]}...")
            
            # Check if it has the detailed structure
            if result.get('phases') and result['phases'][0].get('topics'):
                print("🎯 Teacher-style roadmap detected!")
                topic = result['phases'][0]['topics'][0]
                print(f"   First topic: {topic.get('title')}")
                print(f"   Subtopics: {len(topic.get('subtopics', []))}")
                print(f"   Mini-project: {topic.get('mini_project', '')[:50]}...")
            else:
                print("⚠️ Basic roadmap structure (missing detailed topics)")
                
            return result
        else:
            print("❌ LLM Service Groq returned None")
            return None
            
    except Exception as e:
        print(f"❌ LLM Service test failed: {e}")
        return None

if __name__ == "__main__":
    test_groq_llm_service()
