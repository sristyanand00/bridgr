"""
Guard test: ensure routes/readiness.py uses the canonical scoring engine.

Background: a previous refactor left two competing scoring implementations in
the repo simultaneously — one in core_ml/scoring.py (the canonical engine with
full test coverage) and an inline re-implementation inside the route handler.
The inline version shadowed the canonical one, so changes to core_ml/scoring.py
had no effect in production.  This test exists to prevent a recurrence.

If this test ever fails it means someone added scoring logic directly to the
route file.  The fix is to move that logic into core_ml/scoring.py and import
the result, not to weaken this test.
"""

import ast
import sys
from pathlib import Path

import pytest

ROUTE_FILE = Path(__file__).parent.parent / "routes" / "readiness.py"


def _load_source() -> str:
    return ROUTE_FILE.read_text(encoding="utf-8")


def test_readiness_imports_score_from_core_ml_scoring():
    """routes/readiness.py must import `score` from core_ml.scoring."""
    source = _load_source()
    tree   = ast.parse(source)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "core_ml.scoring":
                names = [alias.name for alias in node.names]
                if "score" in names:
                    found = True
                    break

    assert found, (
        "routes/readiness.py does not import `score` from core_ml.scoring.  "
        "All scoring must go through the canonical engine — do not inline it."
    )


def test_interview_points_not_computed_in_route():
    """The string 'interview_points' must not appear in routes/readiness.py.

    Its presence would mean scoring arithmetic has been duplicated inside the
    route handler, bypassing core_ml/scoring.py and its test coverage.
    """
    source = _load_source()
    assert "interview_points" not in source, (
        "'interview_points' found in routes/readiness.py.  "
        "Scoring arithmetic belongs exclusively in core_ml/scoring.py."
    )
