"""Additional dividend specifications (Stata A18_additionaldividend.do)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from lib.regressions import feols_clustered
from lib.winsor import winsorize_by

MODEL_ORDER = [
    "cashrat_lag_pos",
    "cashrat_lag_zero",
    "cashrat_divind_pos",
    "cashrat_divind_zero",
    "divgr",
    "divbeq",
    "divy",
    "divshare",
]

BUCKET_TERMS = ["d_1933", "d_1934", "d_After"]


def prepare_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Build dividend outcomes and sample indicators (A18)."""
    out = df.sort_values(["permno", "year"]).copy()
    out = winsorize_by(out, ["payout", "cashrat", "netrep"])

    out["divind2"] = (out["cashrat"] > 0).where(out["year"] == 1932)
    out["divind"] = out.groupby("permno")["divind2"].transform("mean").fillna(0)

    out["Lcashrat"] = out.groupby("permno")["cashrat"].shift(1)
    out["Lcashdiv"] = out.groupby("permno")["cashdiv"].shift(1)

    out["divgr"] = out["cashdiv"] / out["Lcashdiv"] - 1
    out.loc[(out["Lcashdiv"] == 0) & (out["cashdiv"] == 0), "divgr"] = 0
    out.loc[out["divgr"].abs() == np.inf, "divgr"] = np.nan

    out["divbeq"] = (out["cashdiv"] - out["netissue"]) / out["Lbeq_bs"]
    out["marcap2"] = out["marcap"].where(out["year"] == out["min_year"])
    out["marcap_base"] = out.groupby("permno")["marcap2"].transform("mean")
    out["divy"] = (out["cashdiv"] - out["netissue"]) / out["marcap_base"]

    mask = out["ni_is"] > out["cashdiv"]
    out["divshare"] = ((out["cashdiv"] - out["netissue"]) / out["ni_is"]).where(mask)

    out = winsorize_by(out, ["divgr", "divbeq", "divy", "divshare"])
    return out


def _bucket_formula(dep: str, q_control: str = "var_Q") -> str:
    rhs = [q_control, "d"] + BUCKET_TERMS
    return f"{dep} ~ {' + '.join(rhs)} | permno + year"


def run_models(df: pd.DataFrame) -> dict[str, object]:
    panel = prepare_panel(df)
    models: dict[str, object] = {}

    specs = [
        ("cashrat_lag_pos", "cashrat", panel["Lcashrat"] > 0),
        ("cashrat_lag_zero", "cashrat", panel["Lcashrat"] == 0),
        ("cashrat_divind_pos", "cashrat", panel["divind"] == 1),
        ("cashrat_divind_zero", "cashrat", panel["divind"] == 0),
        ("divgr", "divgr", slice(None)),
        ("divbeq", "divbeq", slice(None)),
        ("divy", "divy", slice(None)),
        ("divshare", "divshare", slice(None)),
    ]

    for key, dep, sample in specs:
        sub = panel if sample is slice(None) else panel.loc[sample]
        q = "Q" if key == "divshare" else "var_Q"
        models[key] = feols_clustered(_bucket_formula(dep, q_control=q), sub)

    return models
