"""
Internet Appendix Table 16 — Heterogeneous aggregate effects (Stata A13 extensions).
"""

from __future__ import annotations

from pathlib import Path

from config import A4_PATH, COEF_TOLERANCE, MANUSCRIPT_APPENDIX_TABLES, REFACTOR_OUTPUT_TABLES_APPENDIX
from lib.aggregate import PeriodValues
from lib.aggregate_hetero import HeteroGoldEffects, run_aggregate_hetero
from lib.io import read_dta
from lib.render_aggregate_hetero_tex import render_aggregate_hetero_table

TOL = max(COEF_TOLERANCE, 0.011)


def _parse_manuscript(tex_path: Path) -> dict[str, dict[str, PeriodValues]]:
    parsed: dict[str, dict[str, PeriodValues]] = {}
    current: str | None = None

    for line in tex_path.read_text(encoding="utf-8").splitlines():
        if "Panel A:" in line:
            current = "all_firms"
            parsed.setdefault(current, {})
            continue
        if "Panel B:" in line:
            current = "d_positive"
            parsed.setdefault(current, {})
            continue
        if current is None or "&" not in line:
            continue

        parts = [p.strip() for p in line.split("&")]
        if len(parts) != 4:
            continue

        row = parts[0]
        if "baseline" in row:
            row_key = "baseline"
        elif "rating" in row:
            row_key = "rating"
        elif "size" in row:
            row_key = "size"
        else:
            continue

        try:
            parsed[current][row_key] = PeriodValues(
                y1933=float(parts[1]),
                y1934=float(parts[2]),
                after=float(parts[3].rstrip("\\").strip()),
            )
        except ValueError:
            continue
    return parsed


def validate_against_manuscript(panels: dict[str, HeteroGoldEffects]) -> list[str]:
    parsed = _parse_manuscript(MANUSCRIPT_APPENDIX_TABLES / "16_aggregate_heterogeneous.tex")
    failures: list[str] = []

    for panel_key, rows in parsed.items():
        panel = panels[panel_key]
        for row_key, expected in rows.items():
            actual = getattr(panel, row_key)
            for period in ("y1933", "y1934", "after"):
                exp = getattr(expected, period)
                act = getattr(actual, period)
                if abs(exp - act) > TOL:
                    failures.append(
                        f"{panel_key}.{row_key}.{period}: expected {exp:.4f}, got {act:.4f}"
                    )
    return failures


def write_latex_table(panels: dict[str, HeteroGoldEffects], path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "16_aggregate_heterogeneous.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_aggregate_hetero_table(panels), encoding="utf-8")
    return out


def main() -> dict[str, HeteroGoldEffects]:
    panels = run_aggregate_hetero(read_dta(A4_PATH))
    failures = validate_against_manuscript(panels)
    if failures:
        print(
            f"IA Table 16 validation failed ({len(failures)} checks):\n"
            + "\n".join(failures[:20])
        )

    else:
        print(f"IA Table 16 — all manuscript checks passed (tol={TOL})")
    for key, panel in panels.items():
        print(
            f"  {key}: baseline=({panel.baseline.y1933:.2f}, {panel.baseline.y1934:.2f}, "
            f"{panel.baseline.after:.2f})"
        )

    out_path = write_latex_table(panels)
    print(f"  Wrote LaTeX table -> {out_path}")
    return panels


if __name__ == "__main__":
    main()
