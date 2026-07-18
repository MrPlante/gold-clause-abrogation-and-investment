"""Variance-covariance helpers for two-way clustered reghdfe-style inference."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

REFACTOR_ROOT = Path(__file__).resolve().parents[1]
STATA_DO = REFACTOR_ROOT / "stata" / "reghdfe_vcov.do"
DEFAULT_STATA_BIN = Path("/usr/local/stata/stata-mp")


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


def stata_bin() -> Path | None:
    env = os.environ.get("STATA_BIN")
    if env:
        p = Path(env)
        return p if p.is_file() else None
    return DEFAULT_STATA_BIN if DEFAULT_STATA_BIN.is_file() else None


def use_stata_vcov() -> bool:
    """Use Stata reghdfe vcov when enabled and Stata is on PATH."""
    mode = os.environ.get("USE_STATA_VCOV", "auto").strip().lower()
    if mode in ("0", "false", "no", "off"):
        return False
    if mode in ("1", "true", "yes", "on"):
        return stata_bin() is not None
    return stata_bin() is not None


def _parse_formula(fml: str) -> tuple[str, list[str]]:
    lhs, rest = fml.split("~", 1)
    rhs_part = rest.split("|", 1)[0]
    dep = lhs.strip()
    rhs = [t.strip() for t in rhs_part.split("+") if t.strip()]
    return dep, rhs


def fetch_vcov_stata(
    data: pd.DataFrame,
    dep: str,
    rhs: list[str],
    *,
    absorb: tuple[str, ...] = ("permno", "year"),
    cluster: tuple[str, ...] = ("permno", "year"),
    winsor_cols: list[str] | None = None,
) -> tuple[np.ndarray, list[str]]:
    """
    Run ``reghdfe`` in Stata and return the adjusted variance matrix for ``rhs``.

    Coefficients must match the pyfixest model (same absorbed FEs and clustering).
    """
    stata = stata_bin()
    if stata is None:
        raise RuntimeError("Stata executable not found (set STATA_BIN or install stata-mp).")
    if not STATA_DO.is_file():
        raise FileNotFoundError(STATA_DO)

    cols = list(dict.fromkeys([dep, *rhs, *absorb, *cluster]))
    extra = [c for c in (winsor_cols or []) if c not in cols]
    use_cols = [c for c in cols + extra if c in data.columns]
    use = data.loc[:, use_cols].copy()

    with tempfile.TemporaryDirectory(prefix="reghdfe_vcov_") as tmp:
        tmp_path = Path(tmp)
        dta_in = tmp_path / "input.dta"
        dta_vcov = tmp_path / "vcov.dta"
        dta_names = tmp_path / "coefnames.dta"
        log_path = tmp_path / "stata.log"

        use.to_stata(dta_in, write_index=False)

        def _pack(words: list[str]) -> str:
            return "|".join(words) if words else ""

        absorb_s = _pack(list(absorb))
        cluster_s = _pack(list(cluster))
        rhs_s = _pack(rhs)
        winsor_s = _pack(list(winsor_cols or []))

        cmd = [
            str(stata),
            "-b",
            "do",
            str(STATA_DO),
            str(dta_in),
            dep,
            rhs_s,
            absorb_s,
            cluster_s,
            str(dta_vcov),
            str(dta_names),
            winsor_s,
        ]
        result = subprocess.run(
            cmd, check=False, cwd=tmp_path, capture_output=True, text=True
        )
        logs = sorted(tmp_path.glob("*.log"), key=lambda p: p.stat().st_mtime)
        log_tail = logs[-1].read_text()[-6000:] if logs else result.stderr

        if result.returncode != 0 or not dta_vcov.is_file():
            raise RuntimeError(
                f"Stata vcov export failed (rc={result.returncode}).\n{log_tail}"
            )

        vcov_df = pd.read_stata(dta_vcov)
        names_df = pd.read_stata(dta_names)
        names = list(names_df["name"].astype(str))
        vcols = [c for c in vcov_df.columns if c.startswith("v")]
        return vcov_df[vcols].to_numpy(dtype=float), names


def align_vcov(
    stata_vcov: np.ndarray,
    stata_names: list[str],
    model_names: list[str],
) -> np.ndarray:
    """Map Stata ``e(V)`` (may include ``_cons``) onto pyfixest coefficient order."""
    k = len(model_names)
    out = np.zeros((k, k), dtype=float)
    idx = {n: i for i, n in enumerate(stata_names)}
    for i, ni in enumerate(model_names):
        if ni not in idx:
            continue
        si = idx[ni]
        for j, nj in enumerate(model_names):
            if nj not in idx:
                continue
            sj = idx[nj]
            out[i, j] = stata_vcov[si, sj]
    return out


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
    data: pd.DataFrame,
    *,
    dep: str | None = None,
    rhs: list[str] | None = None,
    winsor_cols: list[str] | None = None,
) -> object:
    """
    Attach reghdfe-compatible vcov to a pyfixest model.

    When ``USE_STATA_VCOV`` is enabled and Stata is available, runs ``reghdfe``;
    otherwise applies the CGM eigenvalue fix to pyfixest's vcov.
    """
    names = list(model.coef().index)
    if dep is None or rhs is None:
        dep_parsed, rhs_parsed = _parse_formula(model._fml)
        dep = dep or dep_parsed
        rhs = rhs or rhs_parsed

    if use_stata_vcov():
        v_st, st_names = fetch_vcov_stata(
            data, dep, rhs, winsor_cols=winsor_cols
        )
        patch_model_vcov(model, align_vcov(v_st, st_names, names))
    else:
        patch_model_vcov(model, fix_vcov(model._vcov))
    return model


def model_se(model) -> pd.Series:
    """Standard errors from (possibly Stata-adjusted) vcov."""
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
