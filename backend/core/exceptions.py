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
    def __init__(self):
        super().__init__(
            message="AI service temporarily unavailable. Please try again in a moment.",
            status_code=503,
        )


class RoadmapError(BridgrException):
    def __init__(self):
        super().__init__(
            message="Unable to generate roadmap. Please try again.",
            status_code=503,
        )


async def bridgr_exception_handler(request: Request, exc: BridgrException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "type": type(exc).__name__},
    )