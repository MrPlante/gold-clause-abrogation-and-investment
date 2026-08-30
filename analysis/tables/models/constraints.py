"""Firm-characteristic triple interactions (Stata A17_sizecashlev.do)."""

from __future__ import annotations

import pandas as pd
from lib.stata_reg import stata_models

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
    from pipeline.lib.winsor import STATA_QUANTILE_METHOD

    x = values.dropna().to_numpy()
    if len(x) == 0:
        return float("nan")
    return float(np.quantile(x, q, method=STATA_QUANTILE_METHOD))


def prepare_firm_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Corrected A17_sizecashlev.do (Mete, 2026-08: `if year == min_year`
    restored on the gen lines).

    The cutoff is the Stata summarize,detail median of the variable over
    min-year observations of d>0 firms. Each firm is classified 0/1 at its
    min year (1930 or first year thereafter); firms with no min-year
    observation are dropped. The original do-file lacked the min-year
    condition on the indicator, yielding a fraction-of-years measure; the
    round-1 table was built from that version (see revision summary).
    Stata missing semantics: missing < p50 is FALSE, missing > p50 is TRUE.
    """
    out = df.copy()
    at_base = out["year"] == out["min_year"]
    for var, col, high in [
        ("var_logasset", "small", False),
        ("var_cash", "lowcash", False),
        ("var_booklev", "highlev", True),
    ]:
        base = out.loc[at_base & (out["d"] > 0), var]
        p50 = _stata_quantile(base, 0.50)
        if high:
            flag = (out[var] > p50) | out[var].isna()
        else:
            flag = out[var] < p50
        out = out.drop(columns=[col], errors="ignore")
        out[col] = flag.astype(float).where(at_base).groupby(out["permno"]).transform("mean")
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
    keep = ["permno", "year", "var_inv_rate", "var_Q", "d", "d_x", "y1933_x",
            "y1934_x", "After_x", "d_1933", "d_1934", "d_After",
            "d_1933_x", "d_1934_x", "d_After_x"]
    frames = []
    for key, ind in INDICATOR_BY_MODEL.items():
        sub = _add_interactions(panel, ind)[keep].copy()
        sub["mkey"] = key
        frames.append(sub)
    return stata_models("ia14_constraints", pd.concat(frames))
