#!/usr/bin/env python3
"""Compare Stata vs Python exported regression coefficients."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

COMPARE_DIR = Path(__file__).resolve().parent
STATA_CSV = COMPARE_DIR / "output" / "stata_regressions.csv"
PYTHON_CSV = COMPARE_DIR / "output" / "python_regressions.csv"
REPORT_MD = COMPARE_DIR / "output" / "comparison_report.md"

COEF_TOL = 1e-3
SE_TOL = 1e-3
N_TOL = 0
R2_TOL = 1e-3
PVAL_TOL = 1e-2


def _load(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run export step first.")
    df = pd.read_csv(path)
    for col in ("table", "model", "term"):
        df[col] = df[col].astype(str)
    return df


def compare(stata: pd.DataFrame, python: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    key = ["table", "model", "term"]
    merged = stata.merge(
        python,
        on=key,
        how="outer",
        suffixes=("_stata", "_python"),
        indicator=True,
    )

    both = merged["_merge"] == "both"
    merged["coef_diff"] = merged["coef_python"] - merged["coef_stata"]
    merged["se_diff"] = merged["se_python"] - merged["se_stata"]
    merged["N_diff"] = merged["N_python"] - merged["N_stata"]
    merged["r2_diff"] = merged["r2_python"] - merged["r2_stata"]

    merged["coef_match"] = both & (merged["coef_diff"].abs() <= COEF_TOL)
    merged["se_match"] = both & (merged["se_diff"].abs() <= SE_TOL)
    merged["N_match"] = both & (merged["N_diff"].abs() <= N_TOL)
    merged["r2_match"] = both & (merged["r2_diff"].abs() <= R2_TOL)

    stats = {
        "stata_rows": len(stata),
        "python_rows": len(python),
        "both": int(both.sum()),
        "stata_only": int((merged["_merge"] == "left_only").sum()),
        "python_only": int((merged["_merge"] == "right_only").sum()),
        "coef_fail": int(both.sum() - merged.loc[both, "coef_match"].sum()),
        "se_fail": int(both.sum() - merged.loc[both, "se_match"].sum()),
        "N_fail": int(both.sum() - merged.loc[both, "N_match"].sum()),
        "r2_fail": int(both.sum() - merged.loc[both, "r2_match"].sum()),
    }
    return merged, stats


def _format_failures(merged: pd.DataFrame, limit: int = 40) -> list[str]:
    lines: list[str] = []
    both = merged["_merge"] == "both"
    bad = both & ~merged["coef_match"]
    for _, row in merged.loc[bad].head(limit).iterrows():
        lines.append(
            f"- `{row['table']}.{row['model']}.{row['term']}`: "
            f"coef stata={row['coef_stata']:.6f} python={row['coef_python']:.6f} "
            f"(diff={row['coef_diff']:+.6f})"
        )
    if bad.sum() > limit:
        lines.append(f"- ... and {int(bad.sum()) - limit} more coefficient mismatches")
    return lines


def write_report(merged: pd.DataFrame, stats: dict, path: Path) -> None:
    both = merged["_merge"] == "both"
    n_ok = int(merged.loc[both, "coef_match"].sum()) if both.any() else 0
    lines = [
        "# Stata vs Python regression comparison",
        "",
        f"- Stata rows: {stats['stata_rows']}",
        f"- Python rows: {stats['python_rows']}",
        f"- Matched keys: {stats['both']}",
        f"- Coefficients within tol {COEF_TOL}: **{n_ok}/{stats['both']}**",
        f"- Coefficient mismatches: {stats['coef_fail']}",
        f"- SE mismatches (tol {SE_TOL}): {stats['se_fail']}",
        f"- N mismatches: {stats['N_fail']}",
        f"- R² mismatches (tol {R2_TOL}): {stats['r2_fail']}",
        f"- Stata-only terms: {stats['stata_only']}",
        f"- Python-only terms: {stats['python_only']}",
        "",
    ]

    if stats["coef_fail"]:
        lines.append("## Largest coefficient differences")
        lines.append("")
        sub = merged.loc[both].copy()
        sub["abs_coef_diff"] = sub["coef_diff"].abs()
        for _, row in sub.nlargest(15, "abs_coef_diff").iterrows():
            lines.append(
                f"- `{row['table']}.{row['model']}.{row['term']}`: "
                f"diff={row['coef_diff']:+.6f} "
                f"(stata={row['coef_stata']:.6f}, python={row['coef_python']:.6f}, "
                f"N stata={row['N_stata']:.0f} python={row['N_python']:.0f})"
            )
        lines.append("")
        lines.append("## All coefficient mismatches (first 40)")
        lines.append("")
        lines.extend(_format_failures(merged))
        lines.append("")

    n_only = merged.loc[both & ~merged["N_match"], ["table", "model", "term", "N_stata", "N_python"]]
    if len(n_only):
        lines.append("## N count mismatches (sample)")
        lines.append("")
        for (table, model), grp in n_only.groupby(["table", "model"]):
            r = grp.iloc[0]
            lines.append(
                f"- `{table}.{model}`: stata N={r['N_stata']:.0f}, python N={r['N_python']:.0f}"
            )
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare Stata and Python regression exports")
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="Exit with code 1 if any coefficient differs beyond tolerance",
    )
    args = parser.parse_args(argv)

    stata = _load(STATA_CSV)
    python = _load(PYTHON_CSV)
    merged, stats = compare(stata, python)
    write_report(merged, stats, REPORT_MD)

    merged.to_csv(COMPARE_DIR / "output" / "comparison_merged.csv", index=False)
    print(f"Wrote {REPORT_MD}")
    print(
        f"Matched {stats['both']} terms; "
        f"{stats['coef_fail']} coef mismatches (tol={COEF_TOL})"
    )

    if args.fail_on_mismatch and stats["coef_fail"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
