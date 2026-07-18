"""Coefficient validation tests for Table 1."""

from __future__ import annotations

import sys
from pathlib import Path

REFACTOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFACTOR))

from config import COEF_TOLERANCE  # noqa: E402
from tables.body.t01_summary_stats import (  # noqa: E402
    compute_all_panels,
    load_panel,
    validate_against_manuscript,
)


def test_table1_matches_manuscript():
    df = load_panel()
    panels = compute_all_panels(df)
    checks = validate_against_manuscript(panels)
    tol = max(COEF_TOLERANCE, 0.011)
    failures = [
        (name, expected, actual)
        for name, expected, actual in checks
        if abs(expected - actual) > tol
    ]
    assert not failures, failures[:10]
