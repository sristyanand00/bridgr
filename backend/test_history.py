#!/usr/bin/env python3
"""
Test the user history endpoint
"""
import requests
import json

def test_history_endpoint():
    """Test the user history endpoint"""
    
    url = "http://localhost:8000/api/user/history"
    
    print("🔍 Testing /api/user/history endpoint...")
    
    # Test without authentication (should fail)
    try:
        response = requests.get(url)
        print(f"❌ No auth - Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly requires authentication")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test with fake token (should fail)
    try:
        headers = {"Authorization": "Bearer fake_token"}
        response = requests.get(url, headers=headers)
        print(f"❌ Fake token - Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly rejects fake token")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n📝 To test with real authentication:")
    print("1. Login to the frontend app")
    print("2. Get the Firebase ID token from browser network tab")
    print("3. Test with: curl -H 'Authorization: Bearer <token>' http://localhost:8000/api/user/history")

if __name__ == "__main__":
    test_history_endpoint()
