import os
import sys
import time

# Add backend to path
sys.path.append(os.getcwd())

from ml.model_loader import get_core

def test_analysis():
    print("🚀 Starting manual ML analysis test...")
    start = time.time()
    
    try:
        print("🧠 Initializing Core...")
        core = get_core()
        print(f"✅ Core initialized in {time.time() - start:.2f}s")
        
        # Test with a known role
        test_role = "Data Scientist"
        print(f"⚡ Testing analysis for '{test_role}' (synthetic mode)...")
        
        # FallbackCore and IntelligenceCore both have analyze_dict
        # We'll use a dummy resume text
        synthetic_resume = {
            "full_text": "Experienced Python developer with machine learning knowledge. Worked with SQL, pandas, and scikit-learn.",
            "sections": {"skills": "Python, SQL, Machine Learning"},
            "metadata": {"pages": 1, "char_count": 100, "has_skills_section": True}
        }
        
        # Depending on which core was loaded, we might need to use analyze_dict
        if hasattr(core, 'analyze_dict'):
            result = core.analyze_dict(synthetic_resume, test_role)
        else:
            # For IntelligenceCore, we need a real file. Let's just test get_job_profile if it exists.
            if hasattr(core, 'dataset_loader'):
                print("Checking O*NET lookup...")
                profile = core.dataset_loader.get_job_profile(test_role)
                print(f"Profile found: {profile['job_title'] if profile is not None else 'None'}")
        
        print(f"Test completed successfully in {time.time() - start:.2f}s")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analysis()
