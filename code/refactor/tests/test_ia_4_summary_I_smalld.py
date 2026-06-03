"""Validation tests for Internet Appendix Table 4 (below-median tilde-d summary stats)."""

from __future__ import annotations

import sys
from pathlib import Path

REFACTOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFACTOR))

from lib.summary_stats_ia import compute_distribution_table  # noqa: E402
from tables.appendix.ia_4_summary_I_smalld import (  # noqa: E402
    TOL,
    PERCENTILE_TOL,
    VARIABLES_BY_PANEL,
    load_panel,
    validate_against_manuscript,
)


def test_ia_4_summary_I_smalld_matches_manuscript():
    panels = compute_distribution_table(load_panel(), VARIABLES_BY_PANEL)
    checks = validate_against_manuscript(panels)
    failures = [
        (name, expected, actual)
        for name, expected, actual in checks
        if abs(expected - actual) > (
            PERCENTILE_TOL
            if name.split(".")[-1] in ("p5", "p25", "p50", "p75", "p95")
            else TOL
        )
    ]
    assert not failures, failures
