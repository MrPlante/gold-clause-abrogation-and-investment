"""Firm-characteristic triple interactions (Stata A17_sizecashlev.do)."""

from __future__ import annotations

import pandas as pd
from lib.regressions import feols_clustered

MODEL_ORDER = ["small", "lowcash", "highlev"]

INDICATOR_BY_MODEL = {
    "small": "small",
    "lowcash": "lowcash",
    "highlev": "highlev",
}

DISPLAY_TERMS = [
    "var_Q",
    "d",
    "d_x",
    "y1933_x",
    "y1934_x",
    "After_x",
    "d_1933",
    "d_1934",
    "d_After",
    "d_1933_x",
    "d_1934_x",
    "d_After_x",
]

TERM_LABELS = {
    "var_Q": "Q",
    "d": r"\ensuremath{\tilde{d}}",
    "d_x": r"\ensuremath{\tilde{d}} \ensuremath{\times \text{ I}}",
    "y1933_x": r"1933 \ensuremath{\times \text{ I}}",
    "y1934_x": r"1934 \ensuremath{\times \text{ I}}",
    "After_x": r"After \ensuremath{\times \text{ I}}",
    "d_1933": r"1933 \ensuremath{\times \tilde{d}}",
    "d_1934": r"1934 \ensuremath{\times \tilde{d}}",
    "d_After": r"After \ensuremath{\times \tilde{d}}",
    "d_1933_x": r"1933 \ensuremath{\times \tilde{d} \times \text{I}}",
    "d_1934_x": r"1934 \ensuremath{\times \tilde{d} \times \text{I}}",
    "d_After_x": r"After \ensuremath{\times \tilde{d} \times \text{I}}",
}


def _stata_quantile(values: pd.Series, q: float) -> float:
    import numpy as np

    x = values.dropna().to_numpy()
    if len(x) == 0:
        return float("nan")
    method = "linear"
    return float(np.quantile(x, q, method=method))


def prepare_firm_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for var, col, high in [
        ("var_logasset", "small", False),
        ("var_cash", "lowcash", False),
        ("var_booklev", "highlev", True),
    ]:
        base = out.loc[(out["year"] == out["min_year"]) & (out["d"] > 0), ["permno", var]]
        p50 = _stata_quantile(base[var], 0.50)
        firm_flag = base.copy()
        firm_flag[col] = ((firm_flag[var] > p50) if high else (firm_flag[var] < p50)).astype(int)
        out = out.drop(columns=[col], errors="ignore")
        out = out.merge(firm_flag[["permno", col]], on="permno", how="left")
        out[col] = out[col].fillna(0)
    return out


def _add_interactions(df: pd.DataFrame, ind: str) -> pd.DataFrame:
    out = df.copy()
    i = out[ind]
    y33 = (out["year"] == 1933).astype(int)
    y34 = (out["year"] == 1934).astype(int)
    ya = (out["year"] >= 1935).astype(int)
    out["d_x"] = out["d"] * i
    out["y1933_x"] = y33 * i
    out["y1934_x"] = y34 * i
    out["After_x"] = ya * i
    out["d_1933_x"] = out["d"] * y33 * i
    out["d_1934_x"] = out["d"] * y34 * i
    out["d_After_x"] = out["d"] * ya * i
    return out


def constraints_formula(ind: str) -> str:
    rhs = [
        "var_Q",
        "d",
        "d_x",
        "y1933_x",
        "y1934_x",
        "After_x",
        "d_1933",
        "d_1934",
        "d_After",
        "d_1933_x",
        "d_1934_x",
        "d_After_x",
    ]
    return f"var_inv_rate ~ {' + '.join(rhs)} | permno + year"


def run_models(df: pd.DataFrame) -> dict[str, object]:
    panel = prepare_firm_indicators(df)
    models: dict[str, object] = {}
    for key, ind in INDICATOR_BY_MODEL.items():
        sub = _add_interactions(panel, ind)
        models[key] = feols_clustered(constraints_formula(ind), sub)
    return models
