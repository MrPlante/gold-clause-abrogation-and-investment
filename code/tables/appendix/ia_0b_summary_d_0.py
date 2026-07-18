"""
Internet Appendix Table 0b — Summary statistics for d = 0 firms (tabapp:summary_d_0).

Uses contemporaneous exposure ``d_orig == 0`` (manuscript). Panel C omits ``d`` rows.
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
from lib.summary_stats_ia import BASE_VARIABLES, compute_distribution_table

TOL = max(COEF_TOLERANCE, 0.011)

VARIABLES_BY_PANEL = {
    "A": BASE_VARIABLES
    + [
        ("d_orig", r"\ensuremath{d}"),
        ("dind_orig", r"\ensuremath{I_{d>0}}"),
    ],
    "B": BASE_VARIABLES
    + [
        ("d_orig", r"\ensuremath{d}"),
        ("dind_orig", r"\ensuremath{I_{d>0}}"),
    ],
    "C": BASE_VARIABLES,
}

TABLE_NOTES = (
    r"\scriptsize{\textit{Notes.} This table reports summary statistics for publicly "
    r"traded industrial firms with no contemporaneous gold clause exposure ($d = 0$). "
    r"Panel A covers the pre-abrogation period (1926--1932), Panel B the legal "
    r"uncertainty period surrounding the abrogation of the gold clause (1933--1934), "
    r"and Panel C the post-resolution period (1935--1940). Long-term liabilities (LTL) "
    r"are the sum of corporate bonds, preferred shares, and bank debt. All variables "
    r"are winsorized at the 0.5\% and 99.5\% levels within each year. See Appendix "
    r"\ref{secapp:vars} for detailed variable definitions.}"
)


def load_panel():
    df = read_dta(A4_PATH)
    return df.loc[df["d_orig"] == 0].copy()


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
        if current is None or "&" not in line or line.strip().startswith("\\"):
            continue
        if line.strip().startswith("Variable"):
            continue

        parts = [p.strip() for p in line.split("&")]
        if len(parts) != 10:
            continue

        label = parts[0]
        if not label or label.startswith("("):
            continue

        def _num(s: str) -> float | None:
            s = s.strip().replace("$-$", "-").rstrip("\\")
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


def validate_against_manuscript(panels: dict) -> list[tuple[str, float, float]]:
    parsed = _parse_manuscript_table(MANUSCRIPT_APPENDIX_TABLES / "0b_summary_d_0.tex")
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
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "0b_summary_d_0.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        render_distribution_table(
            panels,
            caption="Summary statistics for $d = 0$ firms",
            label="tabapp:summary_d_0",
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
        if abs(exp - act) > TOL
    ]
    if failures:
        print(
            f"IA Table 0b validation failed ({len(failures)}/{len(checks)} checks):\n"
            + "\n".join(failures[:20])
        )

    else:
        print(f"IA Table 0b — all {len(checks)} manuscript checks passed (tol={TOL})")
    for key in ("A", "B", "C"):
        first = panels[key].rows[0].stats
        print(f"  Panel {key}: firms={first.n_firms}, N={first.n_obs}")

    out_path = write_latex_table(panels)
    print(f"  Wrote LaTeX table -> {out_path}")
    return panels


if __name__ == "__main__":
    main()
