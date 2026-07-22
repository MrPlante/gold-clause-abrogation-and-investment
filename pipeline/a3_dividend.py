"""Dividend and net issuance from CRSP (Stata A3_dividend.do)."""

import pandas as pd

from config import CRSP_MONTHLY_PATH
from pipeline.io import read_dta, require_file


def build_dividend() -> tuple[pd.DataFrame, pd.DataFrame]:
    require_file(CRSP_MONTHLY_PATH, "crsp_monthly.dta")
    df = read_dta(CRSP_MONTHLY_PATH)

    df = df.rename(
        columns={
            "PERMNO": "permno",
            "PRC": "prc",
            "SHROUT": "shrout",
            "CFACSHR": "cfacshr",
            "CFACPR": "cfacpr",
            "RET": "ret",
            "RETX": "retx",
        }
    )
    df = df.loc[df["prc"] != 0].copy()
    df["shrout"] = df["shrout"] * 1e3
    df.loc[df["prc"] < 0, "prc"] = -df.loc[df["prc"] < 0, "prc"]
    df["month"] = pd.to_datetime(df["date"]).dt.month
    df["year"] = pd.to_datetime(df["date"]).dt.year

    df = df.sort_values(["permno", "year", "month"])
    df["timeid"] = df.groupby(["year", "month"]).ngroup()
    df = df.sort_values(["permno", "timeid"])

    df["L_shrout"] = df.groupby("permno")["shrout"].shift(1)
    df["L_prc"] = df.groupby("permno")["prc"].shift(1)
    df["L_cfacshr"] = df.groupby("permno")["cfacshr"].shift(1)
    df["L_cfacpr"] = df.groupby("permno")["cfacpr"].shift(1)

    df.loc[df["cfacshr"] == 0, "cfacshr"] = df["L_cfacshr"]
    df.loc[df["cfacpr"] == 0, "cfacpr"] = df["L_cfacpr"]

    df["cashdiv"] = df["L_shrout"] * df["L_prc"] * (df["ret"] - df["retx"])
    df["netissue"] = (df["shrout"] * df["cfacshr"] - df["L_shrout"] * df["L_cfacshr"]) * (
        df["prc"] / df["cfacpr"] + df["L_prc"] / df["L_cfacpr"]
    ) / 2

    monthly = df[["permno", "year", "month", "cashdiv", "netissue"]].copy()
    annual = monthly.groupby(["permno", "year"], as_index=False)[["cashdiv", "netissue"]].sum()
    return monthly, annual
