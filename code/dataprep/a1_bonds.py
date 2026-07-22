"""Build bond-level and firm-level bond panels (Stata A1_bond_data.do)."""

import numpy as np
import pandas as pd

from config import A1_BOND_PATH, A1_FIRM_PATH, GOLD_CLAUSES_XLSX
from lib.io import require_file, write_dta


RATING_MAP = {
    "C": 1,
    "Ca": 2,
    "Caa": 3,
    "B": 4,
    "Ba": 5,
    "Baa": 6,
    "A": 7,
    "Aa": 8,
    "Aaa": 9,
}


def build_bond_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    require_file(GOLD_CLAUSES_XLSX, "gold_clauses.xlsx")
    df = pd.read_excel(GOLD_CLAUSES_XLSX, sheet_name="REAL ENTRY")

    # Stata `import excel, firstrow` strips spaces/punctuation from headers
    # ("Manual Year" -> ManualYear, "Funded Debt?" -> FundedDebt, ...); the
    # do-file references the currency-notes column as NotesonCurrency.
    df.columns = ["".join(ch for ch in str(c) if ch.isalnum()) for c in df.columns]
    df = df.rename(columns={"NotesonCurrencyType": "NotesonCurrency"})

    df = df.rename(columns={"PERMNO": "permno"})
    df["permno_end"] = df["permno"].astype(str).str[5:6]
    df["permno"] = df["permno"].astype(str).str[:5]
    df.loc[df["permno_end"] != "", "permno"] = df.loc[df["permno_end"] != "", "permno"]
    df["permno"] = pd.to_numeric(df["permno"], errors="coerce")

    df["iss_year"] = pd.to_numeric(df["Dated"].astype(str).str[:4], errors="coerce")
    df["due_year"] = pd.to_numeric(df["Due"].astype(str).str[:4], errors="coerce")
    df.loc[df["ManualYear"] == 1036, "ManualYear"] = 1936
    df["year"] = df["ManualYear"] - 1

    df = df.loc[df["NotesonCurrency"].fillna("") == ""].copy()
    df.loc[
        (df["permno"] == 25822) & (df["ManualYear"] == 1935),
        "AmountOutstanding",
    ] = "2755500"
    df["AmountOutstanding"] = pd.to_numeric(
        df["AmountOutstanding"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )

    df["debt_ind"] = (df["FundedDebt"] == "Reported").astype(int)
    df["gold_ind"] = (df["Gold"] == "Reported").astype(int)
    df = df.loc[(df["debt_ind"] == 1) & df["AmountOutstanding"].notna()].copy()

    df["ind_3134"] = ((df["due_year"] >= 1931) & (df["due_year"] <= 1934)).astype(float)
    # Stata: bys permno year: egen rating_med = median(rating2) — the firm-year
    # median broadcast to every bond
    df["rating2"] = df["Rating"].map(RATING_MAP)
    df["rating_med"] = df.groupby(["permno", "year"], dropna=False)["rating2"].transform("median")

    bond = df[
        [
            "permno",
            "ManualYear",
            "gold_ind",
            "AmountOutstanding",
            "debt_ind",
            "year",
            "ind_3134",
            "rating_med",
        ]
    ].copy()
    # stable sort keeps the spreadsheet's within-group bond order, matching
    # Stata's sort + bys ... : gen bondnum = _n
    bond = bond.sort_values(["permno", "year"], kind="stable")
    # dropna=False: two bonds have missing ManualYear/year; Stata keeps them
    bond["bondnum"] = bond.groupby(["permno", "year"], dropna=False).cumcount() + 1
    bond["AO_g0"] = bond["AmountOutstanding"] * (1 - bond["gold_ind"])
    bond["AO_g1"] = bond["AmountOutstanding"] * bond["gold_ind"]
    write_dta(bond, A1_BOND_PATH)

    firm = bond.copy()
    # Stata: replace ind_3134 = 0 if missing, then
    # bys permno: egen ind_3134_max = max(ind_3134) — a FIRM-wide max across
    # all years, not a per-firm-year max
    firm["ind_3134"] = firm["ind_3134"].fillna(0)
    firm["ind_3134_max"] = firm.groupby("permno")["ind_3134"].transform("max")
    agg = firm.groupby(["permno", "ManualYear"], as_index=False, dropna=False).agg(
        fd_amount=("AmountOutstanding", "sum"),
        fd_amount_g0=("AO_g0", "sum"),
        fd_amount_g1=("AO_g1", "sum"),
        debt_ind=("debt_ind", "max"),
        year=("year", "first"),
        ind_3134_max=("ind_3134_max", "max"),
        rating_med=("rating_med", "median"),
    )
    write_dta(agg, A1_FIRM_PATH)
    return bond, agg
