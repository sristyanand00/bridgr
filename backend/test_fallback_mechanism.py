#!/usr/bin/env python3
"""
Test the Gemini -> Groq fallback mechanism in LLM service
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.llm_service import llm_service
from dotenv import load_dotenv

load_dotenv()

def test_fallback_mechanism():
    """Test if the system properly falls back from Gemini to Groq"""
    
    print("🔄 Testing Gemini -> Groq Fallback Mechanism")
    print("=" * 50)
    
    # Test 1: Check API Keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    print(f"🔑 Gemini API Key: {'✅ Present' if gemini_key else '❌ Missing'}")
    print(f"🔑 Groq API Key: {'✅ Present' if groq_key else '❌ Missing'}")
    
    # Test 2: Test Gemini directly (should fail due to quota)
    print("\n📡 Testing Gemini API...")
    try:
        from google.generativeai import GenerativeModel
        import google.generativeai as genai
        
        if gemini_key:
            genai.configure(api_key=gemini_key)
            model = GenerativeModel("gemini-2.0-flash")
            response = model.generate_content("test")
            print("✅ Gemini working")
        else:
            print("❌ No Gemini key")
    except Exception as e:
        print(f"❌ Gemini failed: {e}")
        print("🔄 Should fallback to Groq")
    
    # Test 3: Test Groq directly
    print("\n📡 Testing Groq API...")
    try:
        from groq import Groq
        
        if groq_key:
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            print("✅ Groq working")
        else:
            print("❌ No Groq key")
    except Exception as e:
        print(f"❌ Groq failed: {e}")
    
    # Test 4: Test LLM Service fallback for roadmap
    print("\n🎯 Testing LLM Service Roadmap Fallback...")
    try:
        result = llm_service.generate_roadmap_with_gemini(
            target_role="Software Engineer",
            match_score=25,
            missing_required=[{"name": "React"}, {"name": "Node.js"}],
            matched_skills=["Python"],
            total_days=90
        )
        
        if result:
            print("✅ LLM Service succeeded!")
            print(f"📊 Phases: {len(result.get('phases', []))}")
            print(f"📝 Summary: {result.get('summary', '')[:100]}...")
        else:
            print("❌ LLM Service returned None")
            
    except Exception as e:
        print(f"❌ LLM Service failed: {e}")
    
    # Test 5: Test LLM Service fallback for feasibility
    print("\n🎯 Testing LLM Service Feasibility Fallback...")
    try:
        result = llm_service.generate_feasibility_score_with_gemini(
            target_role="Software Engineer",
            match_score=25,
            user_skills=["Python"],
            missing_required=[{"name": "React"}, {"name": "Node.js"}],
            current_role="Developer"
        )
        
        if result:
            print("✅ Feasibility score generated!")
            print(f"📊 Score: {result.get('score')}")
            print(f"📝 Reasoning: {result.get('reasoning', '')[:100]}...")
        else:
            print("❌ Feasibility score returned None")
            
    except Exception as e:
        print(f"❌ Feasibility score failed: {e}")

if __name__ == "__main__":
    test_fallback_mechanism()
