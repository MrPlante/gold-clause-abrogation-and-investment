"""
Full-period cumulative-return overview figure for the gold clause episode.

Addresses R2's request (round 2) for a single time series of cumulative
returns with vertical "event lines" marking the key legal developments,
visualizing how the market moved around the abrogation.

Series (columns of pf_returns.xls):
  mkt   -- CRSP value-weighted market
  dwret -- gold-clause firms, gold-exposure-weighted (d_j weights)

Cumulative returns are indexed to 0 at the close of the anchor date.

Output: manuscript/figures/online-appendix/event_overview.pdf
"""

import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

DATA_PATH = "../../data/returns/pf_returns.xls"
OUT_PATHS = [
    "../../manuscript/figures/online-appendix/event_overview.pdf",
    "../../output/figures/event-study/event_overview.pdf",
]

ANCHOR = datetime(1933, 3, 31)   # cumulative returns indexed to 0 here
WINDOW_END = datetime(1935, 4, 30)

SERIES = [
    ("mkt",   "Market",                        "#333333", "-",  1.8),
    ("dwret", "Gold-exposure-weighted",        "#1f77b4", "--", 2.0),
]

# Event lines: (date, label, label height as fraction of y-range).
# Heights are staggered so labels of nearby events do not overlap.
EVENTS = [
    (datetime(1933, 4, 19), "Gold standard suspended", 0.62),
    (datetime(1933, 6, 5),  "Joint Resolution (abrogation)", 0.98),
    (datetime(1935, 1, 8),  "Supreme Court oral arguments", 0.62),
    (datetime(1935, 2, 18), "Supreme Court decision", 0.98),
]


def load(path):
    df = pd.read_excel(path, sheet_name="Sheet1")
    df["_date"] = pd.to_datetime(df["date"])
    return df.sort_values("_date").reset_index(drop=True)


def cumulative(df, anchor, end):
    sub = df[(df["_date"] >= anchor) & (df["_date"] <= end)].copy()
    out = {"_date": sub["_date"].tolist()}
    for col, *_ in SERIES:
        running = 1.0
        vals = []
        for v in sub[col]:
            if pd.notna(v):
                running *= (1 + v)
            vals.append((running - 1) * 100)
        out[col] = vals
    return out


def make_figure(cum):
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    ax.axhline(0, color="black", linewidth=0.6, zorder=1)

    for col, label, color, ls, lw in SERIES:
        ax.plot(cum["_date"], cum[col], color=color, linestyle=ls,
                linewidth=lw, label=label, zorder=3)

    ymin, ymax = ax.get_ylim()
    for date, label, hfrac in EVENTS:
        ax.axvline(date, color="#999999", linewidth=0.9, linestyle="--", zorder=2)
        ax.text(date, ymin + hfrac * (ymax - ymin), "  " + label, rotation=90,
                va="top", ha="left", fontsize=7.5, color="#555555", zorder=4)

    ax.set_ylabel("Cumulative return (%)", fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=30, ha="right", fontsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=9, frameon=False, loc="upper left")
    fig.tight_layout()
    return fig


def main():
    df = load(DATA_PATH)
    cum = cumulative(df, ANCHOR, WINDOW_END)
    fig = make_figure(cum)
    for p in OUT_PATHS:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        fig.savefig(p, bbox_inches="tight")
        print(f"Saved: {p}")
    plt.close(fig)


if __name__ == "__main__":
    main()
