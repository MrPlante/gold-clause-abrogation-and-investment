"""Internet Appendix summary tables with full distributions (Stata A14)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

BASE_VARIABLES: list[tuple[str, str]] = [
    ("var_inv_rate", "Net investment"),
    ("var_Q", "Tobin's Q"),
    ("var_logasset", "log(Assets)"),
    ("var_netinc", "Net income/assets"),
    ("var_cash", "Cash/assets"),
    ("var_payout", "Payout/common stock"),
    ("var_booklev", "Book leverage"),
    ("var_marketlev", "Market leverage"),
    ("var_logltl", "log(LTL)"),
    ("var_cbltl", "Corp. bonds/LTL"),
    ("var_psltl", "Pref. share/LTL"),
    ("var_bdltl", "Bank debt/LTL"),
]

PANEL_PERIODS = {
    "A": (1926, 1932),
    "B": (1933, 1934),
    "C": (1935, 1940),
}


@dataclass
class DistributionStats:
    n_firms: int
    n_obs: int
    mean: float
    std: float
    p5: float
    p25: float
    p50: float
    p75: float
    p95: float


@dataclass
class DistributionRow:
    label: str
    var: str
    stats: DistributionStats


@dataclass
class DistributionPanel:
    panel: str
    year_lo: int
    year_hi: int
    rows: list[DistributionRow]


def _stata_quantile(values: pd.Series, q: float) -> float:
    """Match Stata ``summarize, detail`` percentile definitions."""
    x = values.dropna().to_numpy()
    if len(x) == 0:
        return float("nan")
    if q == 0.05:
        method = "lower"
    elif q == 0.95:
        method = "higher"
    else:
        method = "linear"
    return float(np.quantile(x, q, method=method))


def _distribution_stats(sub: pd.DataFrame, var: str) -> DistributionStats:
    values = sub[var]
    firms = sub["permno"].nunique()
    nonmissing = values.dropna()
    if nonmissing.empty:
        nan = float("nan")
        return DistributionStats(int(firms), 0, nan, nan, nan, nan, nan, nan, nan)

    return DistributionStats(
        n_firms=int(firms),
        n_obs=int(len(nonmissing)),
        mean=float(nonmissing.mean()),
        std=float(nonmissing.std()),
        p5=_stata_quantile(values, 0.05),
        p25=_stata_quantile(values, 0.25),
        p50=_stata_quantile(values, 0.50),
        p75=_stata_quantile(values, 0.75),
        p95=_stata_quantile(values, 0.95),
    )


def compute_distribution_panel(
    df: pd.DataFrame,
    panel_key: str,
    variables: list[tuple[str, str]],
) -> DistributionPanel:
    lo, hi = PANEL_PERIODS[panel_key]
    sub = df.loc[(df["year"] >= lo) & (df["year"] <= hi)]
    rows = [
        DistributionRow(label=label, var=var, stats=_distribution_stats(sub, var))
        for var, label in variables
    ]
    return DistributionPanel(panel_key, lo, hi, rows)


def compute_distribution_table(
    df: pd.DataFrame,
    variables_by_panel: dict[str, list[tuple[str, str]]],
) -> dict[str, DistributionPanel]:
    return {
        key: compute_distribution_panel(df, key, variables_by_panel[key])
        for key in variables_by_panel
    }
