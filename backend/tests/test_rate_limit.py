"""
Rate-limit tests.

Strategy:
- Only /api/user/sync is hit in the tight loop — it's cheap (auth is overridden)
  and is rate-limited at 30/minute, which is low enough to cross with ≤35 calls.
- The ML pipeline is never invoked here; /api/readiness is NOT called in a loop.
- Dependencies are overridden via FastAPI's app.dependency_overrides mechanism
  (not via patch()) because FastAPI resolves dependencies before calling the
  route function, so patching the route module's reference doesn't intercept it.
- A pytest fixture clears the limiter's in-memory storage before each test so
  counts from previous tests don't bleed across.
"""

import sys
from unittest.mock import MagicMock

import pytest

# ── Stub heavy packages (same approach as test_api.py) ────────────────────────
if "pydantic_settings" not in sys.modules:
    _ps = MagicMock()
    _ps.BaseSettings = object
    sys.modules["pydantic_settings"] = _ps

if "sqlalchemy" not in sys.modules:
    _sa = MagicMock()
    _sa.orm    = MagicMock()
    _sa.ext    = MagicMock()
    _sa.ext.declarative = MagicMock()
    _sa.sql    = MagicMock()
    _sa.engine = MagicMock()
    _sa.pool   = MagicMock()
    sys.modules["sqlalchemy"]                 = _sa
    sys.modules["sqlalchemy.orm"]             = _sa.orm
    sys.modules["sqlalchemy.ext"]             = _sa.ext
    sys.modules["sqlalchemy.ext.declarative"] = _sa.ext.declarative
    sys.modules["sqlalchemy.sql"]             = _sa.sql
    sys.modules["sqlalchemy.engine"]          = _sa.engine
    sys.modules["sqlalchemy.pool"]            = _sa.pool

for _pkg in ["google", "google.generativeai", "groq", "firebase_admin",
             "firebase_admin.credentials", "firebase_admin.auth"]:
    if _pkg not in sys.modules:
        sys.modules[_pkg] = MagicMock()

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402
from core.limiter import limiter  # noqa: E402
from services.auth_service import get_current_user  # noqa: E402
from db.database import get_db  # noqa: E402


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_limiter():
    """Clear in-memory rate-limit counters before and after every test."""
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture()
def client_with_auth():
    """TestClient with auth + DB overridden via FastAPI's dependency_overrides.

    This is the correct mechanism — patching the route module's local name
    does NOT intercept FastAPI's dependency resolution, so side_effect-based
    patches silently fail to apply.
    """
    _user = {"uid": "test-uid-456", "email": "test@example.com"}
    _db = MagicMock()
    _db.query.return_value.filter.return_value.first.return_value = MagicMock(
        id="test-uid-456",
        email="test@example.com",
        name="Test User",
        quiz_data=None,
        created_at=None,
    )

    async def _fake_auth():
        return _user

    def _fake_db():
        yield _db

    app.dependency_overrides[get_current_user] = _fake_auth
    app.dependency_overrides[get_db] = _fake_db

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client

    # Clean up overrides so other test modules aren't affected.
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_db, None)


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_sync_endpoint_allows_requests_under_limit(client_with_auth):
    """First request under the 30/minute limit must succeed (200)."""
    resp = client_with_auth.post("/api/user/sync")
    assert resp.status_code != 429, (
        f"First request should not be rate-limited; got {resp.status_code}"
    )


def test_sync_endpoint_returns_429_after_limit_exceeded(client_with_auth):
    """Hitting /api/user/sync more than 30 times in a minute must yield 429.

    We send up to 35 requests — enough to cross the 30/minute threshold.
    The 429 response body must contain an 'error' key.
    """
    hit_429 = False
    last_429_body = None

    for _ in range(35):
        resp = client_with_auth.post("/api/user/sync")
        if resp.status_code == 429:
            hit_429 = True
            last_429_body = resp.json()
            break

    assert hit_429, (
        "Expected a 429 after 30 calls to /api/user/sync but never got one. "
        "Check that SlowAPIMiddleware is registered and limiter.reset() works."
    )

    assert last_429_body is not None
    assert "error" in last_429_body, (
        f"429 body missing 'error' key: {last_429_body}"
    )


def test_429_response_body_shape(client_with_auth):
    """The 429 body must have an 'error' key with a non-empty string value."""
    body = None
    for _ in range(35):
        resp = client_with_auth.post("/api/user/sync")
        if resp.status_code == 429:
            body = resp.json()
            break

    assert body is not None, "Never reached rate limit in 35 requests"
    assert isinstance(body.get("error"), str) and body["error"], (
        f"'error' must be a non-empty string; got: {body}"
    )
