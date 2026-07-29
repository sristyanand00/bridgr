"""
Tests that POST /api/readiness persists an Analysis row when the request
is made by an authenticated user, and that GET /api/user/history returns it.

Pattern follows test_api.py:
- Heavy optional packages that have no real install are stubbed before any
  app import.
- SQLAlchemy IS installed, so we must NOT stub it — we need the real ORM.
- `get_user_optional` and `get_current_user` are overridden via
  app.dependency_overrides so no real Firebase token is needed.
- An in-memory SQLite database is injected via `get_db` override so the
  test suite stays hermetic.
"""

import io
import sys
from unittest.mock import MagicMock, patch

import pytest

# ── Import real SQLAlchemy FIRST so test_api.py's stub guard never fires ──
# test_api.py does `if "sqlalchemy" not in sys.modules:` — by importing the
# real package here we put it in sys.modules and the guard is a no-op when
# both test files share the same pytest process.
import sqlalchemy                                             # noqa: F401  (real pkg)
import sqlalchemy.orm                                         # noqa: F401
import sqlalchemy.ext.declarative                             # noqa: F401
from sqlalchemy import create_engine                          # noqa: E402
from sqlalchemy.orm import sessionmaker                       # noqa: E402

# ── Stub ONLY packages that are genuinely not installed ───────────────────
# Do NOT stub sqlalchemy — it is installed and the persistence tests need it.

if "pydantic_settings" not in sys.modules:
    _ps = MagicMock()
    _ps.BaseSettings = object
    sys.modules["pydantic_settings"] = _ps

def _stub(name: str) -> MagicMock:
    if name not in sys.modules:
        sys.modules[name] = MagicMock()
    return sys.modules[name]  # type: ignore[return-value]

_stub("google")
_stub("google.generativeai")
_stub("groq")
_stub("firebase_admin")
_stub("firebase_admin.credentials")
_stub("firebase_admin.auth")

# ── Now we can import the real app ────────────────────────────────────────
from fastapi.testclient import TestClient                     # noqa: E402
from main import app                                          # noqa: E402
from db.database import get_db, Base                         # noqa: E402
from db.models import Analysis, User                          # noqa: E402
from services.auth_service import get_user_optional, get_current_user  # noqa: E402

# ── In-memory test database ───────────────────────────────────────────────
# Use StaticPool so every connection shares the same in-memory database;
# without this, sqlite:///:memory: would give each connection an empty DB
# and create_all tables would be invisible to the route's session.
from sqlalchemy.pool import StaticPool                        # noqa: E402

_TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # share one connection across all sessions
)
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_TEST_ENGINE)


@pytest.fixture(autouse=True)
def _fresh_db():
    """Create all tables fresh for every test, then drop them."""
    Base.metadata.create_all(bind=_TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=_TEST_ENGINE)


def _get_test_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


# Fake authenticated user injected into every dependency call
_FAKE_USER = {"uid": "test-uid-abc123", "email": "test@example.com"}

VALID_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog >>\nendobj\n"
    b"xref\n0 1\n0000000000 65535 f \ntrailer\n<< /Size 1 >>\n%%EOF"
)
TARGET_ROLE = "Data Engineer"
JD = "We need Python, SQL, and Docker experience."


def _make_core_mock():
    core = MagicMock()
    core.resume_parser.parse.return_value = {
        "full_text": "Python developer with SQL experience. Jan 2022 - Present",
        "sections": {
            "skills":     "Python, SQL",
            "experience": "Built pipelines using Python and SQL. Jan 2022 - Present",
        },
    }
    core.skill_extractor.skill_list = ["python", "sql", "docker"]

    def _make_skill(name, ctx):
        s = MagicMock()
        s.normalized = name
        s.context    = ctx
        s.source     = "phrase_match"
        return s

    core.skill_extractor.extract.return_value = [
        _make_skill("python", "Built pipelines using Python. Jan 2022 - Present"),
        _make_skill("sql",    "SQL database work. Jan 2022 - Present"),
    ]
    return core


def _make_client():
    """TestClient with auth + db overrides applied, tables pre-created."""
    # Ensure tables exist on the test engine before any request
    Base.metadata.create_all(bind=_TEST_ENGINE)
    app.dependency_overrides[get_db]            = _get_test_db
    app.dependency_overrides[get_user_optional]  = lambda: _FAKE_USER
    app.dependency_overrides[get_current_user]   = lambda: _FAKE_USER
    return TestClient(app)


# ── The User FK must exist before the Analysis insert ─────────────────────
def _seed_user(db):
    user = User(id=_FAKE_USER["uid"], email=_FAKE_USER["email"], name="Test User")
    db.add(user)
    db.commit()


# ── Tests ─────────────────────────────────────────────────────────────────

def test_analysis_row_is_persisted_after_readiness_call():
    """
    After a successful POST /api/readiness the test DB must contain
    exactly one Analysis row with the correct user_id and target_role,
    and the JSON columns must be non-null and valid.
    """
    with _make_client() as client:
        # Seed the user row so the FK constraint is satisfied
        db = _TestSession()
        _seed_user(db)
        db.close()

        with patch("routes.readiness.get_core", return_value=_make_core_mock()):
            resp = client.post(
                "/api/readiness",
                files={"resume": ("resume.pdf", io.BytesIO(VALID_PDF), "application/pdf")},
                data={"target_role": TARGET_ROLE, "job_descriptions": JD},
            )

        assert resp.status_code == 200, resp.text

        # Query DB directly
        db = _TestSession()
        rows = db.query(Analysis).all()
        assert len(rows) == 1, f"Expected 1 Analysis row, got {len(rows)}"

        row = rows[0]
        assert row.user_id     == _FAKE_USER["uid"]
        assert row.target_role == TARGET_ROLE
        assert isinstance(row.match_score, int)

        # skill_gaps and matched_skills must be non-null lists (serialised RequirementGap)
        assert row.skill_gaps is not None, "skill_gaps should not be None"
        assert isinstance(row.skill_gaps, list)

        assert row.matched_skills is not None, "matched_skills should not be None"
        assert isinstance(row.matched_skills, list)

        # roadmap_inputs must be a non-null dict with required keys
        assert row.roadmap_inputs is not None, "roadmap_inputs should not be None"
        assert isinstance(row.roadmap_inputs, dict)
        for key in ("screen_score", "interview_score", "job_score", "verdict", "has_blocker", "top_roi_gaps"):
            assert key in row.roadmap_inputs, f"roadmap_inputs missing key: {key}"

        # feasibility_score should be a dict with job_score and verdict
        assert row.feasibility_score is not None, "feasibility_score should not be None"
        assert isinstance(row.feasibility_score, dict)
        assert "job_score" in row.feasibility_score
        assert "verdict"   in row.feasibility_score

        db.close()

    app.dependency_overrides.clear()


def test_history_endpoint_returns_persisted_analysis():
    """
    GET /api/user/history for the authenticated user must return the
    analysis saved by the previous POST, with matching target_role and
    match_score.
    """
    with _make_client() as client:
        db = _TestSession()
        _seed_user(db)
        db.close()

        with patch("routes.readiness.get_core", return_value=_make_core_mock()):
            post_resp = client.post(
                "/api/readiness",
                files={"resume": ("resume.pdf", io.BytesIO(VALID_PDF), "application/pdf")},
                data={"target_role": TARGET_ROLE, "job_descriptions": JD},
            )
        assert post_resp.status_code == 200, post_resp.text
        expected_score = post_resp.json()["screen_score"]

        history_resp = client.get("/api/user/history")
        assert history_resp.status_code == 200, history_resp.text

        body = history_resp.json()
        # The history response wraps records under an "analyses" key
        analyses = body.get("analyses", body) if isinstance(body, dict) else body
        if isinstance(analyses, dict):
            analyses = analyses.get("analyses", [])

        assert len(analyses) >= 1, f"Expected at least 1 analysis in history, got: {body}"

        found = [a for a in analyses if a.get("target_role") == TARGET_ROLE]
        assert found, f"No analysis with target_role='{TARGET_ROLE}' in history"
        assert found[0]["match_score"] == expected_score

    app.dependency_overrides.clear()


def test_db_failure_does_not_break_api_response():
    """
    If the DB commit raises an exception, the API must still return 200
    with a valid ReadinessResponse (the error is logged, not propagated).
    """
    with _make_client() as client:
        db = _TestSession()
        _seed_user(db)
        db.close()

        with patch("routes.readiness.get_core", return_value=_make_core_mock()):
            # Patch db.add to raise, simulating a DB failure mid-save
            with patch("sqlalchemy.orm.Session.add", side_effect=Exception("DB exploded")):
                resp = client.post(
                    "/api/readiness",
                    files={"resume": ("resume.pdf", io.BytesIO(VALID_PDF), "application/pdf")},
                    data={"target_role": TARGET_ROLE, "job_descriptions": JD},
                )

        # Response must still be 200 — DB failure must not leak to the client
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "screen_score" in body

    app.dependency_overrides.clear()
