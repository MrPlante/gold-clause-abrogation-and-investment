"""
Table 6 — Gold clause exposure and net investment with controls (tab:controls).

Replicates Stata A12_controls.do: industry-year FE (col 1), linear 1930 controls
(col 2), and decile portfolio controls (cols 3–10).
"""

from __future__ import annotations

import re
from pathlib import Path

from config import A4_PATH, COEF_TOLERANCE, MANUSCRIPT_BODY_TABLES, REFACTOR_OUTPUT_TABLES_BODY
from lib.controls import CORE_TERMS, MODEL_ORDER, run_models
from lib.io import read_dta
from lib.render_controls_tex import DISPLAY_TERMS, render_table6_latex


def load_panel():
    return read_dta(A4_PATH)


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


def _parse_manuscript_table(tex_path: Path) -> dict[str, list[float | None]]:
    text = tex_path.read_text(encoding="utf-8")
    rows: dict[str, list[float | None]] = {}

    for line in text.splitlines():
        if "&" not in line:
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) != 11:
            continue
        label = _normalize_label(parts[0])
        if label is None:
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
            rows[label] = vals
    return rows


def validate_against_manuscript(models: dict[str, object]) -> list[tuple[str, float, float]]:
    parsed = _parse_manuscript_table(MANUSCRIPT_BODY_TABLES / "6_controls.tex")
    checks: list[tuple[str, float, float]] = []

    for col_idx, col_key in enumerate(MODEL_ORDER):
        for term in CORE_TERMS:
            if term not in parsed:
                continue
            expected = parsed[term][col_idx]
            if expected is None:
                continue
            actual = float(models[col_key].coef()[term])
            checks.append((f"{col_key}.{term}", expected, actual))

    return checks


def write_latex_table(models: dict[str, object], path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_BODY / "6_controls.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_table6_latex(models), encoding="utf-8")
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
            f"Table 6 validation failed ({len(failures)}/{len(checks)} checks):\n"
            + "\n".join(failures[:20])
        )

    print(f"Table 6 — all {len(checks)} manuscript checks passed (tol={COEF_TOLERANCE})")
    for key in MODEL_ORDER:
        m = models[key]
        print(f"  {key}: N={int(m._N)}, R2={m._r2:.3f}")

    out_path = write_latex_table(models)
    print(f"  Wrote LaTeX table -> {out_path}")
    return models


if __name__ == "__main__":
    main()
