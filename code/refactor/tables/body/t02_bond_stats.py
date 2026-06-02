"""
Table 2 — Bond statistics (tab:bond_stats).

Replicates Stata A6_bondstats.do sample construction and year-level summaries.
Manuscript reports 1930–1934; Mete's Overleaf export includes 1935 and uses
% gold bonds instead of gold bond counts.
"""

from __future__ import annotations

from pathlib import Path

from config import COEF_TOLERANCE, MANUSCRIPT_BODY_TABLES, REFACTOR_OUTPUT_TABLES_BODY
from lib.bond_stats import BondYearStats, compute_bond_stats
from lib.render_bond_stats_tex import render_table2_latex

STAT_FIELDS = (
    "n_firms",
    "n_firms_gold",
    "n_bonds",
    "n_bonds_gold",
    "mean_d",
    "median_d",
    "rho_d1930",
)


def _parse_manuscript_table(tex_path: Path) -> dict[int, dict[str, float]]:
    text = tex_path.read_text(encoding="utf-8")
    rows: dict[int, dict[str, float]] = {}
    field_names = list(STAT_FIELDS)

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("\\") or "&" not in line:
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) != 8:
            continue
        try:
            year = int(parts[0])
        except ValueError:
            continue
        values: dict[str, float] = {}
        for name, cell in zip(field_names, parts[1:], strict=True):
            cell = cell.rstrip("\\").strip()
            values[name] = float(cell)
        rows[year] = values
    return rows


def validate_against_manuscript(rows: list[BondYearStats]) -> list[tuple[str, float, float]]:
    parsed = _parse_manuscript_table(MANUSCRIPT_BODY_TABLES / "2_bond_stats.tex")
    tol = max(COEF_TOLERANCE, 0.011)
    checks: list[tuple[str, float, float]] = []

    by_year = {r.year: r for r in rows}
    for year, expected in parsed.items():
        actual_row = by_year.get(year)
        if actual_row is None:
            continue
        for field in STAT_FIELDS:
            expected_val = expected[field]
            actual_val = float(getattr(actual_row, field))
            checks.append((f"{year}.{field}", expected_val, actual_val))

    return checks


def write_latex_table(rows: list[BondYearStats], path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_BODY / "2_bond_stats.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_table2_latex(rows), encoding="utf-8")
    return out


def main() -> list[BondYearStats]:
    rows = compute_bond_stats()
    checks = validate_against_manuscript(rows)
    tol = max(COEF_TOLERANCE, 0.011)

    failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in checks
        if abs(exp - act) > tol
    ]
    if failures:
        raise AssertionError(
            f"Table 2 validation failed ({len(failures)}/{len(checks)} checks):\n"
            + "\n".join(failures)
        )

    print(f"Table 2 — all {len(checks)} manuscript checks passed")
    for r in rows:
        print(
            f"  {r.year}: firms {r.n_firms}/{r.n_firms_gold}, "
            f"bonds {r.n_bonds}/{r.n_bonds_gold}, "
            f"mean d={r.mean_d:.2f}, rho={r.rho_d1930:.2f}"
        )

    out_path = write_latex_table(rows)
    print(f"  Wrote LaTeX table -> {out_path}")
    return rows


if __name__ == "__main__":
    main()
