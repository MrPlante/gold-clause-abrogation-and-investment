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


def _netppe_denominator(df: pd.DataFrame) -> pd.Series:
    """
    Fixed-capital denominator for ``nippe`` / ``cashppe`` (A10_otheroutcomes.do).

    Uses ``netppe_bs`` through ``min_year``. Firms with no post-1930 years have
    missing ``min_year`` in A4; Stata still includes them in the regression, so
    fall back to each firm's earliest sample year (matches manuscript N).
    """
    min_year = df["min_year"].fillna(df.groupby("permno")["year"].transform("min"))
    denom2 = df["netppe_bs"].where(df["year"] <= min_year)
    return denom2.groupby(df["permno"]).transform("mean")


def prepare_panel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build Table 4 variables following A10_otheroutcomes.do.

    Payout uses ``var_payout`` (winsorized at A4 merge), matching the manuscript.
    Dividend and net rep. are winsorized here; profits and cash use net PPE in 1930.
    Leverage uses ``var_booklev`` (winsorized at A4 merge).
    """
    out = df.copy()
    out = winsorize_by(out, ["cashrat", "netrep"])

    out["denom"] = _netppe_denominator(out)
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
