"""
Internet Appendix Table 14 — Extensive-margin indicators (Stata A19).
"""

from __future__ import annotations

import re
from pathlib import Path

from config import A4_PATH, COEF_TOLERANCE, MANUSCRIPT_APPENDIX_TABLES, REFACTOR_OUTPUT_TABLES_APPENDIX
from lib.indicator_investment import DISPLAY_TERMS, MODEL_ORDER, TERM_LABELS, run_models
from lib.io import read_dta
from lib.render_indicators_d_tex import render_indicators_d_table


def _parse_manuscript(tex_path: Path) -> dict[str, list[float | None]]:
    rows: dict[str, list[float | None]] = {}
    label_to_term = {v: k for k, v in TERM_LABELS.items()}

    for line in tex_path.read_text(encoding="utf-8").splitlines():
        if "&" not in line:
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) != 4:
            continue
        raw = parts[0].strip()
        if not raw or raw.startswith("("):
            continue

        key = None
        if raw.startswith("Q"):
            key = "var_Q"
        else:
            for label, term in label_to_term.items():
                if label in raw:
                    key = term
                    break
        if key is None:
            continue

        vals: list[float | None] = []
        for cell in parts[1:]:
            cell = re.sub(r"\\sym\{[*]+\}", "", cell).rstrip("\\").strip()
            try:
                vals.append(float(cell) if cell else None)
            except ValueError:
                vals.append(None)
        if any(v is not None for v in vals):
            rows[key] = vals
    return rows


def validate_against_manuscript(models: dict[str, object]) -> list[tuple[str, float, float]]:
    parsed = _parse_manuscript(MANUSCRIPT_APPENDIX_TABLES / "14_indicators_d.tex")
    checks: list[tuple[str, float, float]] = []

    for col_idx, col_key in enumerate(MODEL_ORDER):
        m = models[col_key]
        for term in DISPLAY_TERMS:
            if term not in parsed:
                continue
            expected = parsed[term][col_idx]
            if expected is None:
                continue
            actual = float(m.coef()[term])
            checks.append((f"{col_key}.{term}", expected, actual))

    return checks


def write_latex_table(models: dict[str, object], path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "14_indicators_d.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_indicators_d_table(models), encoding="utf-8")
    return out


def main() -> dict[str, object]:
    models = run_models(read_dta(A4_PATH))
    checks = validate_against_manuscript(models)
    failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in checks
        if abs(exp - act) > COEF_TOLERANCE
    ]
    if failures:
        raise AssertionError(
            f"IA Table 14 validation failed ({len(failures)}/{len(checks)} checks):\n"
            + "\n".join(failures[:20])
        )

    print(f"IA Table 14 — all {len(checks)} manuscript checks passed (tol={COEF_TOLERANCE})")
    out_path = write_latex_table(models)
    print(f"  Wrote LaTeX table -> {out_path}")
    return models


if __name__ == "__main__":
    main()
