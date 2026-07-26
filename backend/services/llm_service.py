# backend/services/llm_service.py

import json
import logging
import os
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

_GEMINI_MODEL = "gemini-2.0-flash"
_GROQ_MODEL = "llama-3.1-8b-instant"


def _extract_name(gap) -> str:
    """Safely get the skill name from a SkillGap dict, plain dict, or string."""
    if isinstance(gap, dict):
        return gap.get("name") or gap.get("skill_name") or str(gap)
    return str(gap)


def _clean_json(text: str) -> str:
    """Strip markdown code fences that AI models sometimes wrap around JSON."""
    if not text:
        return "{}"
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
    text = text.replace(",\n}", "\n}").replace(",\n]", "\n]")
    text = text.replace(",}", "}").replace(",]", "]")
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("//"):
            if line and not (
                line.startswith('"')
                or line.startswith("{")
                or line.startswith("[")
                or line.startswith("}")
            ):
                if cleaned_lines:
                    cleaned_lines[-1] = cleaned_lines[-1] + " " + line
                else:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


class LLMService:
    """Unified LLM service with Gemini primary and Groq fallback."""

    def __init__(self):
        self.groq_client = None
        if GROQ_API_KEY:
            self.groq_client = Groq(api_key=GROQ_API_KEY)

    def _try_gemini(self, prompt: str, method_name: str) -> Optional[Dict[str, Any]]:
        if not GEMINI_API_KEY:
            return None
        try:
            logger.info("Sending Gemini request for %s", method_name)
            model = genai.GenerativeModel(_GEMINI_MODEL)
            response = model.generate_content(prompt)
            result = json.loads(_clean_json(response.text))
            logger.info("Gemini %s succeeded", method_name)
            return result
        except Exception as e:
            logger.warning("Gemini %s failed: %s", method_name, e)
            return None

    def _try_groq(self, prompt: str, method_name: str) -> Optional[Dict[str, Any]]:
        if not self.groq_client:
            logger.warning("Groq client not available")
            return None
        try:
            logger.info("Sending Groq request for %s", method_name)
            response = self.groq_client.chat.completions.create(
                model=_GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048,
            )
            content = response.choices[0].message.content
            logger.debug("Groq raw response length: %d", len(content))
            try:
                result = json.loads(_clean_json(content))
                logger.info("Groq %s succeeded", method_name)
                return result
            except json.JSONDecodeError as je:
                logger.warning("Groq JSON parsing failed: %s", je)
                logger.debug("Groq raw content preview: %.200s", content)
                return None
        except Exception as e:
            logger.warning("Groq %s failed: %s", method_name, e)
            return None

    # ── job profile ────────────────────────────────────────────────────────

    def fetch_job_profile_from_gemini(self, role: str) -> Optional[Dict[str, Any]]:
        prompt = f"""You are a career expert. Extract the key skills required for a "{role}" position.

Think about what real job postings ask for. Be specific and practical.

Return ONLY valid JSON, no markdown, no explanation:
{{
    "tech_skills": ["skill1", "skill2", "skill3"],
    "soft_skills": ["skill1", "skill2"],
    "job_description": "one sentence description of what this role does"
}}

Now extract skills for: {role}"""

        result = self._try_gemini(prompt, f"job profile for '{role}'")
        if result:
            result["source"] = "gemini"
            return result
        result = self._try_groq(prompt, f"job profile for '{role}'")
        if result:
            result["source"] = "groq"
            return result
        logger.warning("All LLM providers failed for job profile: %s", role)
        return None

    # ── feasibility score ──────────────────────────────────────────────────

    def generate_feasibility_score_with_gemini(
        self,
        target_role: str,
        match_score: int,
        user_skills: List[str],
        missing_required: List[Any],
        current_role: str = "Not specified",
    ) -> Dict[str, Any]:
        missing_names = [_extract_name(g) for g in missing_required[:5]]
        skills_display = ", ".join(user_skills[:10]) if user_skills else "None listed"
        missing_display = ", ".join(missing_names) if missing_names else "None"

        prompt = f"""You are an experienced career coach assessing how feasible a career transition is.

Candidate profile:
- Current role / background: {current_role}
- Target role: {target_role}
- Resume-to-job-description match score: {match_score}%
- Skills they already have: {skills_display}
- Critical skills they are missing: {missing_display}

Assess the feasibility of this transition on a 0-100 scale:
  0   = impossible without 2+ years of full-time retraining
  50  = achievable but requires significant effort (6-12 months)
  100 = ready to apply today

Return ONLY valid JSON (no markdown, no explanation):
{{
    "score": 72,
    "reasoning": "2-3 sentence personalised explanation referencing their actual skills and gaps",
    "confidence": 0.82,
    "key_strengths": ["strength1", "strength2"],
    "key_blockers": ["blocker1", "blocker2"],
    "weeks_to_ready": 12
}}"""

        result = self._try_gemini(prompt, f"feasibility score for '{target_role}'")
        if result:
            return result
        result = self._try_groq(prompt, f"feasibility score for '{target_role}'")
        if result:
            return result
        logger.warning("Using match score fallback for feasibility: %s", target_role)
        return {
            "score": match_score,
            "reasoning": "Using match score as fallback (all LLM providers unavailable).",
            "confidence": 0.6,
        }

    # ── roadmap ────────────────────────────────────────────────────────────

    def generate_roadmap_with_gemini(
        self,
        target_role: str,
        match_score: int,
        missing_required: List[Any],
        available_hours_per_week: int = 10,
        matched_skills: List[str] = None,
        total_days: int = 90,
    ) -> Dict[str, Any]:
        top_gaps = [_extract_name(g) for g in missing_required[:6]]
        existing = ", ".join(matched_skills[:8]) if matched_skills else "Not specified"
        phase_days = total_days // 3
        p1_end = phase_days
        p2_end = phase_days * 2
        p3_end = total_days

        prompt = f"""You are an expert teacher and career mentor creating a comprehensive {total_days}-day learning roadmap for a student aspiring to become a {target_role}.

STUDENT PROFILE:
- Target Role: {target_role}
- Current Match Score: {match_score}%
- Skills Already Mastered: {existing}
- Skills to Develop: {", ".join(top_gaps) if top_gaps else "Core role competencies"}
- Study Time Available: {available_hours_per_week} hours per week
- Total Learning Period: {total_days} days ({total_days // 7} weeks)

Return ONLY valid JSON (no markdown formatting):
{{
  "phases": [
    {{
      "phase": 1,
      "label": "Foundation Building",
      "day_range": "Days 1-{p1_end}",
      "goal": "Establish strong fundamentals in core concepts",
      "skills": ["fundamental_skill_1"],
      "topics": [],
      "resources": []
    }},
    {{
      "phase": 2,
      "label": "Skill Development",
      "day_range": "Days {p1_end + 1}-{p2_end}",
      "goal": "Develop advanced technical skills through practical application",
      "skills": ["intermediate_skill_1"],
      "topics": [],
      "resources": []
    }},
    {{
      "phase": 3,
      "label": "Professional Readiness",
      "day_range": "Days {p2_end + 1}-{p3_end}",
      "goal": "Build portfolio and prepare for job market",
      "skills": ["advanced_skill_1"],
      "topics": [],
      "resources": []
    }}
  ],
  "total_weeks": {total_days // 7},
  "total_days": {total_days},
  "summary": "Comprehensive {total_days}-day learning journey."
}}"""

        result = self._try_gemini(prompt, f"roadmap for '{target_role}' ({total_days} days)")
        if result:
            result["total_days"] = result.get("total_days", total_days)
            return result
        result = self._try_groq(prompt, f"roadmap for '{target_role}' ({total_days} days)")
        if result:
            result["total_days"] = result.get("total_days", total_days)
            return result
        logger.warning("All LLM providers failed for roadmap: %s", target_role)
        return {
            "phases": [],
            "total_weeks": total_days // 7,
            "total_days": total_days,
            "summary": "All AI providers unavailable. Please try again later.",
        }


# Singleton instance
llm_service = LLMService()
