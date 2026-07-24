"""Matching engine for computing resume-job similarity scores."""

from __future__ import annotations
import logging
import hashlib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple

from .schemas import TransferableSkill

logger = logging.getLogger(__name__)

try:
    from cachetools import LRUCache as _LRUCache
    _lru_available = True
except ImportError:
    _lru_available = False


class MatchingEngine:
    def __init__(self, embed_model):
        self.embed_model = embed_model
        # Handle case when embed_model is None
        if embed_model is not None:
            self._embed_dim  = embed_model.get_sentence_embedding_dimension()
        else:
            self._embed_dim = 384  # Default dimension for MiniLM-L6-v2
        # Bounded LRU cache — no unbounded memory growth
        if _lru_available:
            self._vec_cache = _LRUCache(maxsize=512)
        else:
            self._vec_cache = {}   # fallback if cachetools not installed

    def compute_match(
        self,
        user_skills:     List[str],
        job_tech_skills: List[str],
        job_soft_skills: List[str],
    ) -> Tuple[int, float]:
        job_all = (
            {s.lower().strip() for s in job_tech_skills} |
            {s.lower().strip() for s in job_soft_skills}
        )

        # Return explicit sentinel so caller knows why score is 0
        if not user_skills or not job_all:
            if not job_all:
                logger.info("Job profile has no skills — cannot compute match score. "
                          "Check that the role was found in the dataset.")
            return 0, 0.3

        user_set = {s.lower().strip() for s in user_skills}
        job_tech = {s.lower().strip() for s in job_tech_skills}
        job_soft = {s.lower().strip() for s in job_soft_skills}

        tech_matched     = len(user_set & job_tech)
        soft_matched     = len(user_set & job_soft)
        numerator        = tech_matched * 3.0 + soft_matched * 1.0
        denominator      = len(job_tech) * 3.0 + len(job_soft) * 1.0
        weighted_jaccard = numerator / denominator if denominator > 0 else 0.0

        # Handle case when embed_model is None
        if self.embed_model is not None:
            user_vec     = self._embed_skill_set(list(user_set))
            job_vec      = self._embed_skill_set(list(job_all))
            semantic_sim = max(0.0, float(cosine_similarity([user_vec], [job_vec])[0][0]))
        else:
            semantic_sim = 0.0  # No semantic similarity without embeddings

        raw      = 0.60 * semantic_sim + 0.40 * weighted_jaccard
        ceiling  = 0.60 * 1.0 + 0.40 * 1.0
        scaled   = min(100, int((raw / ceiling) * 100))

        coverage   = min(len(user_set), len(job_all)) / max(len(job_all), 1)
        confidence = round(min(0.95, 0.5 + coverage * 0.45), 2)
        return scaled, confidence

    def find_transferable_skills(
        self,
        user_skills:    List[str],
        missing_skills: List[str],
        min_score:      float = 0.72,
    ) -> List[TransferableSkill]:
        if not user_skills or not missing_skills or self.embed_model is None:
            return []
        user_vecs    = self.embed_model.encode(user_skills,    normalize_embeddings=True)
        missing_vecs = self.embed_model.encode(missing_skills, normalize_embeddings=True)
        if user_vecs.shape[0] == 0 or missing_vecs.shape[0] == 0:
            return []
        results = []
        for missing_skill, missing_vec in zip(missing_skills, missing_vecs):
            sims     = np.dot(user_vecs, missing_vec)
            best_idx = int(np.argmax(sims))
            best_sim = float(sims[best_idx])
            if best_sim >= min_score:
                results.append(TransferableSkill(
                    user_skill=user_skills[best_idx],
                    maps_to_job_skill=missing_skill,
                    transfer_score=round(best_sim, 3),
                    explanation=(
                        f"Your '{user_skills[best_idx]}' experience shows "
                        f"{int(best_sim * 100)}% overlap with '{missing_skill}'."
                    ),
                ))
        return results

    def _embed_skill_set(self, skills: List[str]) -> np.ndarray:
        if not skills or self.embed_model is None:
            return np.zeros(self._embed_dim)
        cache_key = hashlib.md5("|".join(sorted(skills)).encode()).hexdigest()
        cached    = self._vec_cache.get(cache_key)
        if cached is not None:
            return cached
        vecs   = self.embed_model.encode(skills, normalize_embeddings=True)
        pooled = np.mean(vecs, axis=0)
        norm   = np.linalg.norm(pooled)
        if norm > 0:
            pooled = pooled / norm
        self._vec_cache[cache_key] = pooled
        return pooled
