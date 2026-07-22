"""Build accounting panel (Stata A0_accounting_data.do)."""

import pandas as pd

from config import A0_PATH, ACCOUNTING_CSV
from lib.io import require_file, write_dta
from lib.sample import drop_unreliable_permnos


def _calendar_lag(df: pd.DataFrame, group: str, col: str) -> pd.Series:
    """Stata ``L.col`` under ``xtset {group} year``: value at year-1 within the
    group, not the previous observed row."""
    lag = df[[group, "year", col]].copy()
    lag["year"] += 1
    lag = lag.rename(columns={col: "_lagval"})
    out = df[[group, "year"]].merge(lag, on=[group, "year"], how="left")
    return pd.Series(out["_lagval"].to_numpy(), index=df.index)


def build_accounting() -> pd.DataFrame:
    require_file(ACCOUNTING_CSV, "accounting_data.csv")
    df = pd.read_csv(ACCOUNTING_CSV)
    # Stata `import delimited` lowercases variable names (PPE_BS -> ppe_bs)
    df.columns = df.columns.str.lower()
    df = drop_unreliable_permnos(df)

    df = df.sort_values(["permno", "manual_year", "year"])
    df["permno_man"] = df.groupby(["permno", "manual_year"]).ngroup() + 1

    # Stata: duplicates within permno_man x year all have ppe_bs missing,
    # so `drop if ppe_bs == .` also removes every duplicate.
    df = df.dropna(subset=["ppe_bs"])

    df = df.sort_values(["permno_man", "year"]).reset_index(drop=True)
    df["Lnetppe_bs"] = _calendar_lag(df, "permno_man", "netppe_bs")

    valid = (df["netppe_bs"] >= 0) & (df["Lnetppe_bs"] > 0)
    df["inv_rate"] = float("nan")
    df.loc[valid, "inv_rate"] = df.loc[valid, "netppe_bs"] / df.loc[valid, "Lnetppe_bs"] - 1

    # Stata: bys permno_man year: egen cc = count(year) — recomputed after the
    # ppe drop, all 1 (no duplicates remain); the column stays in the file.
    df["cc"] = df.groupby(["permno_man", "year"])["year"].transform("count").astype(float)

    bs_cols = [c for c in df.columns if c.endswith("_bs") and c != "Lnetppe_bs"]
    is_cols = [c for c in df.columns if c.endswith("_is")]
    for col in bs_cols + is_cols:
        if col == "netppe_bs":
            continue  # Lnetppe_bs already computed above
        if pd.api.types.is_numeric_dtype(df[col]):
            df[f"L{col}"] = _calendar_lag(df, "permno_man", col)
        else:
            # Stata's `gen L`v' = L.`v'` on string vars yields an all-missing
            # float column; reproduce that.
            df[f"L{col}"] = float("nan")

    df = df.dropna(subset=["inv_rate"])
    df["max_manual"] = df.groupby(["permno", "year"])["manual_year"].transform("max")
    df = df.loc[df["manual_year"] == df["max_manual"]].copy()

    write_dta(df, A0_PATH)
    return df
