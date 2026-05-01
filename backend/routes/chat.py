# backend/routes/chat.py

import os
import sys
import json
import google.generativeai as genai
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import get_settings
from core.exceptions import AIServiceError
from models.analysis import ChatRequest, ChatResponse

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

router = APIRouter()


def _build_system_prompt(context: dict) -> str:
    """Build a rich system prompt from the user's analysis context."""
    return f"""You are Bridgr, an expert AI career coach. You are warm, direct, and specific.
Your tagline: "The bridge between who you are and who you want to become."

USER'S CURRENT PROFILE:
- Target role: {context.get('target_role', 'not specified')}
- Match score: {context.get('match_score', 'unknown')}%
- Readiness: {context.get('readiness_level', 'unknown')}
- Strong skills: {', '.join(context.get('user_strengths', []))}
- Top gaps to fill: {', '.join(context.get('user_gaps', []))}
- Transferable skills: {json.dumps(context.get('top_transferable', []))}

COACHING STYLE:
- Be specific. Use their actual skills and gaps in your answers.
- Be encouraging but honest. Don't sugarcoat, don't catastrophize.
- Give actionable advice. "Learn SQL" is bad. "Start with Mode Analytics SQL tutorial, takes 3 weeks" is good.
- When suggesting resources, prefer free ones unless the paid ones are significantly better.
- Keep responses under 200 words unless a detailed breakdown is genuinely needed.
- End with one concrete next action the user can take today.
"""


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Stream a Gemini response to the user's coaching question.
    Uses their analysis context to give personalized advice.
    """
    if not GEMINI_API_KEY:
        raise AIServiceError("Gemini API key not configured")

    try:
        model = genai.GenerativeModel("gemini-flash-latest")

        context = request.context or {}
        system_prompt = _build_system_prompt(context)
        full_prompt = f"{system_prompt}\n\nUser: {request.message}\n\nCoach:"

        def generate():
            response = model.generate_content(full_prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    text = chunk.text
                    # Server-Sent Events format — frontend reads this
                    yield f"data: {json.dumps({'text': text})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        print(f"❌ Gemini chat failed: {e}")
        raise AIServiceError("Chat service unavailable")