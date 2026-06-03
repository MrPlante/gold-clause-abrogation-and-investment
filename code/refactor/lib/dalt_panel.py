"""Preferred-equity and bond issuer subsample (Stata A14 dalt blocks)."""

from __future__ import annotations

import pandas as pd

from lib.io import read_dta
from config import A4_PATH


def load_dalt_panel(path=None) -> pd.DataFrame:
    df = read_dta(path or A4_PATH)
    out = df.loc[df["dalt"].notna()].copy()
    out["d"] = out["dalt"]
    out["dind"] = (out["d"] > 0).astype(int)
    return out
