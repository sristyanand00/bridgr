# backend/ml/similarity.py

import hashlib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict
from backend.models.analysis import TransferableSkill


class MatchingEngine:
    """
    Computes a semantic + lexical hybrid match score between user skills and job requirements.

    Formula: score = 0.60 × semantic_sim + 0.40 × weighted_jaccard
    """

    def __init__(self, embed_model: SentenceTransformer):
        # Reuse the embed_model from SkillExtractor — don't load it twice
        self.embed_model = embed_model
        self._vec_cache: Dict[str, np.ndarray] = {}

    def compute_match(
        self,
        user_skills: List[str],
        job_tech_skills: List[str],
        job_soft_skills: List[str],
    ) -> Tuple[int, float]:
        """
        Returns: (match_score 0–100, confidence 0–1)
        """
        if not user_skills or not job_tech_skills:
            return 0, 0.5

        user_set = set(s.lower().strip() for s in user_skills)
        job_tech = set(s.lower().strip() for s in job_tech_skills)
        job_soft = set(s.lower().strip() for s in job_soft_skills)
        job_all  = job_tech | job_soft

        if not job_all:
            return 0, 0.3

        # Component 1: Weighted Jaccard
        tech_matched = len(user_set & job_tech)
        soft_matched = len(user_set & job_soft)

        numerator   = tech_matched * 3.0 + soft_matched * 1.0
        denominator = len(job_tech) * 3.0 + len(job_soft) * 1.0
        weighted_jaccard = numerator / denominator if denominator > 0 else 0.0

        # Component 2: Semantic similarity of entire skill sets
        user_vec = self._embed_skill_set(list(user_set))
        job_vec  = self._embed_skill_set(list(job_all))
        semantic_sim = float(cosine_similarity([user_vec], [job_vec])[0][0])
        semantic_sim = max(0.0, semantic_sim)

        # Blend
        raw = 0.60 * semantic_sim + 0.40 * weighted_jaccard

        # Scale: 0.5 raw → 65 displayed (50% skill overlap is actually decent)
        scaled = min(100, int(raw * 100 * 1.15))

        # Confidence: higher when both sides have more skills to compare
        coverage = min(len(user_set), len(job_all)) / max(len(job_all), 1)
        confidence = round(min(0.95, 0.5 + coverage * 0.45), 2)

        return scaled, confidence

    def find_transferable_skills(
        self,
        user_skills: List[str],
        missing_skills: List[str],
        min_score: float = 0.72,
    ) -> List[TransferableSkill]:
        """
        For each missing skill, check if the user has something similar.
        Example: user has "Tableau" → partially satisfies "data visualization"
        """
        if not user_skills or not missing_skills:
            return []

        user_vecs    = self.embed_model.encode(user_skills,    normalize_embeddings=True)
        missing_vecs = self.embed_model.encode(missing_skills, normalize_embeddings=True)

        results = []
        for missing_skill, missing_vec in zip(missing_skills, missing_vecs):
            sims = np.dot(user_vecs, missing_vec)
            best_idx = int(np.argmax(sims))
            best_sim = float(sims[best_idx])

            if best_sim >= min_score:
                user_skill = user_skills[best_idx]
                results.append(TransferableSkill(
                    user_skill=user_skill,
                    maps_to_job_skill=missing_skill,
                    transfer_score=round(best_sim, 3),
                    explanation=(
                        f"Your '{user_skill}' experience shows {int(best_sim*100)}% "
                        f"overlap with '{missing_skill}'. "
                        f"You'll need less time to learn this than a complete beginner."
                    )
                ))

        return results

    def _embed_skill_set(self, skills: List[str]) -> np.ndarray:
        """Embed a list of skills into one vector by mean-pooling."""
        if not skills:
            return np.zeros(384)   # all-MiniLM-L6-v2 output dim

        # Cache by sorted skill list (same skills in different order = same vector)
        cache_key = hashlib.md5("|".join(sorted(skills)).encode()).hexdigest()
        if cache_key in self._vec_cache:
            return self._vec_cache[cache_key]

        vecs   = self.embed_model.encode(skills, normalize_embeddings=True)
        pooled = np.mean(vecs, axis=0)

        # Re-normalize after pooling
        norm = np.linalg.norm(pooled)
        if norm > 0:
            pooled = pooled / norm

        self._vec_cache[cache_key] = pooled
        return pooled