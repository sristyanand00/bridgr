#!/usr/bin/env python3
"""
Comprehensive ML Model Debugging Script for Bridgr

This script systematically tests each component of the ML pipeline to identify
where issues are occurring and provide detailed diagnostic information.

Usage:
    python debug_ml_model.py
"""

import os
import sys
import traceback
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_success(message):
    print(f"✅ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_error(message):
    print(f"❌ {message}")

def test_python_dependencies():
    """Test if required Python packages are installed"""
    print_section("Testing Python Dependencies")
    
    dependencies = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('spacy', 'spacy'),
        ('pdfplumber', 'pdfplumber'),
        ('sentence_transformers', 'sentence-transformers'),
        ('fastapi', 'fastapi'),
        ('python-dotenv', 'python-dotenv'),
    ]
    
    missing = []
    for import_name, package_name in dependencies:
        try:
            __import__(import_name)
            print_success(f"{package_name} is installed")
        except ImportError:
            print_error(f"{package_name} is NOT installed")
            missing.append(package_name)
    
    if missing:
        print_error(f"Missing packages: {', '.join(missing)}")
        print(f"💡 Install with: pip install {' '.join(missing)}")
        if 'spacy' in missing:
            print("💡 Also run: python -m spacy download en_core_web_sm")
        return False
    else:
        print_success("All required dependencies are installed")
        return True

def test_spacy_model():
    """Test if spaCy English model is downloaded"""
    print_section("Testing spaCy Model")
    
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            print_success("spaCy English model is loaded")
            
            # Test basic functionality
            doc = nlp("Python is a programming language")
            entities = [ent.text for ent in doc.ents]
            print(f"📝 Test NER result: {entities}")
            return True
        except OSError:
            print_error("spaCy English model is NOT downloaded")
            print("💡 Run: python -m spacy download en_core_web_sm")
            return False
    except Exception as e:
        print_error(f"Error testing spaCy: {e}")
        return False

def test_sentence_transformers():
    """Test Sentence Transformers model loading"""
    print_section("Testing Sentence Transformers")
    
    try:
        from sentence_transformers import SentenceTransformer
        print("🔄 Loading Sentence Transformer model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print_success("Sentence Transformer model loaded successfully")
        
        # Test basic functionality
        test_sentences = ["Python programming", "Machine learning"]
        embeddings = model.encode(test_sentences)
        print(f"📝 Generated embeddings shape: {embeddings.shape}")
        return True
    except Exception as e:
        print_error(f"Error loading Sentence Transformers: {e}")
        return False

def test_onet_data():
    """Test O*NET dataset availability and loading"""
    print_section("Testing O*NET Dataset")
    
    # Check for O*NET data
    onet_paths = [
        "data/db_30_2_text",
        "data/raw/db_30_2_text.zip",
        "backend/data/db_30_2_text",
        "backend/data/raw/db_30_2_text.zip"
    ]
    
    data_found = False
    for path in onet_paths:
        if os.path.exists(path):
            print_success(f"O*NET data found at: {path}")
            data_found = True
            break
    
    if not data_found:
        print_warning("O*NET data not found in expected locations")
        print("💡 Download O*NET data or ensure it's extracted in data/ directory")
        return False
    
    # Test dataset loading
    try:
        from ml.dataset_loader import OnetDatasetLoader
        
        # Determine correct paths
        extract_path = "data/"
        zip_path = "data/raw/db_30_2_text.zip" if os.path.exists("data/raw/db_30_2_text.zip") else ""
        
        loader = OnetDatasetLoader(zip_path=zip_path, extract_path=extract_path)
        df = loader.load()
        
        print_success(f"O*NET dataset loaded successfully")
        print(f"📊 Dataset shape: {df.shape}")
        print(f"📊 Sample job titles: {df['job_title'].head(3).tolist()}")
        
        # Test job profile lookup
        profile = loader.get_job_profile("Data Scientist")
        if profile is not None:
            print_success("Job profile lookup working")
            print(f"📝 Found {len(profile['tech_skills'])} tech skills")
            print(f"📝 Found {len(profile['soft_skills'])} soft skills")
        else:
            print_warning("Job profile lookup failed for 'Data Scientist'")
        
        return True
    except Exception as e:
        print_error(f"Error loading O*NET dataset: {e}")
        traceback.print_exc()
        return False

def test_resume_parser():
    """Test resume parsing functionality"""
    print_section("Testing Resume Parser")
    
    try:
        from ml.resume_parser import ResumeParser
        parser = ResumeParser()
        print_success("ResumeParser initialized")
        
        # Check if we have a sample resume
        sample_resumes = [
            "test_resume.pdf",
            "sample_resume.pdf", 
            "backend/test_resume.pdf"
        ]
        
        sample_resume = None
        for path in sample_resumes:
            if os.path.exists(path):
                sample_resume = path
                break
        
        if sample_resume:
            print(f"📄 Testing with sample resume: {sample_resume}")
            try:
                result = parser.parse(sample_resume)
                print_success("Resume parsing successful")
                print(f"📝 Extracted sections: {list(result.keys())}")
                print(f"📝 Full text length: {len(result.get('full_text', ''))}")
                return True
            except Exception as e:
                print_error(f"Resume parsing failed: {e}")
                return False
        else:
            print_warning("No sample resume found for testing")
            print("💡 Place a PDF resume in the root directory to test parsing")
            return False
    except Exception as e:
        print_error(f"Error initializing ResumeParser: {e}")
        return False

def test_skill_extractor():
    """Test skill extraction functionality"""
    print_section("Testing Skill Extractor")
    
    try:
        from ml.skill_extractor import SkillExtractor
        
        # Create a simple skill list for testing
        test_skills = [
            "python", "java", "javascript", "sql", "git", "docker", 
            "aws", "react", "node.js", "machine learning", "data analysis"
        ]
        
        extractor = SkillExtractor(skill_list=test_skills, semantic_threshold=0.75)
        print_success("SkillExtractor initialized")
        
        # Test with sample text
        sample_text = {
            "full_text": "I have experience with Python, Java, and SQL. I worked on machine learning projects using TensorFlow.",
            "sections": {
                "experience": "Python developer with 5 years experience",
                "skills": "Python, Java, SQL, Machine Learning, TensorFlow"
            }
        }
        
        extracted = extractor.extract(sample_text, debug=True)
        print_success(f"Skill extraction successful - found {len(extracted)} skills")
        
        for skill in extracted[:5]:  # Show first 5
            print(f"📝 {skill.name} (confidence: {skill.confidence}, source: {skill.source})")
        
        return True
    except Exception as e:
        print_error(f"Error in SkillExtractor: {e}")
        traceback.print_exc()
        return False

def test_intelligence_core():
    """Test the main IntelligenceCore"""
    print_section("Testing Intelligence Core")
    
    try:
        from services.intelligence_core import IntelligenceCore
        
        config = {
            "ONET_EXTRACT_PATH": "data/",
            "SEMANTIC_THRESHOLD": 0.75,
            "OPENAI_API_KEY": ""
        }
        
        print("🔄 Initializing IntelligenceCore...")
        core = IntelligenceCore(config)
        print_success("IntelligenceCore initialized successfully")
        return True
    except Exception as e:
        print_error(f"Error initializing IntelligenceCore: {e}")
        traceback.print_exc()
        
        # Test fallback core
        try:
            from services.fallback_intelligence_core import FallbackIntelligenceCore
            print("🔄 Testing FallbackIntelligenceCore...")
            core = FallbackIntelligenceCore(config)
            print_success("FallbackIntelligenceCore initialized successfully")
            return True
        except Exception as e2:
            print_error(f"Error initializing FallbackIntelligenceCore: {e2}")
            return False

def test_end_to_end_analysis():
    """Test complete analysis pipeline"""
    print_section("Testing End-to-End Analysis")
    
    try:
        from services.fallback_intelligence_core import FallbackIntelligenceCore
        
        config = {
            "ONET_EXTRACT_PATH": "data/",
            "SEMANTIC_THRESHOLD": 0.75,
            "OPENAI_API_KEY": ""
        }
        
        core = FallbackIntelligenceCore(config)
        
        # Test with a mock resume path (will use fallback logic)
        result = core.analyze("mock_resume.pdf", "Data Scientist")
        
        print_success("End-to-end analysis completed")
        print(f"📊 Match score: {result.match_score}%")
        print(f"📊 Readiness level: {result.readiness_level}")
        print(f"📊 Extracted skills: {len(result.extracted_skills)}")
        print(f"📊 Matched skills: {len(result.matched_skills)}")
        print(f"📊 Missing skills: {len(result.missing_required)}")
        
        return True
    except Exception as e:
        print_error(f"Error in end-to-end analysis: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("🚀 Bridgr ML Model Diagnostic Tool")
    print("This will test each component of your ML pipeline to identify issues.")
    
    tests = [
        ("Python Dependencies", test_python_dependencies),
        ("spaCy Model", test_spacy_model),
        ("Sentence Transformers", test_sentence_transformers),
        ("O*NET Dataset", test_onet_data),
        ("Resume Parser", test_resume_parser),
        ("Skill Extractor", test_skill_extractor),
        ("Intelligence Core", test_intelligence_core),
        ("End-to-End Analysis", test_end_to_end_analysis),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print_section("Diagnostic Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"📊 Tests passed: {passed}/{total}")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    # Recommendations
    print_section("Recommendations")
    
    if not results.get("Python Dependencies", False):
        print("🔧 Install missing Python packages")
    
    if not results.get("spaCy Model", False):
        print("🔧 Download spaCy model: python -m spacy download en_core_web_sm")
    
    if not results.get("Sentence Transformers", False):
        print("🔧 Check internet connection for model download")
    
    if not results.get("O*NET Dataset", False):
        print("🔧 Download and extract O*NET dataset")
    
    if not results.get("Intelligence Core", False):
        print("🔧 Check ML dependencies and data availability")
    
    if passed == total:
        print_success("All tests passed! Your ML model should be working correctly.")
    else:
        print_warning(f"{total - passed} test(s) failed. Fix these issues to get your ML model working.")

if __name__ == "__main__":
    main()
