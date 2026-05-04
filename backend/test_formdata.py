#!/usr/bin/env python3
"""
Test script to simulate FormData upload like the browser
"""
import requests
import io
from pathlib import Path

def test_formdata_upload():
    """Test the analyze endpoint with FormData like browser"""
    
    url = "http://localhost:8000/api/analyze"
    
    print("Testing FormData upload...")
    
    # Create a dummy PDF file content (minimal PDF)
    pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF'
    
    # Create files dict for requests
    files = {
        'resume': ('test.pdf', pdf_content, 'application/pdf')
    }
    
    # Create form data
    data = {
        'target_role': 'Software Engineer'
    }
    
    try:
        # Send request exactly like browser would
        response = requests.post(
            url, 
            files=files, 
            data=data,
            headers={
                'Accept': 'application/json'
            }
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("SUCCESS! Response:")
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        else:
            print(f"Error {response.status_code}:")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_formdata_upload()
