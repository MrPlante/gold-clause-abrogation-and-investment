"""
Internet Appendix Table 6 — Correlations with tilde-d (Stata A15_correlation.do).
"""

from __future__ import annotations

from pathlib import Path

from config import (
    A4_PATH,
    COEF_TOLERANCE,
    MANUSCRIPT_APPENDIX_TABLES,
    REFACTOR_OUTPUT_TABLES_APPENDIX,
)
from lib.correlation import CORRELATION_VARIABLES, compute_correlations
from lib.io import read_dta
from lib.render_correlation_tex import render_correlation_table

RHO_TOL = max(COEF_TOLERANCE, 0.001)
P_TOL = 0.0001


def load_panel():
    return read_dta(A4_PATH)


def _parse_manuscript(tex_path: Path) -> list[dict]:
    text = tex_path.read_text(encoding="utf-8")
    rows: list[dict] = []

    def _num(s: str) -> float | None:
        s = s.strip().replace("(", "").replace(")", "")
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None

    for line in text.splitlines():
        if "&" not in line:
            continue
        parts = [p.strip().rstrip("\\").strip() for p in line.split("&")]
        if len(parts) != 3:
            continue
        label = parts[0]
        if label in ("1926--1932", "1932", "Variable"):
            continue

        c1, c2 = _num(parts[1]), _num(parts[2])
        if label:
            rows.append({"label": label, "rho_a": c1, "rho_b": c2})
        elif rows and c1 is not None:
            rows[-1]["p_a"] = c1
            rows[-1]["p_b"] = c2

    return rows


def _label_key(label: str) -> str:
    return label.replace(r"\ ", " ").strip()


def validate_against_manuscript(rows) -> list[tuple[str, float, float]]:
    parsed = _parse_manuscript(MANUSCRIPT_APPENDIX_TABLES / "6_correlation.tex")
    computed = {_label_key(r.label): r for r in rows}
    checks: list[tuple[str, float, float]] = []

    for exp in parsed:
        key = _label_key(exp["label"])
        row = computed.get(key)
        if row is None:
            continue
        mapping = {
            "rho_1926_32": ("rho_a", row.rho_1926_32),
            "rho_1932": ("rho_b", row.rho_1932),
            "p_1926_32": ("p_a", row.p_1926_32),
            "p_1932": ("p_b", row.p_1932),
        }
        for field, (exp_key, actual) in mapping.items():
            expected = exp.get(exp_key)
            if expected is None:
                continue
            checks.append((f"{key}.{field}", float(expected), float(actual)))

    return checks


def write_latex_table(rows, path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "6_correlation.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_correlation_table(rows), encoding="utf-8")
    return out


def main():
    rows = compute_correlations(load_panel())
    checks = validate_against_manuscript(rows)

    failures = []
    for name, exp, act in checks:
        tol = P_TOL if ".p_" in name else RHO_TOL
        if abs(exp - act) > tol:
            failures.append(f"{name}: expected {exp:.6f}, got {act:.6f}")

    if failures:
        raise AssertionError(
            f"IA Table 6 (correlation) validation failed "
            f"({len(failures)}/{len(checks)} checks):\n" + "\n".join(failures[:20])
        )

    print(f"IA Table 6 (correlation) — all {len(checks)} manuscript checks passed")
    out_path = write_latex_table(rows)
    print(f"  Wrote LaTeX table -> {out_path}")
    return rows


if __name__ == "__main__":
    main()
