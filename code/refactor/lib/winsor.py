"""Winsorization (Stata winsor2 by-group via _pctile)."""

import numpy as np
import pandas as pd

from config import WINSOR_BY, WINSOR_CUTS

# Stata winsor2 / _pctile (empirically matches annual manuscript tables).
STATA_QUANTILE_METHOD = "inverted_cdf"
# Pandas default; used for IA Table 12 quarterly panel (Seb quarterly-div.py).
PANDAS_QUANTILE_METHOD = "linear"


def _pctile(values: np.ndarray, q: float, method: str = STATA_QUANTILE_METHOD) -> float:
    x = values[~np.isnan(values)]
    if len(x) == 0:
        return np.nan
    return float(np.quantile(x, q, method=method))


def _winsorize_series(
    series: pd.Series,
    lo_q: float,
    hi_q: float,
    method: str = STATA_QUANTILE_METHOD,
) -> pd.Series:
    arr = series.to_numpy(dtype=float)
    valid = ~np.isnan(arr)
    if not valid.any():
        return series
    lo = _pctile(arr[valid], lo_q, method=method)
    hi = _pctile(arr[valid], hi_q, method=method)
    out = arr.copy()
    out[valid] = np.clip(arr[valid], lo, hi)
    return pd.Series(out, index=series.index)


def winsorize_by(
    df: pd.DataFrame,
    cols: list[str],
    by: str = WINSOR_BY,
    cuts: tuple[float, float] = WINSOR_CUTS,
    method: str = STATA_QUANTILE_METHOD,
) -> pd.DataFrame:
    out = df.copy()
    lo_q, hi_q = cuts

    for col in cols:
        out[col] = out.groupby(by, observed=True)[col].transform(
            lambda s, l=lo_q, h=hi_q, m=method: _winsorize_series(s, l, h, method=m)
        )
    return out
