#!/usr/bin/env python3
"""Export pyfixest regression results for comparison with Stata."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REFACTOR_ROOT = Path(__file__).resolve().parents[1]
if str(REFACTOR_ROOT) not in sys.path:
    sys.path.insert(0, str(REFACTOR_ROOT))

from config import A4_PATH  # noqa: E402
from lib.credit_ratings import TABLE5_MODEL_ORDER, run_models as run_table5  # noqa: E402
from lib.io import read_dta  # noqa: E402
from lib.other_outcomes import MODEL_ORDER as TABLE4_ORDER, run_models as run_table4  # noqa: E402
from lib.latex import model_pvalue, model_se  # noqa: E402
from lib.regressions import fit_classic, fit_overhang  # noqa: E402
from tables.body.t03_investment import run_models as run_table3  # noqa: E402

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_CSV = OUTPUT_DIR / "python_regressions.csv"


def _fit_to_rows(table: str, model: str, fit) -> list[dict]:
    coef = fit.coef()
    se = model_se(fit)
    pval = model_pvalue(fit)
    n = int(fit._N)
    r2 = float(fit._r2)
    rows = []
    for term in coef.index:
        rows.append(
            {
                "table": table,
                "model": model,
                "term": term,
                "coef": float(coef[term]),
                "se": float(se[term]) if term in se.index else float("nan"),
                "pval": float(pval[term]) if term in pval.index else float("nan"),
                "N": n,
                "r2": r2,
            }
        )
    return rows


def collect_all() -> pd.DataFrame:
    df = read_dta(A4_PATH)
    rows: list[dict] = []

    for key, fit in run_table3(df).items():
        rows.extend(_fit_to_rows("table3", key, fit))

    t4 = run_table4(df)
    for key in TABLE4_ORDER:
        rows.extend(_fit_to_rows("table4", key, t4[key]))

    t5 = run_table5(df)
    for key in TABLE5_MODEL_ORDER:
        rows.extend(_fit_to_rows("table5", key, t5[key]))

    return pd.DataFrame(rows)


def main() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = collect_all()
    out.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {OUTPUT_CSV} ({len(out)} rows)")
    return OUTPUT_CSV


if __name__ == "__main__":
    main()
