"""LaTeX table formatting."""

from __future__ import annotations

import numpy as np
import pandas as pd


def stars_tex(p: float) -> str:
    if np.isnan(p):
        return ""
    if p < 0.01:
        return "\\sym{***}"
    if p < 0.05:
        return "\\sym{**}"
    if p < 0.1:
        return "\\sym{*}"
    return ""


def fmt_coef(value: float, p: float, decimals: int = 3) -> str:
    return f"{value:.{decimals}f}{stars_tex(p)}"


def fmt_se(value: float, decimals: int = 3) -> str:
    return f"({value:.{decimals}f})"


def fix_vcov(vcov: np.ndarray) -> np.ndarray:
    """Project indefinite two-way cluster vcov to PSD (pyfixest numerical fix)."""
    evals, evecs = np.linalg.eigh(vcov)
    evals = np.maximum(evals, 0.0)
    return evecs @ np.diag(evals) @ evecs.T


def model_se(model) -> pd.Series:
    """Standard errors; eigenvalue-clamp vcov when pyfixest returns NaN."""
    se = model.se().copy()
    if not se.isna().any():
        return se

    vcov = fix_vcov(model._vcov)
    names = list(model.coef().index)
    for i, name in enumerate(names):
        if pd.isna(se[name]):
            se[name] = float(np.sqrt(max(vcov[i, i], 0.0)))
    return se


def model_pvalue(model) -> pd.Series:
    """Two-sided p-values; normal approximation when pyfixest returns NaN."""
    from scipy.stats import norm

    p = model.pvalue().copy()
    se = model_se(model)
    coef = model.coef()
    for name in coef.index:
        if not pd.isna(p.get(name)) and not np.isnan(p.get(name)):
            continue
        s = se.get(name)
        c = coef.get(name)
        if s is None or c is None or pd.isna(s) or s <= 0:
            continue
        p[name] = float(2 * norm.sf(abs(c / s)))
    return p
