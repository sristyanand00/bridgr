#!/usr/bin/env python3
"""
Check available Gemini models
"""
import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def check_models():
    """Check available Gemini models"""
    print("🔍 Checking available Gemini models...")
    
    try:
        models = list(genai.list_models())
        print(f"✅ Found {len(models)} models:")
        
        for model in models:
            print(f"   - {model.name}")
            print(f"     Supported methods: {model.supported_generation_methods}")
            
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    check_models()
