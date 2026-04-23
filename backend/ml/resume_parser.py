# backend/ml/resume_parser.py

import re
from typing import Dict
from collections import defaultdict
import pdfplumber


class ResumeParser:
    """
    Parses a PDF resume into structured sections.

    Output format:
    {
      "full_text": "all the text as one string",
      "sections": {
        "experience": "text from the work experience section",
        "skills": "text from the skills section",
        "education": "...",
        "projects": "...",
        "summary": "...",
      },
      "metadata": {
        "pages": 2,
        "char_count": 3842,
        "has_skills_section": True
      }
    }
    """

    # Regex patterns for detecting section headers
    # Each pattern matches the most common ways that section is titled
    SECTION_PATTERNS = {
        "experience":     r"(work\s+experience|professional\s+experience|employment|work\s+history|experience)",
        "education":      r"(education|academic|qualification|degree)",
        "skills":         r"(skills|technical\s+skills|technologies|tools|competencies)",
        "projects":       r"(projects|personal\s+projects|academic\s+projects|portfolio)",
        "summary":        r"(summary|objective|profile|about\s+me|overview)",
        "certifications": r"(certifications?|certificates?|licenses?|credentials?)",
    }

    def parse(self, pdf_path: str) -> Dict:
        """Main entry point. Returns structured dict of resume content."""
        raw_text = self._extract_text(pdf_path)
        sections = self._detect_sections(raw_text)

        return {
            "full_text": raw_text,
            "sections": sections,
            "metadata": {
                "pages": self._count_pages(pdf_path),
                "char_count": len(raw_text),
                "has_skills_section": "skills" in sections,
            }
        }

    def _extract_text(self, path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"Could not read PDF: {e}")

        if not text.strip():
            raise ValueError(
                "This PDF appears to be image-based (scanned). "
                "Bridgr needs a text-based PDF. "
                "Try exporting your resume from Google Docs or Word instead."
            )
        return text

    def _detect_sections(self, text: str) -> Dict[str, str]:
        """Walk through the resume line by line, detect section headers."""
        lines = text.split("\n")
        sections = defaultdict(list)
        current_section = "header"  # everything before the first header

        for line in lines:
            line_lower = line.lower().strip()
            matched_section = None

            for section_name, pattern in self.SECTION_PATTERNS.items():
                # Short lines that match a pattern are likely headers, not content
                if re.match(pattern, line_lower) and len(line_lower) < 50:
                    matched_section = section_name
                    break

            if matched_section:
                current_section = matched_section
            else:
                sections[current_section].append(line)

        return {k: "\n".join(v) for k, v in sections.items()}

    def _count_pages(self, path: str) -> int:
        try:
            with pdfplumber.open(path) as pdf:
                return len(pdf.pages)
        except:
            return 0