"""Validation tests for Internet Appendix Table 0 (tilde-d summary stats)."""

from __future__ import annotations

import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(CODE_DIR.parent))

from tables.appendix.ia03_sum_stats_tilde_d import (  # noqa: E402
    TOL,
    load_panel,
    validate_against_manuscript,
)
from tables.models.summary_stats import compute_tilde_d_panels  # noqa: E402


def test_ia03_sum_stats_tilde_d_matches_manuscript():
    panels = compute_tilde_d_panels(load_panel())
    checks = validate_against_manuscript(panels)
    failures = [
        (name, expected, actual)
        for name, expected, actual in checks
        if abs(expected - actual) > TOL
    ]
    assert not failures, failures
