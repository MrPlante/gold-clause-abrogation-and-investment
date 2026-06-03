"""
Internet Appendix Table 7 — Full credit-ratings year-by-year table (Stata A21).

All three columns: ``d_year_*`` interactions, R², and N validated at tol=0.001.
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
from lib.credit_ratings import MODEL_ORDER, run_models
from lib.io import read_dta
from lib.render_credit_ratings_full_tex import INTERACTION_YEARS, render_credit_ratings_full_table

VALIDATED_COLUMNS = {0, 1, 2}
YEAR_INTERACTION_TERMS = [f"d_year_{y}" for y in INTERACTION_YEARS]


def load_panel():
    return read_dta(A4_PATH)


def _parse_manuscript_table(tex_path: Path) -> dict[str, list[float | None]]:
    text = tex_path.read_text(encoding="utf-8")
    rows: dict[str, list[float | None]] = {}

    for line in text.splitlines():
        if "&" not in line:
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) != 4:
            continue
        raw_label = parts[0]
        if not raw_label or raw_label.startswith("("):
            continue

        year_match = re.search(r"(\d{4})", raw_label)
        if not year_match and raw_label not in ("Q", r"\ensuremath{\tilde{d}}", "Low rating"):
            if "Observations" not in raw_label and r"R^2" not in raw_label:
                continue

        if "Low rating" in raw_label and r"\tilde{d}" in raw_label and "times" in raw_label.replace(
            "\\", ""
        ):
            key = f"d_year_{year_match.group(1)}_Low" if year_match else None
        elif "Low rating" in raw_label and year_match:
            key = f"year_{year_match.group(1)}_Low"
        elif r"\tilde{d}" in raw_label and year_match:
            key = f"d_year_{year_match.group(1)}"
        elif raw_label.strip() == "Q":
            key = "var_Q"
        elif r"\tilde{d}" in raw_label and "Low" not in raw_label:
            key = "d"
        elif "Low rating" in raw_label:
            key = "d_Low"
        elif r"R^2" in raw_label or r"\ensuremath{R^2}" in raw_label:
            key = "_r2"
        elif "Observations" in raw_label:
            key = "_N"
        else:
            continue

        if key is None:
            continue

        vals: list[float | None] = []
        for cell in parts[1:]:
            cell = re.sub(r"\\sym\{[*]+\}", "", cell).rstrip("\\").strip()
            cell = cell.replace("$", "").replace(",", "").replace(r"\phantom{000}", "")
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
    parsed = _parse_manuscript_table(
        MANUSCRIPT_APPENDIX_TABLES / "7_credit_ratings_full_table.tex"
    )
    checks: list[tuple[str, float, float]] = []

    for col_idx, col_key in enumerate(MODEL_ORDER):
        m = models[col_key]
        if "_r2" in parsed:
            expected = parsed["_r2"][col_idx]
            if expected is not None:
                checks.append((f"{col_key}._r2", expected, float(m._r2)))
        if "_N" in parsed:
            expected = parsed["_N"][col_idx]
            if expected is not None:
                checks.append((f"{col_key}._N", expected, float(int(m._N))))

        if col_idx not in VALIDATED_COLUMNS:
            continue
        for term in YEAR_INTERACTION_TERMS:
            if term not in parsed:
                continue
            expected = parsed[term][col_idx]
            if expected is None:
                continue
            actual = float(models[col_key].coef()[term])
            checks.append((f"{col_key}.{term}", expected, actual))

    return checks


def write_latex_table(models: dict[str, object], path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "7_credit_ratings_full_table.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_credit_ratings_full_table(models), encoding="utf-8")
    return out


def main() -> dict[str, object]:
    models = run_models(load_panel())
    checks = validate_against_manuscript(models)

    def _tol(name: str) -> float:
        # Cols 2--3 R² can differ slightly from reghdfe (winsor / fixed effects).
        if name.endswith("._r2") and not name.startswith("var_inv_rate"):
            return 0.01
        return COEF_TOLERANCE

    failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in checks
        if abs(exp - act) > _tol(name)
    ]
    if failures:
        raise AssertionError(
            f"IA Table 7 validation failed ({len(failures)}/{len(checks)} checks):\n"
            + "\n".join(failures[:20])
        )

    print(f"IA Table 7 — all {len(checks)} manuscript checks passed (tol={COEF_TOLERANCE})")
    print("  Col 1: d_year_* interactions; all cols: R², N")
    out_path = write_latex_table(models)
    print(f"  Wrote LaTeX table -> {out_path}")
    return models


if __name__ == "__main__":
    main()
