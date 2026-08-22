"""Stata-generated regression results for the manuscript tables.

Every table whose printed standard errors are reghdfe's is estimated by a
standalone batch do-file in ``analysis/stata/`` (one per table, with the
reghdfe ``version()`` engine pinned to the paper's estimation vintage; see
DISCREPANCIES.md D-023). The Python builders prepare the input panel, write
it to ``data/processed/stata_inputs/``, invoke the do-file, and read back
``analysis/stata/results/<stage>_results.csv``. There is no fallback: if
Stata is unavailable or the do-file fails, the stage fails loudly rather
than silently substituting a different variance estimator.

``StataModel`` mimics the slice of the pyfixest model interface the LaTeX
renderers consume (``coef()``, ``_vcov``, ``_df_t``, ``_r2``, ``_N``), so
the renderers are unchanged: ``lib.vcov.model_se`` reads the diagonal vcov
and ``lib.vcov.model_pvalue`` recomputes reghdfe's p-values from the
exported residual degrees of freedom.
"""

from __future__ import annotations

import csv
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATA_DIR = PROJECT_ROOT / "analysis" / "stata"
RESULTS_DIR = STATA_DIR / "results"
INPUTS_DIR = PROJECT_ROOT / "data" / "processed" / "stata_inputs"
LOGS_DIR = PROJECT_ROOT / "logs"
STATA_BIN = Path("/usr/local/stata/stata-mp")


class StataModel:
    """Renderer-compatible container for one regression column."""

    def __init__(self, terms: list[str], b: list[float], se: list[float],
                 df: float, r2: float, n: int):
        self._coef = pd.Series(b, index=terms, dtype=float)
        self._vcov = np.diag(np.asarray(se, dtype=float) ** 2)
        self._df_t = float(df)
        self._r2 = float(r2)
        self._N = int(n)

    def coef(self) -> pd.Series:
        return self._coef


def write_input(stage: str, df: pd.DataFrame) -> Path:
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    path = INPUTS_DIR / f"{stage}.dta"
    df.to_stata(path, write_index=False)
    return path


def run_dofile(stage: str) -> None:
    """Run ``analysis/stata/<stage>.do`` in batch mode from the project root."""
    do_path = STATA_DIR / f"{stage}.do"
    if not do_path.is_file():
        raise FileNotFoundError(do_path)
    if not STATA_BIN.is_file():
        raise RuntimeError(
            f"{STATA_BIN} not found - the regression tables require Stata "
            "(no fallback; see analysis/lib/stata_reg.py)."
        )
    LOGS_DIR.mkdir(exist_ok=True)
    result = subprocess.run(
        [str(STATA_BIN), "-b", "do", str(do_path), str(PROJECT_ROOT)],
        cwd=LOGS_DIR, check=False, capture_output=True, text=True,
    )
    log = LOGS_DIR / f"{stage}.log"
    if result.returncode != 0:
        tail = log.read_text()[-3000:] if log.is_file() else result.stderr
        raise RuntimeError(f"Stata failed for {stage} (rc={result.returncode}).\n{tail}")


def read_results(stage: str) -> dict[str, StataModel]:
    """Parse ``<stage>_results.csv`` into one StataModel per column."""
    path = RESULTS_DIR / f"{stage}_results.csv"
    cols: dict[str, dict[str, list]] = {}
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                se = float(row["se"])
                b = float(row["b"])
            except ValueError:  # Stata writes missing values as "."
                se, b = float("nan"), float("nan")
            # b = se = 0 is reghdfe's encoding for a regressor omitted for
            # collinearity (e.g. reference decile-period dummies) - keep it.
            # Anything else without a positive finite SE means a degenerate
            # e(V); fail rather than render wrong inference.
            if not (np.isfinite(se) and (se > 0 or (se == 0 and b == 0))):
                raise ValueError(
                    f"{stage} {row['col']} {row['term']}: degenerate SE {row['se']} "
                    "from Stata - refusing to render."
                )
            c = cols.setdefault(row["col"], {"terms": [], "b": [], "se": [],
                                             "df": float(row["df"]),
                                             "r2": float(row["r2"]),
                                             "N": int(float(row["N"]))})
            c["terms"].append(row["term"])
            c["b"].append(float(row["b"]))
            c["se"].append(se)
    return {
        key: StataModel(c["terms"], c["b"], c["se"], c["df"], c["r2"], c["N"])
        for key, c in cols.items()
    }


def stata_models(stage: str, prepared: pd.DataFrame) -> dict[str, StataModel]:
    """Full round trip: write input, run the stage do-file, read results."""
    write_input(stage, prepared)
    run_dofile(stage)
    return read_results(stage)
