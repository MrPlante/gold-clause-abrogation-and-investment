"""Regression helpers mirroring Stata reghdfe."""

from __future__ import annotations

import pyfixest as pf

from config import CLUSTER, OMITTED_YEAR, SAMPLE_YEARS
from lib.vcov import attach_cluster_vcov


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


def feols_clustered(
    fml: str,
    data,
    *,
    winsor_cols: list[str] | None = None,
    **kwargs,
):
    """``feols`` with two-way cluster vcov and the CGM PSD fix.

    Coefficient-only consumers (Table 8 / IA.18 aggregations, Figure 6's
    predecessor). Printed standard errors come from the reghdfe do-files in
    ``analysis/stata/`` instead (lib.stata_reg; DISCREPANCIES.md D-023).
    """
    model = pf.feols(fml, data=data, vcov=CLUSTER, **kwargs)
    return attach_cluster_vcov(model)


def fit_overhang(
    df,
    exposure: str = "d",
    sample=None,
    dep: str = "var_inv_rate",
    controls: tuple[str, ...] = ("var_Q",),
    *,
    winsor_cols: list[str] | None = None,
):
    sub = df if sample is None else df.loc[sample]
    fml = overhang_formula(dep=dep, exposure=exposure, controls=controls)
    return feols_clustered(fml, sub, winsor_cols=winsor_cols)


def fit_classic(df, sample=None, dep: str = "var_inv_rate"):
    sub = df if sample is None else df.loc[sample]
    fml = f"{dep} ~ var_Q | permno + year"
    return feols_clustered(fml, sub)
