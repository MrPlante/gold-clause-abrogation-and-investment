"""Extensive-margin gold clause indicators (Stata A19_indicators.do)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from lib.regressions import feols_clustered

MODEL_ORDER = ["dind", "dind2", "dind3"]

DISPLAY_TERMS = [
    "var_Q",
    "dind",
    "dind2",
    "dind3",
    "d_1933",
    "d_1934",
    "d_After",
    "d2_1933",
    "d2_1934",
    "d2_After",
    "d3_1933",
    "d3_1934",
    "d3_After",
]

TERM_LABELS = {
    "var_Q": "Q",
    "dind": r"\ensuremath{(\tilde{d} > 0)}",
    "dind2": r"\ensuremath{(\tilde{d} > \tilde{d}_{0.5})}",
    "dind3": r"\ensuremath{(\tilde{d} > \tilde{d}_{0.75})}",
    "d_1933": r"1933 \ensuremath{\times (\tilde{d} > 0)}",
    "d_1934": r"1934 \ensuremath{\times (\tilde{d} > 0)}",
    "d_After": r"After \ensuremath{\times (\tilde{d} > 0)}",
    "d2_1933": r"1933 \ensuremath{\times (\tilde{d} > \tilde{d}_{0.5})}",
    "d2_1934": r"1934 \ensuremath{\times (\tilde{d} > \tilde{d}_{0.5})}",
    "d2_After": r"After \ensuremath{\times (\tilde{d} > \tilde{d}_{0.5})}",
    "d3_1933": r"1933 \ensuremath{\times (\tilde{d} > \tilde{d}_{0.75})}",
    "d3_1934": r"1934 \ensuremath{\times (\tilde{d} > \tilde{d}_{0.75})}",
    "d3_After": r"After \ensuremath{\times (\tilde{d} > \tilde{d}_{0.75})}",
}


def _stata_quantile(values: pd.Series, q: float) -> float:
    x = values.dropna().to_numpy()
    if len(x) == 0:
        return float("nan")
    return float(np.quantile(x, q, method="linear"))


def prepare_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    pos = out.loc[out["d"] > 0, "d"]
    p50 = _stata_quantile(pos, 0.50)
    p75 = _stata_quantile(pos, 0.75)
    out["dind"] = (out["d"] > 0).astype(int)
    out["dind2"] = (out["d"] >= p50).astype(int)
    out["dind3"] = (out["d"] >= p75).astype(int)

    for ind, prefix in [("dind", "d"), ("dind2", "d2"), ("dind3", "d3")]:
        out[f"{prefix}_1933"] = out[ind] * (out["year"] == 1933)
        out[f"{prefix}_1934"] = out[ind] * (out["year"] == 1934)
        out[f"{prefix}_After"] = out[ind] * (out["year"] >= 1935)
    return out


def _formula(col: int) -> str:
    if col == 1:
        rhs = ["var_Q", "dind", "d_1933", "d_1934", "d_After"]
    elif col == 2:
        rhs = [
            "var_Q",
            "dind",
            "dind2",
            "d_1933",
            "d_1934",
            "d_After",
            "d2_1933",
            "d2_1934",
            "d2_After",
        ]
    else:
        rhs = [
            "var_Q",
            "dind",
            "dind2",
            "dind3",
            "d_1933",
            "d_1934",
            "d_After",
            "d2_1933",
            "d2_1934",
            "d2_After",
            "d3_1933",
            "d3_1934",
            "d3_After",
        ]
    return f"var_inv_rate ~ {' + '.join(rhs)} | permno + year"


def run_models(df: pd.DataFrame) -> dict[str, object]:
    panel = prepare_indicators(df)
    return {
        "dind": feols_clustered(_formula(1), panel),
        "dind2": feols_clustered(_formula(2), panel),
        "dind3": feols_clustered(_formula(3), panel),
    }
