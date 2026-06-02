"""Market cap from CRSP monthly (Stata A2_marcap.do)."""

import pandas as pd

from config import A2_PATH, CRSP_MONTHLY_PATH
from lib.io import read_dta, require_file, write_dta


def build_marcap() -> pd.DataFrame:
    require_file(CRSP_MONTHLY_PATH, "crsp_monthly.dta")
    df = read_dta(CRSP_MONTHLY_PATH)

    df = df.rename(
        columns={
            "PERMNO": "permno",
            "SICCD": "sic",
            "PRC": "prc",
            "SHROUT": "shrout",
        }
    )
    df["shrout"] = df["shrout"] * 1e3
    df.loc[df["prc"] < 0, "prc"] = -df.loc[df["prc"] < 0, "prc"]
    df["marcap"] = df["prc"] * df["shrout"]

    if "date" in df.columns:
        df["month"] = pd.to_datetime(df["date"]).dt.month
        df["year"] = pd.to_datetime(df["date"]).dt.year
    else:
        raise KeyError("crsp_monthly.dta must contain a date column")

    df = df.dropna(subset=["marcap"])
    min_month = df.groupby(["permno", "year"])["month"].transform("min")
    out = df.loc[df["month"] == min_month, ["permno", "year", "month", "prc", "shrout", "marcap", "sic"]]
    write_dta(out, A2_PATH)
    return out
