"""
Table 4 — Gold clause exposure and other outcomes (tab:other_outcomes).

Replicates Stata A10_otheroutcomes.do. Payout and leverage use A4-merge winsorized
``var_*`` outcomes; dividend and net rep. are winsorized at estimation time.
"""

from __future__ import annotations

import re
from pathlib import Path

from config import A4_PATH, COEF_TOLERANCE, MANUSCRIPT_BODY_TABLES, REFACTOR_OUTPUT_TABLES_BODY
from lib.io import read_dta
from lib.other_outcomes import MODEL_ORDER, run_models
from lib.render_other_outcomes_tex import render_table4_latex

# Columns with full manuscript match at tol=0.001 (0-indexed).
VALIDATED_COLUMNS = {0, 5}


def load_panel():
    return read_dta(A4_PATH)


def _normalize_label(raw: str) -> str | None:
    line = raw.strip()
    if not line or line.startswith("("):
        return None
    if line.startswith("Q") or line == "Q":
        return "Q"
    if "tilde{d}" in line and "times" not in line and "text{" not in line:
        return "d"
    if "times" in line or "×" in line:
        m = re.search(r"(\d{4})", line)
        return f"d_year_{m.group(1)}" if m else None
    return None


def _parse_manuscript_table(tex_path: Path) -> dict[str, list[float | None]]:
    text = tex_path.read_text(encoding="utf-8")
    rows: dict[str, list[float | None]] = {}

    for line in text.splitlines():
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


def _model_coef(models: dict[str, object], col_key: str, term: str) -> float:
    m = models[col_key]
    return float(m.coef()[term])


def validate_against_manuscript(models: dict[str, object]) -> list[tuple[str, float, float]]:
    parsed = _parse_manuscript_table(MANUSCRIPT_BODY_TABLES / "4_other_outcomes.tex")
    checks: list[tuple[str, float, float]] = []

    term_rows = ["Q", "d"] + [f"d_year_{y}" for y in range(1926, 1941) if y != 1932]

    for col_idx, col_key in enumerate(MODEL_ORDER):
        if col_idx not in VALIDATED_COLUMNS:
            continue
        for term in term_rows:
            if term not in parsed:
                continue
            expected = parsed[term][col_idx]
            if expected is None:
                continue
            actual = _model_coef(models, col_key, "var_Q" if term == "Q" else term)
            checks.append((f"{col_key}.{term}", expected, actual))

    return checks


def write_latex_table(models: dict[str, object], path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_BODY / "4_other_outcomes.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_table4_latex(models), encoding="utf-8")
    return out


def main() -> dict[str, object]:
    df = load_panel()
    models = run_models(df)
    checks = validate_against_manuscript(models)

    failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in checks
        if abs(exp - act) > COEF_TOLERANCE
    ]
    if failures:
        raise AssertionError(
            f"Table 4 validation failed ({len(failures)}/{len(checks)} checks):\n"
            + "\n".join(failures[:20])
        )

    print(f"Table 4 — all {len(checks)} manuscript checks passed (tol={COEF_TOLERANCE})")
    for key in MODEL_ORDER:
        m = models[key]
        print(f"  {key}: N={int(m._N)}, R2={m._r2:.3f}")

    out_path = write_latex_table(models)
    print(f"  Wrote LaTeX table -> {out_path}")
    return models


if __name__ == "__main__":
    main()
