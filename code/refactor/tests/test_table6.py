"""Validation tests for Table 6."""

from __future__ import annotations

import sys
from pathlib import Path

REFACTOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFACTOR))

from config import COEF_TOLERANCE  # noqa: E402
from tables.body.t06_controls import (  # noqa: E402
    load_panel,
    run_models,
    validate_against_manuscript,
)


def test_table6_matches_manuscript():
    models = run_models(load_panel())
    checks = validate_against_manuscript(models)
    failures = [
        (name, expected, actual)
        for name, expected, actual in checks
        if abs(expected - actual) > COEF_TOLERANCE
    ]
    assert not failures, failures
