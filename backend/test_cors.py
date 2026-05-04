#!/usr/bin/env python3
"""
Test CORS headers from backend
"""
import requests

def test_cors_headers():
    """Test if CORS headers are properly set"""
    
    url = "http://localhost:8000/api/roadmap"
    
    # Simulate a browser request from localhost:3000
    headers = {
        "Origin": "http://localhost:3000",
        "Content-Type": "application/json"
    }
    
    payload = {
        "target_role": "Software Engineer",
        "match_score": 25,
        "readiness_level": "Foundation Stage",
        "roadmap_inputs": {},
        "matched_skills": ["Python"],
        "missing_required": ["React"],
        "total_days": 90
    }
    
    try:
        print(f"🔍 Testing CORS headers for {url}")
        print(f"📤 Origin: {headers['Origin']}")
        
        response = requests.post(
            url, 
            json=payload,
            headers=headers
        )
        
        print(f"✅ Status: {response.status_code}")
        print(f"📋 CORS Headers:")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
        }
        
        for header, value in cors_headers.items():
            if value:
                print(f"  {header}: {value}")
            else:
                print(f"  {header}: ❌ MISSING")
        
        if response.status_code == 200:
            print("🎉 CORS is working correctly!")
            data = response.json()
            print(f"📊 Phases: {len(data.get('phases', []))}")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_cors_headers()
