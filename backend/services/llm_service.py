# backend/services/llm_service.py

import os
import json
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configure Gemini if available
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Model configurations
_GEMINI_MODEL = "gemini-2.0-flash"
_GROQ_MODEL = "llama-3.1-8b-instant"  # Fast, free tier model

def _extract_name(gap) -> str:
    """Safely get the skill name from a SkillGap dict, plain dict, or string."""
    if isinstance(gap, dict):
        return gap.get("name") or gap.get("skill_name") or str(gap)
    return str(gap)

def _clean_json(text: str) -> str:
    """Strip markdown code fences that AI models sometimes wrap around JSON."""
    text = text.strip()
    
    # Look for JSON content in code blocks
    if "```" in text:
        # Find all code blocks and extract the first valid JSON
        lines = text.split("\n")
        in_json_block = False
        json_lines = []
        
        for line in lines:
            if line.strip().startswith("```"):
                if not in_json_block:
                    in_json_block = True
                    continue
                else:
                    # End of code block
                    break
            elif in_json_block:
                json_lines.append(line)
        
        if json_lines:
            text = "\n".join(json_lines)
    
    # If still not starting with {, try to find the first { and last }
    if not text.strip().startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]
    
    return text.strip()

class LLMService:
    """Unified LLM service with Gemini primary and Groq fallback"""

    def __init__(self):
        self.groq_client = None
        if GROQ_API_KEY:
            self.groq_client = Groq(api_key=GROQ_API_KEY)

    def _try_gemini(self, prompt: str, method_name: str) -> Optional[Dict[str, Any]]:
        """Try Gemini first, return None if fails"""
        if not GEMINI_API_KEY:
            return None
        
        try:
            print(f"[API] Sending Gemini request for {method_name}...")
            model = genai.GenerativeModel(_GEMINI_MODEL)
            response = model.generate_content(prompt)
            result = json.loads(_clean_json(response.text))
            print(f"[OK] Gemini {method_name} succeeded")
            return result
        except Exception as e:
            print(f"    Gemini {method_name} failed: {e}")
            return None

    def _try_groq(self, prompt: str, method_name: str) -> Optional[Dict[str, Any]]:
        """Try Groq as fallback, return None if fails"""
        if not self.groq_client:
            print("    Groq client not available")
            return None
        
        try:
            print(f"[API] Sending Groq request for {method_name}...")
            response = self.groq_client.chat.completions.create(
                model=_GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048
            )
            result = json.loads(_clean_json(response.choices[0].message.content))
            print(f"[OK] Groq {method_name} succeeded")
            return result
        except Exception as e:
            print(f"    Groq {method_name} failed: {e}")
            return None

    #    job profile                                                           

    def fetch_job_profile_from_gemini(self, role: str) -> Optional[Dict[str, Any]]:
        """
        Fetch job profile for unknown roles using Gemini with Groq fallback.
        Returns: {"tech_skills": [...], "soft_skills": [...], "source": "gemini" or "groq"}
        """
        prompt = f"""You are a career expert. Extract the key skills required for a "{role}" position.

Think about what real job postings ask for. Be specific and practical.

Return ONLY valid JSON, no markdown, no explanation:
{{
    "tech_skills": ["skill1", "skill2", "skill3"],
    "soft_skills": ["skill1", "skill2"],
    "job_description": "one sentence description of what this role does"
}}

Now extract skills for: {role}"""

        # Try Gemini first
        result = self._try_gemini(prompt, f"job profile for '{role}'")
        if result:
            result["source"] = "gemini"
            return result

        # Fallback to Groq
        result = self._try_groq(prompt, f"job profile for '{role}'")
        if result:
            result["source"] = "groq"
            return result

        print(f"  All LLM providers failed for job profile: {role}")
        return None

    #    feasibility score                                                     

    def generate_feasibility_score_with_gemini(
        self,
        target_role: str,
        match_score: int,
        user_skills: List[str],
        missing_required: List[Any],
        current_role: str = "Not specified",
    ) -> Dict[str, Any]:
        """
        Generate feasibility score using Gemini with Groq fallback.
        Returns: {"score": 72, "reasoning": "...", "confidence": 0.85, ...}
        """
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

Consider:
1. How transferable their existing skills are to the target role
2. How many skills are missing and how hard each is to learn
3. Realistic self-study time to close the gap
4. Market demand and competition for the target role

Return ONLY valid JSON (no markdown, no explanation):
{{
    "score": 72,
    "reasoning": "2-3 sentence personalised explanation referencing their actual skills and gaps",
    "confidence": 0.82,
    "key_strengths": ["strength1", "strength2"],
    "key_blockers": ["blocker1", "blocker2"],
    "weeks_to_ready": 12
}}"""

        # Try Gemini first
        result = self._try_gemini(prompt, f"feasibility score for '{target_role}'")
        if result:
            return result

        # Fallback to Groq
        result = self._try_groq(prompt, f"feasibility score for '{target_role}'")
        if result:
            return result

        # Final fallback to simple calculation
        print(f"[WARN] Using match score fallback for feasibility: {target_role}")
        return {
            "score": match_score,
            "reasoning": "Using match score as fallback (all LLM providers unavailable).",
            "confidence": 0.6,
        }

    #    roadmap                                                               

    def generate_roadmap_with_gemini(
        self,
        target_role: str,
        match_score: int,
        missing_required: List[Any],
        available_hours_per_week: int = 10,
        matched_skills: List[str] = None,
        total_days: int = 90,
    ) -> Dict[str, Any]:
        """
        Generate roadmap using Gemini with Groq fallback.
        Returns: {"phases": [...], "total_weeks": 12, "total_days": 90, "summary": "..."}
        """
        top_gaps = [_extract_name(g) for g in missing_required[:6]]
        existing = ", ".join(matched_skills[:8]) if matched_skills else "Not specified"

        # Divide days into 3 roughly equal phases
        phase_days = total_days // 3
        p1_end = phase_days
        p2_end = phase_days * 2
        p3_end = total_days

        prompt = f"""You are an expert teacher creating a personalised {total_days}-day learning syllabus.

Student profile:
- Target role: {target_role}
- Current match score: {match_score}%
- Skills ALREADY HAVE (do NOT teach these): {existing}
- Skills MISSING (focus syllabus on these): {", ".join(top_gaps) if top_gaps else "General role fundamentals"}
- Available study time: {available_hours_per_week} hours/week

Create a 3-phase syllabus split as:
  Phase 1: Days 1 {p1_end}   (Foundation)
  Phase 2: Days {p1_end+1} {p2_end} (Core Skills)
  Phase 3: Days {p2_end+1} {p3_end} (Job Ready)

Rules:
- Each phase has 2 4 topics
- Each topic has a title, day range within the phase, 3 5 subtopics to learn, one mini project, and one specific FREE resource
- Resources must be real URLs: freeCodeCamp, Kaggle, fast.ai, official docs, YouTube, MDN, CS50, etc.
- Do NOT teach skills they already have
- Mini projects should be concrete and buildable

Return ONLY valid JSON (no markdown, no extra text):
{{
  "phases": [
    {{
      "phase": 1,
      "label": "Foundation",
      "day_range": "Days 1 {p1_end}",
      "goal": "one sentence goal for this phase",
      "skills": ["skill1", "skill2"],
      "milestones": ["Built X", "Completed Y"],
      "topics": [
        {{
          "title": "Topic Name",
          "days": "Days 1 {p1_end // 3}",
          "subtopics": [
            "Specific thing to learn 1",
            "Specific thing to learn 2",
            "Specific thing to learn 3"
          ],
          "mini_project": "Concrete project description",
          "resource": {{
            "name": "Exact Resource Name",
            "url": "https://real-url.com/...",
            "free": true
          }}
        }}
      ],
      "resources": [
        {{"name": "Resource Name", "url": "https://...", "free": true}}
      ]
    }},
    {{
      "phase": 2,
      "label": "Core Skills",
      "day_range": "Days {p1_end+1} {p2_end}",
      "goal": "one sentence goal",
      "skills": ["skill3", "skill4"],
      "milestones": ["Built X", "Completed Y"],
      "topics": [...],
      "resources": [...]
    }},
    {{
      "phase": 3,
      "label": "Job Ready",
      "day_range": "Days {p2_end+1} {p3_end}",
      "goal": "one sentence goal",
      "skills": ["skill5"],
      "milestones": ["Portfolio live", "Applied to 5 roles"],
      "topics": [...],
      "resources": [...]
    }}
  ],
  "total_weeks": {total_days // 7},
  "total_days": {total_days},
  "summary": "2-3 sentence personalised summary of the plan"
}}"""

        # Try Gemini first
        result = self._try_gemini(prompt, f"roadmap for '{target_role}' ({total_days} days)")
        if result:
            result["total_days"] = result.get("total_days", total_days)
            return result

        # Fallback to Groq
        result = self._try_groq(prompt, f"roadmap for '{target_role}' ({total_days} days)")
        if result:
            result["total_days"] = result.get("total_days", total_days)
            return result

        # Final fallback
        print(f"    All LLM providers failed for roadmap: {target_role}")
        return {
            "phases": [], 
            "total_weeks": total_days // 7, 
            "total_days": total_days,
            "summary": "All AI providers unavailable. Please try again later.",
        }


# Singleton instance
llm_service = LLMService()