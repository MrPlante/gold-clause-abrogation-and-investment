"""Validation tests for Table 8 (aggregate investment)."""

from __future__ import annotations

import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(CODE_DIR.parent))

from config import COEF_TOLERANCE  # noqa: E402
from tables.body.t08_aggregate import (  # noqa: E402
    TOL,
    load_panel,
    run_aggregate,
    validate_against_manuscript,
)


def test_table8_matches_manuscript():
    panels = run_aggregate(load_panel())
    failures = validate_against_manuscript(panels)
    assert not failures, failures
    assert TOL >= max(COEF_TOLERANCE, 0.011)


if __name__ == "__main__":
    test_table8_matches_manuscript()
    print("OK test_table8.py")
