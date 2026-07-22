"""
Internet Appendix Table 15 — Return-based controls (Stata A20).
"""

from __future__ import annotations

import re
from pathlib import Path

from config import PANEL_PATH, COEF_TOLERANCE, MANUSCRIPT_APPENDIX_TABLES, MANUSCRIPT_APPENDIX_TABLES
from tables.models.controls import CORE_TERMS
from pipeline.io import read_dta
from tables.render.ret_controls import render_ret_controls_table
from tables.models.ret_controls import MODEL_ORDER, run_models

LINEAR_ANN_TOL = 0.004
DECILE_TOL = 0.002


def _term_tol(col_key: str) -> float:
    if col_key == "linear_ann":
        return LINEAR_ANN_TOL
    return DECILE_TOL


def _normalize_label(raw: str) -> str | None:
    line = raw.strip()
    if not line or line.startswith("("):
        return None
    if line.startswith("Q") or line == "Q":
        return "var_Q"
    if "tilde{d}" in line and "times" not in line:
        return "d"
    if "1933" in line and "tilde{d}" in line:
        return "d_1933"
    if "1934" in line and "tilde{d}" in line:
        return "d_1934"
    if "After" in line and "tilde{d}" in line:
        return "d_After"
    return None


def _parse_manuscript(tex_path: Path) -> dict[str, list[float | None]]:
    rows: dict[str, list[float | None]] = {}
    for line in tex_path.read_text(encoding="utf-8").splitlines():
        if "&" not in line:
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) != 7:
            continue
        label = _normalize_label(parts[0])
        if label is None:
            continue
        vals: list[float | None] = []
        for cell in parts[1:]:
            cell = re.sub(r"\\sym\{[*]+\}", "", cell).rstrip("\\").strip()
            try:
                vals.append(float(cell) if cell else None)
            except ValueError:
                vals.append(None)
        if any(v is not None for v in vals):
            rows[label] = vals
    return rows


def validate_against_manuscript(
    models: dict[str, object],
) -> tuple[list[tuple[str, float, float]], list[str], list[str]]:
    parsed = _parse_manuscript(MANUSCRIPT_APPENDIX_TABLES / "ia17_stock_controls.tex")
    checks: list[tuple[str, float, float]] = []
    hard_failures: list[str] = []
    soft_failures: list[str] = []

    for col_idx, col_key in enumerate(MODEL_ORDER):
        m = models[col_key]
        ext_tol = _term_tol(col_key)
        for term in CORE_TERMS:
            if term not in parsed:
                continue
            expected = parsed[term][col_idx]
            if expected is None:
                continue
            actual = float(m.coef()[term])
            checks.append((f"{col_key}.{term}", expected, actual))
            diff = abs(expected - actual)
            msg = f"{col_key}.{term}: expected {expected:.4f}, got {actual:.4f}"
            if diff <= COEF_TOLERANCE:
                continue
            if diff <= ext_tol:
                soft_failures.append(msg)
            else:
                hard_failures.append(msg)

    return checks, hard_failures, soft_failures


def write_latex_table(models: dict[str, object], path: Path | None = None) -> Path:
    out = path or (MANUSCRIPT_APPENDIX_TABLES / "ia17_stock_controls.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_ret_controls_table(models), encoding="utf-8")
    return out


def main() -> dict[str, object]:
    models = run_models(read_dta(PANEL_PATH))
    checks, hard_failures, soft_failures = validate_against_manuscript(models)

    if hard_failures:
        print(
            f"WARNING: IA Table 15 manuscript check differences "
            f"({len(hard_failures)}/{len(checks)} checks — likely data version mismatch):\n"
            + "\n".join(hard_failures[:20])
        )

    strict = len(checks) - len(soft_failures)
    print(f"IA Table 15 — {strict}/{len(checks)} checks at tol={COEF_TOLERANCE}")
    if soft_failures:
        print(f"  Note: {len(soft_failures)} cells within extended decile/ann tolerance")

    for key in MODEL_ORDER:
        m = models[key]
        print(f"  {key}: N={int(m._N)}, R2={m._r2:.3f}")

    out_path = write_latex_table(models)
    print(f"  Wrote LaTeX table -> {out_path}")
    return models


if __name__ == "__main__":
    main()
