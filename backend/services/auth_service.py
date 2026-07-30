import logging
import os

from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# firebase-admin pulls in google-cloud-firestore and grpcio — well over 100MB
# of dependencies that a deployment with no auth configured never executes.
# Treat it as an optional extra: absent, the auth endpoints return 503 exactly
# as they already do when credentials are missing, and the anonymous
# /api/readiness path (the whole demo flow) is unaffected.
try:
    import firebase_admin
    from firebase_admin import auth, credentials
    _firebase_installed = True
except ImportError:
    firebase_admin = None
    auth = None
    credentials = None
    _firebase_installed = False

logger = logging.getLogger(__name__)


# ── Firebase Admin SDK init ────────────────────────────────────────────────────
def _init_firebase() -> bool:
    """Initialise the Admin SDK from whichever credential source is present.

    Returns True if auth is usable.  Never raises — a deployment without
    credentials is a supported configuration (the demo flow is anonymous).
    """
    if not _firebase_installed:
        logger.warning(
            "firebase-admin is not installed — authentication is disabled. "
            "Install it to enable the /api/user endpoints."
        )
        return False

    try:
        firebase_admin.get_app()
        return True
    except ValueError:
        pass  # No app yet — fall through and create one.

    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if cred_path and os.path.exists(cred_path):
        try:
            firebase_admin.initialize_app(credentials.Certificate(cred_path))
            logger.info("Firebase Admin SDK initialized from credentials file.")
            return True
        except Exception as e:
            logger.warning("Firebase init failed from file: %s", e)
            return False

    project_id = os.getenv("FIREBASE_PROJECT_ID")
    private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
    client_email = os.getenv("FIREBASE_CLIENT_EMAIL")

    if project_id and private_key and client_email:
        try:
            firebase_admin.initialize_app(credentials.Certificate({
                "type": "service_account",
                "project_id": project_id,
                "private_key": private_key,
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }))
            logger.info("Firebase Admin SDK initialized from env vars.")
            return True
        except Exception as e:
            logger.warning("Firebase init failed from env vars: %s", e)
            return False

    logger.warning(
        "Firebase credentials not configured. "
        "Set FIREBASE_CREDENTIALS_PATH or "
        "FIREBASE_PROJECT_ID + FIREBASE_PRIVATE_KEY + FIREBASE_CLIENT_EMAIL. "
        "Authentication endpoints will return 503."
    )
    return False


_firebase_ready = _init_firebase()

security = HTTPBearer()

# ── Startup-time status log (WARNING level — always visible in Render logs) ───
# This single log line makes it immediately obvious whether Firebase is wired
# up correctly after a deploy, without having to trigger an auth request.
if _firebase_ready:
    logger.warning("Firebase Admin SDK: CONFIGURED ✔ — authentication is active.")
else:
    logger.warning(
        "Firebase Admin SDK: NOT CONFIGURED — authentication is disabled. "
        "All /api/readiness scans will be anonymous (no DB persistence). "
        "Set FIREBASE_CREDENTIALS_PATH or FIREBASE_PROJECT_ID + "
        "FIREBASE_PRIVATE_KEY + FIREBASE_CLIENT_EMAIL to enable auth."
    )


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
