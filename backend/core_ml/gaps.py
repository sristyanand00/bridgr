"""Gap analysis, learning roadmaps, and salary band estimation."""

from __future__ import annotations
import logging
import copy
from collections import Counter
from typing import Dict, List, Tuple, Optional, Any

from .schemas import SkillGap, TransferableSkill

logger = logging.getLogger(__name__)

HIGH_DEMAND_THRESHOLD = 0.15

_SKILL_RESOURCES: List[tuple] = [
    ("python",           ["Python Official Tutorial|https://docs.python.org/3/tutorial/",
                          "Real Python|https://realpython.com"]),
    ("pandas",           ["Pandas Getting Started|https://pandas.pydata.org/docs/getting_started/"]),
    ("numpy",            ["NumPy Quickstart|https://numpy.org/doc/stable/user/quickstart.html"]),
    ("machine learning", ["Andrew Ng ML Specialization|https://www.coursera.org/specializations/machine-learning-introduction",
                          "fast.ai|https://course.fast.ai"]),
    ("deep learning",    ["DeepLearning.AI|https://www.deeplearning.ai",
                          "fast.ai|https://course.fast.ai"]),
    ("tensorflow",       ["TensorFlow Tutorials|https://www.tensorflow.org/tutorials"]),
    ("pytorch",          ["PyTorch Tutorials|https://pytorch.org/tutorials/"]),
    ("scikit",           ["Scikit-learn User Guide|https://scikit-learn.org/stable/user_guide.html"]),
    ("statistics",       ["Khan Academy Statistics|https://www.khanacademy.org/math/statistics-probability",
                          "StatQuest|https://www.youtube.com/@statquest"]),
    ("sql",              ["SQLZoo|https://sqlzoo.net",
                          "Mode SQL Tutorial|https://mode.com/sql-tutorial/"]),
    ("spark",            ["Apache Spark Docs|https://spark.apache.org/docs/latest/"]),
    ("airflow",          ["Airflow Tutorial|https://airflow.apache.org/docs/apache-airflow/stable/tutorial/"]),
    ("docker",           ["Docker Getting Started|https://docs.docker.com/get-started/"]),
    ("kubernetes",       ["Kubernetes Basics|https://kubernetes.io/docs/tutorials/kubernetes-basics/"]),
    ("aws",              ["AWS Skill Builder|https://skillbuilder.aws"]),
    ("azure",            ["Microsoft Learn Azure|https://learn.microsoft.com/en-us/training/azure/"]),
    ("google cloud",     ["Google Cloud Skills Boost|https://www.cloudskillsboost.google"]),
    ("mlops",            ["MLOps Zoomcamp|https://github.com/DataTalksClub/mlops-zoomcamp"]),
    ("tableau",          ["Tableau Free Training|https://www.tableau.com/learn/training"]),
    ("power bi",         ["Microsoft Learn Power BI|https://learn.microsoft.com/en-us/training/powerplatform/power-bi"]),
    ("natural language", ["HuggingFace NLP Course|https://huggingface.co/learn/nlp-course/"]),
    ("computer vision",  ["CS231n Stanford|http://cs231n.stanford.edu"]),
    ("communication",    ["Coursera Communication Skills|https://www.coursera.org/learn/wharton-communication-skills"]),
    ("problem solving",  ["Brilliant.org|https://brilliant.org"]),
]

_DEFAULT_RESOURCES = [
    "Coursera|https://www.coursera.org",
    "LinkedIn Learning|https://www.linkedin.com/learning/",
]


def _get_learning_resources(skill: str) -> List[str]:
    skill_lower = skill.lower()
    for keyword, resources in _SKILL_RESOURCES:
        if keyword in skill_lower:
            return resources[:]
    return _DEFAULT_RESOURCES[:]


# Salary band keys and lookup both use lowercase with spaces
INDIA_SALARY_BANDS: Dict[str, Dict] = {
    "data scientist":            {"min": 700_000,  "max": 2_000_000, "median": 1_200_000, "currency": "INR"},
    "software engineer":         {"min": 500_000,  "max": 2_000_000, "median": 1_000_000, "currency": "INR"},
    "data analyst":              {"min": 400_000,  "max": 1_200_000, "median":   700_000, "currency": "INR"},
    "machine learning engineer": {"min": 900_000,  "max": 2_500_000, "median": 1_600_000, "currency": "INR"},
    "ml engineer":               {"min": 900_000,  "max": 2_500_000, "median": 1_600_000, "currency": "INR"},
    "data engineer":             {"min": 600_000,  "max": 2_000_000, "median": 1_200_000, "currency": "INR"},
    "frontend developer":        {"min": 450_000,  "max": 1_800_000, "median":   900_000, "currency": "INR"},
    "backend developer":         {"min": 500_000,  "max": 2_000_000, "median": 1_000_000, "currency": "INR"},
    "fullstack developer":       {"min": 500_000,  "max": 2_000_000, "median": 1_000_000, "currency": "INR"},
    "devops":                    {"min": 600_000,  "max": 2_000_000, "median": 1_200_000, "currency": "INR"},
    "site reliability":          {"min": 900_000,  "max": 2_500_000, "median": 1_600_000, "currency": "INR"},
    "platform engineer":         {"min": 700_000,  "max": 2_200_000, "median": 1_300_000, "currency": "INR"},
    "cloud engineer":            {"min": 700_000,  "max": 2_200_000, "median": 1_300_000, "currency": "INR"},
    "mlops":                     {"min": 900_000,  "max": 2_800_000, "median": 1_700_000, "currency": "INR"},
    "product manager":           {"min": 900_000,  "max": 3_000_000, "median": 1_800_000, "currency": "INR"},
    "product owner":             {"min": 700_000,  "max": 2_000_000, "median": 1_300_000, "currency": "INR"},
    "ux designer":               {"min": 500_000,  "max": 1_800_000, "median": 1_000_000, "currency": "INR"},
    "research scientist":        {"min": 1_000_000,"max": 3_500_000, "median": 2_000_000, "currency": "INR"},
    "nlp engineer":              {"min": 900_000,  "max": 2_800_000, "median": 1_700_000, "currency": "INR"},
    "computer vision":           {"min": 900_000,  "max": 2_800_000, "median": 1_700_000, "currency": "INR"},
    "business analyst":          {"min": 450_000,  "max": 1_500_000, "median":   900_000, "currency": "INR"},
    "android developer":         {"min": 450_000,  "max": 1_800_000, "median":   950_000, "currency": "INR"},
    "ios developer":             {"min": 450_000,  "max": 1_800_000, "median":   950_000, "currency": "INR"},
    "sdet":                      {"min": 500_000,  "max": 1_800_000, "median":   950_000, "currency": "INR"},
    "security engineer":         {"min": 700_000,  "max": 2_500_000, "median": 1_400_000, "currency": "INR"},
    "developer":                 {"min": 400_000,  "max": 1_800_000, "median":   900_000, "currency": "INR"},
    "engineer":                  {"min": 500_000,  "max": 2_000_000, "median": 1_000_000, "currency": "INR"},
    "analyst":                   {"min": 400_000,  "max": 1_500_000, "median":   800_000, "currency": "INR"},
    "manager":                   {"min": 800_000,  "max": 2_500_000, "median": 1_500_000, "currency": "INR"},
    "default":                   {"min": 400_000,  "max": 1_500_000, "median":   800_000, "currency": "INR"},
}


def update_salary_bands(overrides: Dict[str, Dict]) -> None:
    """Update salary bands with custom overrides."""
    for role_key, band in overrides.items():
        INDIA_SALARY_BANDS[role_key.lower().strip()] = copy.deepcopy(band)
    logger.info(f"Salary bands updated for: {list(overrides.keys())}")


class GapAnalyzer:
    def __init__(self, skill_market_demand: Dict[str, float], dataset_loader=None):
        self.skill_market_demand = skill_market_demand
        self.dataset_loader      = dataset_loader
        self._prerequisite_map:  Optional[Dict[str, List[str]]] = None
        self._learning_time_map: Optional[Dict[str, int]]       = None
        self._max_weeks:         Optional[int]                   = None

    @property
    def prerequisite_map(self) -> Dict[str, List[str]]:
        if self._prerequisite_map is None:
            self._prerequisite_map = self._build_prerequisite_map()
        return self._prerequisite_map

    @property
    def learning_time_map(self) -> Dict[str, int]:
        if self._learning_time_map is None:
            self._learning_time_map = self._build_learning_time_map()
        return self._learning_time_map

    @property
    def max_weeks(self) -> int:
        if self._max_weeks is None:
            vals = list(self.learning_time_map.values())
            self._max_weeks = max(vals) if vals else 4
        return self._max_weeks

    def _build_prerequisite_map(self) -> Dict[str, List[str]]:
        if self.dataset_loader is None:
            return self._fallback_prerequisites()

        df       = self.dataset_loader.load()
        exploded = (df[["job_title", "tech_skills"]]
                    .explode("tech_skills").dropna()
                    .rename(columns={"tech_skills": "skill"}))
        exploded["skill"] = exploded["skill"].str.lower().str.strip()

        skill_to_jobs = exploded.groupby("skill")["job_title"].apply(set)
        all_skills    = skill_to_jobs.index.tolist()

        # Cap at 500 skills to avoid O(N²) hang on full O*NET
        if len(all_skills) > 500:
            logger.info(f"Capping prerequisite map at 500 skills (full set: {len(all_skills)})")
            all_skills = all_skills[:500]

        prereq_map: Dict[str, List[str]] = {}
        logger.info(f"Building prerequisite map for {len(all_skills)} skills")
        for i, skill in enumerate(all_skills):
            jobs_with_skill = skill_to_jobs.get(skill, set())
            if len(jobs_with_skill) < 5:
                prereq_map[skill] = []
                continue
            co: Counter = Counter()
            for other in all_skills:
                if other == skill:
                    continue
                overlap = len(jobs_with_skill & skill_to_jobs.get(other, set()))
                if overlap:
                    co[other] = overlap
            prereq_map[skill] = [s for s, _ in co.most_common(4)]
        logger.info("Prerequisite map complete")
        return prereq_map

    def _build_learning_time_map(self) -> Dict[str, int]:
        # Heuristic: complex skills take longer
        RULES = [
            (["machine learning","deep learning","artificial intelligence","neural"], 10),
            (["docker","kubernetes","aws","azure","google cloud"],                    8),
            (["python","java","javascript","typescript","scala","sql"],               6),
            (["tableau","power bi","excel"],                                          2),
        ]
        lmap: Dict[str, int] = {}
        for skill, demand in self.skill_market_demand.items():
            base = 6 if demand > 0.1 else 4 if demand > 0.05 else 2
            sl   = skill.lower()
            for keywords, override in RULES:
                if any(kw in sl for kw in keywords):
                    base = max(base, override)
                    break
            lmap[skill] = base
        lmap["default"] = 4
        return lmap

    def _fallback_prerequisites(self) -> Dict[str, List[str]]:
        """Minimal prerequisite map when dataset unavailable."""
        return {
            "machine learning": ["python", "statistics"],
            "deep learning":    ["machine learning", "python"],
            "data science":     ["python", "statistics", "sql"],
            "kubernetes":       ["docker", "linux"],
            "spark":            ["python", "sql"],
            "default":          [],
        }

    def analyze(
        self,
        user_skills:     List[str],
        job_tech_skills: List[str],
        job_soft_skills: List[str],
        transferable:    List[TransferableSkill],
    ) -> Tuple[List[SkillGap], List[SkillGap]]:
        """Identify missing skills and prioritize them."""
        user_set             = {s.lower().strip() for s in user_skills}
        job_tech             = {s.lower().strip() for s in job_tech_skills}
        job_soft             = {s.lower().strip() for s in job_soft_skills}
        transferable_targets = {t.maps_to_job_skill.lower() for t in transferable}

        required_gaps = sorted(
            [self._build_gap(s, user_set, transferable_targets, True)  for s in job_tech - user_set],
            key=lambda g: g.priority_score, reverse=True,
        )
        preferred_gaps = sorted(
            [self._build_gap(s, user_set, transferable_targets, False) for s in job_soft - user_set],
            key=lambda g: g.priority_score, reverse=True,
        )
        return required_gaps, preferred_gaps

    def _build_gap(
        self,
        skill:               str,
        user_set:            set,
        transferable_targets: set,
        is_required:         bool,
    ) -> SkillGap:
        """Build a single SkillGap with priority scoring."""
        market_demand    = self.skill_market_demand.get(skill, 0.05)
        weeks            = self.learning_time_map.get(skill, self.learning_time_map["default"])
        difficulty       = weeks / self.max_weeks

        prereqs          = self.prerequisite_map.get(skill, [])
        prereqs_met      = sum(1 for p in prereqs if p in user_set)
        has_foundation   = prereqs_met > 0 and prereqs
        foundation_bonus = prereqs_met / len(prereqs) if prereqs else 0.0
        transfer_bonus   = 0.5 if skill in transferable_targets else 0.0

        # Priority = 40% market demand + 30% ease + 20% foundation + 10% transferability
        priority_score = round(
            0.40 * market_demand
            + 0.30 * (1 - difficulty)
            + 0.20 * foundation_bonus
            + 0.10 * transfer_bonus,
            4,
        )

        if   priority_score >= 0.35: priority = "Critical"
        elif priority_score >= 0.25: priority = "High"
        elif priority_score >= 0.15: priority = "Medium"
        else:                        priority = "Low"

        parts = []
        if market_demand > HIGH_DEMAND_THRESHOLD:
            parts.append(f"required by {int(market_demand * 100)}% of job postings")
        if has_foundation:
            met = [p for p in prereqs if p in user_set]
            parts.append(f"you already know {', '.join(met[:2])}")
        if skill in transferable_targets:
            parts.append("you have a transferable skill that covers this")
        reason = "; ".join(parts) if parts else f"commonly required for this role"

        return SkillGap(
            name=skill,
            priority=priority,
            priority_score=priority_score,
            market_demand=market_demand,
            reason=reason,
            estimated_weeks=weeks,
            has_foundation=has_foundation,
            learning_resources=_get_learning_resources(skill),
        )

    def get_salary_band(self, target_role: str) -> Dict:
        """Return salary band for a role using keyword matching."""
        role_lower = target_role.lower().strip()
        # Sort by key length descending so "data scientist" beats "scientist"
        for keyword in sorted(INDIA_SALARY_BANDS.keys(), key=len, reverse=True):
            if keyword == "default":
                continue
            if keyword in role_lower:
                return INDIA_SALARY_BANDS[keyword]
        return INDIA_SALARY_BANDS["default"]

    def build_roadmap(
        self,
        critical: List[SkillGap],
        high:     List[SkillGap],
        medium:   List[SkillGap],
        match_score: int,
    ) -> Dict[str, Any]:
        """Build a phased learning roadmap."""
        p1_skills = critical[:4]
        p2_skills = high[:4]
        p3_skills = medium[:3] + high[4:6]

        # Duration computed from actual gap weeks, not hardcoded
        p1_weeks = max(2, sum(g.estimated_weeks for g in p1_skills))
        p2_weeks = max(2, sum(g.estimated_weeks for g in p2_skills))
        p3_weeks = max(2, sum(g.estimated_weeks for g in p3_skills))
        total    = p1_weeks + p2_weeks + p3_weeks

        return {
            "phases": [
                {
                    "phase": 1, "label": "Foundation",
                    "skills":         [g.name for g in p1_skills],
                    "resources":      [r for g in p1_skills for r in g.learning_resources[:2]],
                    "duration_weeks": p1_weeks,
                    "start_week": 1, "end_week": p1_weeks,
                },
                {
                    "phase": 2, "label": "Core Skills",
                    "skills":         [g.name for g in p2_skills],
                    "resources":      [r for g in p2_skills for r in g.learning_resources[:2]],
                    "duration_weeks": p2_weeks,
                    "start_week": p1_weeks + 1, "end_week": p1_weeks + p2_weeks,
                },
                {
                    "phase": 3, "label": "Advanced & Projects",
                    "skills":         [g.name for g in p3_skills],
                    "resources":      [r for g in p3_skills for r in g.learning_resources[:2]],
                    "duration_weeks": p3_weeks,
                    "start_week": p1_weeks + p2_weeks + 1, "end_week": total,
                },
            ],
            "total_estimated_weeks": total,
            "current_match_score":   match_score,
            "target_match_score":    min(100, match_score + 25),
        }
