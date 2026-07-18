"""Validation tests for Table 2."""

from __future__ import annotations

import sys
from pathlib import Path

REFACTOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFACTOR))

from config import COEF_TOLERANCE  # noqa: E402
from lib.bond_stats import compute_bond_stats  # noqa: E402
from tables.body.t02_bond_stats import validate_against_manuscript  # noqa: E402


def test_table2_matches_manuscript():
    rows = compute_bond_stats()
    checks = validate_against_manuscript(rows)
    tol = max(COEF_TOLERANCE, 0.011)
    failures = [
        (name, expected, actual)
        for name, expected, actual in checks
        if abs(expected - actual) > tol
    ]
    assert not failures, failures
