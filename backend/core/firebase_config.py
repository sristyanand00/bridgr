import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional
from backend.core.config import get_settings

settings = get_settings()

# Initialize Firebase Admin SDK
firebase_credentials = {
    "type": "service_account",
    "project_id": "bridgr-72de1",
    "private_key_id": "your-private-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR-PRIVATE-KEY\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-xxxxx@bridgr-72de1.iam.gserviceaccount.com",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
}

# For development, we'll use a simpler approach
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Firebase initialization error: {e}")
    # For development, continue without Firebase
    pass

async def verify_firebase_token(id_token: str) -> Optional[dict]:
    """Verify Firebase ID token and return user data"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return {
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture")
        }
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None
