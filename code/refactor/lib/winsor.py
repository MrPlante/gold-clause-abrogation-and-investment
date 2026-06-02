"""Winsorization (Stata winsor2 by-group)."""

import pandas as pd

from config import WINSOR_BY, WINSOR_CUTS


def winsorize_by(
    df: pd.DataFrame,
    cols: list[str],
    by: str = WINSOR_BY,
    cuts: tuple[float, float] = WINSOR_CUTS,
) -> pd.DataFrame:
    out = df.copy()
    lo_q, hi_q = cuts

    def _clip(series: pd.Series) -> pd.Series:
        lo = series.quantile(lo_q)
        hi = series.quantile(hi_q)
        return series.clip(lo, hi)

    for col in cols:
        out[col] = out.groupby(by, observed=True)[col].transform(_clip)
    return out
