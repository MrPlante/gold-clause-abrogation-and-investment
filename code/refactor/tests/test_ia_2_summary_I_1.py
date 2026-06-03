"""Validation tests for Internet Appendix Table 2 (tilde-d > 0 summary stats)."""

from __future__ import annotations

import sys
from pathlib import Path

REFACTOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFACTOR))

from lib.summary_stats_ia import compute_distribution_table  # noqa: E402
from tables.appendix.ia_2_summary_I_1 import (  # noqa: E402
    TOL,
    VARIABLES_BY_PANEL,
    load_panel,
    validate_against_manuscript,
)


def test_ia_2_summary_I_1_matches_manuscript():
    panels = compute_distribution_table(load_panel(), VARIABLES_BY_PANEL)
    checks = validate_against_manuscript(panels)
    failures = [
        (name, expected, actual)
        for name, expected, actual in checks
        if abs(expected - actual) > TOL
    ]
    assert not failures, failures
