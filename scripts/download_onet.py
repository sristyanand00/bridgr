#!/usr/bin/env python3
"""
Download O*NET Dataset for Bridgr

This script downloads the O*NET database which contains:
- Job titles and descriptions
- Skills importance ratings  
- Technology skills requirements

Usage: python scripts/download_onet.py
"""

import os
import urllib.request
import zipfile
from pathlib import Path

# O*NET Database URLs (latest version 30.2)
ONET_URLS = {
    "db_30_2_text.zip": "https://www.onetcenter.org/dl_files/db_30_2_text.zip"
}

def download_onet_data():
    """Download and extract O*NET dataset."""
    
    # Create directories
    raw_dir = Path("data/raw")
    extract_dir = Path("data")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    print("📦 Downloading O*NET Database...")
    
    for filename, url in ONET_URLS.items():
        zip_path = raw_dir / filename
        
        # Download if not exists
        if not zip_path.exists():
            print(f"  Downloading {filename}...")
            try:
                urllib.request.urlretrieve(url, zip_path)
                print(f"  ✅ Downloaded: {zip_path}")
            except Exception as e:
                print(f"  ❌ Download failed: {e}")
                return False
        else:
            print(f"  ✅ Already exists: {zip_path}")
        
        # Extract if not already extracted
        db_folder = extract_dir / filename.replace('.zip', '')
        if not db_folder.exists():
            print(f"  Extracting {filename}...")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                print(f"  ✅ Extracted to: {db_folder}")
            except Exception as e:
                print(f"  ❌ Extraction failed: {e}")
                return False
        else:
            print(f"  ✅ Already extracted: {db_folder}")
    
    print("\n🎉 O*NET dataset setup complete!")
    print(f"   Data location: {extract_dir.absolute()}")
    
    # Verify required files
    required_files = [
        "db_30_2_text/Occupation Data.txt",
        "db_30_2_text/Skills.txt", 
        "db_30_2_text/Technology Skills.txt"
    ]
    
    print("\n📋 Verifying required files...")
    all_good = True
    for file_path in required_files:
        full_path = extract_dir / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ Missing: {file_path}")
            all_good = False
    
    if all_good:
        print("\n✨ All O*NET files ready! Your backend can now use real data.")
    else:
        print("\n⚠️  Some files are missing. Please check the download.")
    
    return all_good

if __name__ == "__main__":
    download_onet_data()
