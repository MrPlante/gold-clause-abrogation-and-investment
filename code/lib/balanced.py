"""Balanced-panel and repayer regressions (Stata A16_balanced.do)."""

from __future__ import annotations

import pandas as pd
import pyfixest as pf

from config import CLUSTER
from lib.regressions import fit_overhang

COLUMN_ORDER = ["omit_repayer", "balanced_1930_36", "balanced_1929_40", "balanced_1926_40"]

COLUMN_LABELS = [
    ("Omit repayer", "(1)"),
    ("1930--1936", "(2)"),
    ("1929--1940", "(3)"),
    ("1926--1940", "(4)"),
]


def prepare_balanced_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["b1"] = ((out["year"] >= 1930) & (out["year"] <= 1936)).astype(int)
    out["b2"] = ((out["year"] >= 1929) & (out["year"] <= 1940)).astype(int)
    out["b3"] = ((out["year"] >= 1926) & (out["year"] <= 1940)).astype(int)
    out["b1s"] = out.groupby("permno")["b1"].transform("sum")
    out["b2s"] = out.groupby("permno")["b2"].transform("sum")
    out["b3s"] = out.groupby("permno")["b3"].transform("sum")

    out = out.sort_values(["permno", "year"])
    out["d_lag"] = out.groupby("permno", observed=True)["d"].shift(1)
    repay2 = (
        (out["d"] == 0)
        & (out["d_lag"] > 0)
        & (out["year"] >= 1931)
        & (out["year"] <= 1935)
    )
    out["repay2"] = repay2.astype(float)
    out["repay"] = out.groupby("permno")["repay2"].transform("mean").fillna(0)
    out.loc[out["repay"] > 0, "repay"] = 1.0
    return out


def sample_masks(df: pd.DataFrame) -> dict[str, pd.Series]:
    df = prepare_balanced_flags(df)
    return {
        "omit_repayer": df["repay"] == 0,
        "balanced_1930_36": df["b1s"] == 7,
        "balanced_1929_40": df["b2s"] == 12,
        "balanced_1926_40": df["b3s"] == 15,
    }


def run_models(df: pd.DataFrame) -> dict[str, object]:
    masks = sample_masks(df)
    return {key: fit_overhang(df, sample=masks[key]) for key in COLUMN_ORDER}
