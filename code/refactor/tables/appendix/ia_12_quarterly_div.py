"""
Internet Appendix Table 12 — Quarter-specific dividend regressions.

Port of ``code/seb/quarterly-div.py`` (cluster SEs by permno only).
"""

from __future__ import annotations

import re
from pathlib import Path

from config import COEF_TOLERANCE, MANUSCRIPT_APPENDIX_TABLES, REFACTOR_OUTPUT_TABLES_APPENDIX
from lib.quarterly_dividends import MODEL_ORDER, run_models
from lib.render_quarterly_div_tex import render_quarterly_div_table

KEY_TERMS_ANNUAL = ["var_Q", "d"] + [f"d_year_{y}" for y in range(1926, 1941) if y != 1932]
KEY_TERMS_QUARTER = ["d_year_1933", "d_year_1934"]


def _normalize_label(raw: str) -> str | None:
    line = raw.strip()
    if not line or line.startswith("("):
        return None
    if line.startswith("Q") or line == "Q":
        return "var_Q"
    if "tilde{d}" in line and "times" not in line and "text{" not in line:
        return "d"
    if "times" in line:
        m = re.search(r"(\d{4})", line)
        return f"d_year_{m.group(1)}" if m else None
    return None


def _parse_manuscript(tex_path: Path) -> dict[str, list[float | None]]:
    rows: dict[str, list[float | None]] = {}
    for line in tex_path.read_text(encoding="utf-8").splitlines():
        if "&" not in line:
            continue
        parts = [p.strip() for p in line.split("&")]
        if len(parts) != 6:
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


def validate_against_manuscript(models: dict[str, object]) -> list[tuple[str, float, float]]:
    parsed = _parse_manuscript(MANUSCRIPT_APPENDIX_TABLES / "12_quarterly_div.tex")
    checks: list[tuple[str, float, float]] = []

    for col_idx, col_key in enumerate(MODEL_ORDER):
        terms = KEY_TERMS_ANNUAL if col_key == "annual" else KEY_TERMS_QUARTER
        m = models[col_key]
        for term in terms:
            if term not in parsed:
                continue
            expected = parsed[term][col_idx]
            if expected is None:
                continue
            actual = float(m.coef()[term])
            checks.append((f"{col_key}.{term}", expected, actual))

    return checks


def write_latex_table(models: dict[str, object], path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "12_quarterly_div.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_quarterly_div_table(models), encoding="utf-8")
    return out


def main() -> dict[str, object]:
    models = run_models()
    checks = validate_against_manuscript(models)
    failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in checks
        if abs(exp - act) > COEF_TOLERANCE
    ]
    if failures:
        raise AssertionError(
            f"IA Table 12 validation failed ({len(failures)}/{len(checks)} checks):\n"
            + "\n".join(failures[:20])
        )

    print(f"IA Table 12 — all {len(checks)} manuscript checks passed (tol={COEF_TOLERANCE})")
    for key in MODEL_ORDER:
        m = models[key]
        print(f"  {key}: N={int(m._N)}, R2={m._r2:.3f}")

    out_path = write_latex_table(models)
    print(f"  Wrote LaTeX table -> {out_path}")
    return models


if __name__ == "__main__":
    main()
