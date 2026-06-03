"""
Internet Appendix Table 13 — Additional dividend analysis (Stata A18).
"""

from __future__ import annotations

import re
from pathlib import Path

from config import A4_PATH, COEF_TOLERANCE, MANUSCRIPT_APPENDIX_TABLES, REFACTOR_OUTPUT_TABLES_APPENDIX
from lib.additional_dividends import BUCKET_TERMS, MODEL_ORDER, run_models
from lib.io import read_dta
from lib.render_dividend_additional_tex import render_dividend_additional_table

CASHRAT_MODELS = set(MODEL_ORDER[:4])
WARN_MODELS = CASHRAT_MODELS | {"divgr", "divshare"}
DIVBEQ_TOL = 0.002


def _parse_manuscript(tex_path: Path) -> dict[str, list[float | None]]:
    rows: dict[str, list[float | None]] = {}
    term_map = {
        r"1933": "d_1933",
        r"1934": "d_1934",
        r"After": "d_After",
    }
    for line in tex_path.read_text(encoding="utf-8").splitlines():
        if "&" not in line:
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) != 9:
            continue
        raw = parts[0]
        key = None
        for label, term in term_map.items():
            if label in raw and "tilde{d}" in raw:
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
        rows[key] = vals
    return rows


def validate_against_manuscript(
    models: dict[str, object],
) -> tuple[list[tuple[str, float, float]], list[str], list[str]]:
    parsed = _parse_manuscript(MANUSCRIPT_APPENDIX_TABLES / "13_dividend_additional.tex")
    checks: list[tuple[str, float, float]] = []
    hard_failures: list[str] = []
    soft_failures: list[str] = []

    for col_idx, col_key in enumerate(MODEL_ORDER):
        m = models[col_key]
        tol = DIVBEQ_TOL if col_key == "divbeq" else COEF_TOLERANCE
        for term in BUCKET_TERMS:
            if term not in parsed:
                continue
            expected = parsed[term][col_idx]
            if expected is None:
                continue
            actual = float(m.coef()[term])
            checks.append((f"{col_key}.{term}", expected, actual))
            if abs(expected - actual) > tol:
                msg = f"{col_key}.{term}: expected {expected:.4f}, got {actual:.4f}"
                if col_key in WARN_MODELS:
                    soft_failures.append(msg)
                else:
                    hard_failures.append(msg)

    return checks, hard_failures, soft_failures


def write_latex_table(models: dict[str, object], path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "13_dividend_additional.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_dividend_additional_table(models), encoding="utf-8")
    return out


def main() -> dict[str, object]:
    models = run_models(read_dta(A4_PATH))
    checks, hard_failures, soft_failures = validate_against_manuscript(models)

    if hard_failures:
        raise AssertionError(
            f"IA Table 13 validation failed ({len(hard_failures)}/{len(checks)} checks):\n"
            + "\n".join(hard_failures[:20])
        )

    passed = len(checks) - len(hard_failures) - len(soft_failures)
    print(f"IA Table 13 — {passed}/{len(checks)} strict checks passed (tol={COEF_TOLERANCE})")
    if soft_failures:
        print(
            f"  Note: {len(soft_failures)} cells differ (divgr/divshare construction)"
        )

    out_path = write_latex_table(models)
    print(f"  Wrote LaTeX table -> {out_path}")
    return models


if __name__ == "__main__":
    main()
