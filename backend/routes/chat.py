# backend/routes/chat.py

import json
import anthropic
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.core.config import get_settings
from backend.core.exceptions import AIServiceError
from backend.models.analysis import ChatRequest, ChatResponse

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
    Stream a Claude response to the user's coaching question.
    Uses their analysis context to give personalized advice.
    """
    settings = get_settings()

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        context = request.context or {}
        system_prompt = _build_system_prompt(context)

        def generate():
            with client.messages.stream(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": request.message}],
            ) as stream:
                for text in stream.text_stream:
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

    except anthropic.APIError:
        raise AIServiceError()