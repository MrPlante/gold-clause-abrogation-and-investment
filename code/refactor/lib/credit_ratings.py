"""Table 5 sample prep and regressions (Stata A21_ratings_yearbyyear.do)."""

from __future__ import annotations

import pandas as pd
import pyfixest as pf

from config import CLUSTER, OMITTED_YEAR, SAMPLE_YEARS
from lib.winsor import winsorize_by

MODEL_ORDER = ["var_inv_rate", "cashrat"]

DEP_BY_MODEL = {
    "var_inv_rate": "var_inv_rate",
    "cashrat": "cashrat",
}


def prepare_panel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build Table 5 panel following A21_ratings_yearbyyear.do.

    Winsorizes payout/cashrat/netrep, demeans ``d`` among firms with ``d > 0``,
    then rebuilds d-based interaction terms. ``year_*_Low`` from A4 is unchanged
    (does not depend on ``d``). ``d_year_1932`` is omitted (collinear with year FE).
    """
    out = df.copy()
    out = winsorize_by(out, ["payout", "cashrat", "netrep"])

    d_mean = out.loc[out["d"] > 0, "d"].mean()
    out["d"] = out["d"] - d_mean
    out["d_Low"] = out["d"] * out["rating_ind"]

    lo, hi = SAMPLE_YEARS
    for yr in range(lo, hi + 1):
        if yr == OMITTED_YEAR:
            continue
        out[f"d_year_{yr}"] = out["d"] * out[f"year_{yr}"]
        out[f"d_year_{yr}_Low"] = out["d"] * out[f"year_{yr}"] * out["rating_ind"]
    return out


def ratings_formula(dep: str) -> str:
    lo, hi = SAMPLE_YEARS
    dy = [f"d_year_{y}" for y in range(lo, hi + 1) if y != OMITTED_YEAR]
    yl = [f"year_{y}_Low" for y in range(lo, hi + 1) if y != OMITTED_YEAR]
    dyl = [f"d_year_{y}_Low" for y in range(lo, hi + 1) if y != OMITTED_YEAR]
    rhs = ["var_Q", "d", "d_Low"] + dy + yl + dyl
    return f"{dep} ~ {' + '.join(rhs)} | permno + year"


def run_models(df: pd.DataFrame) -> dict[str, object]:
    panel = prepare_panel(df)
    return {
        key: pf.feols(ratings_formula(DEP_BY_MODEL[key]), data=panel, vcov=CLUSTER)
        for key in MODEL_ORDER
    }
