"""Sample restrictions and derived indicators."""

import pandas as pd

from config import UNRELIABLE_PERMNO


def drop_unreliable_permnos(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[~df["permno"].isin(UNRELIABLE_PERMNO)].copy()


def drop_excluded_industries(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    sic = out["sic"].fillna(0)
    sic2 = (sic // 100).astype(int)
    mask = ((sic2 >= 40) & (sic2 <= 49)) | ((sic2 >= 60) & (sic2 <= 69))
    return out.loc[~mask]


def restrict_analysis_years(df: pd.DataFrame) -> pd.DataFrame:
    lo, hi = SAMPLE_YEARS
    return df.loc[(df["year"] >= lo) & (df["year"] <= hi)].copy()


def bond_repurchase_firms_1933_1934(firm_bond: pd.DataFrame) -> set[int]:
    """Firms with a decrease in total identified gold debt (1933 or 1934 vs prior year)."""
    reps: set[int] = set()
    for yr in (1933, 1934):
        cur = firm_bond.loc[firm_bond["year"] == yr].set_index("permno")["fd_amount_g1"]
        prev = firm_bond.loc[firm_bond["year"] == yr - 1].set_index("permno")["fd_amount_g1"]
        for permno in cur.index.intersection(prev.index):
            if cur[permno] < prev[permno] and prev[permno] > 0:
                reps.add(int(permno))
    return reps
