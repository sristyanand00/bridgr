import logging
import os

import firebase_admin
from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials

logger = logging.getLogger(__name__)

# ── Firebase Admin SDK init ────────────────────────────────────────────────────
_firebase_ready = False

try:
    firebase_admin.get_app()
    _firebase_ready = True
except ValueError:
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

    if cred_path and os.path.exists(cred_path):
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            _firebase_ready = True
            logger.info("Firebase Admin SDK initialized from credentials file.")
        except Exception as e:
            logger.warning("Firebase init failed from file: %s", e)
    else:
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
        client_email = os.getenv("FIREBASE_CLIENT_EMAIL")

        if project_id and private_key and client_email:
            try:
                cred = credentials.Certificate(
                    {
                        "type": "service_account",
                        "project_id": project_id,
                        "private_key": private_key,
                        "client_email": client_email,
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                )
                firebase_admin.initialize_app(cred)
                _firebase_ready = True
                logger.info("Firebase Admin SDK initialized from env vars.")
            except Exception as e:
                logger.warning("Firebase init failed from env vars: %s", e)
        else:
            logger.warning(
                "Firebase credentials not configured. "
                "Set FIREBASE_CREDENTIALS_PATH or "
                "FIREBASE_PROJECT_ID + FIREBASE_PRIVATE_KEY + FIREBASE_CLIENT_EMAIL. "
                "Authentication endpoints will return 503."
            )

security = HTTPBearer()


async def get_current_user(
    res: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    if not _firebase_ready:
        raise HTTPException(
            status_code=503,
            detail=(
                "Authentication service is not configured. "
                "Please set Firebase credentials in the backend .env file."
            ),
        )
    token = res.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_user_optional(request: Request):
    """Returns decoded token or None — never raises."""
    if not _firebase_ready:
        return None
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        return auth.verify_id_token(token)
    except Exception:
        return None
