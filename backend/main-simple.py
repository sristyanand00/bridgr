# Simple backend for Bridgr - Works without complex ML dependencies

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Bridgr API",
    description="The bridge between who you are and who you want to become",
    version="1.0.0",
)

# CORS — allow your React frontend to call this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Bridgr API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/chat")
async def chat(request: dict):
    """Simple chat endpoint using OpenAI"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        message = request.get("message", "")
        context = request.get("context", {})
        
        system_prompt = f"""You are Bridgr, an expert AI career coach. You are warm, direct, and specific.
Your tagline: "The bridge between who you are and who you want to become."

USER'S CURRENT PROFILE:
- Target role: {context.get('target_role', 'not specified')}
- Match score: {context.get('match_score', 'unknown')}%
- Readiness: {context.get('readiness_level', 'unknown')}
- Strong skills: {', '.join(context.get('user_strengths', []))}
- Top gaps to fill: {', '.join(context.get('user_gaps', []))}

COACHING STYLE:
- Be specific. Use their actual skills and gaps in your answers.
- Be encouraging but honest. Don't sugarcoat, don't catastrophize.
- Give actionable advice.
- Keep responses under 200 words.
- End with one concrete next action the user can take today."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=300,
            stream=False
        )
        
        return {"response": response.choices[0].message.content}
        
    except Exception as e:
        return {"error": f"AI service error: {str(e)}"}

@app.post("/api/analyze")
async def analyze_resume(request: dict):
    """Simple resume analysis without complex ML"""
    # Mock analysis for now - you can enhance this later
    return {
        "analysis_id": "mock-analysis-123",
        "target_role": request.get("target_role", "Software Developer"),
        "match_score": 75,
        "readiness_level": "Almost Ready",
        "extracted_skills": ["Python", "JavaScript", "React"],
        "matched_skills": ["Python", "JavaScript"],
        "missing_required": ["Docker", "AWS"],
        "priority_skills": ["Docker", "AWS"],
        "explanations": ["Good foundation in programming", "Learn cloud technologies"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
