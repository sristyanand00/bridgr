# backend/ml/fallback_skills.py

from typing import Dict, List, Optional
try:
    from backend.ml.dataset_loader import OnetDatasetLoader
except ImportError:
    OnetDatasetLoader = None


class DatasetDrivenSkills:
    """
    Dataset-driven skill database that uses O*NET data instead of hardcoded values.
    Falls back to minimal hardcoded data only when O*NET is unavailable.
    """

    def __init__(self, dataset_loader: Optional[OnetDatasetLoader] = None):
        self.dataset_loader = dataset_loader
        self._job_skills_cache = None
        self._transferable_map = None
        self._skill_priorities = None

    def get_job_skills(self, role_name: str) -> dict:
        """Get skills for a job role using dataset or fallback."""
        if self.dataset_loader:
            # Try to get from dataset first
            profile = self.dataset_loader.get_job_profile(role_name)
            if profile is not None:
                return {
                    "tech_skills": profile.get("tech_skills", []),
                    "soft_skills": profile.get("soft_skills", [])
                }
        
        # Fallback to minimal hardcoded data
        return self._get_fallback_job_skills(role_name)
    
    def get_all_job_titles(self) -> List[str]:
        """Get all available job titles from dataset."""
        if self.dataset_loader:
            df = self.dataset_loader.load()
            return df["job_title"].tolist()
        return list(self._get_minimal_fallback_skills().keys())
    
    def get_skill_priority(self, skill_name: str) -> str:
        """Get priority level for a skill based on market demand."""
        if self.dataset_loader:
            # Use market demand to determine priority
            demand = self.dataset_loader.skill_market_demand.get(skill_name.lower(), 0.0)
            if demand > 0.1:
                return "Critical"
            elif demand > 0.05:
                return "High"
            elif demand > 0.02:
                return "Medium"
            else:
                return "Low"
        
        return "Medium"  # Default priority
    
    def get_transferable_skills(self, user_skills: List[str]) -> List[dict]:
        """Find transferable skills based on semantic similarity."""
        if self.dataset_loader:
            # Build transferable map based on skill co-occurrence
            if self._transferable_map is None:
                self._build_transferable_map()
            
            transferable = []
            for skill in user_skills:
                skill_lower = skill.lower()
                if skill_lower in self._transferable_map:
                    for transfer in self._transferable_map[skill_lower]:
                        if transfer not in user_skills and transfer not in [t["to"] for t in transferable]:
                            transferable.append({
                                "from": skill,
                                "to": transfer,
                                "confidence": 0.8
                            })
            return transferable
        
        return self._get_minimal_transferable_skills(user_skills)
    
    def _build_transferable_map(self):
        """Build transferable skill map from dataset co-occurrence."""
        df = self.dataset_loader.load()
        self._transferable_map = {}
        
        # Analyze skill co-occurrence to find transferable relationships
        all_skills = set(df['tech_skills'].explode().dropna().tolist())
        
        for skill in all_skills:
            # Find jobs that have this skill
            skill_jobs = df[df['tech_skills'].apply(lambda x: skill in x if isinstance(x, list) else False)]
            
            if len(skill_jobs) > 3:
                # Find commonly co-occurring skills
                co_skills = []
                for _, row in skill_jobs.iterrows():
                    co_skills.extend([s for s in row['tech_skills'] if s != skill and isinstance(s, str)])
                
                from collections import Counter
                co_skill_counts = Counter(co_skills)
                
                # Take top co-occurring skills as transferable
                if co_skill_counts:
                    top_transfer = [skill for skill, _ in co_skill_counts.most_common(3)]
                    self._transferable_map[skill] = top_transfer
                else:
                    self._transferable_map[skill] = []
            else:
                self._transferable_map[skill] = []
    
    def _get_fallback_job_skills(self, role_name: str) -> dict:
        """Minimal fallback when dataset is unavailable."""
        fallback_skills = self._get_minimal_fallback_skills()
        
        role_name = role_name.lower().strip()
        
        # Direct match
        for role, skills in fallback_skills.items():
            if role.lower() == role_name:
                return skills
        
        # Partial match
        for role, skills in fallback_skills.items():
            if role.lower() in role_name or role_name in role.lower():
                return skills
        
        # Default fallback
        return fallback_skills["Data Scientist"]
    
    def _get_minimal_fallback_skills(self) -> Dict[str, dict]:
        """Minimal fallback skills database."""
        return {
            "Data Scientist": {
                "tech_skills": [
                    "Python", "R", "SQL", "Machine Learning", "Deep Learning", 
                    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
                    "Data Analysis", "Statistics", "Data Visualization", "Jupyter"
                ],
                "soft_skills": [
                    "Problem Solving", "Communication", "Critical Thinking",
                    "Teamwork", "Analytical Skills", "Presentation Skills"
                ]
            },
            "Software Engineer": {
                "tech_skills": [
                    "Python", "Java", "JavaScript", "C++", "React", "Node.js",
                    "Git", "Docker", "AWS", "SQL", "MongoDB", "REST APIs"
                ],
                "soft_skills": [
                    "Problem Solving", "Communication", "Teamwork",
                    "Critical Thinking", "Project Management"
                ]
            }
        }
    
    def _get_minimal_transferable_skills(self, user_skills: List[str]) -> List[dict]:
        """Minimal transferable skills fallback."""
        transferable_map = {
            "Data Analysis": ["Business Analysis", "Data Science", "Product Analytics"],
            "Problem Solving": ["Software Engineering", "Product Management", "Business Analysis"],
            "Communication": ["Product Management", "Business Analysis", "Software Engineering"],
            "Project Management": ["Product Management", "Software Engineering", "Business Analysis"],
            "Python": ["Data Science", "Software Engineering"],
            "SQL": ["Data Science", "Business Analysis", "Product Analytics"],
            "Research": ["Data Science", "Business Analysis"]
        }
        
        transferable = []
        for skill in user_skills:
            skill_lower = skill.lower()
            if skill_lower in transferable_map:
                for transfer in transferable_map[skill_lower]:
                    if transfer not in user_skills and transfer not in [t["to"] for t in transferable]:
                        transferable.append({
                            "from": skill,
                            "to": transfer,
                            "confidence": 0.8
                        })
        
        return transferable


# Legacy compatibility functions
def get_job_skills(role_name: str) -> dict:
    """Legacy function - use DatasetDrivenSkills.get_job_skills() instead."""
    skills_db = DatasetDrivenSkills()
    return skills_db.get_job_skills(role_name)

def get_skill_priority(skill_name: str) -> str:
    """Legacy function - use DatasetDrivenSkills.get_skill_priority() instead."""
    skills_db = DatasetDrivenSkills()
    return skills_db.get_skill_priority(skill_name)

def get_transferable_skills(user_skills: list) -> list:
    """Legacy function - use DatasetDrivenSkills.get_transferable_skills() instead."""
    skills_db = DatasetDrivenSkills()
    return skills_db.get_transferable_skills(user_skills)
