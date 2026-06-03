"""Summary statistics by exposure group (manuscript Table 1)."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from scipy import stats

SPLIT_COL = "dind_orig"

VARIABLES_AB: list[tuple[str, str]] = [
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
    ("d_orig", "d"),
]

VARIABLES_C = VARIABLES_AB[:-1]  # no d row in panel C

PANELS = {
    "A": {"year_lo": 1926, "year_hi": 1932, "split": True},
    "B": {"year_lo": 1933, "year_hi": 1934, "split": True},
    "C": {"year_lo": 1935, "year_hi": 1940, "split": False},
}


@dataclass
class GroupStats:
    n_firms: int
    n_obs: int
    mean: float
    std: float


@dataclass
class VariableRow:
    label: str
    var: str
    group0: GroupStats | None
    group1: GroupStats | None
    delta_mean: float | None
    p_value: float | None


@dataclass
class PanelStats:
    panel: str
    year_lo: int
    year_hi: int
    rows: list[VariableRow]


def _group_stats(sub: pd.DataFrame, var: str, mask) -> GroupStats:
    s = sub.loc[mask, var].dropna()
    firms = sub.loc[mask, "permno"].nunique()
    return GroupStats(
        n_firms=int(firms),
        n_obs=int(len(s)),
        mean=float(s.mean()) if len(s) else float("nan"),
        std=float(s.std()) if len(s) else float("nan"),
    )


def _ttest_p(g0: pd.Series, g1: pd.Series) -> float:
    g0 = g0.dropna()
    g1 = g1.dropna()
    if len(g0) < 2 or len(g1) < 2:
        return float("nan")
    return float(stats.ttest_ind(g1, g0, equal_var=False).pvalue)


def _compute_panel_impl(
    df: pd.DataFrame,
    panel_key: str,
    *,
    panels: dict,
    split_col: str,
    variables_split: list[tuple[str, str]],
    variables_pooled: list[tuple[str, str]],
) -> PanelStats:
    cfg = panels[panel_key]
    lo, hi = cfg["year_lo"], cfg["year_hi"]
    sub = df.loc[(df["year"] >= lo) & (df["year"] <= hi)].copy()
    variables = variables_split if cfg["split"] else variables_pooled
    rows: list[VariableRow] = []

    for var, label in variables:
        if cfg["split"]:
            m0 = sub[split_col] == 0
            m1 = sub[split_col] == 1
            gs0 = _group_stats(sub, var, m0)
            gs1 = _group_stats(sub, var, m1)
            p = _ttest_p(sub.loc[m0, var], sub.loc[m1, var])
            delta = gs1.mean - gs0.mean
            rows.append(VariableRow(label, var, gs0, gs1, delta, p))
        else:
            gs = _group_stats(sub, var, pd.Series(True, index=sub.index))
            rows.append(VariableRow(label, var, gs, None, None, None))

    return PanelStats(panel_key, lo, hi, rows)


def compute_panel(df: pd.DataFrame, panel_key: str) -> PanelStats:
    return _compute_panel_impl(
        df,
        panel_key,
        panels=PANELS,
        split_col=SPLIT_COL,
        variables_split=VARIABLES_AB,
        variables_pooled=VARIABLES_C,
    )


TILDE_D_SPLIT_COL = "dind"
TILDE_D_VARIABLES = VARIABLES_C + [("d", r"\ensuremath{\tilde{d}}")]
TILDE_D_PANELS = {
    key: {**cfg, "split": True} for key, cfg in PANELS.items()
}


def compute_tilde_d_panels(df: pd.DataFrame) -> dict[str, PanelStats]:
    return {
        key: _compute_panel_impl(
            df,
            key,
            panels=TILDE_D_PANELS,
            split_col=TILDE_D_SPLIT_COL,
            variables_split=TILDE_D_VARIABLES,
            variables_pooled=TILDE_D_VARIABLES,
        )
        for key in TILDE_D_PANELS
    }


def compute_all_panels(df: pd.DataFrame) -> dict[str, PanelStats]:
    return {key: compute_panel(df, key) for key in PANELS}
