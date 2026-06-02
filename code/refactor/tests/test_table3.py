"""Coefficient validation tests for Table 3."""

from __future__ import annotations

import sys
from pathlib import Path

REFACTOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFACTOR))

from config import COEF_TOLERANCE  # noqa: E402
from tables.body.t03_investment import load_panel, run_models, validate_against_manuscript  # noqa: E402


def test_table3_matches_manuscript():
    df = load_panel()
    models = run_models(df)
    checks = validate_against_manuscript(models)
    failures = [
        (name, expected, actual)
        for name, expected, actual in checks
        if abs(expected - actual) > COEF_TOLERANCE
    ]
    assert not failures, failures
