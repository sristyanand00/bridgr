#!/usr/bin/env python3
"""
Test script to debug the /api/analyze endpoint 422 error
"""
import requests
import json
from pathlib import Path

def test_analyze_endpoint():
    """Test the analyze endpoint with sample data"""
    
    # Backend URL
    url = "http://localhost:8000/api/analyze"
    
    print("Testing /api/analyze endpoint...")
    
    # Test 1: Check if endpoint exists
    try:
        response = requests.get(url)
        print(f"GET {url}: {response.status_code}")
    except Exception as e:
        print(f"GET failed: {e}")
    
    # Test 2: Test with empty form data to see validation error
    try:
        response = requests.post(url, data={})
        print(f"POST empty: {response.status_code}")
        if response.status_code == 422:
            print("422 Error details:")
            print(response.text)
    except Exception as e:
        print(f"POST empty failed: {e}")
    
    # Test 3: Test with minimal required fields
    try:
        data = {
            'target_role': 'Software Engineer'
        }
        response = requests.post(url, data=data)
        print(f"POST with role only: {response.status_code}")
        if response.status_code == 422:
            print("422 Error details:")
            print(response.text)
    except Exception as e:
        print(f"POST with role failed: {e}")

if __name__ == "__main__":
    test_analyze_endpoint()
