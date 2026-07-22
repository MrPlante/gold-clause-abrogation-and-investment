"""Data pipeline orchestration (Stata A0–A4)."""

from __future__ import annotations

from pathlib import Path

from config import A1_BOND_PATH, A4_PATH, ACCOUNTING_CSV, GOLD_CLAUSES_XLSX
from pipeline.a0_accounting import build_accounting
from pipeline.a1_bonds import build_bond_data
from pipeline.a2_marcap import build_marcap
from pipeline.a3_dividend import build_dividend
from pipeline.a4_merge import build_merged
from pipeline.io import read_dta, roundtrip_dta, write_dta


def build_all() -> Path:
    """
    Run A0–A4 from data/raw/ and write the two pipeline outputs to
    data/processed/: A4_merged.dta and A1_bond_data_bondlevel.dta (the
    bond-level panel Table 3 reads directly).

    The remaining A0–A3 stages are held in memory; each is round-tripped
    through the .dta format (in an in-memory buffer) before the merge so
    dtypes match the historical on-disk intermediates and the A4 build stays
    verified-exact.
    """
    if not ACCOUNTING_CSV.exists() or not GOLD_CLAUSES_XLSX.exists():
        raise FileNotFoundError(
            "Raw files missing in data/raw/. "
            "Add accounting_data.csv and gold_clauses.xlsx."
        )
    accounting = roundtrip_dta(build_accounting())
    bond, firm = build_bond_data()
    write_dta(bond, A1_BOND_PATH)
    firm = roundtrip_dta(firm)
    marcap = roundtrip_dta(build_marcap())
    _monthly, annual = build_dividend()
    annual = roundtrip_dta(annual)

    build_merged(accounting, firm, marcap, annual)
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
