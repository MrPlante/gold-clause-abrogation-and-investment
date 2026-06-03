"""
Table 5 — Gold clause exposure, investment, and payout by credit rating.

Replicates Stata A21_ratings_yearbyyear.do (not A11_ratings.do, which uses a
different interaction parameterization). Both columns validated against the manuscript at tol=0.001.
"""

from __future__ import annotations

import re
from pathlib import Path

from config import A4_PATH, COEF_TOLERANCE, MANUSCRIPT_BODY_TABLES, REFACTOR_OUTPUT_TABLES_BODY
from lib.credit_ratings import TABLE5_MODEL_ORDER, run_models
from lib.io import read_dta
from lib.render_credit_ratings_tex import DISPLAY_ROWS, render_table5_latex

# Both columns validated at tol=0.001 (0-indexed).
VALIDATED_COLUMNS = {0, 1}


def load_panel():
    return read_dta(A4_PATH)


def _parse_manuscript_table(tex_path: Path) -> dict[str, list[float | None]]:
    text = tex_path.read_text(encoding="utf-8")
    rows: dict[str, list[float | None]] = {}

    for line in text.splitlines():
        if "&" not in line:
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) != 3:
            continue
        raw_label = parts[0]
        if not raw_label or raw_label.startswith("("):
            continue
        year_match = re.search(r"(\d{4})", raw_label)
        if not year_match:
            continue
        year = year_match.group(1)
        if "Low rating" in raw_label and r"\tilde{d}" in raw_label:
            key = f"d_year_{year}_Low"
        elif "Low rating" in raw_label:
            key = f"year_{year}_Low"
        elif r"\tilde{d}" in raw_label:
            key = f"d_year_{year}"
        else:
            continue

        vals: list[float | None] = []
        for cell in parts[1:]:
            cell = re.sub(r"\\sym\{[*]+\}", "", cell).rstrip("\\").strip()
            if not cell:
                vals.append(None)
                continue
            try:
                vals.append(float(cell))
            except ValueError:
                vals.append(None)
        if any(v is not None for v in vals):
            rows[key] = vals
    return rows


def validate_against_manuscript(models: dict[str, object]) -> list[tuple[str, float, float]]:
    parsed = _parse_manuscript_table(MANUSCRIPT_BODY_TABLES / "5_credit_ratings.tex")
    checks: list[tuple[str, float, float]] = []

    for col_idx, col_key in enumerate(TABLE5_MODEL_ORDER):
        if col_idx not in VALIDATED_COLUMNS:
            continue
        for _label, term in DISPLAY_ROWS:
            if term not in parsed:
                continue
            expected = parsed[term][col_idx]
            if expected is None:
                continue
            actual = float(models[col_key].coef()[term])
            checks.append((f"{col_key}.{term}", expected, actual))

    return checks


def write_latex_table(models: dict[str, object], path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_BODY / "5_credit_ratings.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_table5_latex(models), encoding="utf-8")
    return out


def main() -> dict[str, object]:
    models = run_models(load_panel())
    checks = validate_against_manuscript(models)

    failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in checks
        if abs(exp - act) > COEF_TOLERANCE
    ]
    if failures:
        raise AssertionError(
            f"Table 5 validation failed ({len(failures)}/{len(checks)} checks):\n"
            + "\n".join(failures)
        )

    print(f"Table 5 — all {len(checks)} manuscript checks passed (tol={COEF_TOLERANCE})")
    for key in TABLE5_MODEL_ORDER:
        m = models[key]
        print(f"  {key}: N={int(m._N)}, R2={m._r2:.3f}")

    out_path = write_latex_table(models)
    print(f"  Wrote LaTeX table -> {out_path}")
    return models


if __name__ == "__main__":
    main()
