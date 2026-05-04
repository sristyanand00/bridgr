import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from ml.model_loader import get_core
import time

def test_analysis():
    print("--- Starting ML Analysis Test ---")
    start_time = time.time()
    
    try:
        print("1. Loading ML Core...")
        core_start = time.time()
        core = get_core()
        print(f"   Done in {time.time() - core_start:.2f}s")
        
        # Test with a synthetic job role
        target_role = "Data Scientist"
        print(f"2. Analyzing for role: {target_role}")
        
        # We'll use a dummy resume dict instead of a PDF for speed
        synthetic_resume = {
            "full_text": "Python SQL Machine Learning engineer with 5 years experience. Built models using TensorFlow and Scikit-learn. Data visualization with Tableau.",
            "sections": {
                "skills": "Python, SQL, Machine Learning, TensorFlow, Scikit-learn, Tableau",
                "experience": "Data Scientist at Tech Corp. Built predictive models.",
            },
            "metadata": {"pages": 1, "char_count": 200, "has_skills_section": True},
        }
        
        analysis_start = time.time()
        result = core.analyze_dict(synthetic_resume, target_role)
        print(f"   Analysis done in {time.time() - analysis_start:.2f}s")
        
        print(f"3. Result Summary:")
        print(f"   Match Score: {result.match_score}%")
        print(f"   Skills Matched: {len(result.matched_skills)}")
        print(f"   Gaps Found: {len(result.missing_required)}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

    print(f"--- Test Finished in {time.time() - start_time:.2f}s ---")

if __name__ == "__main__":
    test_analysis()
