"""Validation tests for Table 7."""

from __future__ import annotations

import sys
from pathlib import Path

REFACTOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFACTOR))

from config import COEF_TOLERANCE  # noqa: E402
from tables.body.t07_aggregate import (  # noqa: E402
    TOL,
    load_panel,
    run_aggregate,
    validate_against_manuscript,
)


def test_table7_matches_manuscript():
    panels = run_aggregate(load_panel())
    failures = validate_against_manuscript(panels)
    assert not failures, failures
    assert TOL >= max(COEF_TOLERANCE, 0.011)
