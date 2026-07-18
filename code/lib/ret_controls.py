"""Return-based investment controls (Stata A20_retcontrols.do)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from config import CHARS_ANNUAL_PATH
from lib.regressions import feols_clustered
from lib.controls import CORE_TERMS, LINEAR_CONTROLS
from lib.io import read_dta

MODEL_ORDER = [
    "linear_ann",
    "ret_mean_deciles",
    "ret_sd_deciles",
    "beta_mktrf_deciles",
    "beta_smb_deciles",
    "beta_hml_deciles",
]

ANN_VARS = [
    "ann_ret_mean",
    "ann_ret_sd",
    "ann_beta_mktrf",
    "ann_beta_smb",
    "ann_beta_hml",
]

DECILE_PREFIX_BY_MODEL = {
    "ret_mean_deciles": "fix_ann_ret_mean_port",
    "ret_sd_deciles": "fix_ann_ret_sd_port",
    "beta_mktrf_deciles": "fix_ann_beta_mktrf_port",
    "beta_smb_deciles": "fix_ann_beta_smb_port",
    "beta_hml_deciles": "fix_ann_beta_hml_port",
}

PERIODS = ("before", "1933", "1934", "after")


def _stata_astile(series: pd.Series, nq: int = 10) -> pd.Series:
    ranks = series.rank(method="average")
    n = ranks.notna().sum()
    if n == 0:
        return pd.Series(np.nan, index=series.index)
    return np.ceil(ranks / n * nq).clip(1, nq)


def ann_portfolio_cols(prefix: str) -> list[str]:
    return [f"{prefix}_{decile}{period}" for period in PERIODS for decile in range(1, 11)]


def prepare_panel(df: pd.DataFrame) -> pd.DataFrame:
    chars = read_dta(CHARS_ANNUAL_PATH)
    out = df.merge(chars, on=["permno", "year"], how="left", indicator=False)
    out = out.dropna(subset=["var_inv_rate"]).copy()

    for var in ANN_VARS:
        base = out.loc[out["year"] == out["min_year"], ["permno", var]].drop_duplicates("permno")
        base = base.rename(columns={var: f"fix_{var}"})
        out = out.merge(base, on="permno", how="left")
        out[f"{var}_before"] = out[f"fix_{var}"] * (out["year"] < 1933)
        out[f"{var}_1933"] = out[f"fix_{var}"] * (out["year"] == 1933)
        out[f"{var}_1934"] = out[f"fix_{var}"] * (out["year"] == 1934)
        out[f"{var}_after"] = out[f"fix_{var}"] * (out["year"] > 1934)

    for var in ANN_VARS:
        fix = f"fix_{var}"
        out[f"{fix}_port"] = _stata_astile(out[fix])
        for decile in range(1, 11):
            in_dec = (out[f"{fix}_port"] == decile).fillna(False).astype(int)
            out[f"{fix}_port_{decile}before"] = in_dec * (out["year"] < 1933)
            out[f"{fix}_port_{decile}1933"] = in_dec * (out["year"] == 1933)
            out[f"{fix}_port_{decile}1934"] = in_dec * (out["year"] == 1934)
            out[f"{fix}_port_{decile}after"] = in_dec * (out["year"] > 1934)

    return out


def _formula(rhs: list[str]) -> str:
    return f"var_inv_rate ~ {' + '.join(rhs)} | permno + year"


def run_models(df: pd.DataFrame) -> dict[str, object]:
    panel = prepare_panel(df)
    ann_linear = []
    for var in ANN_VARS:
        ann_linear.extend([f"{var}_before", f"{var}_1933", f"{var}_1934", f"{var}_after"])

    models: dict[str, object] = {}
    models["linear_ann"] = feols_clustered(
        _formula(LINEAR_CONTROLS + ann_linear + CORE_TERMS),
        panel,
    )

    for key, prefix in DECILE_PREFIX_BY_MODEL.items():
        models[key] = feols_clustered(
            _formula(ann_portfolio_cols(prefix) + CORE_TERMS),
            panel,
        )

    return models
