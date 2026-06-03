"""Table 7 aggregate investment effects (Stata A13_aggregation.do + d1 panels)."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from config import OMITTED_YEAR, SAMPLE_YEARS
from lib.io import read_dta
from lib.regressions import feols_clustered, year_interaction_cols


@dataclass(frozen=True)
class PeriodValues:
    y1933: float
    y1934: float
    after: float


@dataclass(frozen=True)
class AggregatePanel:
    total: PeriodValues
    gold_effect: PeriodValues | None = None


def _baseline_year_betas(df: pd.DataFrame) -> dict[int, float]:
    """Year-specific d coefficients from Table 3 baseline overhang spec."""
    dy = year_interaction_cols("d")
    fml = f"var_inv_rate ~ var_Q + d + {' + '.join(dy)} | permno + year"
    model = feols_clustered(fml, df)

    betas: dict[int, float] = {OMITTED_YEAR: 0.0}
    lo, hi = SAMPLE_YEARS
    for year in range(lo, hi + 1):
        term = f"d_year_{year}"
        if term in model.coef().index:
            betas[year] = float(model.coef()[term])
    return betas


def _prepare_flows(df: pd.DataFrame) -> pd.DataFrame:
    """Construct net-PPE flows and lagged capital (Stata ``netppe``, ``Lnetppe_new``)."""
    out = df.copy()
    out["netppe"] = out["netppe_bs"]
    out["Lnetppe_new"] = out["netppe"] / (1 + out["var_inv_rate"])
    return out


def _year_level_series(sub: pd.DataFrame, betas: dict[int, float] | None) -> pd.DataFrame:
    work = _prepare_flows(sub)
    work["sumk"] = work.groupby("year")["netppe"].transform("sum")
    work["Lsumk"] = work.groupby("year")["Lnetppe_new"].transform("sum")
    work["total_inv_rate"] = work["sumk"] / work["Lsumk"] - 1

    if betas is not None:
        work["dKlag"] = work["d"] * work["Lnetppe_new"]
        work["sum_dKlag"] = work.groupby("year")["dKlag"].transform("sum")
        work["sum_Klag"] = work.groupby("year")["Lnetppe_new"].transform("sum")
        work["w_d"] = work["sum_dKlag"] / work["sum_Klag"]
        work["beta_tv"] = work["year"].map(betas)
        work["agg_inv_d_tv"] = work["beta_tv"] * work["w_d"]

    return work.groupby("year", as_index=True).first()


def _period_values(year_df: pd.DataFrame, col: str) -> PeriodValues:
    return PeriodValues(
        y1933=float(year_df.loc[1933, col] * 100),
        y1934=float(year_df.loc[1934, col] * 100),
        after=float(year_df.loc[year_df.index >= 1935, col].mean() * 100),
    )


def _aggregate_panel(sub: pd.DataFrame, betas: dict[int, float] | None) -> AggregatePanel:
    year_df = _year_level_series(sub, betas)
    total = _period_values(year_df, "total_inv_rate")
    gold = _period_values(year_df, "agg_inv_d_tv") if betas is not None else None
    return AggregatePanel(total=total, gold_effect=gold)


def run_aggregate(df: pd.DataFrame | None = None) -> dict[str, AggregatePanel]:
    """
    Compute manuscript Table 7 panels.

    Panel A: all firms (A13_aggregation.do baseline aggregation).
    Panel B: ``d > 0`` subsample with full-sample betas (A13_aggregationd1.do).
    Panel C: ``d == 0`` subsample, total investment only.
    """
    panel = read_dta(A4_PATH) if df is None else df.copy()
    betas = _baseline_year_betas(panel)

    return {
        "all_firms": _aggregate_panel(panel, betas),
        "d_positive": _aggregate_panel(panel.loc[panel["d"] > 0], betas),
        "d_zero": _aggregate_panel(panel.loc[panel["d"] == 0], betas=None),
    }
