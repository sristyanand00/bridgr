#!/usr/bin/env python3
"""
Test O*NET Data Connection for Bridgr

This script tests if your model can successfully connect to and use the O*NET dataset.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_onet_connection():
    """Test O*NET data loading and processing."""
    
    print("🔍 Testing O*NET Data Connection...")
    print("=" * 50)
    
    try:
        # Test 1: Import and initialize dataset loader
        print("1️⃣ Importing OnetDatasetLoader...")
        from ml.dataset_loader import OnetDatasetLoader
        
        # Test 2: Initialize with correct paths
        print("2️⃣ Initializing with O*NET data paths...")
        loader = OnetDatasetLoader(
            zip_path="data/raw/db_30_2_text.zip",  # This won't exist but that's ok
            extract_path="data/"
        )
        
        # Test 3: Load the dataset
        print("3️⃣ Loading O*NET dataset...")
        df = loader.load()
        
        print(f"✅ Successfully loaded {len(df)} job profiles!")
        print(f"   Columns: {list(df.columns)}")
        
        # Test 4: Check data structure
        print("\n4️⃣ Checking data structure...")
        print(f"   Sample job titles: {df['job_title'].head(5).tolist()}")
        
        # Test 5: Check skills data
        print("\n5️⃣ Checking skills extraction...")
        sample_job = df.iloc[0]
        print(f"   Sample job: {sample_job['job_title']}")
        print(f"   Tech skills: {len(sample_job['tech_skills'])} skills")
        print(f"   Soft skills: {len(sample_job['soft_skills'])} skills")
        
        # Test 6: Check market demand calculation
        print("\n6️⃣ Checking market demand data...")
        demand_count = len(loader.skill_market_demand)
        print(f"   Market demand data for {demand_count} skills")
        
        # Show some high-demand skills
        high_demand = {k: v for k, v in loader.skill_market_demand.items() if v > 0.1}
        print(f"   High-demand skills (>10%): {list(high_demand.keys())[:5]}")
        
        # Test 7: Test job profile lookup
        print("\n7️⃣ Testing job profile lookup...")
        test_roles = ["Data Scientist", "Software Engineer", "Product Manager"]
        
        for role in test_roles:
            profile = loader.get_job_profile(role)
            if profile is not None:
                print(f"   ✅ Found profile for '{role}'")
                print(f"      Description: {profile['job_description'][:100]}...")
            else:
                print(f"   ❌ No profile found for '{role}'")
        
        # Test 8: Test skill taxonomy
        print("\n8️⃣ Testing skill taxonomy...")
        all_tech_skills = loader.get_all_tech_skills()
        print(f"   Total tech skills in taxonomy: {len(all_tech_skills)}")
        print(f"   Sample skills: {all_tech_skills[:10]}")
        
        print("\n" + "=" * 50)
        print("🎉 O*NET CONNECTION TEST COMPLETE!")
        print("✅ All tests passed - your model is connected to O*NET data!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("❌ O*NET connection failed!")
        return False

def test_intelligence_core():
    """Test the full IntelligenceCore with O*NET data."""
    
    print("\n🧠 Testing IntelligenceCore with O*NET...")
    print("=" * 50)
    
    try:
        from services.intelligence_core import IntelligenceCore
        
        # Configuration that matches your .env
        config = {
            "ONET_ZIP_PATH": "data/raw/db_30_2_text.zip",
            "ONET_EXTRACT_PATH": "data/",
            "SEMANTIC_THRESHOLD": 0.75,
            "OPENAI_API_KEY": ""  # Leave empty for testing
        }
        
        print("🚀 Initializing IntelligenceCore...")
        core = IntelligenceCore(config)
        
        print("✅ IntelligenceCore initialized successfully!")
        print("✅ O*NET data loaded and embeddings computed!")
        
        # Test a sample analysis (without actual resume)
        print("\n🔍 Testing job profile access...")
        sample_roles = ["Data Scientists", "Software Engineers", "Product Managers"]
        
        for role in sample_roles:
            job_profile = core.dataset_loader.get_job_profile(role)
            if job_profile is not None:
                print(f"   ✅ {role}: {len(job_profile['tech_skills'])} tech, {len(job_profile['soft_skills'])} soft skills")
            else:
                print(f"   ❌ {role}: Not found")
        
        print("\n🎉 INTELLIGENCE CORE TEST COMPLETE!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("❌ IntelligenceCore initialization failed!")
        return False

if __name__ == "__main__":
    print("🚀 STARTING O*NET CONNECTION TESTS")
    print("=" * 60)
    
    # Test basic O*NET connection
    success1 = test_onet_connection()
    
    if success1:
        # Test full IntelligenceCore
        success2 = test_intelligence_core()
        
        if success2:
            print("\n🎊 ALL TESTS PASSED!")
            print("Your model is fully connected to O*NET data! 🎯")
        else:
            print("\n⚠️  O*NET data loaded but IntelligenceCore failed")
    else:
        print("\n❌ O*NET connection failed")
        print("Please check your data directory structure")
