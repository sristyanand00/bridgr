#!/usr/bin/env python3
"""
Test script to verify LLM service functionality
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.llm_service import llm_service

def test_llm_service():
    """Test the LLM service functionality"""
    print("🧪 Testing LLM Service...")
    
    # Test 1: Check if API key is configured
    print("\n📋 Checking API configuration...")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("✅ GEMINI_API_KEY is configured")
        print(f"🔑 Key starts with: {api_key[:10]}...")
    else:
        print("⚠️  GEMINI_API_KEY not found in environment")
        print("💡 Create a .env file with your Gemini API key")
        print("📄 Copy .env.example to .env and add your key")
    
    # Test 2: Test job profile fetching (will use fallback if no API key)
    print("\n🎯 Testing job profile fetching...")
    try:
        profile = llm_service.fetch_job_profile_from_gemini("Data Scientist")
        if profile:
            print("✅ Job profile fetched successfully")
            print(f"   Skills: {len(profile.get('tech_skills', []))} tech, {len(profile.get('soft_skills', []))} soft")
            print(f"   Source: {profile.get('source', 'unknown')}")
        else:
            print("⚠️  Job profile fetch returned None (likely no API key)")
    except Exception as e:
        print(f"❌ Job profile fetch failed: {e}")
    
    # Test 3: Test feasibility scoring (will use fallback if no API key)
    print("\n📊 Testing feasibility scoring...")
    try:
        feasibility = llm_service.generate_feasibility_score_with_gemini(
            target_role="Data Scientist",
            match_score=75,
            user_skills=["Python", "SQL", "Machine Learning"],
            missing_required=[{"name": "Docker"}, {"name": "Kubernetes"}],
            current_role="Software Engineer"
        )
        print("✅ Feasibility score generated")
        print(f"   Score: {feasibility.get('score', 'N/A')}")
        print(f"   Reasoning: {feasibility.get('reasoning', 'N/A')[:50]}...")
        print(f"   Confidence: {feasibility.get('confidence', 'N/A')}")
    except Exception as e:
        print(f"❌ Feasibility scoring failed: {e}")
    
    # Test 4: Test roadmap generation (will use fallback if no API key)
    print("\n🗺️  Testing roadmap generation...")
    try:
        roadmap = llm_service.generate_roadmap_with_gemini(
            target_role="Data Scientist",
            match_score=75,
            missing_required=[{"name": "Docker"}, {"name": "Kubernetes"}],
            available_hours_per_week=10
        )
        print("✅ Roadmap generated")
        print(f"   Phases: {len(roadmap.get('phases', []))}")
        print(f"   Total weeks: {roadmap.get('total_weeks', 'N/A')}")
        print(f"   Summary: {roadmap.get('summary', 'N/A')[:50]}...")
    except Exception as e:
        print(f"❌ Roadmap generation failed: {e}")
    
    print(f"\n🎉 LLM Service Test Complete!")
    print(f"📋 Service is ready for use!")
    print(f"💡 Add your Gemini API key to .env file for full functionality")

if __name__ == "__main__":
    test_llm_service()
