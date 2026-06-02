"""Bond statistics for Table 2 (Stata A6_bondstats.do)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from config import A1_BOND_PATH, A4_PATH
from lib.io import read_dta, require_file

BOND_SAMPLE_YEAR_LO = 1930
BOND_SAMPLE_YEAR_HI = 1935
BOND_TABLE_YEARS = range(1930, 1935)


@dataclass
class BondYearStats:
    year: int
    n_firms: int
    n_firms_gold: int
    n_bonds: int
    n_bonds_gold: int
    mean_d: float
    median_d: float
    rho_d1930: float


def _prepare_a4(df: pd.DataFrame) -> pd.DataFrame:
    out = df[(df["year"] >= BOND_SAMPLE_YEAR_LO) & (df["year"] <= BOND_SAMPLE_YEAR_HI)].copy()
    for col in ("fd_amount", "fd_amount_g0", "fd_amount_g1"):
        out[col] = out[col].fillna(0)
    out["bond_1930"] = np.where(out["year"] == 1930, (out["fd_amount"] > 0).astype(float), np.nan)
    return out


def _tsfill(a4: pd.DataFrame) -> pd.DataFrame:
    years = np.arange(BOND_SAMPLE_YEAR_LO, BOND_SAMPLE_YEAR_HI + 1)
    grid = pd.MultiIndex.from_product(
        [a4["permno"].unique(), years],
        names=["permno", "year"],
    ).to_frame(index=False)
    filled = grid.merge(a4, on=["permno", "year"], how="left")
    filled["there_1935"] = np.where(
        filled["year"] == 1935,
        filled["inv_rate"].notna().astype(float),
        np.nan,
    )
    filled["ind_bond_1930"] = filled.groupby("permno")["bond_1930"].transform("mean")
    filled["ind_there_1935"] = filled.groupby("permno")["there_1935"].transform("mean")
    return filled


def _prepare_bondlevel(df: pd.DataFrame) -> pd.DataFrame:
    out = df[df["year"].between(BOND_SAMPLE_YEAR_LO, BOND_SAMPLE_YEAR_HI)].copy()
    if "AmountOutstanding" in out.columns and "Amount" not in out.columns:
        out = out.rename(columns={"AmountOutstanding": "Amount"})
    return out


def build_bond_panel(
    a4: pd.DataFrame | None = None,
    bondlevel: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Replicate A6 sample construction.

    Returns (merged bond-level panel, firm-year panel after duplicates drop).
    """
    if a4 is None:
        require_file(A4_PATH, "A4 merged panel")
        a4 = read_dta(A4_PATH)
    if bondlevel is None:
        require_file(A1_BOND_PATH, "A1 bond-level data")
        bondlevel = read_dta(A1_BOND_PATH)

    filled = _tsfill(_prepare_a4(a4))
    panel = filled[
        (filled["ind_bond_1930"] == 1)
        & (filled["ind_there_1935"] == 1)
        & (filled["fd_amount"] > 0)
    ].copy()

    bonds = _prepare_bondlevel(bondlevel)
    merged = panel.merge(bonds, on=["permno", "year"], how="left")
    merged = merged[merged["inv_rate"].notna()].copy()

    merged["d_year"] = merged["fd_amount_g1"] / merged["ll_bs_new"]
    merged.loc[merged["d_year"] > 1, "d_year"] = 1
    merged.loc[merged["ll_bs_new"] == 0, "d_year"] = 0

    firm_year = merged.drop_duplicates(["permno", "year"])
    return merged, firm_year


def compute_bond_stats(
    a4: pd.DataFrame | None = None,
    bondlevel: pd.DataFrame | None = None,
) -> list[BondYearStats]:
    """Yearly bond statistics matching manuscript Table 2 (1930–1934)."""
    merged, firm_year = build_bond_panel(a4, bondlevel)

    d1930 = (
        firm_year.loc[firm_year["year"] == 1930, ["permno", "d_year"]]
        .set_index("permno")["d_year"]
    )

    rows: list[BondYearStats] = []
    for year in BOND_TABLE_YEARS:
        fy = firm_year[firm_year["year"] == year]
        bond_y = merged[merged["year"] == year]
        tmp = fy[["permno", "d_year"]].copy()
        tmp["d1930"] = tmp["permno"].map(d1930)
        rows.append(
            BondYearStats(
                year=year,
                n_firms=int(fy["permno"].nunique()),
                n_firms_gold=int((fy["d_year"] > 0).sum()),
                n_bonds=int(len(bond_y)),
                n_bonds_gold=int((bond_y["gold_ind"] == 1).sum()),
                mean_d=float(fy["d_year"].mean()),
                median_d=float(fy["d_year"].median()),
                rho_d1930=float(tmp["d_year"].corr(tmp["d1930"])),
            )
        )
    return rows
