"""Validation tests for Table 6 (credit ratings)."""

from __future__ import annotations

import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(CODE_DIR.parent))

from config import COEF_TOLERANCE  # noqa: E402
from tables.body.t06_credit_ratings import (  # noqa: E402
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


if __name__ == "__main__":
    test_table6_matches_manuscript()
    print("OK test_table6.py")
