#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')

from backend.ml.dataset_loader import OnetDatasetLoader

def test_dataset():
    """Test the db_30_2_text dataset loading and functionality."""
    print("Testing db_30_2_text dataset loading...")
    
    try:
        loader = OnetDatasetLoader(
            zip_path='data/raw/db_30_2_text.zip',
            extract_path='data/'
        )
        
        # Check if dataset exists
        if os.path.exists('data/db_30_2_text'):
            print('✅ Dataset folder exists')
            
            # Test loading
            df = loader.load()
            print(f'✅ Dataset loaded successfully: {len(df)} job profiles')
            print(f'✅ Sample job titles: {list(df["job_title"].head(5))}')
            
            # Test skill extraction
            all_skills = loader.get_all_tech_skills()
            print(f'✅ Total tech skills available: {len(all_skills)}')
            
            # Test job profile lookup
            profile = loader.get_job_profile('Data Scientists')
            if profile is not None:
                print(f'✅ Found Data Scientists profile with {len(profile["tech_skills"])} tech skills and {len(profile["soft_skills"])} soft skills')
                print(f'   Sample tech skills: {profile["tech_skills"][:5]}')
                print(f'   Sample soft skills: {profile["soft_skills"][:5]}')
            else:
                print('⚠️  Data Scientists profile not found')
                
        else:
            print('❌ Dataset folder does not exist')
            
    except Exception as e:
        print(f'❌ Error loading dataset: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dataset()
