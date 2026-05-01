# backend/services/llm_service.py

import os
import json
from typing import Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class LLMService:
    """Unified LLM service using Gemini Flash (free tier)"""
    
    @staticmethod
    def fetch_job_profile_from_gemini(role: str) -> Optional[Dict[str, Any]]:
        """
        Fetch job profile for unknown roles using Gemini Flash.
        Returns: {"tech_skills": [...], "soft_skills": [...], "source": "gemini"}
        """
        if not GEMINI_API_KEY:
            print("⚠️  GEMINI_API_KEY not set — skipping live job profile fetch")
            return None
        
        try:
            model = genai.GenerativeModel("gemini-flash-latest")
            
            prompt = f"""You are a career expert. Extract the key skills required for a "{role}" position.

Think about what real job postings ask for. Be specific and practical.

Return ONLY valid JSON, no markdown, no explanation:
{{
    "tech_skills": ["skill1", "skill2", "skill3", ...],
    "soft_skills": ["skill1", "skill2", ...],
    "job_description": "one sentence description of what this role does"
}}

Example for Data Scientist:
{{
    "tech_skills": ["Python", "SQL", "Machine Learning", "Statistics", "Pandas", "scikit-learn", "TensorFlow"],
    "soft_skills": ["Communication", "Problem Solving", "Data Storytelling"],
    "job_description": "Analyzes data to drive business decisions using statistical and ML methods"
}}

Now extract skills for: {role}"""
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up markdown if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            profile = json.loads(response_text)
            profile["source"] = "gemini"
            print(f"✅ Fetched job profile for '{role}' from Gemini Flash")
            return profile
        
        except json.JSONDecodeError as e:
            print(f"⚠️  Gemini returned invalid JSON: {e}")
            return None
        except Exception as e:
            print(f"❌ Gemini job profile fetch failed: {e}")
            return None
    
    @staticmethod
    def generate_feasibility_score_with_gemini(
        target_role: str,
        match_score: int,
        user_skills: list,
        missing_required: list,
        current_role: str = "Not specified"
    ) -> Dict[str, Any]:
        """
        Use Gemini Flash to generate a feasibility score (0-100) with explanation.
        Returns: {"score": 72, "reasoning": "...", "confidence": 0.85}
        """
        if not GEMINI_API_KEY:
            # Fallback to simple calculation
            return {
                "score": match_score,
                "reasoning": "Using match score as fallback (no Gemini API key)",
                "confidence": 0.6
            }
        
        try:
            model = genai.GenerativeModel("gemini-flash-latest")
            
            prompt = f"""You are a career coach assessing career transition feasibility.

User Profile:
- Current role: {current_role}
- Target role: {target_role}
- Resume match score: {match_score}%
- Skills they have: {', '.join(user_skills[:10]) if user_skills else 'None listed'}
- Critical skills they're missing: {', '.join([g.get('name', g) if isinstance(g, dict) else g for g in missing_required[:5]]) if missing_required else 'None'}

Based on this, assess how feasible this career transition is on a scale of 0-100.
0 = impossible/would take 2+ years of full-time study
100 = ready to apply today

Consider:
1. How transferable their current skills are
2. How many skills they're missing
3. The difficulty of learning those skills
4. Time it would realistically take

Return ONLY valid JSON:
{{
    "score": 72,
    "reasoning": "They have strong Python foundation which transfers well. Main gap is Docker/MLOps which takes 4-6 weeks.",
    "confidence": 0.82,
    "key_strengths": ["Python", "Statistics"],
    "key_blockers": ["Docker", "System Design"],
    "weeks_to_ready": 12
}}"""
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean markdown
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            result = json.loads(response_text)
            print(f"✅ Gemini feasibility score for {target_role}: {result['score']}")
            return result
        
        except json.JSONDecodeError as e:
            print(f"⚠️  Gemini feasibility JSON parse failed: {e}")
            return {
                "score": match_score,
                "reasoning": "Gemini JSON parse failed — using match score",
                "confidence": 0.5
            }
        except Exception as e:
            print(f"❌ Gemini feasibility generation failed: {e}")
            return {
                "score": match_score,
                "reasoning": f"Gemini error: {str(e)}",
                "confidence": 0.4
            }
    
    @staticmethod
    def generate_roadmap_with_gemini(
        target_role: str,
        match_score: int,
        missing_required: list,
        available_hours_per_week: int = 10
    ) -> Dict[str, Any]:
        """
        Generate a 30/60/90 day roadmap using Gemini Flash (free).
        Returns: {"phases": [...], "total_weeks": 12, "summary": "..."}
        """
        if not GEMINI_API_KEY:
            return {
                "phases": [],
                "total_weeks": 12,
                "summary": "No Gemini API key — fallback roadmap unavailable"
            }
        
        try:
            model = genai.GenerativeModel("gemini-flash-latest")
            
            top_gaps = [g.get('name', g) if isinstance(g, dict) else g for g in missing_required[:5]]
            
            prompt = f"""Create a concrete 30-60-90 day learning roadmap for someone transitioning to {target_role}.

Context:
- Current match score: {match_score}%
- Available time: {available_hours_per_week} hours/week
- Top skill gaps to close: {', '.join(top_gaps) if top_gaps else 'None'}

Create 3 phases (30 days each). For each phase, include:
- Weekly breakdown (what to learn each week)
- Specific FREE resources (courses, tutorials, platforms)
- Practical projects/milestones to build
- Skills to focus on

Prefer FREE resources: freeCodeCamp, Kaggle, Mode Analytics, official docs, YouTube.

Return ONLY valid JSON:
{{
    "phases": [
        {{
            "phase": 1,
            "label": "Foundation",
            "duration_weeks": 4,
            "goal": "Master SQL window functions",
            "weeks": [
                {{
                    "week": 1,
                    "focus": "SQL basics + WHERE/JOIN",
                    "resource": "Mode Analytics SQL Tutorial (free)",
                    "project": "Write 5 complex queries on Mode Analytics"
                }},
                {{
                    "week": 2,
                    "focus": "Window functions (ROW_NUMBER, RANK, LAG)",
                    "resource": "Mode Analytics window functions tutorial",
                    "project": "Build ranking query for top 10 customers per city"
                }},
                {{
                    "week": 3,
                    "focus": "CTEs and advanced queries",
                    "resource": "Leetcode SQL (free tier)",
                    "project": "Solve 10 LeetCode SQL problems"
                }},
                {{
                    "week": 4,
                    "focus": "Practice + mock interview",
                    "resource": "HackerRank SQL challenges",
                    "project": "Timed SQL competition (30 min, 3 problems)"
                }}
            ]
        }},
        {{
            "phase": 2,
            "label": "Core Skills",
            "duration_weeks": 4,
            "goal": "Build end-to-end ML projects",
            "weeks": [...]
        }},
        {{
            "phase": 3,
            "label": "Interview Ready",
            "duration_weeks": 4,
            "goal": "Polish and apply",
            "weeks": [...]
        }}
    ],
    "total_weeks": 12,
    "summary": "A 12-week plan focusing on SQL mastery (4 weeks), feature engineering + modeling (4 weeks), then interview prep and real projects (4 weeks)."
}}"""
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean markdown
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            result = json.loads(response_text)
            print(f"✅ Generated Gemini roadmap for {target_role}")
            return result
        
        except json.JSONDecodeError as e:
            print(f"⚠️  Gemini roadmap JSON parse failed: {e}")
            return {
                "phases": [],
                "total_weeks": 12,
                "summary": "Failed to parse Gemini response"
            }
        except Exception as e:
            print(f"❌ Gemini roadmap generation failed: {e}")
            return {
                "phases": [],
                "total_weeks": 12,
                "summary": f"Gemini error: {str(e)}"
            }


# Singleton instance
llm_service = LLMService()