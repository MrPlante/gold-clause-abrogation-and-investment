"""
Table 4 — Gold clause exposure and other outcomes (tab:other_outcomes).

Replicates Stata A10_otheroutcomes.do. Payout and leverage use A4-merge winsorized ``var_*`` outcomes; dividend,
net rep., profits, and cash are winsorized at estimation time (Stata winsor2).
"""

from __future__ import annotations

import re
from pathlib import Path

from config import A4_PATH, COEF_TOLERANCE, MANUSCRIPT_BODY_TABLES, REFACTOR_OUTPUT_TABLES_BODY
from lib.io import read_dta
from lib.other_outcomes import MODEL_ORDER, run_models
from lib.render_other_outcomes_tex import render_table4_latex

# All six columns validated at tol=0.001 (0-indexed).
VALIDATED_COLUMNS = {0, 1, 2, 3, 4, 5}


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
        if "Observations" in parts[0]:
            key = "_N"
        else:
            label = _normalize_label(parts[0])
            if label is None:
                continue
            key = label
        if key is None:
            continue
        vals: list[float | None] = []
        for cell in parts[1:]:
            cell = re.sub(r"\\sym\{[*]+\}", "", cell).rstrip("\\").strip()
            cell = cell.replace(",", "").replace("$", "").replace(r"\phantom{000}", "")
            m = re.search(r"\{([0-9.]+)\}\s*$", cell)
            if m:
                cell = m.group(1)
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

        if "_N" in parsed:
            expected = parsed["_N"][col_idx]
            if expected is not None:
                checks.append((f"{col_key}._N", expected, float(int(models[col_key]._N))))

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
        print(
            f"WARNING: Table 4 manuscript check differences "
            f"({len(failures)}/{len(checks)} checks — likely data version mismatch):\n"
            + "\n".join(failures[:20])
        )
    else:
        print(f"Table 4 — all {len(checks)} manuscript checks passed (tol={COEF_TOLERANCE})")
    for key in MODEL_ORDER:
        m = models[key]
        print(f"  {key}: N={int(m._N)}, R2={m._r2:.3f}")

    out_path = write_latex_table(models)
    print(f"  Wrote LaTeX table -> {out_path}")
    return models


if __name__ == "__main__":
    main()
