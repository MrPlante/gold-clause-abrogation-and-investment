"""Merge master analysis panel (Stata A4_merge.do)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import (
    A0_PATH,
    A1_FIRM_PATH,
    A2_PATH,
    A3_ANNUAL_PATH,
    A4_PATH,
    NETINCOME_PATH,
    OMITTED_YEAR,
    SAMPLE_YEARS,
)
from lib.io import read_dta, write_dta
from lib.sample import drop_excluded_industries, drop_unreliable_permnos
from lib.winsor import winsorize_by


def _add_year_interactions(
    df: pd.DataFrame, exposure: str, *, include_omitted_year: bool = False
) -> pd.DataFrame:
    lo, hi = SAMPLE_YEARS
    for yr in range(lo, hi + 1):
        if f"year_{yr}" not in df.columns:
            df[f"year_{yr}"] = (df["year"] == yr).astype(int)
        if yr != OMITTED_YEAR or include_omitted_year:
            df[f"{exposure}_year_{yr}"] = df[exposure] * df[f"year_{yr}"]
    return df


def _exposure_from_1930(
    df: pd.DataFrame,
    balance_num: str,
    name: str,
    *,
    cap_at_one: bool = True,
    allow_missing_gt_one: bool = False,
) -> pd.DataFrame:
    num = df[balance_num]
    denom = df["ll_bs_new"]
    lag_num = df[f"L{balance_num}"]
    lag_denom = df["Lll_bs_new"]

    base = np.where(df["year"] == 1930, num / denom, np.nan)
    base = np.where((df["year"] == 1930) & (denom == 0), 0, base)
    if cap_at_one:
        base = np.where((df["year"] == 1930) & (base > 1), 1, base)
    elif allow_missing_gt_one:
        base = np.where((df["year"] == 1930) & (base > 1), np.nan, base)

    df[f"{name}_1930"] = base
    df[name] = df.groupby("permno")[f"{name}_1930"].transform("mean")
    all_ratio = np.where(lag_denom > 0, lag_num / lag_denom, np.nan)
    df.loc[df["year"] <= 1930, name] = pd.Series(all_ratio, index=df.index)[df["year"] <= 1930]
    df[name] = df[name].fillna(0)
    # bd and ps keep the omitted-year interaction in A4 (Stata A4_merge.do does
    # not drop bd_year_1932 or ps_year_1932, unlike d_year_1932).
    return _add_year_interactions(df, name, include_omitted_year=True)


def build_merged() -> pd.DataFrame:
    df = read_dta(A0_PATH)
    firm = read_dta(A1_FIRM_PATH)
    marcap = read_dta(A2_PATH)
    div = read_dta(A3_ANNUAL_PATH)
    netinc = read_dta(NETINCOME_PATH)

    df = df.merge(firm, on=["permno", "year"], how="left")
    df = df.merge(marcap, on=["permno", "year"], how="left", suffixes=("", "_mcap"))
    if "sic" not in df.columns and "sic_mcap" in df.columns:
        df["sic"] = df["sic_mcap"]
    df = df.merge(div, on=["permno", "year"], how="left")
    df = df.drop(columns=["ni_is"], errors="ignore")
    df = df.merge(netinc, on=["permno", "year"], how="left")

    df["sic"] = df.get("sic", pd.Series(0, index=df.index)).fillna(0)
    df = drop_excluded_industries(df)
    df = drop_unreliable_permnos(df)
    df = df.dropna(subset=["inv_rate"])

    df = df.sort_values(["permno", "year"])
    df["Lta_bs"] = df.groupby("permno")["ta_bs"].shift(1)
    df["Lbeq_bs"] = df.groupby("permno")["beq_bs"].shift(1)
    # Compute component lags before filtering so gaps created by Q.notna() don't
    # cause positional shift to bridge over missing years (Stata uses pre-stored L. lags).
    for c in ("cb", "ps", "bd"):
        df[f"L{c}_bs"] = df.groupby("permno")[f"{c}_bs"].shift(1)
    df["Q"] = (df["marcap"] + df["Lta_bs"] - df["Lbeq_bs"]) / df["Lta_bs"]

    lo, hi = SAMPLE_YEARS
    df = df.loc[(df["year"] >= lo) & (df["year"] <= hi) & df["Q"].notna()].copy()

    df["ll_bs_new"] = df["cb_bs"] + df["ps_bs"] + df["bd_bs"]
    df["Lll_bs_new"] = df["Lcb_bs"] + df["Lps_bs"] + df["Lbd_bs"]

    for col in ("fd_amount", "fd_amount_g0", "fd_amount_g1"):
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # tilde{d}
    df["d_1930"] = np.where(df["year"] == 1930, df["fd_amount_g1"] / df["ll_bs_new"], np.nan)
    df.loc[(df["year"] == 1930) & (df["ll_bs_new"] == 0), "d_1930"] = 0
    df.loc[(df["year"] == 1930) & (df["d_1930"] > 1), "d_1930"] = 1
    df["d"] = df.groupby("permno")["d_1930"].transform("mean")
    df["d_all"] = np.where(df["Lll_bs_new"] > 0, df["Lcb_bs"] / df["Lll_bs_new"], np.nan)
    df.loc[df["year"] <= 1930, "d"] = df.loc[df["year"] <= 1930, "d_all"]
    df["d"] = df["d"].fillna(0)

    # Guard: Stata produces missing (.) when denominator is 0; avoid Inf in .dta
    df["dd"] = np.where(df["ll_bs_new"] > 0, df["fd_amount_g1"] / df["ll_bs_new"], np.nan)
    df["d_orig"] = df["d"]
    df.loc[(df["year"] >= 1932) & (df["year"] <= 1936), "d_orig"] = df.groupby("permno")["dd"].shift(1)
    df["d_orig"] = df["d_orig"].fillna(0)
    df = _add_year_interactions(df, "d")

    df["d_Before"] = df["d"] * (df["year"] <= 1932)
    df["d_1933"] = df["d"] * (df["year"] == 1933)
    df["d_1934"] = df["d"] * (df["year"] == 1934)
    df["d_After"] = df["d"] * (df["year"] >= 1935)

    df["rating_ind2"] = np.nan
    m30 = df["year"] == 1930
    df.loc[m30 & df["rating_med"].notna(), "rating_ind2"] = (df.loc[m30, "rating_med"] <= 5).astype(float)
    df.loc[m30 & df["rating_ind2"].isna(), "rating_ind2"] = 0
    df["rating_ind"] = df.groupby("permno")["rating_ind2"].transform("mean").fillna(0)

    df["d_Low"] = df["d"] * df["rating_ind"]
    for yr in range(lo, hi + 1):
        # Create all years (including omitted 1932) so Stata export do files
        # that create-then-drop the 1932 column work against our A4.
        df[f"d_year_{yr}_Low"] = df["d"] * (df["year"] == yr) * df["rating_ind"]
        df[f"year_{yr}_Low"] = df[f"year_{yr}"] * df["rating_ind"]

    df = _exposure_from_1930(df, "bd_bs", "bd", allow_missing_gt_one=True)
    df = _exposure_from_1930(df, "ps_bs", "ps", allow_missing_gt_one=True)

    denom_dalt = df["bd_bs"] + df["cb_bs"] + df["ps_bs"]
    df["dalt_1930"] = np.where(
        (df["year"] == 1930) & (denom_dalt > 0),
        df["fd_amount_g1"] / denom_dalt,
        np.nan,
    )
    df.loc[(df["year"] == 1930) & (df["dalt_1930"] > 1), "dalt_1930"] = 1
    for c in ("bd_bs", "cb_bs", "ps_bs"):
        df[f"m_{c[:2]}"] = df.groupby("permno")[c].transform("mean")
    has_debt = (df["m_bd"] > 0) | (df["m_cb"] > 0) | (df["m_ps"] > 0)
    df.loc[(df["year"] == 1930) & df["dalt_1930"].isna() & has_debt, "dalt_1930"] = 0
    df["dalt"] = df.groupby("permno")["dalt_1930"].transform("mean")
    _dalt_lag_denom = df["Lbd_bs"] + df["Lcb_bs"] + df["Lps_bs"]
    df["dalt_all"] = np.where(_dalt_lag_denom > 0, df["Lcb_bs"] / _dalt_lag_denom, np.nan)
    df.loc[df["dalt_all"].isna() & has_debt, "dalt_all"] = 0
    df.loc[df["year"] <= 1930, "dalt"] = df.loc[df["year"] <= 1930, "dalt_all"]
    df["ddalt"] = np.where(denom_dalt > 0, df["fd_amount_g1"] / denom_dalt, np.nan)
    df["dalt_orig"] = df["dalt"]
    df.loc[(df["year"] >= 1932) & (df["year"] <= 1936), "dalt_orig"] = df.groupby("permno")["ddalt"].shift(1)
    df["dalt_orig"] = df["dalt_orig"].fillna(0)
    df["daltind_orig"] = (df["dalt"] > 0).astype(int)
    # Stata A4_merge.do keeps dalt_year_1932 (no drop), so include it here.
    df = _add_year_interactions(df, "dalt", include_omitted_year=True)

    df["year2"] = df["year"].where(df["year"] >= 1930)
    df["min_year"] = df.groupby("permno")["year2"].transform("min")
    # Stata: gen denom2 = cs_bs if year <= min_year; bys permno: egen denom3 = mean(denom2)
    df["_cs_pre"] = df["cs_bs"].where(df["year"] <= df["min_year"])
    df["denom"] = df.groupby("permno")["_cs_pre"].transform("mean")
    df = df.drop(columns=["_cs_pre"])
    _denom_safe = df["denom"].replace(0, np.nan)
    df["cashrat"] = (df["cashdiv"] / _denom_safe).fillna(0)
    df["payout"] = ((df["cashdiv"] - df["netissue"]) / _denom_safe).fillna(0)
    df["netrep"] = ((-df["netissue"]) / _denom_safe).fillna(0)

    df["var_inv_rate"] = df["inv_rate"]
    df["var_Q"] = df["Q"]
    df["var_logasset"] = np.log(df["ta_bs"])
    df["var_netinc"] = df["ni_is"] / df["ta_bs"]
    df["var_cash"] = df["cash_bs"] / df["ta_bs"]
    df["var_payout"] = df["payout"]
    df["var_booklev"] = (df["ta_bs"] - df["beq_bs"]) / df["ta_bs"]
    df["var_marketlev"] = (df["ta_bs"] - df["beq_bs"]) / (df["ta_bs"] - df["beq_bs"] + df["marcap"])
    df["var_logltl"] = np.where(df["ll_bs_new"] > 0, np.log(df["ll_bs_new"]), 0)
    for num, var in (("cb_bs", "var_cbltl"), ("ps_bs", "var_psltl"), ("bd_bs", "var_bdltl")):
        df[var] = np.where(df["ll_bs_new"] > 0, df[num] / df["ll_bs_new"], 0)
    df["dind"] = (df["d"] > 0).astype(int)
    df["dind_orig"] = (df["d_orig"] > 0).astype(int)

    var_cols = [c for c in df.columns if c.startswith("var_")]
    df = winsorize_by(df, var_cols)

    for v in var_cols:
        base = df.loc[df["year"] == df["min_year"], ["permno", v]].drop_duplicates("permno")
        base = base.rename(columns={v: f"fix_{v}"})
        df = df.merge(base, on="permno", how="left")
        df[f"{v}_before"] = df[f"fix_{v}"] * (df["year"] < 1933)
        df[f"{v}_1933"] = df[f"fix_{v}"] * (df["year"] == 1933)
        df[f"{v}_1934"] = df[f"fix_{v}"] * (df["year"] == 1934)
        df[f"{v}_after"] = df[f"fix_{v}"] * (df["year"] > 1934)

    write_dta(df, A4_PATH)
    return df
