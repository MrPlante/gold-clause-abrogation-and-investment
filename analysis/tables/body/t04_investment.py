"""
Table 3 — Leverage and investment (manuscript tab:inv_main).

Replicates panel regressions from the original Stata A9_inv_results.do (removed from tree; git show d54b0c3:code/legacy/mete/A9_inv_results.do) with column
definitions from manuscript/tables/body/table4_investment.tex.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from config import PANEL_PATH, COEF_TOLERANCE, MANUSCRIPT_BODY_TABLES, OMITTED_YEAR, SAMPLE_YEARS
from pipeline.lib.io import read_dta
from lib.stata_reg import stata_models
from tables.render.regression_table import render_table3_latex


@dataclass
class ColumnSpec:
    label: str
    exposure: str = "d"
    sample: str = "full"


# Tolerance for the adopted cols 4-5 sample reconstructions vs the published
# table (exact definitions lost with the RFS-era A9 do-file; D-016).
RECON_TOLERANCE = 0.02


def load_panel() -> pd.DataFrame:
    return read_dta(PANEL_PATH)


def _exclude_repurchasers(df: pd.DataFrame) -> pd.Series:
    """Column 4 sample: drop firms whose gold exposure d went from positive to
    zero during the litigation window (1931-1935), i.e. firms that retired
    their gold-clause debt. This is Mete's A16_balanced.do ``repay`` flag
    (Stata: gen repay2 = 1 if d == 0 & L.d > 0 & year >= 1931 & year <= 1935),
    adopted as the closest reconstruction of the published column 4 (published
    d = -0.097, N = 5,572; this sample gives d = -0.094, N = 5,918; the
    original RFS-era do-file defining the exact sample is lost)."""
    lag = df[["permno", "year", "d"]].copy()
    lag["year"] += 1
    lag = lag.rename(columns={"d": "_Ld"})
    m = df[["permno", "year", "d"]].merge(lag, on=["permno", "year"], how="left")
    repay2 = (m["d"] == 0) & (m["_Ld"] > 0) & m["year"].between(1931, 1935)
    bad = set(m.loc[repay2.to_numpy(), "permno"])
    return ~df["permno"].isin(bad)


def _fixed_claims_exposure(df: pd.DataFrame) -> pd.Series:
    """Column 5 exposure level: Mete's original code (recovered 2026-08-22,
    D-023 addendum 2), which reproduces the published column exactly
    (d = -0.057, N = 6,048). Gold-clause debt over total fixed claims
    (bank debt + bonds + preferred stock) measured in 1930, capped at one,
    zero for firms whose average fixed claims are positive but whose 1930
    ratio is undefined; for pre-1930 years the LEVEL is the lagged share of
    bonds in fixed claims (mirroring the pre-1930 construction of the
    baseline d in pipeline/merge.py - a firm-constant level would be
    absorbed by the firm fixed effects). The year interactions use the
    panel's firm-constant dalt_year_* columns."""
    import numpy as np

    out = df.sort_values(["permno", "year"])

    def _stata_div(num: pd.Series, den: pd.Series) -> pd.Series:
        r = num / den
        return r.replace([np.inf, -np.inf], np.nan)  # Stata: x/0 is missing

    ratio30 = _stata_div(
        out["fd_amount_g1"], out["bd_bs"] + out["cb_bs"] + out["ps_bs"]
    ).where(out["year"] == 1930)
    ratio30 = ratio30.clip(upper=1.0)

    def _pos_or_missing(col: str) -> pd.Series:
        m = out.groupby("permno")[col].transform("mean")
        return m.gt(0) | m.isna()  # Stata: missing > 0 is TRUE

    m_any = _pos_or_missing("bd_bs") | _pos_or_missing("cb_bs") | _pos_or_missing("ps_bs")
    ratio30 = ratio30.where(~(ratio30.isna() & m_any & (out["year"] == 1930)), 0.0)
    level = ratio30.groupby(out["permno"]).transform("mean")
    pre = _stata_div(out["Lcb_bs"], out["Lbd_bs"] + out["Lcb_bs"] + out["Lps_bs"])
    pre = pre.where(~(pre.isna() & m_any), 0.0)
    level = level.where(out["year"] > 1930, pre)
    return level.reindex(df.index)


def run_models(df: pd.DataFrame) -> dict[str, object]:
    prepared = df.copy()
    prepared["no_maturity"] = (prepared["ind_3134_max"] != 1).astype(int)
    prepared["no_redemption"] = _exclude_repurchasers(df).astype(int).to_numpy()
    prepared["dalt"] = _fixed_claims_exposure(df).to_numpy()

    years = [y for y in range(SAMPLE_YEARS[0], SAMPLE_YEARS[1] + 1) if y != OMITTED_YEAR]
    cols = (["permno", "year", "var_inv_rate", "var_Q", "d", "ps", "bd", "dalt",
             "no_maturity", "no_redemption"]
            + [f"{stem}_year_{y}" for stem in ("d", "ps", "bd", "dalt") for y in years])
    return stata_models("table4_investment", prepared[cols])


def validate_against_manuscript(models: dict[str, object]) -> list[tuple[str, float, float]]:
    """Return list of (name, expected, actual) for key coefficients."""
    tex = MANUSCRIPT_BODY_TABLES / "table4_investment.tex"
    text = tex.read_text(encoding="utf-8")

    # Parse Q row (first numeric line after Q header)
    import re

    def _parse_row(pattern: str) -> list[float | None]:
        match = re.search(pattern, text, re.MULTILINE)
        if not match:
            return []
        row = match.group(1)
        if not row.endswith("&"):
            row = row + "&"
        cells = row.split("&")
        vals: list[float | None] = []
        for cell in cells:
            cell = re.sub(r"\\sym\{[*]+\}", "", cell).strip()
            if not cell:
                vals.append(None)
                continue
            try:
                vals.append(float(cell))
            except ValueError:
                vals.append(None)
        return vals

    q_vals = _parse_row(r"Q\s*&(.*?)\\\\")
    d_vals = _parse_row(r"\\ensuremath\{\\tilde\{d\}\}\s*&(.*?)\\\\")

    order = ["classic", "overhang", "no_maturity", "no_redemption", "fixed_claims", "pref_shares", "bank_debt"]
    # The manuscript table is generated by this builder, so all seven
    # columns validate strictly against it. Col 4 is the D-017 sample
    # reconstruction; col 5 is Mete's recovered fixed-claims exposure
    # (D-023 addendum 2, matches the published column); col 7 SEs are
    # version(5) (D-023).
    validated_indices = {0, 1, 2, 3, 4, 5, 6}
    recon_indices: set[int] = set()
    checks: list[tuple[str, float, float]] = []
    recon_checks: list[tuple[str, float, float]] = []

    for i, key in enumerate(order):
        m = models[key]
        bucket = checks if i in validated_indices else recon_checks if i in recon_indices else None
        if bucket is None:
            continue
        if i < len(q_vals) and q_vals[i] is not None:
            bucket.append((f"{key}.var_Q", q_vals[i], float(m.coef().loc["var_Q"])))
        exp_name = {"pref_shares": "ps", "bank_debt": "bd", "fixed_claims": "dalt"}.get(key, "d")
        if key != "classic" and i < len(d_vals) and d_vals[i] is not None:
            bucket.append((f"{key}.{exp_name}", d_vals[i], float(m.coef().loc[exp_name])))

    return checks, recon_checks


def write_latex_table(models: dict[str, object], path: Path | None = None) -> Path:
    out = path or (MANUSCRIPT_BODY_TABLES / "table4_investment.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_table3_latex(models), encoding="utf-8")
    return out


def main() -> dict[str, object]:
    df = load_panel()
    models = run_models(df)
    checks, recon_checks = validate_against_manuscript(models)

    failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in checks
        if abs(exp - act) > COEF_TOLERANCE
    ]
    recon_failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in recon_checks
        if abs(exp - act) > RECON_TOLERANCE
    ]
    if failures or recon_failures:
        print(
            f"WARNING: Table 3 manuscript check differences "
            f"({len(failures)} strict + {len(recon_failures)} reconstruction):\n"
            + "\n".join(failures + recon_failures)
        )
    else:
        print(
            f"Table 3 — strict checks passed (tol={COEF_TOLERANCE}); "
            f"cols 4-5 reconstructions within {RECON_TOLERANCE} of published"
        )
    for name, exp, act in checks:
        print(f"  {name}: {act:.4f} (expected {exp:.4f})")
    for name, exp, act in recon_checks:
        print(f"  [recon] {name}: {act:.4f} (published {exp:.4f})")

    out_path = write_latex_table(models)
    print(f"  Wrote LaTeX table -> {out_path}")

    return models


if __name__ == "__main__":
    main()
