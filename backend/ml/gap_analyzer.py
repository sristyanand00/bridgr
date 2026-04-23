# backend/ml/gap_analyzer.py

from typing import List, Dict, Tuple, Set
from backend.models.analysis import SkillGap, TransferableSkill


# Prerequisite relationships. If user has a prereq, they learn faster.
PREREQUISITE_MAP = {
    "machine learning":     ["python", "statistics", "linear algebra", "numpy"],
    "deep learning":        ["machine learning", "python", "tensorflow", "pytorch"],
    "natural language processing": ["python", "machine learning", "text mining"],
    "data science":         ["python", "statistics", "sql", "machine learning"],
    "feature engineering":  ["python", "pandas", "statistics"],
    "model deployment":     ["python", "docker", "flask", "fastapi"],
    "mlops":                ["docker", "kubernetes", "python", "ci/cd"],
    "sql":                  [],
    "pandas":               ["python"],
    "tensorflow":           ["python", "machine learning", "numpy"],
    "pytorch":              ["python", "machine learning", "numpy"],
    "spark":                ["python", "sql", "hadoop"],
    "kubernetes":           ["docker", "linux"],
    "react":                ["javascript", "html", "css"],
    "node.js":              ["javascript"],
    "django":               ["python"],
    "fastapi":              ["python"],
    "aws":                  ["linux", "networking"],
    "gcp":                  ["linux"],
    "azure":                ["linux"],
    "data visualization":   ["python", "matplotlib"],
    "tableau":              [],
    "power bi":             [],
    "a/b testing":          ["statistics"],
    "time series":          ["statistics", "python", "pandas"],
}

# Estimated weeks for someone with some technical background
LEARNING_TIME_MAP = {
    "sql": 3, "python": 6, "pandas": 2, "numpy": 2,
    "machine learning": 8, "deep learning": 10, "tensorflow": 4, "pytorch": 4,
    "spark": 6, "docker": 3, "kubernetes": 6, "react": 8, "javascript": 8,
    "aws": 8, "statistics": 6, "feature engineering": 4, "data visualization": 3,
    "tableau": 2, "nlp": 6, "mlops": 8,
    "default": 4,
}

# Indian salary bands by role keyword
INDIA_SALARY_BANDS = {
    "data scientist":      {"min": 700000,  "max": 2000000, "median": 1200000,  "currency": "INR"},
    "data analyst":        {"min": 400000,  "max": 1200000, "median": 700000,   "currency": "INR"},
    "machine learning":    {"min": 900000,  "max": 2500000, "median": 1600000,  "currency": "INR"},
    "software engineer":   {"min": 500000,  "max": 2000000, "median": 1000000,  "currency": "INR"},
    "frontend":            {"min": 400000,  "max": 1500000, "median": 800000,   "currency": "INR"},
    "backend":             {"min": 500000,  "max": 1800000, "median": 1000000,  "currency": "INR"},
    "fullstack":           {"min": 500000,  "max": 2000000, "median": 1100000,  "currency": "INR"},
    "product manager":     {"min": 800000,  "max": 2500000, "median": 1500000,  "currency": "INR"},
    "devops":              {"min": 600000,  "max": 2000000, "median": 1200000,  "currency": "INR"},
    "default":             {"min": 400000,  "max": 1500000, "median": 800000,   "currency": "INR"},
}

HIGH_DEMAND_THRESHOLD = 0.15


class GapAnalyzer:
    """
    Computes prioritized skill gaps between a user and a job profile.

    Priority formula:
        score = 0.40 × market_demand
              + 0.30 × (1 - learning_difficulty)
              + 0.20 × foundation_bonus
              + 0.10 × transfer_bonus
    """

    def __init__(self, skill_market_demand: Dict[str, float]):
        self.skill_market_demand = skill_market_demand

    def analyze(
        self,
        user_skills: List[str],
        job_tech_skills: List[str],
        job_soft_skills: List[str],
        transferable: List[TransferableSkill],
    ) -> Tuple[List[SkillGap], List[SkillGap]]:
        """
        Returns: (missing_required_ranked, missing_preferred_ranked)
        Both sorted by priority_score descending.
        """
        user_set    = set(s.lower().strip() for s in user_skills)
        job_tech    = set(s.lower().strip() for s in job_tech_skills)
        job_soft    = set(s.lower().strip() for s in job_soft_skills)
        transferable_targets = {t.maps_to_job_skill.lower() for t in transferable}

        missing_tech = job_tech - user_set
        missing_soft = job_soft - user_set

        required_gaps  = [self._build_gap(s, user_set, transferable_targets, True)  for s in missing_tech]
        preferred_gaps = [self._build_gap(s, user_set, transferable_targets, False) for s in missing_soft]

        required_gaps  = sorted(required_gaps,  key=lambda g: g.priority_score, reverse=True)
        preferred_gaps = sorted(preferred_gaps, key=lambda g: g.priority_score, reverse=True)

        return required_gaps, preferred_gaps

    def _build_gap(
        self,
        skill: str,
        user_set: Set[str],
        transferable_targets: Set[str],
        is_required: bool,
    ) -> SkillGap:
        market_demand = self.skill_market_demand.get(skill, 0.05)
        weeks = LEARNING_TIME_MAP.get(skill, LEARNING_TIME_MAP["default"])
        max_weeks = max(LEARNING_TIME_MAP.values())
        difficulty = weeks / max_weeks

        prereqs = PREREQUISITE_MAP.get(skill, [])
        prereqs_met = sum(1 for p in prereqs if p in user_set)
        has_foundation = prereqs_met > 0 and len(prereqs) > 0
        foundation_bonus = prereqs_met / len(prereqs) if prereqs else 0.0

        transfer_bonus = 0.5 if skill in transferable_targets else 0.0

        priority_score = round(
            0.40 * market_demand
            + 0.30 * (1 - difficulty)
            + 0.20 * foundation_bonus
            + 0.10 * transfer_bonus,
            4
        )

        if priority_score >= 0.35:   priority = "Critical"
        elif priority_score >= 0.25: priority = "High"
        elif priority_score >= 0.15: priority = "Medium"
        else:                        priority = "Low"

        # Build human reason
        parts = []
        if market_demand > HIGH_DEMAND_THRESHOLD:
            parts.append(f"required by {int(market_demand*100)}% of job postings")
        if has_foundation:
            met = [p for p in prereqs if p in user_set]
            parts.append(f"you already know {', '.join(met[:2])} (related)")
        if skill in transferable_targets:
            parts.append("you have a transferable skill that covers this partially")
        reason = "; ".join(parts) if parts else f"important for {skill} roles"

        return SkillGap(
            name=skill,
            priority=priority,
            priority_score=priority_score,
            market_demand=market_demand,
            reason=reason,
            estimated_weeks=weeks,
            has_foundation=has_foundation,
        )

    def get_salary_band(self, target_role: str) -> Dict:
        role_lower = target_role.lower()
        for keyword, band in INDIA_SALARY_BANDS.items():
            if keyword in role_lower:
                return band
        return INDIA_SALARY_BANDS["default"]