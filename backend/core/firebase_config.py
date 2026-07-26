import logging
from typing import Optional

import firebase_admin
from firebase_admin import auth, credentials

logger = logging.getLogger(__name__)

# Placeholder credential dict — real credentials come from the service account
# file or env vars wired through auth_service.py.  This file exists for
# legacy compatibility and is not the primary init path.
_firebase_credentials = {
    "type": "service_account",
    "project_id": "bridgr-72de1",
    "private_key_id": "your-private-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR-PRIVATE-KEY\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-xxxxx@bridgr-72de1.iam.gserviceaccount.com",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
}

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(_firebase_credentials)
        firebase_admin.initialize_app(cred)
except Exception as e:
    logger.warning("Firebase initialization error: %s", e)


async def verify_firebase_token(id_token: str) -> Optional[dict]:
    """Verify Firebase ID token and return user data."""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return {
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture"),
        }
    except Exception as e:
        logger.warning("Token verification failed: %s", e)
        return None
