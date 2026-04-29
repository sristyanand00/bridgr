# backend/ml/gap_analyzer.py

from typing import List, Dict, Tuple, Set
from backend.models.analysis import SkillGap, TransferableSkill


class GapAnalyzer:
    """
    Computes prioritized skill gaps between a user and a job profile.

    Priority formula:
        score = 0.40 × market_demand
              + 0.30 × (1 - learning_difficulty)
              + 0.20 × foundation_bonus
              + 0.10 × transfer_bonus
    """

    def __init__(self, skill_market_demand: Dict[str, float], dataset_loader=None):
        self.skill_market_demand = skill_market_demand
        self.dataset_loader = dataset_loader
        self._prerequisite_map = None
        self._learning_time_map = None
        self._salary_bands = None

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
    def salary_bands(self) -> Dict[str, Dict]:
        if self._salary_bands is None:
            self._salary_bands = self._build_salary_bands()
        return self._salary_bands

    def _build_prerequisite_map(self) -> Dict[str, List[str]]:
        """Build prerequisite relationships from dataset."""
        if self.dataset_loader is None:
            return self._get_fallback_prerequisites()
        
        # Analyze skill co-occurrence to infer prerequisites
        df = self.dataset_loader.load()
        prerequisite_map = {}
        
        # For each skill, find commonly co-occurring skills that might be prerequisites
        all_skills = set(df['tech_skills'].explode().dropna().tolist())
        
        for skill in all_skills:
            # Find jobs that require this skill
            skill_jobs = df[df['tech_skills'].apply(lambda x: skill in x if isinstance(x, list) else False)]
            
            if len(skill_jobs) > 5:  # Only analyze skills with sufficient data
                # Find other skills that frequently appear with this skill
                co_skills = []
                for _, row in skill_jobs.iterrows():
                    co_skills.extend([s for s in row['tech_skills'] if s != skill and isinstance(s, str)])
                
                from collections import Counter
                co_skill_counts = Counter(co_skills)
                
                # Take top 3-5 most common co-occurring skills as potential prerequisites
                if co_skill_counts:
                    top_co_skills = [skill for skill, _ in co_skill_counts.most_common(4)]
                    prerequisite_map[skill] = top_co_skills
                else:
                    prerequisite_map[skill] = []
            else:
                prerequisite_map[skill] = []
        
        return prerequisite_map
    
    def _build_learning_time_map(self) -> Dict[str, int]:
        """Build learning time estimates based on skill complexity and demand."""
        if self.dataset_loader is None:
            return self._get_fallback_learning_times()
        
        # Estimate learning time based on skill frequency and complexity
        learning_time_map = {}
        
        for skill, demand in self.skill_market_demand.items():
            # Base time on demand and skill characteristics
            if demand > 0.1:  # High demand skills
                base_time = 6
            elif demand > 0.05:  # Medium demand
                base_time = 4
            else:  # Low demand
                base_time = 2
            
            # Adjust for skill complexity (heuristic based on skill name)
            skill_lower = skill.lower()
            if any(comp in skill_lower for comp in ['machine learning', 'deep learning', 'artificial intelligence', 'neural']):
                base_time = max(base_time, 10)
            elif any(comp in skill_lower for comp in ['python', 'java', 'javascript', 'sql']):
                base_time = max(base_time, 6)
            elif any(comp in skill_lower for comp in ['docker', 'kubernetes', 'aws', 'azure', 'google cloud']):
                base_time = max(base_time, 8)
            elif any(comp in skill_lower for comp in ['excel', 'powerpoint', 'word']):
                base_time = min(base_time, 2)
            
            learning_time_map[skill] = base_time
        
        learning_time_map['default'] = 4
        return learning_time_map
    
    def _build_salary_bands(self) -> Dict[str, Dict]:
        """Build salary bands from dataset job titles and descriptions."""
        if self.dataset_loader is None:
            return self._get_fallback_salary_bands()
        
        # Analyze job titles to infer salary ranges
        df = self.dataset_loader.load()
        
        # Group similar job titles and estimate salary ranges
        salary_bands = {}
        
        # Common role keywords and their estimated salary ranges (in INR)
        role_keywords = {
            'data scientist': {'min': 700000, 'max': 2000000, 'median': 1200000},
            'data analyst': {'min': 400000, 'max': 1200000, 'median': 700000},
            'machine learning': {'min': 900000, 'max': 2500000, 'median': 1600000},
            'software engineer': {'min': 500000, 'max': 2000000, 'median': 1000000},
            'developer': {'min': 400000, 'max': 1800000, 'median': 900000},
            'engineer': {'min': 500000, 'max': 2000000, 'median': 1000000},
            'manager': {'min': 800000, 'max': 2500000, 'median': 1500000},
            'analyst': {'min': 400000, 'max': 1500000, 'median': 800000},
            'architect': {'min': 800000, 'max': 2500000, 'median': 1600000},
            'consultant': {'min': 600000, 'max': 2000000, 'median': 1200000},
        }
        
        for keyword, band in role_keywords.items():
            salary_bands[keyword] = {**band, 'currency': 'INR'}
        
        salary_bands['default'] = {'min': 400000, 'max': 1500000, 'median': 800000, 'currency': 'INR'}
        return salary_bands
    
    def _get_fallback_prerequisites(self) -> Dict[str, List[str]]:
        """Fallback prerequisite map when dataset is not available."""
        return {
            "machine learning": ["python", "statistics", "linear algebra"],
            "deep learning": ["machine learning", "python", "tensorflow"],
            "data science": ["python", "statistics", "sql"],
            "python": [],
            "sql": [],
            "default": []
        }
    
    def _get_fallback_learning_times(self) -> Dict[str, int]:
        """Fallback learning time map when dataset is not available."""
        return {
            "python": 6, "sql": 3, "machine learning": 8, "deep learning": 10,
            "statistics": 6, "docker": 3, "kubernetes": 6, "aws": 8,
            "default": 4
        }
    
    def _get_fallback_salary_bands(self) -> Dict[str, Dict]:
        """Fallback salary bands when dataset is not available."""
        return {
            "data scientist": {"min": 700000, "max": 2000000, "median": 1200000, "currency": "INR"},
            "software engineer": {"min": 500000, "max": 2000000, "median": 1000000, "currency": "INR"},
            "default": {"min": 400000, "max": 1500000, "median": 800000, "currency": "INR"}
        }

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
        weeks = self.learning_time_map.get(skill, self.learning_time_map["default"])
        max_weeks = max(self.learning_time_map.values()) if self.learning_time_map else 4
        difficulty = weeks / max_weeks

        prereqs = self.prerequisite_map.get(skill, [])
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
        if market_demand > 0.15:
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
        for keyword, band in self.salary_bands.items():
            if keyword in role_lower:
                return band
        return self.salary_bands.get("default", {"min": 400000, "max": 1500000, "median": 800000, "currency": "INR"})