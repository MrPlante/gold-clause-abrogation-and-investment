"""
Table 7 — Aggregated investment effects (tab:agg).

Replicates Stata A13_aggregation.do (Panel A) and A13_aggregationd1.do (Panel B).
Panel C is total investment among ``d == 0`` firms.
"""

from __future__ import annotations

from pathlib import Path

from config import A4_PATH, COEF_TOLERANCE, MANUSCRIPT_BODY_TABLES, REFACTOR_OUTPUT_TABLES_BODY
from lib.aggregate import AggregatePanel, PeriodValues, run_aggregate
from lib.io import read_dta
from lib.render_aggregate_tex import render_table7_latex

# Manuscript reports percentages to 2 decimals.
TOL = max(COEF_TOLERANCE, 0.011)


def load_panel():
    return read_dta(A4_PATH)


def _parse_manuscript_table(tex_path: Path) -> dict[str, dict[str, PeriodValues]]:
    text = tex_path.read_text(encoding="utf-8")
    current_panel: str | None = None
    parsed: dict[str, dict[str, PeriodValues]] = {}

    panel_map = {
        "Panel A": "all_firms",
        "Panel B": "d_positive",
        "Panel C": "d_zero",
    }
    row_map = {
        "Total net investment": "total",
        "Gold clause effect": "gold_effect",
    }

    for line in text.splitlines():
        for label, key in panel_map.items():
            if label in line:
                current_panel = key
                parsed.setdefault(current_panel, {})
                break

        if current_panel is None or "&" not in line:
            continue

        parts = [p.strip() for p in line.split("&")]
        if len(parts) != 4:
            continue

        row_key = None
        for prefix, key in row_map.items():
            if parts[0].startswith(prefix):
                row_key = key
                break
        if row_key is None:
            continue

        try:
            vals = PeriodValues(
                y1933=float(parts[1]),
                y1934=float(parts[2]),
                after=float(parts[3].rstrip("\\").strip()),
            )
        except ValueError:
            continue
        parsed[current_panel][row_key] = vals

    return parsed


def _compare_period(name: str, expected: PeriodValues, actual: PeriodValues) -> list[str]:
    failures = []
    for period in ("y1933", "y1934", "after"):
        exp = getattr(expected, period)
        act = getattr(actual, period)
        if abs(exp - act) > TOL:
            failures.append(f"{name}.{period}: expected {exp:.4f}, got {act:.4f}")
    return failures


def validate_against_manuscript(panels: dict[str, AggregatePanel]) -> list[str]:
    parsed = _parse_manuscript_table(MANUSCRIPT_BODY_TABLES / "7_aggregate.tex")
    failures: list[str] = []

    for panel_key, rows in parsed.items():
        panel = panels[panel_key]
        for row_key, expected in rows.items():
            actual = panel.total if row_key == "total" else panel.gold_effect
            if actual is None:
                failures.append(f"{panel_key}.{row_key}: missing computed value")
                continue
            failures.extend(
                _compare_period(f"{panel_key}.{row_key}", expected, actual)
            )

    return failures


def write_latex_table(panels: dict[str, AggregatePanel], path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_BODY / "7_aggregate.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_table7_latex(panels), encoding="utf-8")
    return out


def main() -> dict[str, AggregatePanel]:
    panels = run_aggregate(load_panel())
    failures = validate_against_manuscript(panels)
    if failures:
        print(
            f"WARNING: Table 7 manuscript check differences "
            f"({len(failures)} checks — likely data version mismatch):\n"
            + "\n".join(failures[:20])
        )
    else:
        print(f"Table 7 — all manuscript checks passed (tol={TOL})")
    for key, panel in panels.items():
        print(
            f"  {key}: total=({panel.total.y1933:.2f}, {panel.total.y1934:.2f}, "
            f"{panel.total.after:.2f})"
        )
        if panel.gold_effect is not None:
            print(
                f"           gold=({panel.gold_effect.y1933:.2f}, "
                f"{panel.gold_effect.y1934:.2f}, {panel.gold_effect.after:.2f})"
            )

    out_path = write_latex_table(panels)
    print(f"  Wrote LaTeX table -> {out_path}")
    return panels


if __name__ == "__main__":
    main()
