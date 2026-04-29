# backend/routes/interview.py

import os
import sys
import json
import re
import openai
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import get_settings
from core.exceptions import AIServiceError

router = APIRouter()


class InterviewStartRequest(BaseModel):
    target_role: str
    weak_areas: List[str]
    strong_areas: List[str]
    difficulty: str = "Intermediate"


class InterviewAnswerRequest(BaseModel):
    question: str
    answer: str
    target_role: str
    skill_being_tested: str


@router.post("/interview/start")
async def start_interview(request: InterviewStartRequest):
    """Generate a set of interview questions tailored to the user's gaps."""
    settings = get_settings()

    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""Generate 5 interview questions for a {request.target_role} role.

Focus these questions on testing: {', '.join(request.weak_areas[:3])}
Difficulty level: {request.difficulty}

Return JSON:
{{
  "questions": [
    {{
      "id": 1,
      "question": "the question text",
      "type": "technical|behavioral|case",
      "skill": "what skill this tests",
      "hint": "what a good answer should cover"
    }}
  ]
}}

Return ONLY valid JSON."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = re.sub(r"```json|```", "", response.choices[0].message.content).strip()
        return json.loads(raw)

    except openai.APIError:
        raise AIServiceError()


@router.post("/interview/evaluate")
async def evaluate_answer(request: InterviewAnswerRequest):
    """Evaluate a user's interview answer and give feedback."""
    settings = get_settings()

    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""Evaluate this interview answer for a {request.target_role} role.

Question: {request.question}
Skill being tested: {request.skill_being_tested}
Candidate's answer: {request.answer}

Return JSON:
{{
  "score": 7,
  "max_score": 10,
  "verdict": "Good|Excellent|Needs Work|Poor",
  "what_worked": ["specific thing 1", "specific thing 2"],
  "what_to_improve": ["specific improvement 1"],
  "model_answer_hint": "what an ideal answer would include",
  "follow_up_question": "a natural follow-up question"
}}

Return ONLY valid JSON."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = re.sub(r"```json|```", "", response.choices[0].message.content).strip()
        return json.loads(raw)

    except openai.APIError:
        raise AIServiceError()
