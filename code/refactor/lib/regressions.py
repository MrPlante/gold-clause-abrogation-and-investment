"""Regression helpers mirroring Stata reghdfe."""

from __future__ import annotations

import pyfixest as pf

from config import CLUSTER, OMITTED_YEAR, SAMPLE_YEARS


def year_interaction_cols(prefix: str = "d") -> list[str]:
    lo, hi = SAMPLE_YEARS
    return [f"{prefix}_year_{y}" for y in range(lo, hi + 1) if y != OMITTED_YEAR]


def overhang_formula(
    dep: str = "var_inv_rate",
    exposure: str = "d",
    controls: tuple[str, ...] = ("var_Q",),
) -> str:
    rhs = list(controls) + [exposure] + year_interaction_cols(exposure)
    return f"{dep} ~ {' + '.join(rhs)} | permno + year"


def fit_overhang(
    df,
    exposure: str = "d",
    sample=None,
    dep: str = "var_inv_rate",
    controls: tuple[str, ...] = ("var_Q",),
):
    sub = df if sample is None else df.loc[sample]
    fml = overhang_formula(dep=dep, exposure=exposure, controls=controls)
    return pf.feols(fml, data=sub, vcov=CLUSTER)


def fit_classic(df, sample=None, dep: str = "var_inv_rate"):
    sub = df if sample is None else df.loc[sample]
    return pf.feols(f"{dep} ~ var_Q | permno + year", data=sub, vcov=CLUSTER)
