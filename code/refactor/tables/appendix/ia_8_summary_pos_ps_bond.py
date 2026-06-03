"""
Internet Appendix Table 8 — Summary stats for preferred-equity / bond issuers with d > 0.

Uses ``dalt`` exposure (Stata A14 dalt blocks).
"""

from __future__ import annotations

from pathlib import Path

from config import (
    COEF_TOLERANCE,
    MANUSCRIPT_APPENDIX_TABLES,
    REFACTOR_OUTPUT_TABLES_APPENDIX,
)
from lib.dalt_panel import load_dalt_panel
from lib.ia_distribution_validate import (
    check_failures,
    parse_distribution_table,
    validate_distribution_panels,
)
from lib.render_summary_ia_tex import render_distribution_table
from lib.summary_stats_ia import BASE_VARIABLES, compute_distribution_table

TOL = max(COEF_TOLERANCE, 0.011)
# Manuscript built on earlier A4 (452 vs 486 firms in current panel); see DISCREPANCIES.
PERCENTILE_TOL = 0.09

VARIABLES_BY_PANEL = {
    "A": BASE_VARIABLES
    + [
        ("d", r"\ensuremath{\tilde{d}}"),
        ("dind", r"\ensuremath{I_{\tilde{d}>0}}"),
    ],
    "B": BASE_VARIABLES,
    "C": BASE_VARIABLES
    + [
        ("d", r"\ensuremath{\tilde{d}}"),
        ("dind", r"\ensuremath{I_{\tilde{d}>0}}"),
    ],
}

TABLE_NOTES = (
    r"\scriptsize{\textit{Notes.} This table reports summary statistics for publicly "
    r"traded industrial firms that issued preferred equity and/or corporate bonds, among "
    r"firms with positive gold clause exposure ($\tilde{d} > 0$). Panel A covers the "
    r"pre-abrogation period (1926--1932), Panel B the legal uncertainty period (1933--1934), "
    r"and Panel C the post-resolution period (1935--1940). Long-term liabilities (LTL) are "
    r"the sum of corporate bonds, preferred shares, and bank debt. All variables are "
    r"winsorized at the 0.5\% and 99.5\% levels within each year. See Appendix "
    r"\ref{secapp:vars} for detailed variable definitions.}"
)


def load_panel():
    """All preferred-equity / bond issuers (``dalt != .``); Stata A14 dalt block."""
    return load_dalt_panel()


def validate_against_manuscript(panels: dict) -> list[tuple[str, float, float]]:
    parsed = parse_distribution_table(
        MANUSCRIPT_APPENDIX_TABLES / "8_summary_pos_ps_bond.tex"
    )
    return validate_distribution_panels(
        panels, parsed, tol=TOL, percentile_tol=PERCENTILE_TOL
    )


def write_latex_table(panels: dict, path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "8_summary_pos_ps_bond.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        render_distribution_table(
            panels,
            caption="Summary statistics for preferred equity and/or bond issuers",
            label="tab:sum_pos",
            notes=TABLE_NOTES,
            panel_order=["A", "B", "C"],
        ),
        encoding="utf-8",
    )
    return out


def main() -> dict:
    panels = compute_distribution_table(load_panel(), VARIABLES_BY_PANEL)
    checks = validate_against_manuscript(panels)
    failures = check_failures(checks, tol=TOL, percentile_tol=PERCENTILE_TOL)

    out_path = write_latex_table(panels)
    if failures:
        print(
            f"IA Table 8 — {len(checks) - len(failures)}/{len(checks)} checks passed "
            f"(tol={TOL}; {len(failures)} failures — see DISCREPANCIES D-013)"
        )
        print("  First failures:")
        for line in failures[:5]:
            print(f"    {line}")
    else:
        print(f"IA Table 8 — all {len(checks)} manuscript checks passed (tol={TOL})")
    print(f"  Wrote LaTeX table -> {out_path}")
    return panels


if __name__ == "__main__":
    main()
