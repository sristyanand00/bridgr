# backend/core/exceptions.py

from fastapi import Request
from fastapi.responses import JSONResponse


class BridgrException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ResumeParseFailed(BridgrException):
    def __init__(self, detail: str):
        super().__init__(
            message=f"Could not read your resume: {detail}",
            status_code=422,
        )


class JobRoleNotFound(BridgrException):
    def __init__(self, role: str):
        super().__init__(
            message=f"'{role}' not found in our database. Try 'Data Scientists' or 'Software Developers'.",
            status_code=404,
        )


class AIServiceError(BridgrException):
    def __init__(self, message: str = None):
        final_message = message or "AI service temporarily unavailable. Please try again in a moment."
        super().__init__(
            message=final_message,
            status_code=503,
        )


class RoadmapError(BridgrException):
    def __init__(self):
        super().__init__(
            message="Unable to generate roadmap. Please try again.",
            status_code=503,
        )


async def bridgr_exception_handler(request: Request, exc: BridgrException):
    from datetime import datetime
    
    # For analyze endpoint failures, return a proper AnalysisResult structure
    if "/api/analyze" in str(request.url):
        error_result = {
            "analysis_id": f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "target_role": "unknown",
            "match_score": 0,
            "readiness_level": "Analysis Failed",
            "confidence_score": 0.0,
            "extracted_skills": [],
            "matched_skills": [],
            "missing_required": [],
            "missing_preferred": [],
            "transferable_skills": [],
            "priority_skills": [],
            "market_demand_skills": [],
            "learning_roadmap_inputs": {},
            "mock_interview_inputs": {},
            "career_chat_context": {},
            "salary_band_estimate": {},
            "feasibility": None,
            "explanations": [exc.message],
            "error": exc.message
        }
        return JSONResponse(
            status_code=exc.status_code,
            content=error_result,
        )
    
    # For other endpoints, return simple error
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "type": type(exc).__name__},
    )