"""
Internet Appendix Table 11 — Constraints triple interactions (Stata A17_sizecashlev.do).
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
from lib.constraints import DISPLAY_TERMS, MODEL_ORDER, run_models

# Full coef validation: pyfixest vs reghdfe with triple interactions (see DISCREPANCIES).
STRICT_TERMS = ["var_Q"]
from lib.io import read_dta
from lib.render_constraints_tex import render_constraints_table

TERM_TO_MANUSCRIPT = {
    "var_Q": "Q",
    "d": r"\ensuremath{\tilde{d}}",
    "d_x": r"\ensuremath{\tilde{d}} \ensuremath{\times \text{ I}}",
    "y1933_x": r"1933 \ensuremath{\times \text{ I}}",
    "y1934_x": r"1934 \ensuremath{\times \text{ I}}",
    "After_x": r"After \ensuremath{\times \text{ I}}",
    "d_1933": r"1933 \ensuremath{\times \tilde{d}}",
    "d_1934": r"1934 \ensuremath{\times \tilde{d}}",
    "d_After": r"After \ensuremath{\times \tilde{d}}",
    "d_1933_x": r"1933 \ensuremath{\times \tilde{d} \times \text{I}}",
    "d_1934_x": r"1934 \ensuremath{\times \tilde{d} \times \text{I}}",
    "d_After_x": r"After \ensuremath{\times \tilde{d} \times \text{I}}",
}


def load_panel():
    return read_dta(A4_PATH)


def _parse_manuscript(tex_path: Path) -> dict[str, list[float | None]]:
    text = tex_path.read_text(encoding="utf-8")
    rows: dict[str, list[float | None]] = {}

    for line in text.splitlines():
        if "&" not in line:
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) != 4:
            continue
        raw = parts[0].strip()
        if not raw or raw.startswith("("):
            continue

        key = None
        # Match longer labels first (d_x before d).
        for term, label in sorted(TERM_TO_MANUSCRIPT.items(), key=lambda x: -len(x[1])):
            if term == "var_Q" and raw.strip().startswith("Q"):
                key = term
                break
            if label in raw:
                key = term
                break
        if r"R^2" in raw or r"\ensuremath{R^2}" in raw:
            key = "_r2"
        elif "Observations" in raw:
            key = "_N"
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
    parsed = _parse_manuscript(MANUSCRIPT_APPENDIX_TABLES / "11_constraints.tex")
    checks: list[tuple[str, float, float]] = []

    for col_idx, col_key in enumerate(MODEL_ORDER):
        m = models[col_key]
        for term in STRICT_TERMS + ["_r2", "_N"]:
            if term not in parsed:
                continue
            expected = parsed[term][col_idx]
            if expected is None:
                continue
            if term == "_r2":
                actual = float(m._r2)
            elif term == "_N":
                actual = float(int(m._N))
            else:
                actual = float(m.coef()[term])
            checks.append((f"{col_key}.{term}", expected, actual))

    return checks


def write_latex_table(models: dict[str, object], path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "11_constraints.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_constraints_table(models), encoding="utf-8")
    return out


def main() -> dict[str, object]:
    models = run_models(load_panel())
    checks = validate_against_manuscript(models)

    def _tol(name: str) -> float:
        return 0.01 if name.endswith("._r2") else COEF_TOLERANCE

    failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in checks
        if abs(exp - act) > _tol(name)
    ]
    if failures:
        print(
            f"IA Table 11 validation failed ({len(failures)}/{len(checks)} checks):\n"
            + "\n".join(failures[:20])
        )

    else:
        print(
        f"IA Table 11 — {len(checks)} strict checks passed "
        f"(Q, R², N; tol={COEF_TOLERANCE}). "
        f"Other coefs not validated (triple-interaction FE collinearity)."
    )
    out_path = write_latex_table(models)
    print(f"  Wrote LaTeX table -> {out_path}")
    return models


if __name__ == "__main__":
    main()
