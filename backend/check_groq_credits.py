#!/usr/bin/env python3
"""
Check Groq API credits and usage
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_groq_credits():
    """Check Groq API credits and usage"""
    
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found in .env")
        return
    
    print("🔑 Checking Groq API credits...")
    print(f"API Key: {GROQ_API_KEY[:20]}...{GROQ_API_KEY[-10:]}")
    
    # Groq doesn't have a public API endpoint for checking credits
    # But we can check by making a small API call and seeing the response headers
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Make a minimal API call to check if key is valid
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Groq API key is valid and working!")
            
            # Check rate limit headers if available
            rate_limit_headers = {
                'x-ratelimit-limit-requests': response.headers.get('x-ratelimit-limit-requests'),
                'x-ratelimit-remaining-requests': response.headers.get('x-ratelimit-remaining-requests'),
                'x-ratelimit-limit-tokens': response.headers.get('x-ratelimit-limit-tokens'),
                'x-ratelimit-remaining-tokens': response.headers.get('x-ratelimit-remaining-tokens'),
            }
            
            print("\n📊 Rate Limit Information:")
            for key, value in rate_limit_headers.items():
                if value:
                    print(f"  {key}: {value}")
            
        elif response.status_code == 401:
            print("❌ Invalid Groq API key")
        elif response.status_code == 429:
            print("⚠️ Rate limit exceeded - credits may be depleted")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking Groq credits: {e}")
    
    print("\n📝 For detailed usage, visit:")
    print("https://console.groq.com/keys")
    print("https://console.groq.com/usage")

if __name__ == "__main__":
    check_groq_credits()
