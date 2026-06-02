"""Build accounting panel (Stata A0_accounting_data.do)."""

import pandas as pd

from config import A0_PATH, ACCOUNTING_CSV
from lib.io import require_file, write_dta
from lib.sample import drop_unreliable_permnos


def build_accounting() -> pd.DataFrame:
    require_file(ACCOUNTING_CSV, "accounting_data.csv")
    df = pd.read_csv(ACCOUNTING_CSV)
    df = drop_unreliable_permnos(df)

    df = df.sort_values(["permno", "manual_year", "year"])
    df["permno_man"] = df.groupby(["permno", "manual_year"]).ngroup()

    df = df.dropna(subset=["ppe_bs"])
    df = df.drop_duplicates(subset=["permno_man", "year"], keep=False)

    df = df.sort_values(["permno_man", "year"])
    df["Lnetppe_bs"] = df.groupby("permno_man")["netppe_bs"].shift(1)

    valid = (df["netppe_bs"] >= 0) & (df["Lnetppe_bs"] > 0)
    df["inv_rate"] = pd.NA
    df.loc[valid, "inv_rate"] = df.loc[valid, "netppe_bs"] / df.loc[valid, "Lnetppe_bs"] - 1

    bs_cols = [c for c in df.columns if c.endswith("_bs")]
    is_cols = [c for c in df.columns if c.endswith("_is")]
    for col in bs_cols + is_cols:
        df[f"L{col}"] = df.groupby("permno_man")[col].shift(1)

    df = df.dropna(subset=["inv_rate"])
    df["max_manual"] = df.groupby(["permno", "year"])["manual_year"].transform("max")
    df = df.loc[df["manual_year"] == df["max_manual"]].copy()

    write_dta(df, A0_PATH)
    return df
