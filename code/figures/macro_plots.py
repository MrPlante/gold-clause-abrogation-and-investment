"""Manuscript Figures 1-2: gold price vs exchange rates and inflation.

Data: ``figures/source-data/macro_monthly.csv`` (versioned), monthly 12/1930-12/1936,
in primary-source units. Indices (12/1932 = 1) are computed here.

Provenance (assembled 2026-07-18, see DISCREPANCIES.md D-015):
- ``usd_gbp_cents`` / ``usd_frf_cents``: monthly averages of noon buying
  rates in New York, cents per pound / cents per franc, from Board of
  Governors, *Banking and Monetary Statistics, 1914-1941* (1943), Table
  No. 173 (United Kingdom p. 681, France p. 670; FRASER scan,
  fraser.stlouisfed.org). Transcribed from the OCR text layer and
  cross-validated month-by-month against a data-precision vector
  extraction of the original MATLAB figures (which plotted exactly this
  series normalized to 12/1932): one OCR misread corrected (France
  1/1936, 6.6251 not 6.8251, confirmed against the page scan). The one
  real divergence from the original figure is France 9/1936, where the
  published month average (6.3409) straddles the September 26 Tripartite
  devaluation while the original figure plotted ~6.51.
- ``cpiaucns``: BLS CPI, all urban consumers, NSA (FRED ``CPIAUCNS``),
  raw index level; normalized here to 12/1932 (= 13.1). Matches the
  original figure in 10 of 13 plotted months; June-August 1933 differ by
  one 0.1-point tick (the original used an older CPI vintage).
- ``gold_purchase_usd``: U.S. government gold purchasing-program price,
  monthly averages of the official daily prices published in the Federal
  Reserve Bulletin ("Official Price of Gold" tables: Dec. 1933 issue for
  Sept. 8-Dec. 1, Jan. 1934 issue for December, Feb. 1934 issue for
  January; FRASER): $20.67 statutory through 8/1933; 30.77 (9/1933,
  Treasury sales price under the EO of Aug. 29); 30.82 (10/1933,
  Treasury through Oct. 24, RFC-note rate from Oct. 25); 33.34
  (11/1933); 34.03 (12/1933); 34.27 (1/1934, 34.06 through Jan. 15 and
  34.45 after); $35.00 from the Gold Reserve Act (Jan. 30, 1934). The
  original figure plotted lower values (28.00, 29.01, 31.96, 33.32,
  34.06) whose sampling could not be identified (three of them appear in
  the daily tables at non-month-end dates); the primary-source averages
  replace them.
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

MONTHLY_MACRO_CSV = Path(__file__).resolve().parent / "source-data" / "macro_monthly.csv"

MATLAB_BLUE = (0.00, 0.45, 0.74)
# The original MATLAB figures used the default orange (#D95319) while the
# figure notes say "red-dashed"; use the true red of the event-study figures
# (#d62728) so the figures match the notes.
SERIES_RED = (0.839, 0.153, 0.157)
GOLD_ORDER = date(1933, 4, 5)  # Executive Order 6102


def _load() -> pd.DataFrame:
    frame = pd.read_csv(MONTHLY_MACRO_CSV, parse_dates=["date"]).set_index("date")
    base = frame.loc["1932-12-31"]
    frame["usd_gbp_index"] = frame["usd_gbp_cents"] / base["usd_gbp_cents"]
    frame["usd_frf_index"] = frame["usd_frf_cents"] / base["usd_frf_cents"]
    frame["cpi_index"] = frame["cpiaucns"] / base["cpiaucns"]
    return frame


def _fx_panel(frame: pd.DataFrame, fx_col: str, fx_label: str, out_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(5.5, 4.1), dpi=150)
    axr = ax.twinx()

    ax.plot(frame.index, frame["gold_purchase_usd"], color=MATLAB_BLUE,
            linewidth=1.6, label="Gold purchase price")
    axr.plot(frame.index, frame[fx_col], color=SERIES_RED, linestyle="--",
             linewidth=1.6, label=fx_label)
    ax.axvline(pd.Timestamp(GOLD_ORDER), color="black", linewidth=4.0)

    ax.set_xlim(pd.Timestamp("1930-12-31"), pd.Timestamp("1936-09-15"))
    ax.set_ylim(20, 35)
    ax.set_yticks([20, 25, 30, 35])
    ax.set_ylabel("Dollars per ounce", color=MATLAB_BLUE)
    ax.tick_params(axis="y", colors=MATLAB_BLUE)
    axr.set_ylim(0.96, 1.72)
    axr.set_yticks([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7])
    axr.set_ylabel("Exchange rate (12/1932 = 1)", color=SERIES_RED)
    axr.tick_params(axis="y", colors=SERIES_RED)
    ax.xaxis.set_major_locator(mdates.YearLocator(month=12, day=31))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
    ax.tick_params(axis="x", labelsize=7)
    ax.tick_params(axis="y", labelsize=8)
    axr.tick_params(axis="y", labelsize=8)

    handles = [
        plt.Line2D([], [], color="black", linewidth=4.0, label="Ban on gold holdings"),
        plt.Line2D([], [], color=MATLAB_BLUE, linewidth=1.6, label="Gold purchase price"),
        plt.Line2D([], [], color=SERIES_RED, linestyle="--", linewidth=1.6, label=fx_label),
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
    axr.plot(window.index, window["cpi_index"], color=SERIES_RED, linestyle="--",
             linewidth=1.6, label="CPI")
    ax.axvline(pd.Timestamp(GOLD_ORDER), color="black", linewidth=4.0)

    ax.set_xlim(pd.Timestamp("1932-12-31"), pd.Timestamp("1934-05-31"))
    ax.set_ylim(20, 35)
    ax.set_yticks([20, 25, 30, 35])
    ax.set_ylabel("Dollars per ounce", color=MATLAB_BLUE)
    ax.tick_params(axis="y", colors=MATLAB_BLUE)
    axr.set_ylim(0.96, 1.69)
    axr.set_yticks([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
    axr.set_ylabel("CPI (12/1932 = 1)", color=SERIES_RED)
    axr.tick_params(axis="y", colors=SERIES_RED)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(2, 4, 6, 8, 10, 12), bymonthday=28))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
    ax.tick_params(axis="x", labelsize=7)
    ax.tick_params(axis="y", labelsize=8)
    axr.tick_params(axis="y", labelsize=8)

    handles = [
        plt.Line2D([], [], color="black", linewidth=4.0, label="Ban on gold holdings"),
        plt.Line2D([], [], color=MATLAB_BLUE, linestyle="-.", linewidth=1.6, label="Domestic gold price"),
        plt.Line2D([], [], color=MATLAB_BLUE, linewidth=1.6, label="Gold purchase price"),
        plt.Line2D([], [], color=SERIES_RED, linestyle="--", linewidth=1.6, label="CPI"),
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
