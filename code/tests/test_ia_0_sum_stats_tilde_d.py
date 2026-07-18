"""Validation tests for Internet Appendix Table 0 (tilde-d summary stats)."""

from __future__ import annotations

import sys
from pathlib import Path

REFACTOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFACTOR))

from tables.appendix.ia_0_sum_stats_tilde_d import (  # noqa: E402
    TOL,
    load_panel,
    validate_against_manuscript,
)
from lib.summary_stats import compute_tilde_d_panels  # noqa: E402


def test_ia_0_sum_stats_tilde_d_matches_manuscript():
    panels = compute_tilde_d_panels(load_panel())
    checks = validate_against_manuscript(panels)
    failures = [
        (name, expected, actual)
        for name, expected, actual in checks
        if abs(expected - actual) > TOL
    ]
    assert not failures, failures
