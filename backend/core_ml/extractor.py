"""Skill extraction from resume text using multi-tier approach."""

from __future__ import annotations
import logging
import json as _json
import numpy as np
from typing import List, Dict

from .schemas import ExtractedSkill
from .evidence import detect_scope_markers, detect_verb_strength

logger = logging.getLogger(__name__)

# How much a surrounding context proves about a skill.  Used to pick which
# occurrence of a repeated skill to keep — see _tier1_phrase_match.
_VERB_RANK = {"leadership": 3, "strong": 2, "weak": 1, "none": 0}

STOP_SKILLS = {
    "work", "use", "ability", "using", "used", "strong",
    "experience", "skills", "knowledge", "understanding",
    "management", "team", "working", "the", "and",
    "with", "for", "in", "of", "a", "an",
}


class SkillExtractor:
    def __init__(
        self,
        skill_list:         List[str],
        semantic_threshold: float = 0.75,
        openai_key:         str   = "",   # retained for compat; tier-3 uses MiniLM
        verbose:            bool  = True,
    ):
        # Lazy imports — kept inside __init__ so that importing this module
        # at collection time (e.g. `from core_ml.extractor import STOP_SKILLS`)
        # does NOT require spacy or sentence-transformers to be installed.
        # Tests marked `requires_ml` will still fail at runtime if the deps
        # are absent, but they will no longer abort the whole collection pass.
        import spacy as _spacy
        from spacy.matcher import PhraseMatcher as _PhraseMatcher

        # sentence-transformers pulls in torch, together ~400MB of resident
        # memory — more than a 512MB free-tier container has to spare.  Treat it
        # as an optional extra so the service can run without it.
        #
        # This import was previously unconditional, so a missing package raised
        # ImportError here and the embed_model=None fallback below was
        # unreachable: the whole extractor failed to construct.
        try:
            from sentence_transformers import SentenceTransformer as _SentenceTransformer
        except ImportError:
            _SentenceTransformer = None

        self.skill_list = [s for s in skill_list if s.lower() not in STOP_SKILLS]
        self.threshold  = semantic_threshold
        self._has_fallback = True   # PhraseMatcher + fuzzy tiers need no model

        if verbose:
            logger.info("Loading NLP models...")
        self.nlp = _spacy.load("en_core_web_sm") if _spacy.util.is_package("en_core_web_sm") else _spacy.blank("en")

        if _SentenceTransformer is None:
            self.embed_model = None
            logger.info(
                "sentence-transformers not installed — semantic tier disabled, "
                "extraction falls back to PhraseMatcher + fuzzy tiers."
            )
        else:
            try:
                self.embed_model = _SentenceTransformer("all-MiniLM-L6-v2")
                if verbose:
                    logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.info("Embedding model failed: %s", e)
                self.embed_model = None
                if verbose:
                    logger.info("Using basic mode without embeddings")

        self._matcher = _PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = list(self.nlp.pipe(self.skill_list))
        self._matcher.add("SKILLS", patterns)

        if verbose:
            logger.info("Encoding %d skills...", len(self.skill_list))

        self._skill_embeddings = np.array([])

        if self.embed_model is not None:
            self._skill_embeddings = self.embed_model.encode(
                self.skill_list, batch_size=64,
                normalize_embeddings=True, show_progress_bar=verbose,
            )
        else:
            if verbose:
                logger.info("Skipping skill encoding (no embedding model)")
        if verbose:
            logger.info("Skill extractor ready")

    def extract(self, resume_data: Dict, debug: bool = False) -> List[ExtractedSkill]:
        full_text = resume_data["full_text"]
        sections  = resume_data.get("sections", {})

        t1   = self._tier1_phrase_match(full_text, sections)
        seen = {s.normalized for s in t1}
        if debug:
            logger.debug(f"Tier 1 (phrase): {len(t1)} skills")

        priority_text = " ".join(sections.get(k, "") for k in ("skills", "experience", "projects"))
        t2   = self._tier2_semantic(priority_text, seen)
        seen.update(s.normalized for s in t2)
        if debug:
            logger.debug(f"Tier 2 (semantic): {len(t2)} skills")

        all_skills = t1 + t2

        # Threshold raised to 8 (was 5); logs a warning so the issue is visible
        if len(all_skills) < 8:
            logger.info(f"Only {len(all_skills)} skills found — PDF may have "
                       "parsing issues. Running tier-3 MiniLM window pass...")
            t3 = self._tier3_miniLM_fallback(full_text, all_skills)
            all_skills += t3
            if debug:
                logger.debug(f"Tier 3 (MiniLM window): {len(t3)} skills")

        return all_skills

    def _tier1_phrase_match(self, text: str, sections: Dict) -> List[ExtractedSkill]:
        """Phrase-match skills, keeping the BEST-EVIDENCED occurrence of each.

        Keeping the *first* occurrence made evidence level depend on where the
        skill happened to appear first, i.e. on resume section order.  A skill
        listed in a SKILLS header took its context from a comma-separated list
        with no verb — verb_strength "none", which determine_evidence_level caps
        at level 2 — even when a later experience bullet ("Built and deployed
        PyTorch models... 2M users") proved it at level 4.  Moving the
        EXPERIENCE block above SKILLS on an otherwise byte-identical resume
        shifted 13 skills from L2 to L4.

        The context we keep drives verb strength, scope markers and tenure
        downstream, so it must come from the occurrence that demonstrates the
        most, not the one that happens to be typeset first.
        """
        doc     = self.nlp(text)
        matches = self._matcher(doc)

        # normalized -> (rank, span, context) for the strongest occurrence so far
        best: Dict[str, tuple] = {}

        for _, start, end in matches:
            span       = doc[start:end]
            normalized = span.text.lower().strip()
            if not normalized or normalized in STOP_SKILLS:
                continue
            context = doc[max(0, start - 10): end + 10].text
            rank = (
                _VERB_RANK.get(detect_verb_strength(context), 0),
                1 if detect_scope_markers(context) else 0,
            )
            existing = best.get(normalized)
            if existing is None or rank > existing[0]:
                best[normalized] = (rank, span, context)

        results = []
        for normalized, (_rank, span, context) in best.items():
            section_hit = any(
                normalized in sections.get(sec, "").lower()
                for sec in ("skills", "experience", "projects")
            )
            results.append(ExtractedSkill(
                original=span.text,
                normalized=normalized,
                confidence=0.98 if section_hit else 0.90,
                source="phrase_match",
                context=context,
            ))
        return results

    def _tier2_semantic(self, text: str, already_normalized: set) -> List[ExtractedSkill]:
        # Return empty if no embedding model available
        if self.embed_model is None:
            return []
        doc    = self.nlp(text)
        # sorted(), not list(set(...)): chunks are consumed in order and the
        # first chunk to claim a skill wins via already_normalized, so
        # set-iteration order (hash-seed dependent) would make extraction vary
        # between runs on identical input.
        chunks = sorted({
            c.text.strip() for c in doc.noun_chunks
            if len(c.text.strip()) > 2 and c.text.strip().lower() not in STOP_SKILLS
        })
        if not chunks:
            return []
        chunk_vecs = self.embed_model.encode(chunks, batch_size=32, normalize_embeddings=True)
        results    = []
        for chunk, chunk_vec in zip(chunks, chunk_vecs):
            sims      = np.dot(self._skill_embeddings, chunk_vec)
            best_idx  = int(np.argmax(sims))
            best_sim  = float(sims[best_idx])
            if best_sim < self.threshold:
                continue
            normalized = self.skill_list[best_idx].lower().strip()
            if normalized in already_normalized or normalized in STOP_SKILLS:
                continue
            results.append(ExtractedSkill(
                original=self.skill_list[best_idx],
                normalized=normalized,
                confidence=round(best_sim, 3),
                source="semantic",
                context=f"Matched from: '{chunk}'",
            ))
            already_normalized.add(normalized)
        return results

    def _tier3_miniLM_fallback(
        self, text: str, already_found: List[ExtractedSkill]
    ) -> List[ExtractedSkill]:
        """
        No API key needed. Runs overlapping word-window passes through
        the already-loaded MiniLM at a slightly looser threshold (0.70).
        Deterministic, zero cost, consistent embedding space with tiers 1 & 2.
        """
        already_normalized = {s.normalized for s in already_found}
        WINDOW_THRESHOLD   = 0.70

        words = text.split()
        if len(words) < 3:
            return []

        windows: List[str] = []
        for size in (3, 6):
            step = max(1, size // 2)
            for i in range(0, max(1, len(words) - size + 1), step):
                w = " ".join(words[i: i + size]).strip()
                if len(w) > 4:
                    windows.append(w)
        if not windows:
            return []

        # Check if embed_model is None before encoding
        if self.embed_model is None:
            logger.info("Tier-3 skipped: no embedding model available")
            return []
        
        try:
            window_vecs = self.embed_model.encode(windows, batch_size=64, normalize_embeddings=True)
        except Exception as e:
            logger.info(f"Tier-3 encode failed: {e}")
            return []

        results: List[ExtractedSkill] = []
        matched_taxonomy: set = set()

        for window, w_vec in zip(windows, window_vecs):
            sims      = np.dot(self._skill_embeddings, w_vec)
            best_idx  = int(np.argmax(sims))
            best_sim  = float(sims[best_idx])
            if best_sim < WINDOW_THRESHOLD:
                continue
            normalized = self.skill_list[best_idx].lower().strip()
            if normalized in already_normalized or normalized in matched_taxonomy or normalized in STOP_SKILLS:
                continue
            matched_taxonomy.add(normalized)
            results.append(ExtractedSkill(
                original=self.skill_list[best_idx],
                normalized=normalized,
                confidence=round(best_sim, 3),
                source="minilm_fallback",
                context=f"Window: '{window}'",
            ))
        return results
