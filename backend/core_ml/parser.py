"""Resume PDF parsing and section detection."""

from __future__ import annotations
import logging
import re
from collections import defaultdict
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class ResumeParser:
    # Permissive patterns that handle mixed case, ALL CAPS, trailing colons, word boundaries
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
            logger.info(f"pymupdf failed ({e}), trying pdfplumber")

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
            if 1 < len(line_clean) < 80 and not line_clean.startswith((" ", "-", "*")):
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
