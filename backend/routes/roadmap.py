# backend/routes/roadmap.py

import os
import sys
import json
import re
import google.generativeai as genai
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.exceptions import AIServiceError, RoadmapError
from models.analysis import RoadmapResponse

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

router = APIRouter()


class RoadmapRequest(BaseModel):
    target_role: str
    match_score: int
    readiness_level: str
    roadmap_inputs: Dict       # the learning_roadmap_inputs from AnalysisResult
    matched_skills: list = []
    missing_required: list = []


@router.post("/roadmap", response_model=RoadmapResponse)
async def generate_roadmap(request: RoadmapRequest):
    """
    Generate a detailed 30/60/90-day learning roadmap
    using the structured gap analysis as context.
    """
    if not GEMINI_API_KEY:
        raise AIServiceError("Gemini API key not configured")

    try:
        model = genai.GenerativeModel("gemini-flash-latest")

        ri = request.roadmap_inputs
        prompt = f"""Generate a concrete 30-60-90 day learning roadmap for someone targeting {request.target_role}.

Current profile:
- Match score: {request.match_score}% ({request.readiness_level})
- Strong skills: {', '.join(request.matched_skills[:5])}
- Critical gaps: {', '.join([str(g) for g in request.missing_required[:4]])}

Phase breakdown already computed:
- Phase 1 (weeks 1-4): {ri.get('phase_1', {}).get('skills', [])}
- Phase 2 (weeks 4-10): {ri.get('phase_2', {}).get('skills', [])}
- Phase 3 (weeks 10+): {ri.get('phase_3', {}).get('skills', [])}
- Total estimated: {ri.get('total_estimated_weeks', '?')} weeks

Return a JSON object with this exact structure:
{{
  "phases": [
    {{
      "id": "phase_1",
      "label": "Foundation",
      "duration": "Weeks 1–4",
      "goal": "one sentence goal",
      "weeks": [
        {{"week": 1, "focus": "what to do", "resource": "specific course/book/project", "milestone": "what you'll have built"}}
      ]
    }}
  ],
  "total_weeks": 12,
  "summary": "one paragraph summary of full journey"
}}

Be specific. Name actual free resources (Kaggle, freeCodeCamp, fast.ai, official docs). 
Name actual projects to build. Return ONLY valid JSON."""

        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(raw)

        return RoadmapResponse(
            phases=data.get("phases", []),
            total_weeks=data.get("total_weeks", 12),
            summary=data.get("summary", "")
        )

    except Exception as e:
        print(f"❌ Gemini roadmap generation failed: {e}")
        raise AIServiceError(f"Roadmap generation failed: {str(e)}")
