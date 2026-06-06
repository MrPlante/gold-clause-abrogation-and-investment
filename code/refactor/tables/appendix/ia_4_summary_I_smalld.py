"""
Internet Appendix Table 4 — Summary statistics for below-median tilde-d > 0 firms.

Sample: ``0 < d < median(d)`` where the median is computed over 1926--1932 among
``d > 0`` (Stata A14 smalld block). Panel B omits tilde-d indicator rows.
"""

from __future__ import annotations

import re
from pathlib import Path

from config import (
    A4_PATH,
    COEF_TOLERANCE,
    MANUSCRIPT_APPENDIX_TABLES,
    REFACTOR_OUTPUT_TABLES_APPENDIX,
)
from lib.io import read_dta
from lib.render_summary_ia_tex import render_distribution_table
from lib.summary_stats_ia import (
    BASE_VARIABLES,
    _stata_quantile,
    compute_distribution_table,
)

TOL = max(COEF_TOLERANCE, 0.011)
# Panel B (N≈160) percentile gaps vs manuscript; see DISCREPANCIES D-012.
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
    r"traded industrial firms with below-median gold clause exposure "
    r"($0 < \tilde{d} \leq 0.53$). Panel A covers the pre-abrogation period "
    r"(1926--1932), Panel B the legal uncertainty period surrounding the abrogation "
    r"of the gold clause (1933--1934), and Panel C the post-resolution period "
    r"(1935--1940). Long-term liabilities (LTL) are the sum of corporate bonds, "
    r"preferred shares, and bank debt. In Panels A and B, $\tilde{d}$ can be slightly "
    r"greater than Corp.\ bonds/LTL because $\tilde{d}$ is calculated using the "
    r"reported amount outstanding of each bond, whereas Corp.\ bonds/LTL is based on "
    r"balance sheet information. In Panel C, $\tilde{d}$ can differ significantly "
    r"from Corp.\ bonds/LTL because $\tilde{d}$ is frozen at each firm's 1930 value "
    r"while Corp.\ bonds/LTL is contemporaneous. All variables are winsorized at the "
    r"0.5\% and 99.5\% levels within each year. See Appendix \ref{secapp:vars} for "
    r"detailed variable definitions.}"
)


def _median_d_pre_abrogation(df):
    mask = (df["year"] >= 1926) & (df["year"] <= 1932) & (df["d"] > 0)
    return _stata_quantile(df.loc[mask, "d"], 0.50)


def load_panel():
    df = read_dta(A4_PATH)
    p50 = _median_d_pre_abrogation(df)
    return df.loc[(df["d"] > 0) & (df["d"] < p50)].copy()


def _parse_manuscript_table(tex_path: Path) -> dict[str, list[dict]]:
    text = tex_path.read_text(encoding="utf-8")
    panels: dict[str, list[dict]] = {"A": [], "B": [], "C": []}
    current: str | None = None

    for line in text.splitlines():
        if "Panel A:" in line:
            current = "A"
            continue
        if "Panel B:" in line:
            current = "B"
            continue
        if "Panel C:" in line:
            current = "C"
            continue
        if current is None or "&" not in line:
            continue
        stripped = line.strip()
        if stripped.startswith("\\") and not stripped.startswith(r"\ensuremath"):
            continue
        if stripped.startswith("Variable"):
            continue

        parts = [p.strip().rstrip("\\").strip() for p in line.split("&")]
        if len(parts) != 10:
            continue

        label = parts[0]
        if not label or label.startswith("("):
            continue

        def _num(s: str) -> float | None:
            s = s.strip().replace("$-$", "-")
            if not s:
                return None
            try:
                return float(s)
            except ValueError:
                return None

        def _int(s: str) -> int | None:
            s = s.strip().replace(",", "")
            if not s:
                return None
            try:
                return int(s)
            except ValueError:
                return None

        panels[current].append(
            {
                "label": label,
                "firms": _int(parts[1]),
                "n": _int(parts[2]),
                "mean": _num(parts[3]),
                "sd": _num(parts[4]),
                "p5": _num(parts[5]),
                "p25": _num(parts[6]),
                "p50": _num(parts[7]),
                "p75": _num(parts[8]),
                "p95": _num(parts[9]),
            }
        )

    return panels


def _label_key(label: str) -> str:
    label = re.sub(r"\\ensuremath\{([^}]+)\}", r"\1", label)
    return label.replace(r"\ ", " ").strip()


def _field_tol(field: str) -> float:
    if field in ("p5", "p25", "p50", "p75", "p95"):
        return PERCENTILE_TOL
    return TOL


def validate_against_manuscript(panels: dict) -> list[tuple[str, float, float]]:
    parsed = _parse_manuscript_table(
        MANUSCRIPT_APPENDIX_TABLES / "4_summary_I_smalld.tex"
    )
    checks: list[tuple[str, float, float]] = []

    for panel_key in ("A", "B", "C"):
        computed = {_label_key(r.label): r for r in panels[panel_key].rows}
        for exp in parsed[panel_key]:
            key = _label_key(exp["label"])
            row = computed.get(key)
            if row is None:
                continue
            s = row.stats
            mapping = {
                "firms": s.n_firms,
                "n": s.n_obs,
                "mean": s.mean,
                "sd": s.std,
                "p5": s.p5,
                "p25": s.p25,
                "p50": s.p50,
                "p75": s.p75,
                "p95": s.p95,
            }
            for field, actual in mapping.items():
                expected = exp.get(field)
                if expected is None:
                    continue
                checks.append((f"panel{panel_key}.{key}.{field}", float(expected), float(actual)))

    return checks


def write_latex_table(panels: dict, path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "4_summary_I_smalld.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        render_distribution_table(
            panels,
            caption=r"Summary statistics for below median $\tilde{d} > 0$ firms",
            label="tabapp:summary_I_smalld",
            notes=TABLE_NOTES,
            panel_order=["A", "B", "C"],
        ),
        encoding="utf-8",
    )
    return out


def main() -> dict:
    panels = compute_distribution_table(load_panel(), VARIABLES_BY_PANEL)
    checks = validate_against_manuscript(panels)

    failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in checks
        if abs(exp - act) > _field_tol(name.split(".")[-1])
    ]
    if failures:
        print(
            f"IA Table 4 (summary_I_smalld) validation failed "
            f"({len(failures)}/{len(checks)} checks):\n" + "\n".join(failures[:20])
        )

    pct_gaps = [
        (name, exp, act)
        for name, exp, act in checks
        if name.split(".")[-1] in ("p5", "p25", "p50", "p75", "p95")
        and abs(exp - act) > TOL
    ]
    if pct_gaps:
        print(
            f"  Note: {len(pct_gaps)} percentile cells differ at tol={TOL} "
            f"(within {PERCENTILE_TOL}; see DISCREPANCIES D-012)"
        )

    else:
        print(f"IA Table 4 (summary_I_smalld) — all {len(checks)} manuscript checks passed")
    for key in ("A", "B", "C"):
        first = panels[key].rows[0].stats
        print(f"  Panel {key}: firms={first.n_firms}, N={first.n_obs}")

    out_path = write_latex_table(panels)
    print(f"  Wrote LaTeX table -> {out_path}")
    return panels


if __name__ == "__main__":
    main()
