"""Validation tests for Table IA.5 (tilde-d = 0 summary stats)."""

from __future__ import annotations

import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(CODE_DIR.parent))

from tables.models.summary_stats_ia import compute_distribution_table  # noqa: E402
from tables.appendix.ia05_summary_I_0 import (  # noqa: E402
    TOL,
    VARIABLES_BY_PANEL,
    load_panel,
    validate_against_manuscript,
)


def test_ia05_matches_manuscript():
    panels = compute_distribution_table(load_panel(), VARIABLES_BY_PANEL)
    checks = validate_against_manuscript(panels)
    failures = [
        (name, expected, actual)
        for name, expected, actual in checks
        if abs(expected - actual) > TOL
    ]
    assert not failures, failures


if __name__ == "__main__":
    test_ia05_matches_manuscript()
    print("OK test_ia05_summary_I_0.py")
