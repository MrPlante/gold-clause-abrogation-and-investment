"""Data pipeline orchestration (Stata A0–A4)."""

from __future__ import annotations

from pathlib import Path

from config import A4_PATH, ACCOUNTING_CSV, GOLD_CLAUSES_XLSX
from data.a0_accounting import build_accounting
from data.a1_bonds import build_bond_data
from data.a2_marcap import build_marcap
from data.a3_dividend import build_dividend
from data.a4_merge import build_merged
from lib.io import read_dta


def build_all(*, skip_raw: bool = False) -> Path:
    """
    Run A0–A4. Requires data/raw/accounting_data.csv and gold_clauses.xlsx
    unless skip_raw=True (uses existing A0–A3 intermediates).
    """
    if not skip_raw:
        if not ACCOUNTING_CSV.exists() or not GOLD_CLAUSES_XLSX.exists():
            raise FileNotFoundError(
                "Raw files missing in data/raw/. "
                "Add accounting_data.csv and gold_clauses.xlsx, or pass skip_raw=True."
            )
        build_accounting()
        build_bond_data()
        build_marcap()
        build_dividend()

    build_merged()
    return A4_PATH


def validate_against_reference(reference_path: Path, rtol: float = 1e-4) -> dict:
    """Compare rebuilt A4 to a reference .dta on key columns."""
    import numpy as np

    rebuilt = read_dta(A4_PATH)
    reference = read_dta(reference_path)
    keys = ["var_inv_rate", "var_Q", "d", "permno", "year"]
    merged = rebuilt[keys].merge(reference[keys], on=["permno", "year"], suffixes=("_new", "_ref"))
    report = {}
    for col in ("var_inv_rate", "var_Q", "d"):
        diff = (merged[f"{col}_new"] - merged[f"{col}_ref"]).abs()
        report[col] = {
            "max_abs_diff": float(diff.max()),
            "mean_abs_diff": float(diff.mean()),
            "match_rtol": bool((diff <= rtol).all()),
        }
    report["n_rows_new"] = len(rebuilt)
    report["n_rows_ref"] = len(reference)
    return report
