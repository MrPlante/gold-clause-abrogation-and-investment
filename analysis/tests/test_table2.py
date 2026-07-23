"""Coefficient validation tests for Table 2 (summary statistics)."""

from __future__ import annotations

import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(CODE_DIR.parent))

from config import COEF_TOLERANCE  # noqa: E402
from tables.body.t02_summary_stats import (  # noqa: E402
    compute_all_panels,
    load_panel,
    validate_against_manuscript,
)


def test_table2_matches_manuscript():
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


if __name__ == "__main__":
    test_table2_matches_manuscript()
    print("OK test_table2.py")
