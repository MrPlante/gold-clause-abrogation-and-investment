"""Quarter-specific dividend regressions (Stata quarterly-div / IA Table 12)."""

from __future__ import annotations

import pandas as pd
import pyfixest as pf

from config import MONTHLY_DIV_PATH, OMITTED_YEAR
from lib.io import read_dta
from lib.regressions import year_interaction_cols
from lib.winsor import PANDAS_QUANTILE_METHOD, winsorize_by

CLUSTER_PERMNO = {"CRV1": "permno"}

MODEL_ORDER = ["annual", "Q1", "Q2", "Q3", "Q4"]


def build_quarterly_panel(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Aggregate monthly dividends to firm-quarters and construct ``cashrat_q``."""
    raw = read_dta(MONTHLY_DIV_PATH) if df is None else df.copy()
    raw["year_int"] = raw["year"].astype(int)
    raw["month_int"] = raw["month"].astype(int)
    raw["quarter"] = (raw["month_int"] - 1) // 3 + 1
    raw["yq"] = raw["year_int"] * 10 + raw["quarter"]

    quarterly = (
        raw.groupby(["permno", "year_int", "quarter", "yq"], as_index=False)
        .agg(
            cashdiv_q=("cashdiv", "sum"),
            denom=("denom", "first"),
            d=("d", "first"),
            var_Q=("var_Q", "first"),
            cashrat=("cashrat", "first"),
        )
    )

    d_year_cols = [c for c in raw.columns if c.startswith("d_year_")]
    annual_dvars = raw.drop_duplicates(subset=["permno", "year_int"])[
        ["permno", "year_int"] + d_year_cols
    ]
    quarterly = quarterly.merge(annual_dvars, on=["permno", "year_int"], how="left")

    pos_denom = quarterly["denom"] > 0
    quarterly["cashrat_q"] = 0.0
    quarterly.loc[pos_denom, "cashrat_q"] = (
        quarterly.loc[pos_denom, "cashdiv_q"] / quarterly.loc[pos_denom, "denom"]
    )
    quarterly = winsorize_by(
        quarterly, ["cashrat_q"], by="yq", method=PANDAS_QUANTILE_METHOD
    )
    return quarterly.dropna(subset=["cashrat_q", "var_Q", "d"]).copy()


def _overhang_formula(dep: str) -> str:
    dy = year_interaction_cols("d")
    return f"{dep} ~ var_Q + d + {' + '.join(dy)} | permno + year_int"


def run_models(qreg: pd.DataFrame | None = None) -> dict[str, object]:
    panel = build_quarterly_panel() if qreg is None else qreg
    annual = panel.drop_duplicates(subset=["permno", "year_int"]).copy()
    dy = year_interaction_cols("d")

    models: dict[str, object] = {}
    with __import__("warnings").catch_warnings():
        __import__("warnings").simplefilter("ignore")
        models["annual"] = pf.feols(
            _overhang_formula("cashrat"),
            data=annual,
            vcov=CLUSTER_PERMNO,
        )
        fml_q = f"cashrat_q ~ var_Q + d + {' + '.join(dy)} | permno + year_int"
        for q in (1, 2, 3, 4):
            qdf = panel.loc[panel["quarter"] == q].drop_duplicates(
                subset=["permno", "year_int"]
            )
            models[f"Q{q}"] = pf.feols(fml_q, data=qdf, vcov=CLUSTER_PERMNO)

    return models
