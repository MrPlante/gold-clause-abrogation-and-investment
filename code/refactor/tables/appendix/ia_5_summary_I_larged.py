"""
Internet Appendix Table 5 — Summary statistics for above-median tilde-d > 0 firms.

Sample: ``d > median(d)`` where the median is computed over 1926--1932 among
``d > 0`` (Stata A14 larged block; strict ``>`` on median).
"""

from __future__ import annotations

from pathlib import Path

from config import (
    A4_PATH,
    COEF_TOLERANCE,
    MANUSCRIPT_APPENDIX_TABLES,
    REFACTOR_OUTPUT_TABLES_APPENDIX,
)
from lib.ia_distribution_validate import (
    check_failures,
    parse_distribution_table,
    validate_distribution_panels,
)
from lib.io import read_dta
from lib.render_summary_ia_tex import render_distribution_table
from lib.summary_stats_ia import (
    BASE_VARIABLES,
    _stata_quantile,
    compute_distribution_table,
)

TOL = max(COEF_TOLERANCE, 0.011)
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
    r"traded industrial firms with above-median gold clause exposure "
    r"($\tilde{d} > 0.53$ among firms with $\tilde{d} > 0$ in 1926--1932). Panel A "
    r"covers the pre-abrogation period (1926--1932), Panel B the legal uncertainty "
    r"period surrounding the abrogation of the gold clause (1933--1934), and Panel C "
    r"the post-resolution period (1935--1940). Long-term liabilities (LTL) are the sum "
    r"of corporate bonds, preferred shares, and bank debt. In Panels A and B, "
    r"$\tilde{d}$ can be slightly greater than Corp.\ bonds/LTL because $\tilde{d}$ is "
    r"calculated using the reported amount outstanding of each bond, whereas Corp.\ "
    r"bonds/LTL is based on balance sheet information. In Panel C, $\tilde{d}$ can "
    r"differ significantly from Corp.\ bonds/LTL because $\tilde{d}$ is frozen at each "
    r"firm's 1930 value while Corp.\ bonds/LTL is contemporaneous. All variables are "
    r"winsorized at the 0.5\% and 99.5\% levels within each year. See Appendix "
    r"\ref{secapp:vars} for detailed variable definitions.}"
)


def _median_d_pre_abrogation(df):
    mask = (df["year"] >= 1926) & (df["year"] <= 1932) & (df["d"] > 0)
    return _stata_quantile(df.loc[mask, "d"], 0.50)


def load_panel():
    df = read_dta(A4_PATH)
    p50 = _median_d_pre_abrogation(df)
    return df.loc[(df["d"] > 0) & (df["d"] > p50)].copy()


def validate_against_manuscript(panels: dict) -> list[tuple[str, float, float]]:
    parsed = parse_distribution_table(
        MANUSCRIPT_APPENDIX_TABLES / "5_summary_I_larged.tex"
    )
    return validate_distribution_panels(
        panels, parsed, tol=TOL, percentile_tol=PERCENTILE_TOL
    )


def write_latex_table(panels: dict, path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "5_summary_I_larged.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        render_distribution_table(
            panels,
            caption=r"Summary statistics for above median $\tilde{d} > 0$ firms",
            label="tabapp:summary_I_larged",
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

    if failures:
        raise AssertionError(
            f"IA Table 5 (summary_I_larged) validation failed "
            f"({len(failures)}/{len(checks)} checks):\n" + "\n".join(failures[:20])
        )

    pct_gaps = [
        (name, exp, act)
        for name, exp, act in checks
        if name.split(".")[-1].startswith("p") and abs(exp - act) > TOL
    ]
    if pct_gaps:
        print(
            f"  Note: {len(pct_gaps)} percentile cells differ at tol={TOL} "
            f"(within {PERCENTILE_TOL})"
        )

    print(f"IA Table 5 (summary_I_larged) — all {len(checks)} manuscript checks passed")
    out_path = write_latex_table(panels)
    print(f"  Wrote LaTeX table -> {out_path}")
    return panels


if __name__ == "__main__":
    main()
