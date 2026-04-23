# backend/ml/skill_extractor.py

import re
import json
import numpy as np
import spacy
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Set
from backend.models.analysis import ExtractedSkill


# Skills too generic to be useful — they'd match almost everything
STOP_SKILLS = {
    "work", "use", "ability", "using", "used", "strong",
    "experience", "skills", "knowledge", "understanding",
    "management", "communication", "team", "working",
}


class SkillExtractor:
    """
    Three-tier skill extraction from resume text.

    Tier 1: PhraseMatcher (exact/near-exact) — confidence 0.95
    Tier 2: Semantic similarity (noun chunks vs skill taxonomy) — confidence = similarity score
    Tier 3: LLM fallback (only if < 5 skills found) — confidence 0.80
    """

    SEMANTIC_THRESHOLD = 0.75   # minimum cosine similarity to count as a match

    def __init__(
        self,
        skill_list: List[str],
        semantic_threshold: float = 0.75,
        openai_key: str = "",
    ):
        self.skill_list = [s for s in skill_list if s not in STOP_SKILLS]
        self.threshold = semantic_threshold
        self.openai_key = openai_key

        print("🔧 Loading NLP models...")
        self.nlp = spacy.load("en_core_web_sm")
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")

        # ── Build PhraseMatcher ───────────────────────────────
        # Add every skill in the taxonomy as a phrase to match against
        self._matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = list(self.nlp.pipe(self.skill_list))
        self._matcher.add("SKILLS", patterns)

        # ── Precompute all skill embeddings ───────────────────
        # This runs once at startup. Without this, every request would
        # take 30+ seconds. With this, it's under 2 seconds.
        print(f"⚡ Precomputing embeddings for {len(self.skill_list)} skills...")
        self._skill_embeddings = self.embed_model.encode(
            self.skill_list,
            batch_size=64,
            normalize_embeddings=True,   # normalize = dot product = cosine similarity
            show_progress_bar=True,
        )
        print("✅ Skill extractor ready")

    def extract(self, resume_data: Dict, debug: bool = False) -> List[ExtractedSkill]:
        """
        Main entry point. Takes the output of ResumeParser.parse().
        Returns a deduplicated list of ExtractedSkill objects.
        """
        full_text = resume_data["full_text"]
        sections  = resume_data["sections"]

        # Tier 1: phrase matching on the full text
        t1_skills = self._tier1_phrase_match(full_text, sections)
        already_normalized = {s.normalized for s in t1_skills}

        if debug:
            print(f"  Tier 1: {len(t1_skills)} skills found by phrase match")

        # Tier 2: semantic matching on experience + skills sections
        priority_text = " ".join([
            sections.get("experience", ""),
            sections.get("skills", ""),
            sections.get("projects", ""),
        ])
        t2_skills = self._tier2_semantic(priority_text, already_normalized)
        already_normalized.update(s.normalized for s in t2_skills)

        if debug:
            print(f"  Tier 2: {len(t2_skills)} additional skills by semantic match")

        all_skills = t1_skills + t2_skills

        # Tier 3: LLM fallback — only if we found very few skills
        if len(all_skills) < 5 and self.openai_key:
            t3_skills = self._tier3_llm_fallback(full_text, all_skills)
            all_skills += t3_skills
            if debug:
                print(f"  Tier 3: {len(t3_skills)} additional skills from LLM fallback")

        return all_skills

    def _tier1_phrase_match(self, text: str, sections: Dict) -> List[ExtractedSkill]:
        doc = self.nlp(text)
        matches = self._matcher(doc)

        results = []
        seen = set()

        for match_id, start, end in matches:
            span = doc[start:end]
            normalized = span.text.lower().strip()

            if normalized in seen or normalized in STOP_SKILLS:
                continue
            seen.add(normalized)

            # Give higher confidence if found in skills/experience section
            section_hit = any(
                normalized in sections.get(sec, "").lower()
                for sec in ["skills", "experience", "projects"]
            )

            results.append(ExtractedSkill(
                name=span.text,
                normalized=normalized,
                confidence=0.98 if section_hit else 0.90,
                source="phrase_match",
                context=doc[max(0, start-10):end+10].text,
            ))

        return results

    def _tier2_semantic(
        self,
        text: str,
        already_normalized: Set[str],
    ) -> List[ExtractedSkill]:
        doc = self.nlp(text)

        # Extract meaningful noun chunks (multi-word phrases)
        chunks = list(set([
            chunk.text.strip()
            for chunk in doc.noun_chunks
            if len(chunk.text.strip()) > 2
            and chunk.text.strip().lower() not in STOP_SKILLS
        ]))

        if not chunks:
            return []

        # Encode all chunks in one batch
        chunk_vecs = self.embed_model.encode(
            chunks,
            batch_size=32,
            normalize_embeddings=True,
        )

        results = []
        for chunk, chunk_vec in zip(chunks, chunk_vecs):
            # Dot product of two normalized vectors = cosine similarity
            sims = np.dot(self._skill_embeddings, chunk_vec)
            best_idx = int(np.argmax(sims))
            best_sim = float(sims[best_idx])

            if best_sim < self.threshold:
                continue

            # Use the TAXONOMY skill name, not the raw chunk
            # This prevents hallucination (e.g., "predictive modeling" → "machine learning")
            matched_skill = self.skill_list[best_idx]
            normalized    = matched_skill.lower().strip()

            if normalized in already_normalized or normalized in STOP_SKILLS:
                continue

            results.append(ExtractedSkill(
                name=matched_skill,
                normalized=normalized,
                confidence=round(best_sim, 3),
                source="semantic",
                context=f"Matched from: '{chunk}'",
            ))
            already_normalized.add(normalized)

        return results

    def _tier3_llm_fallback(
        self,
        text: str,
        already_found: List[ExtractedSkill],
    ) -> List[ExtractedSkill]:
        """Uses OpenAI to extract skills as a last resort."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)

            already_names = [s.name for s in already_found]
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"""Extract professional and technical skills from this resume text.
Return ONLY a JSON array of skill name strings.
Do NOT include: personal traits, generic words, company names, school names.
Do NOT include these already-found skills: {already_names[:20]}

Resume text:
{text[:2000]}

Return format: ["skill1", "skill2", ...]
Return ONLY the JSON array, nothing else."""
                }]
            )

            raw = response.choices[0].message.content.strip()
            raw = re.sub(r"```json|```", "", raw).strip()
            skills_raw = json.loads(raw)

            return [
                ExtractedSkill(
                    name=skill,
                    normalized=skill.lower().strip(),
                    confidence=0.80,
                    source="llm_fallback",
                )
                for skill in skills_raw
                if isinstance(skill, str) and len(skill) > 1
            ]

        except Exception as e:
            print(f"⚠️  LLM fallback failed: {e}")
            return []