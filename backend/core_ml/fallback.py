"""Fallback IntelligenceCore for when O*NET dataset is unavailable."""

from __future__ import annotations
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List

from .schemas import AnalysisResult, SkillGap, TransferableSkill
from .parser import ResumeParser
from .extractor import SkillExtractor
from .matching import MatchingEngine
from .gaps import GapAnalyzer
from .skill_taxonomy import BASE_SKILLS, merge_skills

logger = logging.getLogger(__name__)


class FallbackIntelligenceCore:
    """Minimal core using hardcoded skill profiles — no O*NET required."""
    
    KNOWN_ROLES: Dict[str, Dict] = {
        "data scientist":            {"tech": ["python","sql","machine learning","statistics","pandas","numpy","scikit-learn","tensorflow","tableau"],  "soft": ["communication","problem solving","data storytelling"]},
        "software engineer":         {"tech": ["python","java","git","docker","sql","rest api","algorithms","data structures","system design"],           "soft": ["teamwork","communication","code review"]},
        "data analyst":              {"tech": ["sql","excel","tableau","python","power bi","statistics"],                                                "soft": ["analytical thinking","attention to detail","communication"]},
        "machine learning engineer": {"tech": ["python","tensorflow","pytorch","mlops","docker","kubernetes","aws"],                                      "soft": ["research","problem solving","communication"]},
        "frontend developer":        {"tech": ["javascript","react","html","css","typescript","git","node.js"],                                          "soft": ["creativity","communication","attention to detail"]},
        "backend developer":         {"tech": ["python","java","node.js","sql","docker","rest api","git","postgresql"],                                  "soft": ["problem solving","teamwork","documentation"]},
        "fullstack developer":       {"tech": ["javascript","react","node.js","sql","docker","git","typescript","rest api"],                             "soft": ["problem solving","communication","teamwork"]},
        "devops engineer":           {"tech": ["docker","kubernetes","aws","ci/cd","linux","terraform","bash","ansible"],                                "soft": ["communication","reliability","incident management"]},
        "data engineer":             {"tech": ["python","sql","spark","airflow","kafka","dbt","docker","aws"],                                           "soft": ["problem solving","communication","collaboration"]},
        "product manager":           {"tech": ["jira","sql","analytics","figma","agile","roadmapping"],                                                 "soft": ["communication","leadership","stakeholder management","product thinking"]},
        "android developer":         {"tech": ["kotlin","java","android sdk","git","rest api","firebase","sqlite"],                                     "soft": ["creativity","problem solving","communication"]},
        "ios developer":             {"tech": ["swift","xcode","git","rest api","core data","firebase","objective-c"],                                  "soft": ["creativity","problem solving","communication"]},
        "nlp engineer":              {"tech": ["python","huggingface","pytorch","transformers","spacy","nltk","sql","docker"],                          "soft": ["research","communication","problem solving"]},
        "sdet":                      {"tech": ["python","selenium","pytest","git","rest api","ci/cd","postman","appium"],                               "soft": ["attention to detail","problem solving","communication"]},
        "cloud engineer":            {"tech": ["aws","gcp","azure","terraform","docker","kubernetes","linux","ci/cd"],                                  "soft": ["problem solving","communication","documentation"]},
    }

    def __init__(self, config: Dict):
        logger.warning("⚠ FALLBACK MODE — O*NET data not found. Run scripts/setup_data.py")
        logger.info("Initialising FallbackIntelligenceCore (no dataset needed)...")
        self.config = config

        self.resume_parser = ResumeParser()
        # Same merge as IntelligenceCore — keeps the resume-side vocabulary in
        # step with the requirement-side one even in fallback mode.
        role_skills = {s for r in self.KNOWN_ROLES.values() for s in r["tech"] + r["soft"]}
        all_skills  = merge_skills(role_skills, BASE_SKILLS)
        self.skill_extractor = SkillExtractor(
            skill_list=all_skills,
            semantic_threshold=float(config.get("SEMANTIC_THRESHOLD", 0.75)),
            verbose=True,
        )
        self.matching_engine = MatchingEngine(self.skill_extractor.embed_model)
        uniform_demand       = {s: 0.10 for s in all_skills}
        self.gap_analyzer    = GapAnalyzer(uniform_demand)
        logger.info("FallbackIntelligenceCore ready")

    def _get_job_profile(self, role: str) -> Dict:
        """Match role against known profiles or generate via LLM."""
        role_lower = role.lower().strip()
        # Exact match first
        if role_lower in self.KNOWN_ROLES:
            val = self.KNOWN_ROLES[role_lower]
            return {"job_title": role_lower, "tech_skills": val["tech"], "soft_skills": val["soft"]}
        # Substring match — longest key wins to avoid "engineer" beating "data engineer"
        best_key, best_len = None, 0
        for key in self.KNOWN_ROLES:
            if (key in role_lower or role_lower in key) and len(key) > best_len:
                best_key, best_len = key, len(key)
        if best_key:
            val = self.KNOWN_ROLES[best_key]
            return {"job_title": best_key, "tech_skills": val["tech"], "soft_skills": val["soft"]}

        # Fallback to LLM — enrichment only. A missing provider package or a
        # dead API must degrade to the generic profile below, never 500 the
        # readiness endpoint.
        llm_profile = None
        try:
            from services.llm_service import llm_service
            logger.info(f"Role '{role}' not in known roles — fetching from LLM...")
            llm_profile = llm_service.fetch_job_profile_from_gemini(role)
        except Exception as e:
            logger.warning(f"LLM profile lookup failed for '{role}': {e}")

        if llm_profile:
            return {
                "job_title": role,
                "tech_skills": llm_profile.get("tech_skills", []),
                "soft_skills": llm_profile.get("soft_skills", [])
            }
        logger.warning(f"AI generation failed for '{role}'. Using generic fallback profile.")
        return {
            "job_title": role,
            "tech_skills": ["problem solving", "communication", "teamwork", "time management", "adaptability", "project management", "data analysis", "customer service"],
            "soft_skills": ["communication", "problem solving", "teamwork", "adaptability"]
        }

    def analyze(self, resume_path: str, target_role: str) -> AnalysisResult:
        """Analyze from PDF path."""
        resume_data = self.resume_parser.parse(resume_path)
        return self.analyze_dict(resume_data, target_role)

    def analyze_dict(self, resume_data: Dict, target_role: str) -> AnalysisResult:
        """Analyze from pre-parsed resume dictionary."""
        extracted   = self.skill_extractor.extract(resume_data)
        user_skills = [s.normalized for s in extracted]

        job_profile  = self._get_job_profile(target_role)
        job_tech     = job_profile["tech_skills"]
        job_soft     = job_profile["soft_skills"]

        match_score, confidence = self.matching_engine.compute_match(user_skills, job_tech, job_soft)
        missing_all  = list((set(job_tech) | set(job_soft)) - set(user_skills))
        transferable = self.matching_engine.find_transferable_skills(user_skills, missing_all)
        missing_required, missing_preferred = self.gap_analyzer.analyze(
            user_skills, job_tech, job_soft, transferable
        )

        readiness = _readiness_label(match_score)
        matched   = list(set(user_skills) & (set(job_tech) | set(job_soft)))

        critical = [g for g in missing_required if g.priority == "Critical"]
        high     = [g for g in missing_required if g.priority == "High"]
        medium   = [g for g in missing_required if g.priority == "Medium"]
        roadmap  = self.gap_analyzer.build_roadmap(critical, high, medium, match_score)
        salary   = self.gap_analyzer.get_salary_band(target_role)
        
        from .core import _build_explanations
        explanations = _build_explanations(match_score, matched, missing_required, transferable)

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
            priority_skills=[g.name for g in missing_required if g.priority in ("Critical","High")][:5],
            market_demand_skills=job_tech[:8],
            learning_roadmap_inputs=roadmap,
            mock_interview_inputs={
                "target_role":  target_role,
                "weak_areas":   [g.name for g in missing_required[:4]],
                "strong_areas": matched[:5],
                "difficulty":   "Beginner" if match_score < 40 else "Intermediate" if match_score < 70 else "Advanced",
            },
            career_chat_context={
                "user_strengths":   matched[:5],
                "user_gaps":        [g.name for g in missing_required[:5]],
                "readiness_level":  readiness,
                "match_score":      match_score,
                "target_role":      target_role,
                "top_transferable": [{"from": t.user_skill, "to": t.maps_to_job_skill} for t in transferable[:3]],
            },
            salary_band_estimate=salary,
            explanations=explanations,
        )


def _readiness_label(score: int) -> str:
    """Map match score to a readiness label."""
    if   score >= 80: return "Job-Ready"
    elif score >= 65: return "Almost Ready"
    elif score >= 50: return "Developing"
    elif score >= 35: return "Early Stage"
    else:             return "Foundation Stage"
