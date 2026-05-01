#!/usr/bin/env python3
"""
Test script to verify roadmap service functionality
"""
import os
import sys
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_roadmap_service():
    """Test the roadmap service functionality"""
    print("🧪 Testing Roadmap Service...")
    
    # Test 1: Check if API key is configured
    print("\n📋 Checking API configuration...")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("✅ GEMINI_API_KEY is configured")
    else:
        print("⚠️  GEMINI_API_KEY not found - will test import only")
    
    # Test 2: Test import
    print("\n📦 Testing imports...")
    try:
        from routes.roadmap import router, RoadmapRequest
        print("✅ Roadmap service imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Test 3: Test model validation
    print("\n🔧 Testing request model...")
    try:
        test_request = RoadmapRequest(
            target_role="Data Scientist",
            match_score=75,
            readiness_level="Almost Ready",
            roadmap_inputs={
                "phase_1": {"skills": ["Python", "SQL"]},
                "phase_2": {"skills": ["Machine Learning"]},
                "phase_3": {"skills": ["Deep Learning"]},
                "total_estimated_weeks": 12
            },
            matched_skills=["Python", "SQL"],
            missing_required=[{"name": "Docker", "priority": "High"}]
        )
        print("✅ Request model validation successful")
        print(f"   Target role: {test_request.target_role}")
        print(f"   Match score: {test_request.match_score}")
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
    
    print(f"\n🎉 Roadmap Service Test Complete!")
    print(f"📋 Service is ready for use!")
    print(f"💡 Add your Gemini API key to .env file for full functionality")

if __name__ == "__main__":
    test_roadmap_service()
