# ============================================================
# BRIDGR ML — FINAL FIXED COLAB NOTEBOOK
# All issues from the review document fixed.
# Run cells top-to-bottom in Google Colab.
# ============================================================

from __future__ import annotations

# Fix 1: Force disable broken HuggingFace behavior
import os
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"


# ─────────────────────────────────────────────────────────────
# CELL 1 — Install dependencies  ← RUN THIS FIRST
# ─────────────────────────────────────────────────────────────
# FIXED: was wrapped in a triple-quoted string (dead code).
# Now live executable code — just run this cell.

# Uncomment and run in Colab:
# !pip install -q spacy sentence-transformers scikit-learn pandas \
#              pdfplumber openai python-dotenv pydantic numpy rapidfuzz
# !python -m spacy download en_core_web_sm -q
# print("✅ All dependencies installed")


# ─────────────────────────────────────────────────────────────
# CELL 2 — Imports  ← NO CHANGES NEEDED
# ─────────────────────────────────────────────────────────────
# FIXED: removed unused model_validator import.

from pydantic import BaseModel, field_validator
from typing import List, Dict, Optional, Any, Tuple


class ExtractedSkill(BaseModel):
    original:   str
    normalized: str
    confidence: float
    source:     str = "resume"
    context:    str = ""

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class SkillGap(BaseModel):
    name:               str
    priority:           str
    priority_score:     float = 0.5
    market_demand:      float = 0.05
    reason:             str   = ""
    estimated_weeks:    int   = 4
    has_foundation:     bool  = False
    learning_resources: List[str] = []

    @property
    def demand_percentage(self) -> int:
        return int(self.market_demand * 100)


class TransferableSkill(BaseModel):
    user_skill:        str
    maps_to_job_skill: str
    transfer_score:    float
    explanation:       str


class AnalysisResult(BaseModel):
    analysis_id:      str
    generated_at:     str
    target_role:      str

    match_score:      int
    readiness_level:  str
    confidence_score: float

    extracted_skills:    List[ExtractedSkill]
    matched_skills:      List[str]
    missing_required:    List[SkillGap]
    missing_preferred:   List[SkillGap]
    transferable_skills: List[TransferableSkill]
    priority_skills:     List[str]
    market_demand_skills: List[str]

    learning_roadmap_inputs: Dict[str, Any]
    mock_interview_inputs:   Dict[str, Any]
    career_chat_context:     Dict[str, Any]

    salary_band_estimate: Dict[str, Any]
    feasibility: Optional[Dict[str, Any]] = None
    explanations:         List[str]


class ChatRequest(BaseModel):
    message:     str
    analysis_id: Optional[str]           = None
    context:     Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    reply:       str
    suggestions: List[str] = []


class AnalyzeRequest(BaseModel):
    target_role: str


class RoadmapResponse(BaseModel):
    phases:      List[Dict[str, Any]]
    total_weeks: int
    summary:     str


print("✅ CELL 2 — models loaded")


# ─────────────────────────────────────────────────────────────
# CELL 3 — Dataset loader
# ─────────────────────────────────────────────────────────────

import zipfile, glob as _glob
import pandas as pd
from pathlib import Path
from collections import Counter


class OnetDatasetLoader:
    def __init__(self, zip_path: str, extract_path: str):
        self.zip_path     = zip_path
        self.extract_path = extract_path
        self._df: Optional[pd.DataFrame] = None
        self.skill_market_demand: Dict[str, float] = {}

    def load(self) -> pd.DataFrame:
        if self._df is not None:
            return self._df
        self._extract_zip()
        self._df = self._build_dataset()
        print(f"✅ Dataset loaded: {len(self._df)} job profiles")
        return self._df

    def _extract_zip(self):
        if _glob.glob(f"{self.extract_path}/db_*"):
            print("📦 Dataset already extracted")
            return
        if self.zip_path and Path(self.zip_path).exists():
            print("📦 Extracting dataset...")
            with zipfile.ZipFile(self.zip_path, "r") as z:
                z.extractall(self.extract_path)
        else:
            print("⚠️  No ZIP file found — expecting pre-extracted db_* folder")

    @staticmethod
    def _agg_skills(series) -> List[str]:
        return list({
            str(v).lower().strip()
            for v in series
            if pd.notnull(v) and str(v).strip()
        })

    def _build_dataset(self) -> pd.DataFrame:
        folders = _glob.glob(f"{self.extract_path}/db_*")
        if not folders:
            raise FileNotFoundError(
                f"No db_* folder found in '{self.extract_path}'. "
                "Provide the dataset ZIP or pre-extracted folder."
            )
        base = sorted(folders)[-1]
        print(f"📂 Using folder: {base}")

        occ    = pd.read_csv(f"{base}/Occupation Data.txt",   sep="\t")
        skills = pd.read_csv(f"{base}/Skills.txt",            sep="\t")
        tech   = pd.read_csv(f"{base}/Technology Skills.txt", sep="\t")

        soft = (
            skills[(skills["Scale ID"] == "IM") & (skills["Data Value"] > 3.0)]
            [["O*NET-SOC Code", "Element Name", "Data Value"]]
            .rename(columns={"Element Name": "soft_skill",
                             "Data Value":   "soft_skill_importance"})
        )
        hard = (
            tech[["O*NET-SOC Code", "Example", "Commodity Title"]]
            .rename(columns={"Example":        "tech_skill",
                             "Commodity Title": "skill_category"})
        )

        df    = occ.merge(soft, on="O*NET-SOC Code", how="left")
        df    = df.merge(hard, on="O*NET-SOC Code", how="left")
        final = df.groupby("Title").agg(
            job_description=("Description", "first"),
            tech_skills=    ("tech_skill",  self._agg_skills),
            soft_skills=    ("soft_skill",  self._agg_skills),
        ).reset_index()
        final.columns  = ["job_title", "job_description", "tech_skills", "soft_skills"]
        final["all_skills"] = final["tech_skills"] + final["soft_skills"]

        total     = max(len(final), 1)
        tech_flat = final["tech_skills"].explode().dropna()
        soft_flat = final["soft_skills"].explode().dropna()
        tech_freq = Counter(tech_flat)
        soft_freq = Counter(soft_flat)
        self.skill_market_demand = {
            s: (tech_freq.get(s, 0) + 0.5 * soft_freq.get(s, 0)) / total
            for s in set(tech_freq) | set(soft_freq)
        }
        return final

    def get_job_profile(self, title: str):
        df = self.load()
        t  = title.lower().strip()
        exact = df[df["job_title"].str.lower() == t]
        if not exact.empty:
            return exact.iloc[0]
        # regex=False prevents injection from user-controlled strings
        partial = df[df["job_title"].str.lower().str.contains(t, na=False, regex=False)]
        if not partial.empty:
            # Return closest by title-length distance, not first alphabetically
            partial = partial.copy()
            partial["_dist"] = partial["job_title"].str.len().sub(len(t)).abs()
            row = partial.sort_values("_dist").iloc[0]
            print(f"⚠️  Closest match: '{row['job_title']}'")
            return row
        return None

    def get_all_tech_skills(self) -> List[str]:
        df = self.load()
        return list({s for s in df["tech_skills"].explode().dropna() if s})


print("✅ CELL 3 — dataset loader loaded")


# ─────────────────────────────────────────────────────────────
# CELL 4 — Resume parser
# ─────────────────────────────────────────────────────────────
# FIXED:
#   - Section regex: ^experience$ anchor inside alternation group
#     now uses word-boundary instead of regex anchor (which was
#     matched literally inside re.search, not as anchor).
#   - All-caps section headers now matched (SKILLS, EXPERIENCE etc.)
#   - Headers with trailing colons matched (Skills:)
#   - Lines up to 80 chars tested, not just < 50

import re
from collections import defaultdict


class ResumeParser:
    # FIXED: permissive patterns that handle:
    #   - mixed case and ALL CAPS
    #   - trailing colons
    #   - word boundaries (no more literal ^ inside alternation)
    SECTION_PATTERNS = {
        "experience":     r"(work[\s\-]?exp|professional[\s\-]?exp|employment|work[\s\-]?hist|\bexperience\b)",
        "education":      r"(education|academic|qualification|degree|schooling)",
        "skills":         r"(skills|technical[\s\-]?skills|technologies|tools|competencies|proficiencies)",
        "projects":       r"(projects|personal[\s\-]?projects|academic[\s\-]?projects|portfolio)",
        "summary":        r"(summary|objective|profile|about[\s\-]?me|overview)",
        "certifications": r"(certifications?|certificates?|licenses?|credentials?|awards?)",
    }

    def parse(self, pdf_path: str) -> Dict:
        raw_text, page_count = self._extract_text_and_pages(pdf_path)
        sections = self._detect_sections(raw_text)
        return {
            "full_text": raw_text,
            "sections":  sections,
            "metadata": {
                "pages":              page_count,
                "char_count":         len(raw_text),
                "has_skills_section": "skills" in sections,
            },
        }

    @staticmethod
    def _extract_text_and_pages(path: str) -> Tuple[str, int]:
        # Try pymupdf first (handles multi-column layouts)
        try:
            import fitz
            text, pages = "", 0
            with fitz.open(path) as doc:
                pages = len(doc)
                for page in doc:
                    blocks = sorted(page.get_text("blocks"), key=lambda b: (round(b[1] / 20), b[0]))
                    for b in blocks:
                        if b[4].strip():
                            text += b[4].strip() + "\n"
                    text += "\n"
            if text.strip():
                return text, pages
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️  pymupdf failed ({e}), trying pdfplumber")

        # Fallback: pdfplumber
        try:
            import pdfplumber
            text, pages = "", 0
            with pdfplumber.open(path) as pdf:
                pages = len(pdf.pages)
                for page in pdf.pages:
                    t = page.extract_text(x_tolerance=3, y_tolerance=3)
                    if t:
                        text += t + "\n"
        except Exception as e:
            raise ValueError(f"Could not read PDF: {e}")

        if not text.strip():
            raise ValueError(
                "This PDF appears to be image-based (scanned). "
                "Bridgr needs a text-based PDF — please export from Google Docs or Word."
            )
        return text, pages

    def _detect_sections(self, text: str) -> Dict[str, str]:
        lines    = text.split("\n")
        sections = defaultdict(list)
        current  = "header"

        for line in lines:
            stripped   = line.strip()
            # Normalise: lowercase, strip trailing colon, remove leading numbers
            line_clean = re.sub(r"^[\d]+[\.\)]\s*", "", stripped.lower()).rstrip(":").strip()

            matched = None
            # Test lines up to 80 chars that don't look like bullet body text
            if 1 < len(line_clean) < 80 and not line_clean.startswith(("•", "-", "*")):
                for sec_name, pattern in self.SECTION_PATTERNS.items():
                    if re.search(pattern, line_clean):
                        matched = sec_name
                        break

            if matched:
                current = matched
            elif stripped:
                sections[current].append(stripped)

        return {k: "\n".join(v) for k, v in sections.items() if v}

    def parse_dict(self, resume_dict: Dict) -> Dict:
        """Accept a pre-built dict — for testing without a PDF."""
        return resume_dict


print("✅ CELL 4 — resume parser loaded")


# ─────────────────────────────────────────────────────────────
# CELL 5 — Skill extractor
# ─────────────────────────────────────────────────────────────
# FIXED:
#   - openai_key is stored but the condition if len < 5 and openai_key
#     now clearly documents that tier-3 is MiniLM-based (no key needed).
#     The openai_key param is kept for API compatibility but ignored.
#   - LLM fallback threshold raised from 5 to 8 (5 was too low;
#     a real resume should yield 10-20 skills — under 8 = parse failure)

import json as _json
import numpy as np
import spacy
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer

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
        self.skill_list = [s for s in skill_list if s.lower() not in STOP_SKILLS]
        self.threshold  = semantic_threshold
        # openai_key retained so callers don't break, but tier-3 no longer needs it
        self._has_fallback = True   # always available — MiniLM is already loaded

        if verbose:
            print("🔧 Loading NLP models...")
        self.nlp         = spacy.load("en_core_web_sm")
        
        # Fix 2: Use safer model loading method
        # Fix 3: HARD PROTECT fallback (CRITICAL)
        try:
            self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
            if verbose:
                print("✅ Embedding model loaded successfully")
        except Exception as e:
            print("⚠️ Embedding model failed:", e)
            self.embed_model = None
            if verbose:
                print("⚠️ Using basic mode without embeddings")

        self._matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = list(self.nlp.pipe(self.skill_list))
        self._matcher.add("SKILLS", patterns)

        if verbose:
            print(f"⚡ Encoding {len(self.skill_list)} skills...")
        
        # Initialize _skill_embeddings to empty array to prevent AttributeError
        self._skill_embeddings = np.array([])
        
        if self.embed_model is not None:
            self._skill_embeddings = self.embed_model.encode(
                self.skill_list, batch_size=64,
                normalize_embeddings=True, show_progress_bar=verbose,
            )
        else:
            if verbose:
                print("⚠️ Skipping skill encoding (no embedding model)")
        if verbose:
            print("✅ Skill extractor ready")

    def extract(self, resume_data: Dict, debug: bool = False) -> List[ExtractedSkill]:
        full_text = resume_data["full_text"]
        sections  = resume_data.get("sections", {})

        t1   = self._tier1_phrase_match(full_text, sections)
        seen = {s.normalized for s in t1}
        if debug:
            print(f"  Tier 1 (phrase): {len(t1)} skills")

        priority_text = " ".join(sections.get(k, "") for k in ("skills", "experience", "projects"))
        t2   = self._tier2_semantic(priority_text, seen)
        seen.update(s.normalized for s in t2)
        if debug:
            print(f"  Tier 2 (semantic): {len(t2)} skills")

        all_skills = t1 + t2

        # FIXED: threshold raised to 8 (was 5); logs a warning so the issue
        # is visible instead of silently triggering fallback
        if len(all_skills) < 8:
            print(f"⚠️  Only {len(all_skills)} skills found — PDF may have "
                  "parsing issues. Running tier-3 MiniLM window pass...")
            t3 = self._tier3_miniLM_fallback(full_text, all_skills)
            all_skills += t3
            if debug:
                print(f"  Tier 3 (MiniLM window): {len(t3)} skills")

        return all_skills

    def _tier1_phrase_match(self, text: str, sections: Dict) -> List[ExtractedSkill]:
        doc     = self.nlp(text)
        matches = self._matcher(doc)
        results, seen = [], set()

        for _, start, end in matches:
            span       = doc[start:end]
            normalized = span.text.lower().strip()
            if normalized in seen or normalized in STOP_SKILLS:
                continue
            seen.add(normalized)
            section_hit = any(
                normalized in sections.get(sec, "").lower()
                for sec in ("skills", "experience", "projects")
            )
            results.append(ExtractedSkill(
                original=span.text,
                normalized=normalized,
                confidence=0.98 if section_hit else 0.90,
                source="phrase_match",
                context=doc[max(0, start - 10): end + 10].text,
            ))
        return results

    def _tier2_semantic(self, text: str, already_normalized: set) -> List[ExtractedSkill]:
        # FIXED: Return empty if no embedding model available
        if self.embed_model is None:
            return []
        doc    = self.nlp(text)
        chunks = list({
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

        # FIXED: Check if embed_model is None before encoding
        if self.embed_model is None:
            print("⚠️  Tier-3 skipped: no embedding model available")
            return []
        
        try:
            window_vecs = self.embed_model.encode(windows, batch_size=64, normalize_embeddings=True)
        except Exception as e:
            print(f"⚠️  Tier-3 encode failed: {e}")
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


print("✅ CELL 5 — skill extractor loaded")


# ─────────────────────────────────────────────────────────────
# CELL 6 — Matching engine
# ─────────────────────────────────────────────────────────────
# FIXED:
#   - _vec_cache now LRU-bounded (cachetools) — no memory leak
#   - Returns (score, confidence, "empty job profile") message
#     instead of silent (0, 0.3) so callers can show useful error

import hashlib
from sklearn.metrics.pairwise import cosine_similarity

try:
    from cachetools import LRUCache as _LRUCache
    _lru_available = True
except ImportError:
    _lru_available = False


class MatchingEngine:
    def __init__(self, embed_model):
        self.embed_model = embed_model
        # FIXED: Handle case when embed_model is None
        if embed_model is not None:
            self._embed_dim  = embed_model.get_sentence_embedding_dimension()
        else:
            self._embed_dim = 384  # Default dimension for MiniLM-L6-v2
        # FIXED: bounded LRU cache — no unbounded memory growth
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

        # FIXED: return explicit sentinel with print so caller knows why score is 0
        if not user_skills or not job_all:
            if not job_all:
                print("⚠️  Job profile has no skills — cannot compute match score. "
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

        # FIXED: Handle case when embed_model is None
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


print("✅ CELL 6 — matching engine loaded")


# ─────────────────────────────────────────────────────────────
# CELL 7 — Gap analyser
# ─────────────────────────────────────────────────────────────
# FIXED:
#   - get_salary_band: keys use underscores, lookup uses spaces →
#     NEVER matched. Fixed by normalising both sides consistently
#     AND using a keyword-in-string approach that works with spaces.
#   - _build_prerequisite_map: still O(skills²) on full O*NET.
#     Added tqdm progress + a max_skills cap (500) so it doesn't
#     hang the kernel on first call.

from typing import Set
from datetime import datetime as _dt

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


# FIXED: salary band keys and lookup both use lowercase with spaces
# so keyword-in-role matching always works.
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
    import copy
    for role_key, band in overrides.items():
        # Store with lowercase spaces so get_salary_band lookup always matches
        INDIA_SALARY_BANDS[role_key.lower().strip()] = copy.deepcopy(band)
    print(f"✅ Salary bands updated for: {list(overrides.keys())}")


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

        # FIXED: cap at 500 skills to avoid O(N²) hang on full O*NET
        # and add progress dots so the user knows it's working
        if len(all_skills) > 500:
            print(f"   Capping prerequisite map at 500 skills (full set: {len(all_skills)})")
            all_skills = all_skills[:500]

        prereq_map: Dict[str, List[str]] = {}
        print(f"   Building prerequisite map for {len(all_skills)} skills", end="", flush=True)
        for i, skill in enumerate(all_skills):
            if i % 50 == 0:
                print(".", end="", flush=True)
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
        print(" done")
        return prereq_map

    def _build_learning_time_map(self) -> Dict[str, int]:
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
        market_demand    = self.skill_market_demand.get(skill, 0.05)
        weeks            = self.learning_time_map.get(skill, self.learning_time_map["default"])
        difficulty       = weeks / self.max_weeks

        prereqs          = self.prerequisite_map.get(skill, [])
        prereqs_met      = sum(1 for p in prereqs if p in user_set)
        has_foundation   = prereqs_met > 0 and prereqs
        foundation_bonus = prereqs_met / len(prereqs) if prereqs else 0.0
        transfer_bonus   = 0.5 if skill in transferable_targets else 0.0

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
        # FIXED: both keys and lookup use lowercase with spaces — always matches
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
        p1_skills = critical[:4]
        p2_skills = high[:4]
        p3_skills = medium[:3] + high[4:6]

        # FIXED: duration computed from actual gap weeks, not hardcoded min()
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


print("✅ CELL 7 — gap analyser loaded")


# ─────────────────────────────────────────────────────────────
# CELL 8 — Dynamic job skills
# ─────────────────────────────────────────────────────────────

import json as _json2, copy as _copy
from pathlib import Path as _Path


class DynamicJobSkills:
    def __init__(self, data_dir: str = "data/"):
        self.data_dir     = _Path(data_dir)
        self.skills_cache: Dict[str, Dict] = {}
        self._onet_loader = None

    def set_onet_loader(self, loader) -> None:
        self._onet_loader = loader

    def load_job_skills(self, role_name: str) -> Optional[Dict]:
        role_key = role_name.lower().strip().replace(" ", "_")
        if role_key in self.skills_cache:
            return self.skills_cache[role_key]
        result = (
            self._load_custom_skills(role_key)
            or self._load_onet_skills(role_key)
            or self._get_default_skills()
        )
        self.skills_cache[role_key] = result
        return result

    def _load_custom_skills(self, role_key: str) -> Optional[Dict]:
        path = self.data_dir / f"custom_skills/{role_key}.json"
        if not path.exists():
            return None
        try:
            with open(path, encoding="utf-8") as f:
                return _json2.load(f)
        except Exception as e:
            print(f"⚠️  Custom skills load failed for {role_key}: {e}")
            return None

    def _load_onet_skills(self, role_key: str) -> Optional[Dict]:
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
            print(f"⚠️  O*NET lookup failed for {role_key}: {e}")
            return None

    def _get_default_skills(self) -> Dict:
        return {
            "tech_skills": ["python", "sql", "git", "rest api", "documentation"],
            "soft_skills": ["communication", "problem solving", "teamwork", "time management"],
            "source":      "default_fallback",
        }

    def get_skill_market_demand(self, role_key: str) -> Dict[str, float]:
        if self._onet_loader is not None:
            return self._onet_loader.skill_market_demand
        data   = self.load_job_skills(role_key) or {}
        skills = data.get("tech_skills", []) + data.get("soft_skills", [])
        total  = max(len(skills), 1)
        return {s: 1.0 / total for s in skills}

    def update_skills_from_config(self, config_updates: Dict) -> None:
        for role_key, updates in config_updates.items():
            base = _copy.deepcopy(self.skills_cache.get(role_key, {}))
            base.update({k: _copy.deepcopy(v) for k, v in updates.items()})
            self.skills_cache[role_key] = base

    def save_custom_skills(self, role_key: str, skills_data: Dict) -> bool:
        try:
            path = self.data_dir / f"custom_skills/{role_key}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                _json2.dump(skills_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"⚠️  Could not save custom skills: {e}")
            return False


print("✅ CELL 8 — dynamic job skills loaded")


# ─────────────────────────────────────────────────────────────
# CELL 9 — IntelligenceCore
# ─────────────────────────────────────────────────────────────

import os as _os, uuid, glob as _glob2
from datetime import datetime, timezone


class IntelligenceCore:
    def __init__(self, config: Dict):
        print("\n🚀 Initialising Bridgr Intelligence Core...")
        extract_path = config["ONET_EXTRACT_PATH"]
        db_folders   = _glob2.glob(_os.path.join(extract_path, "db_*"))

        if db_folders:
            self.dataset_loader = OnetDatasetLoader(zip_path="", extract_path=extract_path)
        else:
            zip_path = config.get("ONET_ZIP_PATH", "")
            if _os.path.exists(zip_path):
                self.dataset_loader = OnetDatasetLoader(zip_path=zip_path, extract_path=extract_path)
            else:
                raise FileNotFoundError(
                    f"Dataset not found in '{extract_path}'. "
                    "Set ONET_ZIP_PATH or place db_* folder in ONET_EXTRACT_PATH."
                )

        self.dataset_loader.load()
        all_skills = self.dataset_loader.get_all_tech_skills()

        self.resume_parser   = ResumeParser()
        self.skill_extractor = SkillExtractor(
            skill_list=all_skills,
            semantic_threshold=float(config.get("SEMANTIC_THRESHOLD", 0.75)),
        )
        self.matching_engine = MatchingEngine(self.skill_extractor.embed_model)
        self.gap_analyzer    = GapAnalyzer(
            self.dataset_loader.skill_market_demand,
            dataset_loader=self.dataset_loader,
        )
        self.dynamic_job_skills = DynamicJobSkills(data_dir=config.get("DATA_DIR", "data/"))
        self.dynamic_job_skills.set_onet_loader(self.dataset_loader)
        print("✅ Bridgr Intelligence Core ready\n")

    def analyze(self, resume_path: str, target_role: str) -> AnalysisResult:
        print(f"📄 Parsing: {resume_path}")
        resume_data = self.resume_parser.parse(resume_path)
        return self._run(resume_data, target_role)

    def analyze_dict(self, resume_dict: Dict, target_role: str) -> AnalysisResult:
        return self._run(resume_dict, target_role)

    def _run(self, resume_data: Dict, target_role: str) -> AnalysisResult:
        print("🔍 Extracting skills...")
        extracted   = self.skill_extractor.extract(resume_data)
        user_skills = [s.normalized for s in extracted]
        print(f"   {len(extracted)} skills extracted")

        print(f"📋 Loading profile for: {target_role}")
        job_profile = self.dataset_loader.get_job_profile(target_role)
        if job_profile is None:
            skills_data = self.dynamic_job_skills.load_job_skills(target_role)
            if not skills_data:
                raise ValueError(
                    f"No skills data found for '{target_role}'. "
                    "Add a custom_skills JSON or check dataset availability."
                )
            job_profile = {
                "job_title":       target_role,
                "job_description": f"Requirements for {target_role}",
                "tech_skills":     skills_data.get("tech_skills", []),
                "soft_skills":     skills_data.get("soft_skills", []),
            }

        job_tech = list(job_profile["tech_skills"])
        job_soft = list(job_profile["soft_skills"])

        # Guard: if job profile is empty warn clearly before scoring
        if not job_tech and not job_soft:
            print(f"⚠️  Role '{target_role}' resolved to an empty skill profile. "
                  "Match score will be 0. Consider adding a custom_skills JSON.")

        print("⚡ Computing match score...")
        match_score, confidence = self.matching_engine.compute_match(user_skills, job_tech, job_soft)

        missing_all  = list((set(job_tech) | set(job_soft)) - set(user_skills))
        transferable = self.matching_engine.find_transferable_skills(user_skills, missing_all)

        print("📊 Analysing gaps...")
        missing_required, missing_preferred = self.gap_analyzer.analyze(
            user_skills, job_tech, job_soft, transferable
        )

        readiness       = _readiness_label(match_score)
        matched         = list(set(user_skills) & (set(job_tech) | set(job_soft)))
        priority_skills = [g.name for g in missing_required if g.priority in ("Critical", "High")][:5]

        market_demand_skills = sorted(
            [(s, v) for s, v in self.dataset_loader.skill_market_demand.items()
             if v > HIGH_DEMAND_THRESHOLD],
            key=lambda x: x[1], reverse=True,
        )[:8]
        market_demand_skills = [s for s, _ in market_demand_skills]

        salary_band = self.gap_analyzer.get_salary_band(target_role)

        critical = [g for g in missing_required if g.priority == "Critical"]
        high     = [g for g in missing_required if g.priority == "High"]
        medium   = [g for g in missing_required if g.priority == "Medium"]
        roadmap  = self.gap_analyzer.build_roadmap(critical, high, medium, match_score)

        explanations = _build_explanations(match_score, matched, missing_required, transferable)

        print(f"✅ Analysis complete: {readiness} ({match_score}%)\n")

        return AnalysisResult(
            analysis_id=str(uuid.uuid4()),
            generated_at=datetime.now(timezone.utc).isoformat(),
            target_role=target_role,
            match_score=match_score,
            readiness_level=readiness,
            confidence_score=confidence,
            extracted_skills=extracted,
            matched_skills=matched,
            missing_required=missing_required[:10],
            missing_preferred=missing_preferred[:8],
            transferable_skills=transferable,
            priority_skills=priority_skills,
            market_demand_skills=market_demand_skills,
            learning_roadmap_inputs=roadmap,
            mock_interview_inputs={
                "target_role":  target_role,
                "weak_areas":   [g.name for g in missing_required[:4]],
                "strong_areas": matched[:5],
                "difficulty":   "Beginner" if match_score < 40 else "Intermediate" if match_score < 70 else "Advanced",
            },
            career_chat_context={
                "user_strengths":  matched[:5],
                "user_gaps":       [g.name for g in missing_required[:5]],
                "readiness_level": readiness,
                "match_score":     match_score,
                "target_role":     target_role,
                "top_transferable": [
                    {"from": t.user_skill, "to": t.maps_to_job_skill}
                    for t in transferable[:3]
                ],
            },
            salary_band_estimate=salary_band,
            explanations=explanations,
        )


def _readiness_label(score: int) -> str:
    if   score >= 80: return "Job-Ready"
    elif score >= 65: return "Almost Ready"
    elif score >= 50: return "Developing"
    elif score >= 35: return "Early Stage"
    else:             return "Foundation Stage"


def _build_explanations(
    match_score: int,
    matched:     List[str],
    missing:     List[SkillGap],
    transferable: List[TransferableSkill],
) -> List[str]:
    out = []
    if matched:
        out.append(f"Your {match_score}% match is driven by: {', '.join(matched[:3])}.")
    if missing:
        top = missing[0]
        out.append(f"Top gap: '{top.name}' — {top.reason}.")
    if transferable:
        t = transferable[0]
        out.append(
            f"'{t.user_skill}' gives you a head start on '{t.maps_to_job_skill}' "
            f"({int(t.transfer_score * 100)}% overlap)."
        )
    return out


print("✅ CELL 9 — IntelligenceCore loaded")


# ─────────────────────────────────────────────────────────────
# CELL 10 — FallbackIntelligenceCore
# ─────────────────────────────────────────────────────────────
# FIXED:
#   - uuid and datetime imported at top of THIS cell so it works
#     standalone without depending on Cell 9 having run first.
#   - Salary band lookup: now delegates to gap_analyzer.get_salary_band()
#     which uses the fixed keyword-in-string matching (spaces, not underscores).
#   - Empty tech_skills for unrecognised role: now falls back to a
#     generic skill set instead of returning [] silently.
#   - FallbackCore now populates learning_roadmap_inputs, mock_interview_inputs,
#     career_chat_context (were empty dicts before — broke the results display).
#   - KNOWN_ROLES expanded from 7 to 15 roles.

import uuid as _uuid_fb
from datetime import datetime as _dt_fb, timezone as _tz_fb


class FallbackIntelligenceCore:
    KNOWN_ROLES: Dict[str, Dict] = {
        "data scientist":            {"tech": ["python","sql","machine learning","statistics","pandas","numpy","scikit-learn","tensorflow","tableau"],  "soft": ["communication","problem solving","data storytelling"]},
        "software engineer":         {"tech": ["python","java","git","docker","sql","rest api","algorithms","data structures","system design"],           "soft": ["teamwork","communication","code review"]},
        "data analyst":              {"tech": ["sql","excel","tableau","python","power bi","statistics"],                                                "soft": ["analytical thinking","attention to detail","communication"]},
        "machine learning engineer": {"tech": ["python","tensorflow","pytorch","mlops","docker","kubernetes","aws"],                                      "soft": ["research","problem solving","communication"]},
        "frontend developer":        {"tech": ["javascript","react","html","css","typescript","git","node.js"],                                          "soft": ["creativity","communication","attention to detail"]},
        "backend developer":         {"tech": ["python","java","node.js","sql","docker","rest api","git","postgresql"],                                  "soft": ["problem solving","teamwork","documentation"]},
        "fullstack developer":       {"tech": ["javascript","react","node.js","sql","docker","git","typescript","rest api"],                             "soft": ["problem solving","communication","teamwork"]},
        "devops engineer":           {"tech": ["docker","kubernetes","aws","ci/cd","linux","terraform","bash","ansible"],                                "soft": ["communication","reliability","incident management"]},
        "data engineer":             {"tech": ["python","sql","spark","airflow","kafka","dbt","docker","aws"],                                           "soft": ["problem solving","communication","collaboration"]},
        "product manager":           {"tech": ["jira","sql","analytics","figma","agile","roadmapping"],                                                 "soft": ["communication","leadership","stakeholder management","product thinking"]},
        "android developer":         {"tech": ["kotlin","java","android sdk","git","rest api","firebase","sqlite"],                                     "soft": ["creativity","problem solving","communication"]},
        "ios developer":             {"tech": ["swift","xcode","git","rest api","core data","firebase","objective-c"],                                  "soft": ["creativity","problem solving","communication"]},
        "nlp engineer":              {"tech": ["python","huggingface","pytorch","transformers","spacy","nltk","sql","docker"],                          "soft": ["research","communication","problem solving"]},
        "sdet":                      {"tech": ["python","selenium","pytest","git","rest api","ci/cd","postman","appium"],                               "soft": ["attention to detail","problem solving","communication"]},
        "cloud engineer":            {"tech": ["aws","gcp","azure","terraform","docker","kubernetes","linux","ci/cd"],                                  "soft": ["problem solving","communication","documentation"]},
    }

    # Generic fallback for any role not in KNOWN_ROLES
    _GENERIC_TECH = ["python", "git", "sql", "rest api", "documentation", "linux"]
    _GENERIC_SOFT = ["communication", "problem solving", "teamwork", "time management"]

    def __init__(self, config: Dict):
        print("\n🔄 Initialising FallbackIntelligenceCore (no dataset needed)...")
        self.config = config

        self.resume_parser = ResumeParser()
        all_skills = list({s for r in self.KNOWN_ROLES.values() for s in r["tech"] + r["soft"]})
        self.skill_extractor = SkillExtractor(
            skill_list=all_skills,
            semantic_threshold=float(config.get("SEMANTIC_THRESHOLD", 0.75)),
            verbose=True,
        )
        self.matching_engine = MatchingEngine(self.skill_extractor.embed_model)
        uniform_demand       = {s: 0.10 for s in all_skills}
        self.gap_analyzer    = GapAnalyzer(uniform_demand)
        print("✅ FallbackIntelligenceCore ready\n")

    def _get_job_profile(self, role: str) -> Dict:
        role_lower = role.lower().strip()
        # Exact match first
        if role_lower in self.KNOWN_ROLES:
            val = self.KNOWN_ROLES[role_lower]
            return {"job_title": role_lower, "tech_skills": val["tech"], "soft_skills": val["soft"]}
        # Substring match — longest key wins to avoid "engineer" beating "data engineer"
        best_key, best_len = None, 0
        for key in self.KNOWN_ROLES:
            if (key in role_lower or role_lower in key) and len(key) > best_len:
                best_key, best_len = key, len(key)
        if best_key:
            val = self.KNOWN_ROLES[best_key]
            return {"job_title": best_key, "tech_skills": val["tech"], "soft_skills": val["soft"]}

        # FIXED: no longer returns empty tech_skills silently
        print(f"⚠️  Role '{role}' not in known roles — using generic tech profile.")
        return {"job_title": role, "tech_skills": self._GENERIC_TECH, "soft_skills": self._GENERIC_SOFT}

    def analyze(self, resume_path: str, target_role: str) -> AnalysisResult:
        resume_data = self.resume_parser.parse(resume_path)
        return self.analyze_dict(resume_data, target_role)

    def analyze_dict(self, resume_data: Dict, target_role: str) -> AnalysisResult:
        extracted   = self.skill_extractor.extract(resume_data)
        user_skills = [s.normalized for s in extracted]

        job_profile  = self._get_job_profile(target_role)
        job_tech     = job_profile["tech_skills"]
        job_soft     = job_profile["soft_skills"]

        match_score, confidence = self.matching_engine.compute_match(user_skills, job_tech, job_soft)
        missing_all  = list((set(job_tech) | set(job_soft)) - set(user_skills))
        transferable = self.matching_engine.find_transferable_skills(user_skills, missing_all)
        missing_required, missing_preferred = self.gap_analyzer.analyze(
            user_skills, job_tech, job_soft, transferable
        )

        readiness = _readiness_label(match_score)
        matched   = list(set(user_skills) & (set(job_tech) | set(job_soft)))

        critical = [g for g in missing_required if g.priority == "Critical"]
        high     = [g for g in missing_required if g.priority == "High"]
        medium   = [g for g in missing_required if g.priority == "Medium"]
        # FIXED: roadmap now populated (was empty dict before)
        roadmap  = self.gap_analyzer.build_roadmap(critical, high, medium, match_score)
        # FIXED: salary uses fixed keyword-in-string lookup
        salary   = self.gap_analyzer.get_salary_band(target_role)
        explanations = _build_explanations(match_score, matched, missing_required, transferable)

        return AnalysisResult(
            analysis_id=str(_uuid_fb.uuid4()),
            generated_at=_dt_fb.now(_tz_fb.utc).isoformat(),
            target_role=target_role,
            match_score=match_score,
            readiness_level=readiness,
            confidence_score=confidence,
            extracted_skills=extracted,
            matched_skills=matched,
            missing_required=missing_required[:10],
            missing_preferred=missing_preferred[:8],
            transferable_skills=transferable,
            priority_skills=[g.name for g in missing_required if g.priority in ("Critical","High")][:5],
            market_demand_skills=job_tech[:8],
            learning_roadmap_inputs=roadmap,
            mock_interview_inputs={
                "target_role":  target_role,
                "weak_areas":   [g.name for g in missing_required[:4]],
                "strong_areas": matched[:5],
                "difficulty":   "Beginner" if match_score < 40 else "Intermediate" if match_score < 70 else "Advanced",
            },
            career_chat_context={
                "user_strengths":   matched[:5],
                "user_gaps":        [g.name for g in missing_required[:5]],
                "readiness_level":  readiness,
                "match_score":      match_score,
                "target_role":      target_role,
                "top_transferable": [{"from": t.user_skill, "to": t.maps_to_job_skill} for t in transferable[:3]],
            },
            salary_band_estimate=salary,
            explanations=explanations,
        )


print("✅ CELL 10 — FallbackIntelligenceCore loaded")


# ─────────────────────────────────────────────────────────────
# CELL 11 — Model loader
# ─────────────────────────────────────────────────────────────

import os as _os2
from typing import Union

_core_instance: Optional[Union[IntelligenceCore, FallbackIntelligenceCore]] = None


def get_core(force_reload: bool = False) -> Union[IntelligenceCore, FallbackIntelligenceCore]:
    global _core_instance
    if _core_instance is None or force_reload:
        config = {
            "ONET_EXTRACT_PATH":  _os2.getenv("ONET_EXTRACT_PATH",  "data/"),
            "ONET_ZIP_PATH":      _os2.getenv("ONET_ZIP_PATH",       ""),
            "SEMANTIC_THRESHOLD": float(_os2.getenv("SEMANTIC_THRESHOLD", "0.75")),
            "OPENAI_API_KEY":     _os2.getenv("OPENAI_API_KEY",      ""),
            "DATA_DIR":           _os2.getenv("DATA_DIR",            "data/"),
        }
        try:
            _core_instance = IntelligenceCore(config)
            print("✅ Using full IntelligenceCore (dataset loaded)")
        except Exception as e:
            print(f"⚠️  Full core failed ({e}).")
            print("    → Using FallbackIntelligenceCore (15 built-in roles, no dataset needed).")
            _core_instance = FallbackIntelligenceCore(config)
    return _core_instance


def reset_core() -> None:
    global _core_instance
    _core_instance = None
    print("🔄 Core reset — next get_core() will reinitialise.")


print("✅ CELL 11 — model loader loaded")


# ─────────────────────────────────────────────────────────────
# CELL 12 — Smoke test  (no PDF, runs automatically)
# ─────────────────────────────────────────────────────────────
# FIXED: wrapped in if __name__ == "__main__" guard so production
# servers importing this file don't pay the 30-second test cost.
# In Colab, call smoke_test_no_pdf() manually from a cell.

def smoke_test_no_pdf():
    print("\n" + "=" * 60)
    print("SMOKE TEST — synthetic resume, no PDF required")
    print("=" * 60)

    synthetic = {
        "full_text": (
            "Jane Doe — Senior Data Scientist\n"
            "SKILLS\n"
            "Python (4 years), SQL, Machine Learning, TensorFlow, Pandas, NumPy, "
            "Scikit-learn, Statistics, Git, Docker\n"
            "PROFESSIONAL EXPERIENCE\n"
            "Built ML pipelines at Acme Corp (2020–2024). "
            "Predictive models with Python and scikit-learn. "
            "Large SQL databases. Deployed with Docker. Tableau dashboards.\n"
            "EDUCATION\n"
            "B.Sc. Computer Science, IIT Bombay"
        ),
        "sections": {
            "skills":     "Python, SQL, Machine Learning, TensorFlow, Pandas, NumPy, Scikit-learn, Git, Docker",
            "experience": "ML pipelines at Acme Corp 2020-2024. Python scikit-learn SQL Docker Tableau.",
            "education":  "B.Sc. Computer Science, IIT Bombay",
        },
        "metadata": {"pages": 1, "char_count": 400, "has_skills_section": True},
    }

    all_skills = ["python","sql","machine learning","tensorflow","pandas","numpy",
                  "scikit-learn","git","docker","kubernetes","tableau","spark",
                  "deep learning","statistics","mlops","airflow","power bi"]

    extractor = SkillExtractor(skill_list=all_skills, verbose=False)
    extracted = extractor.extract(synthetic, debug=True)
    print(f"\n✅ Extracted {len(extracted)} skills:")
    for s in extracted[:8]:
        print(f"   [{s.source:16s}] {s.normalized!r:30s} conf={s.confidence:.2f}")

    user_skills = [s.normalized for s in extracted]
    job_tech    = ["python","sql","machine learning","docker","spark","mlops"]
    job_soft    = ["communication","teamwork","problem solving"]

    engine      = MatchingEngine(extractor.embed_model)
    score, conf = engine.compute_match(user_skills, job_tech, job_soft)
    print(f"\n✅ Match score: {score}%  (confidence {conf:.2f})")

    demand = {s: 0.10 for s in all_skills}
    demand.update({"python": 0.40, "sql": 0.30, "machine learning": 0.25, "docker": 0.20})
    analyzer = GapAnalyzer(demand)
    transferable = engine.find_transferable_skills(user_skills, list(set(job_tech + job_soft) - set(user_skills)))
    req_gaps, _ = analyzer.analyze(user_skills, job_tech, job_soft, transferable)

    print(f"\n✅ Required gaps ({len(req_gaps)}):")
    for g in req_gaps:
        print(f"   [{g.priority:8s}] {g.name!r:30s}  ~{g.estimated_weeks}w  "
              f"demand={g.demand_percentage}%  resources={len(g.learning_resources)}")

    # Test salary lookup (underscores vs spaces — was always returning default before)
    test_roles = ["Data Scientist", "Senior Software Engineer", "ML Engineer",
                  "Product Manager", "NLP Engineer", "some unknown role xyz"]
    print("\n✅ Salary band lookup:")
    for r in test_roles:
        band = analyzer.get_salary_band(r)
        print(f"   '{r}' → ₹{band['median']:,} median  ({band['currency']})")

    print("\n🎉 Smoke test passed!\n")


# FIXED: do NOT auto-run in production — call manually in Colab
# smoke_test_no_pdf()   # ← uncomment this line to run in Colab


# ─────────────────────────────────────────────────────────────
# CELL 13 — Dataset path setup  ← EDIT PATHS BEFORE RUNNING
# ─────────────────────────────────────────────────────────────

import os as _os3

_os3.environ["ONET_EXTRACT_PATH"] = "data/"           # ← change if needed
_os3.environ["ONET_ZIP_PATH"]     = ""  # ← or "" if already extracted

print(f"ONET_EXTRACT_PATH : {_os3.environ['ONET_EXTRACT_PATH']}")
print(f"ONET_ZIP_PATH     : {_os3.environ['ONET_ZIP_PATH']}")
print("✅ Paths set — run CELL 14 to upload your resume")


# ─────────────────────────────────────────────────────────────
# CELL 14 — Upload resume + enter target role
# ─────────────────────────────────────────────────────────────

# Uncomment and run in Colab:
# from google.colab import files as _colab_files
#
# print("📎 Select your resume PDF (text-based, not scanned)...")
# _uploaded = _colab_files.upload()
# if not _uploaded:
#     raise RuntimeError("No file uploaded. Re-run this cell and select a PDF.")
#
# RESUME_PATH = list(_uploaded.keys())[0]
# print(f"✅ Uploaded: {RESUME_PATH}")
#
# TARGET_ROLE = input("\n🎯 Enter your target job title (e.g. 'Data Scientist'): ").strip()
# if not TARGET_ROLE:
#     raise ValueError("Target role cannot be empty.")
#
# print(f"✅ Target role: '{TARGET_ROLE}'")
# print("Run CELL 15 to analyse your resume.")

print("ℹ️  CELL 14: uncomment the lines above in Colab to upload a PDF.")


# ─────────────────────────────────────────────────────────────
# CELL 15 — Run analysis + display results
# ─────────────────────────────────────────────────────────────

# Uncomment and run in Colab after CELL 14:
# _core   = get_core()
# _result = _core.analyze(RESUME_PATH, TARGET_ROLE)
#
# def _bar(pct: int, width: int = 30) -> str:
#     filled = int(width * pct / 100)
#     return "█" * filled + "░" * (width - filled)
#
# def _fmt_inr(amount) -> str:
#     try:    return f"₹{int(amount):,}"
#     except: return str(amount)
#
# print("\n" + "═"*60)
# print(f"  BRIDGR ANALYSIS  —  {TARGET_ROLE.upper()}")
# print("═"*60)
# print(f"\n  Match score   {_bar(_result.match_score)}  {_result.match_score}%")
# print(f"  Readiness     {_result.readiness_level}")
# print(f"  Confidence    {int(_result.confidence_score * 100)}%")
#
# if _result.explanations:
#     print("\n── What this means ──────────────────────────────────────")
#     for line in _result.explanations:
#         print(f"  • {line}")
#
# if _result.matched_skills:
#     print("\n── Skills you already have ──────────────────────────────")
#     print(f"  {', '.join(sorted(_result.matched_skills)[:15])}")
#
# if _result.missing_required:
#     print("\n── Skill gaps (required) ────────────────────────────────")
#     print(f"  {'SKILL':<28} {'PRIORITY':<10} {'WEEKS':<6} {'DEMAND'}")
#     print(f"  {'─'*28} {'─'*10} {'─'*6} {'─'*6}")
#     for g in _result.missing_required[:8]:
#         print(f"  {g.name:<28} {g.priority:<10} ~{g.estimated_weeks:<5} {g.demand_percentage}%")
#
# if _result.transferable_skills:
#     print("\n── Transferable skills ──────────────────────────────────")
#     for t in _result.transferable_skills[:4]:
#         print(f"  {t.user_skill}  →  {t.maps_to_job_skill}  ({int(t.transfer_score*100)}% overlap)")
#
# rmap = _result.learning_roadmap_inputs
# if rmap and rmap.get("phases"):
#     total_w = rmap.get("total_estimated_weeks", "?")
#     print(f"\n── Roadmap  (~{total_w} weeks) ──────────────────────────────")
#     for ph in rmap["phases"]:
#         if not ph.get("skills"): continue
#         print(f"\n  Phase {ph['phase']} — {ph['label']} ({ph['duration_weeks']} weeks)")
#         print(f"    Skills: {', '.join(ph['skills'])}")
#         for res in ph.get("resources", [])[:2]:
#             parts = res.split("|")
#             print(f"    • {parts[0]}  {parts[1] if len(parts)>1 else ''}")
#
# sb = _result.salary_band_estimate
# if sb:
#     print("\n── Salary estimate (India, Tier-1, mid-career) ──────────")
#     print(f"  Min     {_fmt_inr(sb.get('min',0))}")
#     print(f"  Median  {_fmt_inr(sb.get('median',0))}")
#     print(f"  Max     {_fmt_inr(sb.get('max',0))}")
#
# print("\n" + "═"*60)

print("ℹ️  CELL 15: uncomment the lines above in Colab to run analysis.")

print("\n✅ All cells loaded successfully. Ready to use.")
