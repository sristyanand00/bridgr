"""Main IntelligenceCore orchestrating the full analysis pipeline."""

from __future__ import annotations
import logging
import os
import glob
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from .schemas import AnalysisResult, SkillGap, TransferableSkill
from .dataset import OnetDatasetLoader
from .parser import ResumeParser
from .extractor import SkillExtractor
from .matching import MatchingEngine
from .gaps import GapAnalyzer, HIGH_DEMAND_THRESHOLD
from .job_skills import DynamicJobSkills
from .skill_taxonomy import BASE_SKILLS, merge_skills

logger = logging.getLogger(__name__)

# These are set by IntelligenceCore.__init__ so the route layer can read them.
DATA_MODE: str = "fallback"  # "full" | "sample" | "fallback"


class IntelligenceCore:
    def __init__(self, config: Dict):
        global DATA_MODE
        logger.info("Initialising Bridgr Intelligence Core...")
        extract_path = config["ONET_EXTRACT_PATH"]
        db_folders   = glob.glob(os.path.join(extract_path, "db_*"))

        sample_csv = Path(__file__).parent.parent / "data" / "sample" / "occupations.csv"

        if db_folders:
            self.dataset_loader = OnetDatasetLoader(zip_path="", extract_path=extract_path)
            DATA_MODE = "full"
        else:
            zip_path = config.get("ONET_ZIP_PATH", "")
            if os.path.exists(zip_path):
                self.dataset_loader = OnetDatasetLoader(zip_path=zip_path, extract_path=extract_path)
                DATA_MODE = "full"
            elif sample_csv.exists():
                # Use sample CSV — still loads via OnetDatasetLoader which handles the fallback
                self.dataset_loader = OnetDatasetLoader(zip_path="", extract_path=extract_path)
                DATA_MODE = "sample"
                logger.info("SAMPLE MODE — using 50-occupation O*NET extract. "
                            "Run scripts/setup_data.py for full 1,000+ occupation coverage.")
            else:
                raise FileNotFoundError(
                    f"Dataset not found in '{extract_path}'. "
                    "Set ONET_ZIP_PATH or place db_* folder in ONET_EXTRACT_PATH."
                )

        self.dataset_loader.load()
        # Merge BASE_SKILLS in so the resume-side vocabulary matches the
        # requirement-side vocabulary built by routes/readiness._candidate_skills.
        # Without this, O*NET-only coverage leaves modern-stack skills (fastapi,
        # django, redis, microservices, …) detectable in a job posting but never
        # in a resume, so they silently score 0 forever.
        onet_skills = self.dataset_loader.get_all_tech_skills()
        all_skills  = merge_skills(onet_skills, BASE_SKILLS)
        logger.info(
            "Skill vocabulary: %d from O*NET + %d base = %d merged",
            len(onet_skills), len(BASE_SKILLS), len(all_skills),
        )

        self.resume_parser   = ResumeParser()
        self.skill_extractor = SkillExtractor(
            skill_list=all_skills,
            semantic_threshold=float(config.get("SEMANTIC_THRESHOLD", 0.75)),
        )
        self.matching_engine = MatchingEngine(self.skill_extractor.embed_model)
        self.gap_analyzer    = GapAnalyzer(
            self.dataset_loader.skill_market_demand,
            dataset_loader=self.dataset_loader,
        )
        self.dynamic_job_skills = DynamicJobSkills(data_dir=config.get("DATA_DIR", "data/"))
        self.dynamic_job_skills.set_onet_loader(self.dataset_loader)
        logger.info("Bridgr Intelligence Core ready")

    def analyze(self, resume_path: str, target_role: str) -> AnalysisResult:
        """Analyze from a PDF file path."""
        logger.info(f"Parsing: {resume_path}")
        resume_data = self.resume_parser.parse(resume_path)
        return self._run(resume_data, target_role)

    def analyze_dict(self, resume_dict: Dict, target_role: str) -> AnalysisResult:
        """Analyze from a pre-parsed resume dictionary."""
        return self._run(resume_dict, target_role)

    def _run(self, resume_data: Dict, target_role: str) -> AnalysisResult:
        """Core analysis pipeline."""
        logger.info("Extracting skills...")
        extracted   = self.skill_extractor.extract(resume_data)
        user_skills = [s.normalized for s in extracted]
        logger.info(f"{len(extracted)} skills extracted")

        logger.info(f"Loading profile for: {target_role}")
        job_profile = self.dataset_loader.get_job_profile(target_role)
        if job_profile is None:
            skills_data = self.dynamic_job_skills.load_job_skills(target_role)
            if not skills_data:
                raise ValueError(
                    f"No skills data found for '{target_role}'. "
                    "Add a custom_skills JSON or check dataset availability."
                )
            job_profile = {
                "job_title":       target_role,
                "job_description": f"Requirements for {target_role}",
                "tech_skills":     skills_data.get("tech_skills", []),
                "soft_skills":     skills_data.get("soft_skills", []),
            }

        job_tech = list(job_profile["tech_skills"])
        job_soft = list(job_profile["soft_skills"])

        # Guard: if job profile is empty warn clearly before scoring
        if not job_tech and not job_soft:
            logger.info(f"Role '{target_role}' resolved to an empty skill profile. "
                       "Match score will be 0. Consider adding a custom_skills JSON.")

        logger.info("Computing match score...")
        match_score, confidence = self.matching_engine.compute_match(user_skills, job_tech, job_soft)

        missing_all  = list((set(job_tech) | set(job_soft)) - set(user_skills))
        transferable = self.matching_engine.find_transferable_skills(user_skills, missing_all)

        logger.info("Analysing gaps...")
        missing_required, missing_preferred = self.gap_analyzer.analyze(
            user_skills, job_tech, job_soft, transferable
        )

        readiness       = _readiness_label(match_score)
        matched         = list(set(user_skills) & (set(job_tech) | set(job_soft)))
        priority_skills = [g.name for g in missing_required if g.priority in ("Critical", "High")][:5]

        market_demand_skills = sorted(
            [(s, v) for s, v in self.dataset_loader.skill_market_demand.items()
             if v > HIGH_DEMAND_THRESHOLD],
            key=lambda x: x[1], reverse=True,
        )[:8]
        market_demand_skills = [s for s, _ in market_demand_skills]

        salary_band = self.gap_analyzer.get_salary_band(target_role)

        critical = [g for g in missing_required if g.priority == "Critical"]
        high     = [g for g in missing_required if g.priority == "High"]
        medium   = [g for g in missing_required if g.priority == "Medium"]
        roadmap  = self.gap_analyzer.build_roadmap(critical, high, medium, match_score)

        explanations = _build_explanations(match_score, matched, missing_required, transferable)

        logger.info(f"Analysis complete: {readiness} ({match_score}%)")

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
            learning_roadmap_inputs=roadmap,
            mock_interview_inputs={
                "target_role":  target_role,
                "weak_areas":   [g.name for g in missing_required[:4]],
                "strong_areas": matched[:5],
                "difficulty":   "Beginner" if match_score < 40 else "Intermediate" if match_score < 70 else "Advanced",
            },
            career_chat_context={
                "user_strengths":  matched[:5],
                "user_gaps":       [g.name for g in missing_required[:5]],
                "readiness_level": readiness,
                "match_score":     match_score,
                "target_role":     target_role,
                "top_transferable": [
                    {"from": t.user_skill, "to": t.maps_to_job_skill}
                    for t in transferable[:3]
                ],
            },
            salary_band_estimate=salary_band,
            explanations=explanations,
        )


def _readiness_label(score: int) -> str:
    """Map match score to a readiness label."""
    if   score >= 80: return "Job-Ready"
    elif score >= 65: return "Almost Ready"
    elif score >= 50: return "Developing"
    elif score >= 35: return "Early Stage"
    else:             return "Foundation Stage"


def _build_explanations(
    match_score: int,
    matched:     List[str],
    missing:     List[SkillGap],
    transferable: List[TransferableSkill],
) -> List[str]:
    """Generate human-readable explanations for the analysis."""
    out = []
    if matched:
        out.append(f"Your {match_score}% match is driven by: {', '.join(matched[:3])}.")
    if missing:
        top = missing[0]
        out.append(f"Top gap: '{top.name}' — {top.reason}.")
    if transferable:
        t = transferable[0]
        out.append(
            f"'{t.user_skill}' gives you a head start on '{t.maps_to_job_skill}' "
            f"({int(t.transfer_score * 100)}% overlap)."
        )
    return out
