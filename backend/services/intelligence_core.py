# backend/services/intelligence_core.py

import uuid
from datetime import datetime, timezone
from typing import Dict

from backend.ml.dataset_loader import OnetDatasetLoader
from backend.ml.resume_parser import ResumeParser
from backend.ml.skill_extractor import SkillExtractor
from backend.ml.similarity import MatchingEngine
from backend.ml.gap_analyzer import GapAnalyzer, INDIA_SALARY_BANDS, HIGH_DEMAND_THRESHOLD
from backend.models.analysis import AnalysisResult


class IntelligenceCore:
    """
    The single entry point for resume analysis.

    Usage:
        core = IntelligenceCore(config)
        result = core.analyze("/path/to/resume.pdf", "Data Scientists")

    FastAPI creates one instance of this at startup and reuses it for every request.
    This is important because creating it loads the O*NET data and precomputes
    embeddings — takes ~60 seconds. You only want that once.
    """

    def __init__(self, config: Dict):
        print("\n🚀 Initializing Bridgr Intelligence Core...")

        self.dataset_loader = OnetDatasetLoader(
            zip_path=config["ONET_ZIP_PATH"],
            extract_path=config["ONET_EXTRACT_PATH"],
        )
        df = self.dataset_loader.load()

        all_skills = self.dataset_loader.get_all_tech_skills()

        self.resume_parser   = ResumeParser()
        self.skill_extractor = SkillExtractor(
            skill_list=all_skills,
            semantic_threshold=config.get("SEMANTIC_THRESHOLD", 0.75),
            anthropic_key=config.get("ANTHROPIC_API_KEY", ""),
        )
        self.matching_engine = MatchingEngine(self.skill_extractor.embed_model)
        self.gap_analyzer    = GapAnalyzer(self.dataset_loader.skill_market_demand)

        print("✅ Bridgr Intelligence Core ready\n")

    def analyze(self, resume_path: str, target_role: str) -> AnalysisResult:
        """
        Full pipeline. Steps:
        1. Parse PDF → sections
        2. Extract skills (3-tier)
        3. Load O*NET job profile
        4. Compute match score
        5. Find transferable skills
        6. Analyze + rank gaps
        7. Build and return AnalysisResult
        """
        print(f"📄 Parsing: {resume_path}")
        resume_data = self.resume_parser.parse(resume_path)

        print("🔍 Extracting skills...")
        extracted = self.skill_extractor.extract(resume_data)
        user_skills = [s.normalized for s in extracted]
        print(f"   {len(extracted)} skills extracted")

        print(f"📋 Loading job profile: {target_role}")
        job_profile = self.dataset_loader.get_job_profile(target_role)
        if job_profile is None:
            raise ValueError(
                f"'{target_role}' not found in O*NET. "
                f"Try 'Data Scientists', 'Software Developers', 'Business Analysts'."
            )

        job_tech = job_profile["tech_skills"]
        job_soft = job_profile["soft_skills"]

        print("⚡ Computing match score...")
        match_score, confidence = self.matching_engine.compute_match(
            user_skills, job_tech, job_soft
        )

        print("🔄 Finding transferable skills...")
        missing_all = list((set(job_tech) | set(job_soft)) - set(user_skills))
        transferable = self.matching_engine.find_transferable_skills(user_skills, missing_all)

        print("📊 Analyzing gaps...")
        missing_required, missing_preferred = self.gap_analyzer.analyze(
            user_skills, job_tech, job_soft, transferable
        )

        # Build readiness label
        if match_score >= 80:   readiness = "Job-Ready"
        elif match_score >= 65: readiness = "Almost Ready"
        elif match_score >= 50: readiness = "Developing"
        elif match_score >= 35: readiness = "Early Stage"
        else:                   readiness = "Foundation Stage"

        matched = list(set(user_skills) & (set(job_tech) | set(job_soft)))

        # Top 5 skills to learn first (Critical + High priority)
        priority_skills = [
            g.name for g in missing_required if g.priority in ("Critical", "High")
        ][:5]

        # High-demand skills in the market
        market_demand_skills = sorted(
            [(s, v) for s, v in self.dataset_loader.skill_market_demand.items()
             if v > HIGH_DEMAND_THRESHOLD],
            key=lambda x: x[1], reverse=True
        )
        market_demand_skills = [s for s, _ in market_demand_skills[:8]]

        salary_band = self.gap_analyzer.get_salary_band(target_role)

        # Roadmap inputs for /roadmap endpoint
        critical = [g for g in missing_required if g.priority == "Critical"]
        high     = [g for g in missing_required if g.priority == "High"]
        total_weeks = sum(g.estimated_weeks for g in (critical + high)[:6])

        learning_roadmap_inputs = {
            "phase_1": {
                "label": "Foundation (weeks 1–4)",
                "skills": [g.name for g in critical[:3]],
                "duration_weeks": min(4, sum(g.estimated_weeks for g in critical[:3])),
            },
            "phase_2": {
                "label": "Core Skills (weeks 4–10)",
                "skills": [g.name for g in high[:3]],
                "duration_weeks": min(6, sum(g.estimated_weeks for g in high[:3])),
            },
            "phase_3": {
                "label": "Advanced + Projects (weeks 10+)",
                "skills": [g.name for g in missing_required[6:9]],
                "duration_weeks": 8,
            },
            "total_estimated_weeks": total_weeks,
            "current_match_score": match_score,
            "target_match_score": min(100, match_score + 25),
        }

        mock_interview_inputs = {
            "target_role": target_role,
            "weak_areas": [g.name for g in missing_required[:4]],
            "strong_areas": matched[:5],
            "difficulty": "Beginner" if match_score < 40 else "Intermediate" if match_score < 70 else "Advanced",
        }

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

        explanations = []
        if matched:
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
            confidence_score=confidence,
            extracted_skills=extracted,
            matched_skills=matched,
            missing_required=missing_required[:10],
            missing_preferred=missing_preferred[:8],
            transferable_skills=transferable,
            priority_skills=priority_skills,
            market_demand_skills=market_demand_skills,
            learning_roadmap_inputs=learning_roadmap_inputs,
            mock_interview_inputs=mock_interview_inputs,
            career_chat_context=career_chat_context,
            salary_band_estimate=salary_band,
            explanations=explanations,
        )