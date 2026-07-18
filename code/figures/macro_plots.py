"""Manuscript Figures 1-2: gold price vs exchange rates and inflation.

Data: ``figures/data/macro_monthly.csv`` (versioned), monthly 12/1930-12/1936.

Provenance (assembled 2026-07-18, see DISCREPANCIES.md D-015):
- ``usd_gbp_index`` / ``usd_frf_index``: dollar/sterling and dollar/franc
  exchange rates indexed to December 1932 = 1, recovered at full precision
  from the vector paths of the original MATLAB figures (the underlying
  source file was never in the repo). Consistent with the interwar record:
  sterling collapses on Britain's September 1931 exit, the franc devalues
  with the September 1936 Tripartite Agreement.
- ``cpi_index``: BLS CPI, all urban consumers, NSA (FRED ``CPIAUCNS``),
  normalized to December 1932 (= 13.1). Matches the original figure in 10
  of 13 plotted months; June-August 1933 differ by one 0.1-point CPI tick
  (the original used an older CPI vintage).
- ``gold_purchase_usd``: U.S. government gold purchasing-program price,
  $20.67 through 8/1933, Treasury/RFC purchase prices 9/1933-1/1934
  (28.00, 29.01, 31.96, 33.32, 34.06), $35.00 from 2/1934 (Gold Reserve
  Act of January 30, 1934). Values as plotted in the original figure.
- ``gold_official_usd``: official (statutory) gold price, $20.67 to
  1/1934, $35.00 after.

The vertical black line marks Executive Order 6102 (April 5, 1933), the
requirement to deliver gold holdings to the government.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from config import MANUSCRIPT_BODY_FIGURES, REFACTOR_OUTPUT_FIGURES

MONTHLY_MACRO_CSV = Path(__file__).resolve().parent / "data" / "macro_monthly.csv"

MATLAB_BLUE = (0.00, 0.45, 0.74)
MATLAB_RED = (0.85, 0.33, 0.10)
GOLD_ORDER = date(1933, 4, 5)  # Executive Order 6102


def _load() -> pd.DataFrame:
    return pd.read_csv(MONTHLY_MACRO_CSV, parse_dates=["date"]).set_index("date")


def _fx_panel(frame: pd.DataFrame, fx_col: str, fx_label: str, out_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(5.5, 4.1), dpi=150)
    axr = ax.twinx()

    ax.plot(frame.index, frame["gold_purchase_usd"], color=MATLAB_BLUE,
            linewidth=1.6, label="Gold purchase price")
    axr.plot(frame.index, frame[fx_col], color=MATLAB_RED, linestyle="--",
             linewidth=1.6, label=fx_label)
    ax.axvline(pd.Timestamp(GOLD_ORDER), color="black", linewidth=4.0)

    ax.set_xlim(pd.Timestamp("1930-12-31"), pd.Timestamp("1936-09-15"))
    ax.set_ylim(20, 35)
    ax.set_yticks([20, 25, 30, 35])
    ax.set_ylabel("Dollars per ounce", color=MATLAB_BLUE)
    ax.tick_params(axis="y", colors=MATLAB_BLUE)
    axr.set_ylim(0.96, 1.72)
    axr.set_yticks([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7])
    axr.set_ylabel("Exchange rate (12/1932 = 1)", color=MATLAB_RED)
    axr.tick_params(axis="y", colors=MATLAB_RED)
    ax.xaxis.set_major_locator(mdates.YearLocator(month=12, day=31))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
    ax.tick_params(axis="x", labelsize=7)
    ax.tick_params(axis="y", labelsize=8)
    axr.tick_params(axis="y", labelsize=8)

    handles = [
        plt.Line2D([], [], color="black", linewidth=4.0, label="Ban on gold holdings"),
        plt.Line2D([], [], color=MATLAB_BLUE, linewidth=1.6, label="Gold purchase price"),
        plt.Line2D([], [], color=MATLAB_RED, linestyle="--", linewidth=1.6, label=fx_label),
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=8, frameon=True, edgecolor="black")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_dollar_to_sterling(frame: pd.DataFrame, out_path: Path) -> Path:
    return _fx_panel(frame, "usd_gbp_index", "Dollar/Sterling", out_path)


def plot_dollar_to_franc(frame: pd.DataFrame, out_path: Path) -> Path:
    return _fx_panel(frame, "usd_frf_index", "Dollar/Franc", out_path)


def plot_inflation(frame: pd.DataFrame, out_path: Path) -> Path:
    window = frame.loc["1932-12-01":"1934-05-31"]
    fig, ax = plt.subplots(figsize=(5.5, 4.1), dpi=150)
    axr = ax.twinx()

    ax.plot(window.index, window["gold_official_usd"], color=MATLAB_BLUE,
            linestyle="-.", linewidth=1.6, label="Domestic gold price")
    ax.plot(window.index, window["gold_purchase_usd"], color=MATLAB_BLUE,
            linewidth=1.6, label="Gold purchase price")
    axr.plot(window.index, window["cpi_index"], color=MATLAB_RED, linestyle="--",
             linewidth=1.6, label="CPI")
    ax.axvline(pd.Timestamp(GOLD_ORDER), color="black", linewidth=4.0)

    ax.set_xlim(pd.Timestamp("1932-12-31"), pd.Timestamp("1934-05-31"))
    ax.set_ylim(20, 35)
    ax.set_yticks([20, 25, 30, 35])
    ax.set_ylabel("Dollars per ounce", color=MATLAB_BLUE)
    ax.tick_params(axis="y", colors=MATLAB_BLUE)
    axr.set_ylim(0.96, 1.69)
    axr.set_yticks([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
    axr.set_ylabel("CPI (12/1932 = 1)", color=MATLAB_RED)
    axr.tick_params(axis="y", colors=MATLAB_RED)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(2, 4, 6, 8, 10, 12), bymonthday=28))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
    ax.tick_params(axis="x", labelsize=7)
    ax.tick_params(axis="y", labelsize=8)
    axr.tick_params(axis="y", labelsize=8)

    handles = [
        plt.Line2D([], [], color="black", linewidth=4.0, label="Ban on gold holdings"),
        plt.Line2D([], [], color=MATLAB_BLUE, linestyle="-.", linewidth=1.6, label="Domestic gold price"),
        plt.Line2D([], [], color=MATLAB_BLUE, linewidth=1.6, label="Gold purchase price"),
        plt.Line2D([], [], color=MATLAB_RED, linestyle="--", linewidth=1.6, label="CPI"),
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=8, frameon=True, edgecolor="black")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_macro_figures(*, out_dir: Path | None = None) -> dict[str, Path]:
    frame = _load()
    dest = Path(out_dir) if out_dir is not None else REFACTOR_OUTPUT_FIGURES
    paths = {
        "dollar_to_sterling": plot_dollar_to_sterling(frame, dest / "dollar_to_sterling.pdf"),
        "dollar_to_franc": plot_dollar_to_franc(frame, dest / "dollar_to_franc.pdf"),
        "inflation": plot_inflation(frame, dest / "inflation.pdf"),
    }
    MANUSCRIPT_BODY_FIGURES.mkdir(parents=True, exist_ok=True)
    for key, p in list(paths.items()):
        manuscript = MANUSCRIPT_BODY_FIGURES / p.name
        manuscript.write_bytes(p.read_bytes())
        paths[key] = manuscript
    return paths


def main() -> None:
    for name, path in build_macro_figures().items():
        print(f"Wrote {name}: {path}")


if __name__ == "__main__":
    main()
