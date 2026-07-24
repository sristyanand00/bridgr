"""Dynamic job skills loading from custom data, O*NET, or LLM fallback."""

from __future__ import annotations
import logging
import json
import copy
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DynamicJobSkills:
    def __init__(self, data_dir: str = "data/"):
        self.data_dir     = Path(data_dir)
        self.skills_cache: Dict[str, Dict] = {}
        self._onet_loader = None

    def set_onet_loader(self, loader) -> None:
        self._onet_loader = loader

    def load_job_skills(self, role_name: str) -> Optional[Dict]:
        """Load skills for a role from: custom JSON → O*NET → LLM."""
        role_key = role_name.lower().strip().replace(" ", "_")
        if role_key in self.skills_cache:
            return self.skills_cache[role_key]
        result = (
            self._load_custom_skills(role_key)
            or self._load_onet_skills(role_key)
            or self._get_default_skills(role_name)
        )
        if result:
            self.skills_cache[role_key] = result
        return result

    def _load_custom_skills(self, role_key: str) -> Optional[Dict]:
        """Load from data/custom_skills/{role_key}.json."""
        path = self.data_dir / f"custom_skills/{role_key}.json"
        if not path.exists():
            return None
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.info(f"Custom skills load failed for {role_key}: {e}")
            return None

    def _load_onet_skills(self, role_key: str) -> Optional[Dict]:
        """Query O*NET dataset if available."""
        if self._onet_loader is None:
            return None
        try:
            profile = self._onet_loader.get_job_profile(role_key.replace("_", " "))
            if profile is None:
                return None
            return {
                "tech_skills": list(profile["tech_skills"]) if isinstance(profile["tech_skills"], list) else [],
                "soft_skills": list(profile["soft_skills"]) if isinstance(profile["soft_skills"], list) else [],
                "source":      "onet_dataset",
            }
        except Exception as e:
            logger.warning(f"O*NET lookup failed for {role_key}: {e}")
            return None

    def _get_default_skills(self, role: str) -> Optional[Dict]:
        """Fallback to LLM-generated profile."""
        from services.llm_service import llm_service
        logger.info(f"Role '{role}' not in local dataset — fetching from LLM...")
        llm_profile = llm_service.fetch_job_profile_from_gemini(role)
        if llm_profile:
            return {
                "tech_skills": llm_profile.get("tech_skills", []),
                "soft_skills": llm_profile.get("soft_skills", []),
                "source": "llm_generated",
            }
        return None

    def get_skill_market_demand(self, role_key: str) -> Dict[str, float]:
        """Return market demand map for a role."""
        if self._onet_loader is not None:
            return self._onet_loader.skill_market_demand
        data   = self.load_job_skills(role_key) or {}
        skills = data.get("tech_skills", []) + data.get("soft_skills", [])
        total  = max(len(skills), 1)
        return {s: 1.0 / total for s in skills}

    def update_skills_from_config(self, config_updates: Dict) -> None:
        """Merge config overrides into cache."""
        for role_key, updates in config_updates.items():
            base = copy.deepcopy(self.skills_cache.get(role_key, {}))
            base.update({k: copy.deepcopy(v) for k, v in updates.items()})
            self.skills_cache[role_key] = base

    def save_custom_skills(self, role_key: str, skills_data: Dict) -> bool:
        """Save custom skills to disk."""
        try:
            path = self.data_dir / f"custom_skills/{role_key}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(skills_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.info(f"Could not save custom skills: {e}")
            return False
