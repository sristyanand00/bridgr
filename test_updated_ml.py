#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')

from backend.ml.dataset_loader import OnetDatasetLoader
from backend.ml.gap_analyzer import GapAnalyzer
from backend.ml.fallback_skills import DatasetDrivenSkills
from backend.ml.similarity import MatchingEngine
from sentence_transformers import SentenceTransformer

def test_dataset_driven_ml():
    """Test the updated ML model with dataset-driven logic."""
    print("🧪 Testing Dataset-Driven ML Model")
    print("=" * 50)
    
    # Initialize dataset loader
    print("1. Loading O*NET dataset...")
    loader = OnetDatasetLoader(
        zip_path='data/raw/db_30_2_text.zip',
        extract_path='data/'
    )
    df = loader.load()
    print(f"✅ Loaded {len(df)} job profiles")
    print(f"✅ Found {len(loader.skill_market_demand)} unique skills")
    
    # Initialize dataset-driven components
    print("\n2. Initializing dataset-driven components...")
    skills_db = DatasetDrivenSkills(dataset_loader=loader)
    gap_analyzer = GapAnalyzer(
        skill_market_demand=loader.skill_market_demand,
        dataset_loader=loader
    )
    
    # Test job skills retrieval
    print("\n3. Testing job skills retrieval...")
    test_roles = ["Data Scientists", "Software Engineers", "Accountants"]
    for role in test_roles:
        skills = skills_db.get_job_skills(role)
        print(f"✅ {role}: {len(skills['tech_skills'])} tech skills, {len(skills['soft_skills'])} soft skills")
        if skills['tech_skills']:
            print(f"   Sample tech skills: {skills['tech_skills'][:3]}")
    
    # Test gap analysis
    print("\n4. Testing gap analysis...")
    user_skills = ["Python", "SQL", "Communication"]
    job_profile = skills_db.get_job_skills("Data Scientists")
    
    required_gaps, preferred_gaps = gap_analyzer.analyze(
        user_skills=user_skills,
        job_tech_skills=job_profile['tech_skills'],
        job_soft_skills=job_profile['soft_skills'],
        transferable=[]
    )
    
    print(f"✅ Found {len(required_gaps)} required skill gaps")
    for gap in required_gaps[:3]:
        print(f"   - {gap.name}: {gap.priority} priority ({gap.priority_score})")
    
    # Test salary bands
    print("\n5. Testing salary bands...")
    test_roles_salary = ["Data Scientist", "Software Engineer", "Unknown Role"]
    for role in test_roles_salary:
        salary = gap_analyzer.get_salary_band(role)
        print(f"✅ {role}: {salary['currency']} {salary['min']:,} - {salary['max']:,}")
    
    # Test skill priorities
    print("\n6. Testing skill priorities...")
    test_skills = ["Python", "Machine Learning", "Communication", "Excel"]
    for skill in test_skills:
        priority = skills_db.get_skill_priority(skill)
        demand = loader.skill_market_demand.get(skill.lower(), 0.0)
        print(f"✅ {skill}: {priority} priority (demand: {demand:.3f})")
    
    # Test transferable skills
    print("\n7. Testing transferable skills...")
    user_skills_test = ["Python", "SQL", "Problem Solving"]
    transferable = skills_db.get_transferable_skills(user_skills_test)
    print(f"✅ Found {len(transferable)} transferable skills")
    for trans in transferable[:3]:
        print(f"   - {trans['from']} → {trans['to']} (confidence: {trans['confidence']})")
    
    # Test similarity matching
    print("\n8. Testing similarity matching...")
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    matching_engine = MatchingEngine(embed_model)
    
    match_score, confidence = matching_engine.compute_match(
        user_skills=user_skills,
        job_tech_skills=job_profile['tech_skills'],
        job_soft_skills=job_profile['soft_skills']
    )
    print(f"✅ Match score: {match_score}% (confidence: {confidence})")
    
    print("\n🎉 All tests completed successfully!")
    print("📊 Summary:")
    print(f"   - Dataset: {len(df)} job profiles")
    print(f"   - Skills: {len(loader.skill_market_demand)} unique skills")
    print(f"   - Gap analysis: {len(required_gaps)} gaps found")
    print(f"   - Match score: {match_score}%")

if __name__ == "__main__":
    test_dataset_driven_ml()
