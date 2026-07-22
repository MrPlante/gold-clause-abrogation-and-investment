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
