# backend/services/fallback_intelligence_core.py

import uuid
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.fallback_skills import get_job_skills, get_skill_priority, get_transferable_skills
from models.analysis import AnalysisResult, ExtractedSkill, SkillGap, TransferableSkill


class FallbackIntelligenceCore:
    """
    Fallback intelligence core that works without O*NET dataset.
    Uses built-in skill database for common job roles.
    """

    def __init__(self, config: Dict):
        print("\n🚀 Initializing Fallback Bridgr Intelligence Core...")
        print("⚠️  Using fallback skill database (O*NET not available)")
        
        # Check if ML dependencies are available
        self._check_ml_dependencies()
        
        print("✅ Fallback Intelligence Core ready\n")
    
    def _check_ml_dependencies(self):
        """Check if required ML dependencies are available."""
        missing_deps = []
        
        try:
            import pdfplumber
        except ImportError:
            missing_deps.append("pdfplumber")
            
        try:
            import spacy
        except ImportError:
            missing_deps.append("spacy")
            
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            missing_deps.append("sentence-transformers")
        
        if missing_deps:
            print(f"❌ Missing ML dependencies: {', '.join(missing_deps)}")
            print("💡 Install with: pip install " + " ".join(missing_deps))
            if "spacy" in missing_deps:
                print("💡 Also run: python -m spacy download en_core_web_sm")
        else:
            print("✅ ML dependencies are available")

    def analyze(self, resume_path: str, target_role: str) -> AnalysisResult:
        """
        Simplified analysis pipeline that works without external datasets.
        """
        print(f"📄 Analyzing resume for: {target_role}")
        
        # Get job skills from fallback database
        job_skills = get_job_skills(target_role)
        job_tech = job_skills["tech_skills"]
        job_soft = job_skills["soft_skills"]
        all_job_skills = job_tech + job_soft
        
        # Simulate skill extraction from resume (for demo purposes)
        # In production, this would use actual resume parsing
        user_skills = self._extract_skills_from_resume(resume_path, target_role)
        
        print(f"🔍 Found {len(user_skills)} skills in resume")
        
        # Calculate matched skills
        matched = list(set(user_skills) & set(all_job_skills))
        missing = list(set(all_job_skills) - set(user_skills))
        
        print(f"✅ Matched skills: {len(matched)}")
        print(f"❌ Missing skills: {len(missing)}")
        
        # Calculate match score - show 0% if no skills extracted from resume
        if not user_skills:
            match_score = 0
        else:
            match_score = int((len(matched) / len(all_job_skills)) * 100) if all_job_skills else 0
        
        # Find transferable skills
        transferable_raw = get_transferable_skills(user_skills)
        transferable = [
            TransferableSkill(
                user_skill=t["from"],
                maps_to_job_skill=t["to"],
                transfer_score=t["confidence"],
                explanation=f"Your {t['from']} experience transfers well to {t['to']}"
            ) for t in transferable_raw
        ]
        
        # Create skill gaps
        missing_required = []
        missing_preferred = []
        
        for skill in missing:
            priority = get_skill_priority(skill)
            gap = SkillGap(
                name=skill,
                priority=priority,
                reason=f"This skill is {priority.lower()} for {target_role} roles",
                demand_percentage=85 if priority == "Critical" else 65 if priority == "High" else 45,
                estimated_weeks=4 if priority == "Critical" else 6 if priority == "High" else 8,
                learning_resources=[
                    f"Online course for {skill}",
                    f"Practice projects with {skill}"
                ]
            )
            
            if priority in ["Critical", "High"]:
                missing_required.append(gap)
            else:
                missing_preferred.append(gap)
        
        # Sort by priority
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        missing_required.sort(key=lambda x: priority_order.get(x.priority, 3))
        missing_preferred.sort(key=lambda x: priority_order.get(x.priority, 3))
        
        # Build readiness label
        if match_score >= 80:   readiness = "Job-Ready"
        elif match_score >= 65: readiness = "Almost Ready"
        elif match_score >= 50: readiness = "Developing"
        elif match_score >= 35: readiness = "Early Stage"
        else:                   readiness = "Foundation Stage"
        
        # Create extracted skills objects
        extracted_skills = [
            ExtractedSkill(
                original=skill,
                normalized=skill,
                source="resume",
                confidence=0.8
            ) for skill in user_skills
        ]
        
        # Priority skills to learn
        priority_skills = [g.name for g in missing_required[:5]]
        
        # Mock salary bands (simplified)
        salary_bands = {
            "Data Scientist": {"min": "₹8L", "median": "₹14.5L", "max": "₹22L"},
            "Software Engineer": {"min": "₹6L", "median": "₹12L", "max": "₹20L"},
            "Product Manager": {"min": "₹10L", "median": "₹18L", "max": "₹28L"},
            "Business Analyst": {"min": "₹5L", "median": "₹10L", "max": "₹16L"},
            "Aerospace Engineer": {"min": "₹8L", "median": "₹15L", "max": "₹25L"}
        }
        
        salary_band = salary_bands.get(target_role, salary_bands["Data Scientist"])
        
        # Build roadmap inputs
        learning_roadmap_inputs = {
            "phase_1": {
                "label": "Foundation (weeks 1–4)",
                "skills": [g.name for g in missing_required[:3]],
                "duration_weeks": 4,
            },
            "phase_2": {
                "label": "Core Skills (weeks 4–10)",
                "skills": [g.name for g in missing_required[3:6]],
                "duration_weeks": 6,
            },
            "phase_3": {
                "label": "Advanced + Projects (weeks 10+)",
                "skills": [g.name for g in missing_required[6:9]],
                "duration_weeks": 8,
            },
            "total_estimated_weeks": sum(g.estimated_weeks for g in missing_required[:6]),
            "current_match_score": match_score,
            "target_match_score": min(100, match_score + 25),
        }
        
        # Mock interview inputs
        mock_interview_inputs = {
            "target_role": target_role,
            "weak_areas": [g.name for g in missing_required[:4]],
            "strong_areas": matched[:5],
            "difficulty": "Beginner" if match_score < 40 else "Intermediate" if match_score < 70 else "Advanced",
        }
        
        # Career chat context
        career_chat_context = {
            "user_strengths": matched[:5],
            "user_gaps": [g.name for g in missing_required[:5]],
            "readiness_level": readiness,
            "match_score": match_score,
            "target_role": target_role,
            "top_transferable": [
                {"from": t.user_skill, "to": t.maps_to_job_skill}
                for t in transferable[:3]
            ],
        }
        
        # Explanations
        explanations = []
        if not user_skills:
            explanations.append(
                "Unable to extract skills from resume. The ML system may not be properly configured."
            )
        elif matched:
            explanations.append(
                f"Your {match_score}% match is driven by strengths in: {', '.join(matched[:3])}."
            )
        if missing_required:
            top = missing_required[0]
            explanations.append(f"Top priority gap: '{top.name}' — {top.reason}.")
        if transferable:
            t = transferable[0]
            explanations.append(
                f"'{t.user_skill}' gives you a head start on '{t.maps_to_job_skill}' "
                f"({int(t.transfer_score*100)}% overlap)."
            )
        
        print(f"✅ Analysis complete: {readiness} ({match_score}%)\n")
        
        return AnalysisResult(
            analysis_id=str(uuid.uuid4()),
            generated_at=datetime.now(timezone.utc).isoformat(),
            target_role=target_role,
            match_score=match_score,
            readiness_level=readiness,
            confidence_score=0.8,  # Fixed confidence for fallback
            extracted_skills=extracted_skills,
            matched_skills=matched,
            missing_required=missing_required[:10],
            missing_preferred=missing_preferred[:8],
            transferable_skills=transferable,
            priority_skills=priority_skills,
            market_demand_skills=job_tech[:8],  # Use tech skills as market demand
            learning_roadmap_inputs=learning_roadmap_inputs,
            mock_interview_inputs=mock_interview_inputs,
            career_chat_context=career_chat_context,
            salary_band_estimate=salary_band,
            explanations=explanations,
        )
    
    def _extract_skills_from_resume(self, resume_path: str, target_role: str) -> List[str]:
        """
        Attempt actual skill extraction from resume.
        Returns empty list if parsing fails, showing the real state of ML system.
        """
        try:
            # Try to use the actual resume parser
            from ml.resume_parser import ResumeParser
            parser = ResumeParser()
            resume_data = parser.parse(resume_path)
            
            # Basic keyword extraction from resume text
            import re
            text = resume_data.get("full_text", "").lower()
            
            # Look for common technical skills
            common_skills = [
                "python", "java", "javascript", "sql", "git", "docker", "aws", "azure",
                "react", "node.js", "machine learning", "data analysis", "tensorflow",
                "pytorch", "excel", "powerpoint", "communication", "leadership"
            ]
            
            found_skills = []
            for skill in common_skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', text):
                    found_skills.append(skill.title())
            
            return found_skills
            
        except Exception as e:
            print(f"❌ Resume parsing failed: {e}")
            # Return empty list to show ML system is not working
            return []
