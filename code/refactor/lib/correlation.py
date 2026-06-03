"""Correlation table with gold exposure (Stata A15_correlation.do)."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from scipy import stats

CORRELATION_VARIABLES: list[tuple[str, str]] = [
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


@dataclass
class CorrelationRow:
    label: str
    var: str
    rho_1926_32: float
    p_1926_32: float
    rho_1932: float
    p_1932: float


def _corr_and_p(sub: pd.DataFrame, var: str) -> tuple[float, float]:
    pair = sub[[var, "d"]].dropna()
    if len(pair) < 3:
        return float("nan"), float("nan")
    rho = float(pair[var].corr(pair["d"]))
    res = stats.linregress(pair["d"], pair[var])
    return rho, float(res.pvalue)


def compute_correlations(df: pd.DataFrame) -> list[CorrelationRow]:
    sub_a = df.loc[(df["year"] >= 1926) & (df["year"] <= 1932)]
    sub_b = df.loc[df["year"] == 1932]
    rows: list[CorrelationRow] = []
    for var, label in CORRELATION_VARIABLES:
        rho_a, p_a = _corr_and_p(sub_a, var)
        rho_b, p_b = _corr_and_p(sub_b, var)
        rows.append(CorrelationRow(label, var, rho_a, p_a, rho_b, p_b))
    return rows
