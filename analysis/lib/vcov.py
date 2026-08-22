"""Variance-covariance helpers for two-way clustered reghdfe-style inference."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

def symmetrize_vcov(vcov: np.ndarray) -> np.ndarray:
    return (vcov + vcov.T) / 2


def fix_vcov(vcov: np.ndarray) -> np.ndarray:
    """
    Cameron, Gelbach & Miller (2011) PSD adjustment, matching reghdfe ``fix_psd``.

    Symmetrize first, then zero negative eigenvalues and reconstruct.
    """
    v = symmetrize_vcov(np.asarray(vcov, dtype=float))
    evals, evecs = np.linalg.eigh(v)
    if evals.min() < 0:
        evals = evals * (evals >= 0)
        v = evecs @ np.diag(evals) @ evecs.T
    return v


def patch_model_vcov(model, vcov: np.ndarray) -> None:
    """Replace fitted vcov so ``model.se()`` / ``model.pvalue()`` use it."""
    model._vcov = np.asarray(vcov, dtype=float)
    if hasattr(model, "_se"):
        delattr(model, "_se")
    if hasattr(model, "_pvalue"):
        delattr(model, "_pvalue")
    if hasattr(model, "_tstat"):
        delattr(model, "_tstat")


def attach_cluster_vcov(
    model,
    data=None,
    *,
    dep: str | None = None,
    rhs: list[str] | None = None,
    winsor_cols: list[str] | None = None,
) -> object:
    """Apply the CGM eigenvalue fix to the pyfixest two-way cluster vcov.

    Only the coefficient-only consumers (Table 8 / IA.18 aggregations and
    ad-hoc exploration) use this path. Every manuscript table that PRINTS
    standard errors gets them from the per-table reghdfe do-files in
    ``analysis/stata/`` via lib.stata_reg (see DISCREPANCIES.md D-023); the
    old in-process Stata vcov bridge (and its USE_STATA_VCOV switch) was
    removed with D-023.
    """
    patch_model_vcov(model, fix_vcov(model._vcov))
    return model


def model_se(model) -> pd.Series:
    """Standard errors from the model vcov (pyfixest model or lib.stata_reg.StataModel)."""
    names = list(model.coef().index)
    v = fix_vcov(model._vcov)
    return pd.Series(
        {n: float(np.sqrt(max(v[i, i], 0.0))) for i, n in enumerate(names)},
        dtype=float,
    )


def model_pvalue(model) -> pd.Series:
    """Two-sided p-values using cluster df when available."""
    se = model_se(model)
    coef = model.coef()
    df_t = getattr(model, "_df_t", None)
    if df_t is None or (isinstance(df_t, float) and np.isnan(df_t)):
        df_t = 1e6
    else:
        df_t = float(df_t)
    out = {}
    for name in coef.index:
        s = se.get(name)
        c = coef.get(name)
        if s is None or c is None or pd.isna(s) or s <= 0:
            out[name] = float("nan")
        else:
            out[name] = float(2 * student_t.sf(abs(c / s), df_t))
    return pd.Series(out, dtype=float)
