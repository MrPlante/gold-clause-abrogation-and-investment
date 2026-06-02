"""Table 4 sample prep and regressions (Stata A10_otheroutcomes.do)."""

from __future__ import annotations

import pandas as pd

from lib.regressions import fit_overhang
from lib.winsor import winsorize_by

# Column keys match manuscript order.
MODEL_ORDER = [
    "payout",
    "cashrat",
    "netrep",
    "nippe",
    "cashppe",
    "leverage",
]

DEP_BY_MODEL = {
    "payout": "var_payout",
    "cashrat": "cashrat",
    "netrep": "netrep",
    "nippe": "nippe",
    "cashppe": "cashppe",
    "leverage": "var_booklev",
}


def prepare_panel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build Table 4 variables following A10_otheroutcomes.do.

    Payout uses ``var_payout`` (winsorized at A4 merge), matching the manuscript.
    Dividend and net rep. are winsorized here; profits and cash use net PPE in 1930.
    Leverage uses ``var_booklev`` (winsorized at A4 merge).
    """
    out = df.copy()
    out = winsorize_by(out, ["cashrat", "netrep"])

    out["denom2"] = out["netppe_bs"].where(out["year"] <= out["min_year"])
    out["denom"] = out.groupby("permno")["denom2"].transform("mean")
    out["cashppe"] = out["cash_bs"] / out["denom"]
    out["nippe"] = out["ni_is"] / out["denom"]
    out = winsorize_by(out, ["cashppe", "nippe"])
    return out


def run_models(df: pd.DataFrame) -> dict[str, object]:
    panel = prepare_panel(df)
    return {
        key: fit_overhang(panel, exposure="d", dep=DEP_BY_MODEL[key])
        for key in MODEL_ORDER
    }
