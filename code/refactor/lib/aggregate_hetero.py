"""Heterogeneous aggregate investment effects (Stata A13 rating/size extensions)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from config import OMITTED_YEAR, SAMPLE_YEARS
from lib.regressions import feols_clustered
from lib.aggregate import PeriodValues, _baseline_year_betas, _period_values, _prepare_flows
from lib.constraints import _stata_quantile
from lib.regressions import year_interaction_cols


@dataclass(frozen=True)
class HeteroGoldEffects:
    baseline: PeriodValues
    rating: PeriodValues
    size: PeriodValues



def _rating_year_betas(df: pd.DataFrame) -> tuple[dict[int, float], dict[int, float]]:
    dy = year_interaction_cols("d")
    dy_low = [
        f"d_year_{y}_Low"
        for y in range(SAMPLE_YEARS[0], SAMPLE_YEARS[1] + 1)
        if y != OMITTED_YEAR
    ]
    year_low = [
        f"year_{y}_Low"
        for y in range(SAMPLE_YEARS[0], SAMPLE_YEARS[1] + 1)
        if y != OMITTED_YEAR
    ]

    rhs = ["var_Q", "d", "d_Low"] + dy + year_low + dy_low
    model = feols_clustered(
        f"var_inv_rate ~ {' + '.join(rhs)} | permno + year",
        df,
    )
    coef = model.coef()
    betas: dict[int, float] = {OMITTED_YEAR: 0.0}
    gammas: dict[int, float] = {OMITTED_YEAR: 0.0}
    for year in range(SAMPLE_YEARS[0], SAMPLE_YEARS[1] + 1):
        bterm = f"d_year_{year}"
        gterm = f"d_year_{year}_Low"
        if bterm in coef.index:
            betas[year] = float(coef[bterm])
        if gterm in coef.index:
            gammas[year] = float(coef[gterm])
    return betas, gammas


def _firm_size_indicator(df: pd.DataFrame) -> pd.Series:
    min_year = int(df["year"].min())
    p50 = _stata_quantile(
        df.loc[(df["year"] == min_year) & (df["d"] > 0), "var_logasset"],
        0.50,
    )
    work = df[["permno", "var_logasset"]].copy()
    work["tvSB_small2"] = (work["var_logasset"] < p50).astype(float)
    work.loc[work["var_logasset"].isna(), "tvSB_small2"] = np.nan
    work["tvSB_small"] = (
        work.groupby("permno")["tvSB_small2"].transform("mean") >= 0.5
    ).astype(float)
    work.loc[work["tvSB_small2"].isna(), "tvSB_small"] = np.nan
    return work["tvSB_small"]


def _size_bin_betas(df: pd.DataFrame) -> tuple[dict[str, float], dict[str, float], pd.Series]:
    work = df.copy()
    work["tvSB_small"] = _firm_size_indicator(work)
    work["tvSB_y33"] = (work["year"] == 1933).astype(int)
    work["tvSB_y34"] = (work["year"] == 1934).astype(int)
    work["tvSB_post34"] = (work["year"] > 1934).astype(int)
    work["tvSB_d_33"] = work["d"] * work["tvSB_y33"]
    work["tvSB_d_34"] = work["d"] * work["tvSB_y34"]
    work["tvSB_d_post34"] = work["d"] * work["tvSB_post34"]
    work["tvSB_ds_33"] = work["d"] * work["tvSB_small"] * work["tvSB_y33"]
    work["tvSB_ds_34"] = work["d"] * work["tvSB_small"] * work["tvSB_y34"]
    work["tvSB_ds_post34"] = work["d"] * work["tvSB_small"] * work["tvSB_post34"]
    work["d_x_small"] = work["d"] * work["tvSB_small"]

    rhs = [
        "var_Q",
        "d",
        "d_x_small",
        "tvSB_d_33",
        "tvSB_d_34",
        "tvSB_d_post34",
        "tvSB_ds_33",
        "tvSB_ds_34",
        "tvSB_ds_post34",
    ]
    model = feols_clustered(
        f"var_inv_rate ~ {' + '.join(rhs)} | permno + year",
        work,
    )
    coef = model.coef()
    betas = {
        "1933": float(coef["tvSB_d_33"]),
        "1934": float(coef["tvSB_d_34"]),
        "after": float(coef["tvSB_d_post34"]),
    }
    gammas = {
        "1933": float(coef["tvSB_ds_33"]),
        "1934": float(coef["tvSB_ds_34"]),
        "after": float(coef["tvSB_ds_post34"]),
    }
    return betas, gammas, work["tvSB_small"]


def _aggregate_gold_series(
    sub: pd.DataFrame,
    betas: dict[int, float],
    rating_betas: dict[int, float],
    rating_gammas: dict[int, float],
    size_bin_betas: dict[str, float],
    size_bin_gammas: dict[str, float],
    size_small: pd.Series,
) -> pd.DataFrame:
    work = _prepare_flows(sub)
    work["dKlag"] = work["d"] * work["Lnetppe_new"]
    work["sum_dKlag"] = work.groupby("year")["dKlag"].transform("sum")
    work["sum_Klag"] = work.groupby("year")["Lnetppe_new"].transform("sum")
    work["w_d"] = work["sum_dKlag"] / work["sum_Klag"]

    work["beta_tv"] = work["year"].map(betas)
    work["agg_baseline"] = work["beta_tv"] * work["w_d"]

    work["dKlag_low"] = work["d"] * work["rating_ind"] * work["Lnetppe_new"]
    work["sum_dKlag_low"] = work.groupby("year")["dKlag_low"].transform("sum")
    work["w_d_low"] = work["sum_dKlag_low"] / work["sum_Klag"]
    work["beta_rat"] = work["year"].map(rating_betas)
    work["gamma_rat"] = work["year"].map(rating_gammas)
    work["agg_rating"] = work["beta_rat"] * work["w_d"] + work["gamma_rat"] * work["w_d_low"]

    work["tvSB_small"] = size_small.reindex(work.index)
    work["dKlag_small"] = work["d"] * work["tvSB_small"] * work["Lnetppe_new"]
    work["sum_dKlag_small"] = work.groupby("year")["dKlag_small"].transform("sum")
    work["w_d_small"] = work["sum_dKlag_small"] / work["sum_Klag"]

    def _bin_beta(year: int) -> float:
        if year == 1933:
            return size_bin_betas["1933"]
        if year == 1934:
            return size_bin_betas["1934"]
        if year > 1934:
            return size_bin_betas["after"]
        return 0.0

    def _bin_gamma(year: int) -> float:
        if year == 1933:
            return size_bin_gammas["1933"]
        if year == 1934:
            return size_bin_gammas["1934"]
        if year > 1934:
            return size_bin_gammas["after"]
        return 0.0

    work["beta_sz"] = work["year"].map(_bin_beta)
    work["gamma_sz"] = work["year"].map(_bin_gamma)
    work["agg_size"] = work["beta_sz"] * work["w_d"] + work["gamma_sz"] * work["w_d_small"]

    return work.groupby("year", as_index=True).first()


def _hetero_panel(
    sub: pd.DataFrame,
    betas: dict[int, float],
    rating_betas: dict[int, float],
    rating_gammas: dict[int, float],
    size_bin_betas: dict[str, float],
    size_bin_gammas: dict[str, float],
    size_small: pd.Series,
) -> HeteroGoldEffects:
    year_df = _aggregate_gold_series(
        sub,
        betas,
        rating_betas,
        rating_gammas,
        size_bin_betas,
        size_bin_gammas,
        size_small,
    )
    return HeteroGoldEffects(
        baseline=_period_values(year_df, "agg_baseline"),
        rating=_period_values(year_df, "agg_rating"),
        size=_period_values(year_df, "agg_size"),
    )


def run_aggregate_hetero(df: pd.DataFrame) -> dict[str, HeteroGoldEffects]:
    """Panel A: all firms; Panel B: ``d > 0`` with full-sample betas."""
    betas = _baseline_year_betas(df)
    rating_betas, rating_gammas = _rating_year_betas(df)
    size_bin_betas, size_bin_gammas, size_small = _size_bin_betas(df)

    return {
        "all_firms": _hetero_panel(
            df, betas, rating_betas, rating_gammas, size_bin_betas, size_bin_gammas, size_small
        ),
        "d_positive": _hetero_panel(
            df.loc[df["d"] > 0],
            betas,
            rating_betas,
            rating_gammas,
            size_bin_betas,
            size_bin_gammas,
            size_small,
        ),
    }
