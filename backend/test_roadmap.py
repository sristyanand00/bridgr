#!/usr/bin/env python3
"""
Test script to debug the /api/roadmap endpoint
"""
import requests
import json

def test_roadmap_endpoint():
    """Test the roadmap endpoint with sample data"""
    
    url = "http://localhost:8000/api/roadmap"
    
    print("Testing /api/roadmap endpoint...")
    
    # Sample payload similar to what frontend sends
    payload = {
        "target_role": "Software Engineer",
        "match_score": 25,
        "readiness_level": "Foundation Stage",
        "roadmap_inputs": {
            "phases": [
                {
                    "phase": 1,
                    "label": "Foundation Building",
                    "duration_weeks": 4,
                    "skills": ["Python", "JavaScript", "Data Structures"],
                    "resources": ["Python Tutorial|https://docs.python.org", "JS Guide|https://developer.mozilla.org"]
                },
                {
                    "phase": 2,
                    "label": "Advanced Skills",
                    "duration_weeks": 4,
                    "skills": ["React", "Node.js", "Databases"],
                    "resources": ["React Docs|https://react.dev", "Node Guide|https://nodejs.org"]
                }
            ],
            "total_estimated_weeks": 8
        },
        "matched_skills": ["Python", "Problem Solving"],
        "missing_required": ["React", "Node.js", "Databases"],
        "total_days": 90
    }
    
    try:
        print(f"Sending POST request to {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            url, 
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("SUCCESS! Roadmap generated:")
            result = response.json()
            print(f"Phases: {len(result.get('phases', []))}")
            print(f"Total weeks: {result.get('total_weeks')}")
            print(f"Total days: {result.get('total_days')}")
            print(f"Summary: {result.get('summary', '')[:200]}...")
        else:
            print(f"Error {response.status_code}:")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_roadmap_endpoint()
