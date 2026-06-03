"""Figure 3 — year × d̃ interaction coefficients (Stata A9_inv_results.do gold_coeffs block)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import (
    A4_PATH,
    MANUSCRIPT_BODY_FIGURES,
    OMITTED_YEAR,
    REFACTOR_OUTPUT_FIGURES,
    SAMPLE_YEARS,
)
from lib.io import read_dta
from lib.latex import model_se
from lib.regressions import fit_overhang


def _interaction_frame(model) -> pd.DataFrame:
    coef = model.coef()
    se = model_se(model)
    lo, hi = SAMPLE_YEARS
    rows = []
    for year in range(lo, hi + 1):
        if year == OMITTED_YEAR:
            rows.append({"year": year, "beta": 0.0, "se": 0.0})
            continue
        term = f"d_year_{year}"
        b = float(coef[term])
        s = float(se[term])
        rows.append({"year": year, "beta": b, "se": s})
    out = pd.DataFrame(rows)
    out["lower"] = out["beta"] - 1.96 * out["se"]
    out["upper"] = out["beta"] + 1.96 * out["se"]
    return out


def render_parallel_trend_plot(
    frame: pd.DataFrame,
    out_path: Path,
    *,
    ylabel: str = "Coefficient on Year × d",
) -> Path:
    """Stata-style rcap + scatter on white background."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=150)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    years = frame["year"].to_numpy()
    ax.vlines(years, frame["lower"], frame["upper"], color="black", linewidth=0.8, zorder=1)
    ax.scatter(years, frame["beta"], color="black", s=28, zorder=2, marker="o")

    ax.axhline(0.0, color="black", linestyle="--", linewidth=0.8)
    ax.set_xlim(SAMPLE_YEARS[0] - 0.4, SAMPLE_YEARS[1] + 0.4)
    ax.set_xticks(range(SAMPLE_YEARS[0], SAMPLE_YEARS[1] + 1))
    ax.set_xticklabels(range(SAMPLE_YEARS[0], SAMPLE_YEARS[1] + 1), rotation=45, ha="right")
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_parallel_trend_plot(
    df: pd.DataFrame | None = None,
    *,
    out_dir: Path | None = None,
) -> tuple[Path, pd.DataFrame]:
    """Fit Table 3 col. 2 spec and write ``parallel_trend_plot.pdf``."""
    panel = read_dta(A4_PATH) if df is None else df
    model = fit_overhang(panel, exposure="d", dep="var_inv_rate")
    frame = _interaction_frame(model)

    dest = Path(out_dir) if out_dir is not None else REFACTOR_OUTPUT_FIGURES
    refactor_path = render_parallel_trend_plot(
        frame, dest / "parallel_trend_plot.pdf"
    )

    MANUSCRIPT_BODY_FIGURES.mkdir(parents=True, exist_ok=True)
    manuscript_path = render_parallel_trend_plot(
        frame, MANUSCRIPT_BODY_FIGURES / "parallel_trend_plot.pdf"
    )
    return manuscript_path, frame


def main() -> Path:
    path, _ = build_parallel_trend_plot()
    print(f"Wrote {path}")
    return path


if __name__ == "__main__":
    main()
