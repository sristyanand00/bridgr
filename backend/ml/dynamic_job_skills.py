# backend/ml/dynamic_job_skills.py
"""
Dynamic job skills database system that can be configured through data inputs
instead of hardcoded values. This allows the system to adapt to any job role
and market requirements without code changes.
"""

import json
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path

class DynamicJobSkills:
    """
    Dynamic job skills database that loads from configurable JSON files.
    
    Instead of hardcoded fallback skills, this system:
    1. Loads job definitions from JSON files
    2. Supports market demand data from external sources
    3. Allows runtime configuration of skill requirements
    4. Provides fallback to O*NET when external data unavailable
    """
    
    def __init__(self, data_dir: str = "data/"):
        self.data_dir = Path(data_dir)
        self.skills_cache: Dict[str, Dict] = {}
        
    def load_job_skills(self, role_name: str) -> Optional[Dict]:
        """
        Load job skills from dynamic data sources.
        
        Priority order:
        1. Custom JSON files (highest priority)
        2. O*NET dataset (fallback)
        3. Default fallback (lowest priority)
        """
        role_key = role_name.lower().strip().replace(" ", "_")
        
        # Check cache first
        if role_key in self.skills_cache:
            return self.skills_cache[role_key]
        
        # Try to load from custom JSON files
        custom_skills = self._load_custom_skills(role_key)
        if custom_skills:
            self.skills_cache[role_key] = custom_skills
            return custom_skills
        
        # Fallback to O*NET dataset
        onet_skills = self._load_onet_skills(role_key)
        if onet_skills:
            self.skills_cache[role_key] = onet_skills
            return onet_skills
        
        # Final fallback to default skills
        default_skills = self._get_default_skills(role_key)
        self.skills_cache[role_key] = default_skills
        return default_skills
    
    def _load_custom_skills(self, role_key: str) -> Optional[Dict]:
        """Load skills from custom JSON files in data directory."""
        custom_file = self.data_dir / f"custom_skills/{role_key}.json"
        
        if custom_file.exists():
            try:
                with open(custom_file, 'r', encoding='utf-8') as f:
                    skills_data = json.load(f)
                    print(f"✅ Loaded custom skills for {role_key} from {custom_file}")
                    return skills_data
            except Exception as e:
                print(f"⚠️ Error loading custom skills for {role_key}: {e}")
                return None
        
        return None
    
    def _load_onet_skills(self, role_key: str) -> Optional[Dict]:
        """Load skills from O*NET dataset with role matching."""
        try:
            # Try to use existing dataset loader
            from backend.ml.dataset_loader import OnetDatasetLoader
            loader = OnetDatasetLoader(
                zip_path="data/raw/db_30_2_text.zip",
                extract_path="data/"
            )
            
            df = loader.load()
            job_profile = loader.get_job_profile(role_key.replace("_", " "))
            
            if job_profile is not None:
                return {
                    "tech_skills": job_profile["tech_skills"].tolist() if hasattr(job_profile["tech_skills"], 'tolist') else [],
                    "soft_skills": job_profile["soft_skills"].tolist() if hasattr(job_profile["soft_skills"], 'tolist') else [],
                    "source": "onet_dataset"
                }
        except Exception as e:
            print(f"⚠️ Error loading O*NET skills for {role_key}: {e}")
            return None
    
    def _get_default_skills(self, role_key: str) -> Dict:
        """Default fallback skills when no data available."""
        # Basic fallback structure for unknown roles
        return {
            "tech_skills": [
                "Communication", "Teamwork", "Problem Solving", "Time Management",
                "Leadership", "Adaptability", "Research", "Documentation"
            ],
            "soft_skills": [
                "Critical Thinking", "Creativity", "Analytical Skills", 
                "Attention to Detail", "Project Management"
            ],
            "source": "default_fallback"
        }
    
    def get_all_available_roles(self) -> List[str]:
        """Get list of all available roles from custom files and O*NET."""
        roles = set()
        
        # Get roles from custom files
        custom_dir = self.data_dir / "custom_skills"
        if custom_dir.exists():
            for file_path in custom_dir.glob("*.json"):
                role_name = file_path.stem.replace("_", " ")
                roles.add(role_name)
        
        # Get roles from O*NET dataset
        try:
            from backend.ml.dataset_loader import OnetDatasetLoader
            loader = OnetDatasetLoader(
                zip_path="data/raw/db_30_2_text.zip",
                extract_path="data/"
            )
            df = loader.load()
            if df is not None:
                onet_roles = df["job_title"].str.lower().tolist()
                roles.update(onet_roles)
        except Exception as e:
            print(f"⚠️ Error loading O*NET roles: {e}")
        
        return sorted(list(roles))
    
    def save_custom_skills(self, role_key: str, skills_data: Dict) -> bool:
        """Save custom skills to JSON file."""
        try:
            custom_file = self.data_dir / f"custom_skills/{role_key}.json"
            custom_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(custom_file, 'w', encoding='utf-8') as f:
                json.dump(skills_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved custom skills for {role_key} to {custom_file}")
            return True
        except Exception as e:
            print(f"⚠️ Error saving custom skills for {role_key}: {e}")
            return False
    
    def get_skill_market_demand(self, role_key: str) -> Dict[str, float]:
        """Get market demand data for skills."""
        skills_data = self.load_job_skills(role_key)
        if not skills_data:
            return {}
        
        # Return equal market demand for all skills (can be overridden by external data)
        skills = skills_data.get("tech_skills", [])
        return {skill: 1.0 for skill in skills}
    
    def update_skills_from_config(self, config_updates: Dict[str, any]) -> None:
        """Update skill requirements from configuration."""
        for role_key, updates in config_updates.items():
            if role_key in self.skills_cache:
                current_skills = self.skills_cache[role_key]
                updated_skills = current_skills.copy()
                
                # Update tech skills
                if "tech_skills" in updates:
                    updated_skills["tech_skills"] = updates["tech_skills"]
                
                # Update soft skills  
                if "soft_skills" in updates:
                    updated_skills["soft_skills"] = updates["soft_skills"]
                
                # Update metadata
                if "priority" in updates:
                    updated_skills["priority"] = updates["priority"]
                if "learning_time" in updates:
                    updated_skills["learning_time"] = updates["learning_time"]
                
                self.skills_cache[role_key] = updated_skills
                print(f"✅ Updated skills for {role_key}: {updates}")
