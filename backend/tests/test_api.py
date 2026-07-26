"""
API endpoint tests using FastAPI TestClient.

Every test in this file makes a real HTTP request through the full ASGI stack.
`get_core` is mocked so no ML models are loaded, but validation, exception
handling, routing, and response-schema parsing all run for real.

HTTP request count: all test functions below hit the /api/readiness endpoint.
"""

import io
import sys
from unittest.mock import MagicMock, patch

import pytest

# ── Stub heavy optional packages before any app import ────────────────────
# Order matters: stubs must be in sys.modules before the first import that
# transitively requires them, otherwise Python raises ModuleNotFoundError at
# collection time and brings down the entire suite.

def _stub(name: str) -> MagicMock:
    """Register a MagicMock under `name` and return it (no-op if already present)."""
    if name not in sys.modules:
        sys.modules[name] = MagicMock()
    return sys.modules[name]  # type: ignore[return-value]


# pydantic_settings — may not be pip-installed in lightweight envs
if "pydantic_settings" not in sys.modules:
    _ps = MagicMock()
    _ps.BaseSettings = object  # bare object so `class Settings(BaseSettings)` works
    sys.modules["pydantic_settings"] = _ps

# sqlalchemy — needs a real package hierarchy so sub-module imports resolve
if "sqlalchemy" not in sys.modules:
    _sa = MagicMock()
    _sa.orm    = MagicMock()
    _sa.ext    = MagicMock()
    _sa.ext.declarative = MagicMock()
    _sa.sql    = MagicMock()
    _sa.engine = MagicMock()
    _sa.pool   = MagicMock()
    sys.modules["sqlalchemy"]                   = _sa
    sys.modules["sqlalchemy.orm"]               = _sa.orm
    sys.modules["sqlalchemy.ext"]               = _sa.ext
    sys.modules["sqlalchemy.ext.declarative"]   = _sa.ext.declarative
    sys.modules["sqlalchemy.sql"]               = _sa.sql
    sys.modules["sqlalchemy.engine"]            = _sa.engine
    sys.modules["sqlalchemy.pool"]              = _sa.pool

_stub("google")
_stub("google.generativeai")
_stub("groq")
_stub("firebase_admin")
_stub("firebase_admin.credentials")
_stub("firebase_admin.auth")

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402
from routes.readiness import ReadinessResponse  # noqa: E402

# ── Shared test data ───────────────────────────────────────────────────────

VALID_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog >>\nendobj\n"
    b"xref\n0 1\n0000000000 65535 f \ntrailer\n<< /Size 1 >>\n%%EOF"
)
VALID_ROLE = "Software Engineer"
VALID_JD   = "We need a Python developer with SQL and Docker experience."


def _make_core_mock():
    """Return a mock core whose resume_parser and skill_extractor cooperate."""
    core = MagicMock()

    # resume_parser.parse returns a minimal resume dict
    core.resume_parser.parse.return_value = {
        "full_text": "Python developer with SQL experience. Jan 2022 - Present",
        "sections": {
            "skills":     "Python, SQL",
            "experience": "Built APIs using Python and SQL. Jan 2022 - Present",
        },
    }

    # skill_extractor.skill_list drives _candidate_skills
    core.skill_extractor.skill_list = ["python", "sql", "docker"]

    # skill_extractor.extract returns two skills
    def _make_skill(name, ctx):
        s = MagicMock()
        s.normalized = name
        s.context    = ctx
        s.source     = "phrase_match"
        return s

    core.skill_extractor.extract.return_value = [
        _make_skill("python", "Built APIs using Python. Jan 2022 - Present"),
        _make_skill("sql",    "SQL database work. Jan 2022 - Present"),
    ]

    return core


# ── Helpers ────────────────────────────────────────────────────────────────

def _post(client: TestClient, *, pdf=VALID_PDF, role=VALID_ROLE, jd=VALID_JD):
    """POST to /api/readiness with sensible defaults."""
    return client.post(
        "/api/readiness",
        files={"resume": ("resume.pdf", io.BytesIO(pdf), "application/pdf")},
        data={"target_role": role, "job_descriptions": jd},
    )


# ── Happy path ─────────────────────────────────────────────────────────────

def test_happy_path_returns_200_and_valid_schema():
    """200 response body must validate against ReadinessResponse and contain
    scoring_version plus a non-empty components array."""
    with patch("routes.readiness.get_core", return_value=_make_core_mock()):
        with TestClient(app) as client:
            resp = _post(client)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    # Validate against the pydantic schema
    parsed = ReadinessResponse(**body)
    assert parsed.scoring_version != ""
    assert len(parsed.components) > 0


# ── File validation ────────────────────────────────────────────────────────

def test_txt_extension_returns_4xx_with_message():
    """.txt upload must be rejected with a readable error, not a 500."""
    with TestClient(app) as client:
        resp = client.post(
            "/api/readiness",
            files={"resume": ("resume.txt", io.BytesIO(b"%PDF-1.4\ncontent"), "text/plain")},
            data={"target_role": VALID_ROLE, "job_descriptions": VALID_JD},
        )
    assert 400 <= resp.status_code < 500, resp.text
    body = resp.json()
    assert "error" in body
    assert body["error"]  # non-empty message


def test_empty_file_returns_4xx():
    """Empty upload must be rejected before the ML stack is touched."""
    with TestClient(app) as client:
        resp = client.post(
            "/api/readiness",
            files={"resume": ("resume.pdf", io.BytesIO(b""), "application/pdf")},
            data={"target_role": VALID_ROLE, "job_descriptions": VALID_JD},
        )
    assert 400 <= resp.status_code < 500, resp.text


def test_oversized_file_returns_4xx():
    """File exceeding 10 MB must be rejected."""
    big = b"%PDF-1.4\n" + b"x" * (10 * 1024 * 1024 + 1)
    with TestClient(app) as client:
        resp = _post(client, pdf=big)
    assert 400 <= resp.status_code < 500, resp.text
    assert "error" in resp.json()


def test_pdf_extension_but_wrong_magic_bytes_returns_4xx():
    """A file named .pdf whose bytes do not start with %PDF must be rejected."""
    with TestClient(app) as client:
        resp = _post(client, pdf=b"PK\x03\x04this is actually a zip")
    assert 400 <= resp.status_code < 500, resp.text
    body = resp.json()
    assert "error" in body


# ── Form field validation ──────────────────────────────────────────────────

def test_missing_target_role_returns_422():
    """Omitting target_role must return 422 (FastAPI validation)."""
    with TestClient(app) as client:
        resp = client.post(
            "/api/readiness",
            files={"resume": ("resume.pdf", io.BytesIO(VALID_PDF), "application/pdf")},
            data={"job_descriptions": VALID_JD},
        )
    assert resp.status_code == 422, resp.text


def test_target_role_too_short_returns_4xx():
    """target_role='ab' (< 3 chars) must be rejected with a 4xx."""
    with TestClient(app) as client:
        resp = _post(client, role="ab")
    assert 400 <= resp.status_code < 500, resp.text
    assert "error" in resp.json()


def test_empty_job_descriptions_returns_4xx():
    """job_descriptions containing only whitespace must be rejected before ML runs."""
    with TestClient(app) as client:
        # Send whitespace-only — this reaches the route and triggers validation
        resp = _post(client, jd="   ")
    assert 400 <= resp.status_code < 500, resp.text
    body = resp.json()
    # Route raises ResumeParseFailed → handled as {"error": ...}
    assert "error" in body


# ── Parser failure path ────────────────────────────────────────────────────

def test_parser_raises_returns_4xx_not_500():
    """When the resume parser raises ResumeParseFailed (e.g. scanned PDF),
    the endpoint must return a 4xx with a helpful message — never a 500."""
    from core.exceptions import ResumeParseFailed as RPF

    core = _make_core_mock()
    core.resume_parser.parse.side_effect = RPF("Scanned PDF — no text layer found.")

    with patch("routes.readiness.get_core", return_value=core):
        with TestClient(app) as client:
            resp = _post(client)

    assert 400 <= resp.status_code < 500, f"Expected 4xx, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "error" in body
    assert body["error"]  # non-empty, human-readable


# ── Determinism through full stack ─────────────────────────────────────────

def test_two_identical_requests_return_identical_scores():
    """Same inputs must produce identical scores end-to-end (not just in score()).
    This catches any accidental datetime.now() or randomness in the route layer."""
    core = _make_core_mock()
    with patch("routes.readiness.get_core", return_value=core):
        with TestClient(app) as client:
            r1 = _post(client)
            r2 = _post(client)

    assert r1.status_code == 200, r1.text
    assert r2.status_code == 200, r2.text
    b1, b2 = r1.json(), r2.json()
    assert b1["screen_score"]    == b2["screen_score"]
    assert b1["interview_score"] == b2["interview_score"]
    assert b1["job_score"]       == b2["job_score"]
    assert b1["verdict"]         == b2["verdict"]
    assert b1["scoring_version"] == b2["scoring_version"]
