"""Preferred-equity and bond issuer subsample (Stata A14 dalt blocks).

The shipped IA.10/IA.11 were built with the RFS-era ``dalt``: denominator
``cb_bs + ps_bs`` (preferred equity + corporate bonds, NO bank debt) and no
zero-backfills — literally the "preferred equity and bond issuers" of the
table title. The panel's stored ``dalt`` column is the later Oct-2025
variant (``bd+cb+ps`` denominator, has_debt backfills), which selects a
different sample (486 vs 452 firms in Panel A). Reconstructed here from
panel columns; sample counts verified exact against the shipped tables in
all three panels (D-021 addendum).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline.lib.io import read_dta
from config import PANEL_PATH


def load_dalt_panel(path=None) -> pd.DataFrame:
    df = read_dta(path or PANEL_PATH)

    # 1930 firm-level exposure: gold-clause debt over preferred + bonds
    denom30 = df["cb_bs"] + df["ps_bs"]
    d1930 = np.where(
        (df["year"] == 1930) & (denom30 > 0),
        df["fd_amount_g1"] / denom30,
        np.nan,
    )
    d1930 = np.where(d1930 > 1, 1.0, d1930)
    df["_dalt_1930"] = d1930
    dalt = df.groupby("permno")["_dalt_1930"].transform("mean")

    # pre-1930 rows: lagged composition, same denominator convention
    ldenom = df["Lcb_bs"] + df["Lps_bs"]
    dalt_all = np.where(ldenom > 0, df["Lcb_bs"] / ldenom, np.nan)
    pre = df["year"] <= 1930
    dalt = dalt.where(~pre, pd.Series(dalt_all, index=df.index))

    out = df.loc[dalt.notna()].copy()
    out["d"] = dalt.loc[out.index]
    out["dind"] = (out["d"] > 0).astype(int)
    out.drop(columns=["_dalt_1930"], inplace=True)
    return out
