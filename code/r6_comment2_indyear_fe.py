"""
R6 Comment 2: re-run Table 6 columns 2-10 with industry×year (sic2_year) FEs.

Currently columns 2-10 use `permno + year`; this script swaps in `permno + sic2_year`
so we can report whether d, d_1933, d_1934, d_After remain significant.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import A4_PATH
from lib.controls import (
    CORE_TERMS,
    LINEAR_CONTROLS,
    PORTFOLIO_PREFIX_BY_MODEL,
    portfolio_cols,
)
from lib.io import read_dta
from lib.regressions import feols_clustered

COLS_TO_RERUN = {
    "all_controls_linear": LINEAR_CONTROLS,
    "q_deciles": None,
    "logasset_deciles": None,
    "netinc_deciles": None,
    "cash_deciles": None,
    "payout_deciles": None,
    "booklev_deciles": None,
    "marketlev_deciles": None,
    "logltl_deciles": None,
}

FE = "permno + sic2_year"


def stars(pval: float) -> str:
    if pval < 0.01:
        return "***"
    if pval < 0.05:
        return "**"
    if pval < 0.10:
        return "*"
    return ""


def run() -> None:
    df = read_dta(A4_PATH)
    print(f"Panel loaded: {len(df):,} obs\n")

    results: dict[str, object] = {}

    for key in COLS_TO_RERUN:
        if key == "all_controls_linear":
            controls = LINEAR_CONTROLS
        else:
            prefix = PORTFOLIO_PREFIX_BY_MODEL[key]
            controls = portfolio_cols(prefix)

        fml = f"var_inv_rate ~ {' + '.join(controls + CORE_TERMS)} | {FE}"
        print(f"Fitting {key} ...", flush=True)
        results[key] = feols_clustered(fml, df)

    # Print summary table
    header = f"{'Column':<22}" + "".join(f"{t:>18}" for t in CORE_TERMS)
    print("\n" + "=" * (22 + 18 * len(CORE_TERMS)))
    print(f"Table 6 cols 2-10  WITH industry×year FEs (FE: {FE})")
    print("=" * (22 + 18 * len(CORE_TERMS)))
    print(header)
    print("-" * (22 + 18 * len(CORE_TERMS)))

    for key, m in results.items():
        coef_row = f"{key:<22}"
        se_row   = f"{'':22}"
        for term in CORE_TERMS:
            try:
                c = float(m.coef()[term])
                s = float(m.se()[term])
                p = float(m.pvalue()[term])
                coef_row += f"{c:>+12.4f}{stars(p):>6}"
                se_row   += f"{'(' + f'{s:.4f}' + ')':>18}"
            except Exception:
                coef_row += f"{'n/a':>18}"
                se_row   += f"{'':>18}"
        print(coef_row)
        print(se_row)
        print()


if __name__ == "__main__":
    run()
