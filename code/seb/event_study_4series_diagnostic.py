"""
DIAGNOSTIC: 4-series version of the full-period cumulative-return overview.

This is the figure R2 actually asked for (round 2): time series of cumulative
returns for (a) the market, (b) gold-exposed firms equal-weighted, (c) gold-
exposed firms gold-exposure-weighted, (d) firms without gold exposure, with
event lines.

The manuscript ships only the 2-series version (market + gold-weighted) because
the non-exposed series (ewret_no) rallies almost as hard as the gold series over
the Joint Resolution window, which complicates the "gold-specific" narrative.
This script regenerates the full 4-series view so that issue can be re-examined.

Uses xlrd directly (pandas read_excel is broken by an xlrd version mismatch in
this environment).

Output: output/figures/event-study/event_overview_4series.{pdf,png}
"""

import os
from datetime import datetime, timedelta

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import xlrd

DATA_PATH = "../../data/returns/pf_returns.xls"
OUT_PATHS = [
    "../../output/figures/event-study/event_overview_4series.pdf",
    "../../output/figures/event-study/event_overview_4series.png",
]

ANCHOR = datetime(1933, 3, 31)
WINDOW_END = datetime(1935, 4, 30)

# (column, label, color, linestyle, linewidth)
SERIES = [
    ("mkt",       "Market (CRSP VW)",                  "#333333", "-",  1.8),
    ("ewret_no",  "No gold exposure (equal-wt.)",      "#d62728", ":",  2.0),
    ("ewret_yes", "Gold exposure (equal-wt.)",         "#2ca02c", "-.", 2.0),
    ("dwret",     "Gold exposure (exposure-wt.)",      "#1f77b4", "--", 2.2),
]

EVENTS = [
    (datetime(1933, 4, 19), "Gold standard suspended", 0.55),
    (datetime(1933, 6, 5),  "Joint Resolution (abrogation)", 0.98),
    (datetime(1935, 1, 8),  "Supreme Court oral arguments", 0.55),
    (datetime(1935, 2, 18), "Supreme Court decision", 0.98),
]

# Joint Resolution event window for the printed CAR diagnostic.
JR_WINDOW = ((1933, 5, 26), (1933, 6, 6))


def load(path):
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_name("Sheet1")
    headers = [sh.cell_value(0, c) for c in range(sh.ncols)]
    rows = []
    for r in range(1, sh.nrows):
        serial = sh.cell_value(r, 0)
        if not serial:
            continue
        row = {h: sh.cell_value(r, c) for c, h in enumerate(headers)}
        row["_date"] = datetime(1899, 12, 30) + timedelta(days=int(serial))
        rows.append(row)
    rows.sort(key=lambda x: x["_date"])
    return rows


def cumulative(rows, anchor, end):
    sub = [r for r in rows if anchor <= r["_date"] <= end]
    out = {"_date": [r["_date"] for r in sub]}
    for col, *_ in SERIES:
        running, vals = 1.0, []
        for r in sub:
            v = r.get(col)
            if v not in ("", None):
                running *= 1 + v
            vals.append(running * 100)
        out[col] = vals
    return out


def compound(rows, start, end, col):
    s, e = datetime(*start), datetime(*end)
    period = [r for r in rows if s <= r["_date"] <= e and r.get(col) not in ("", None)]
    prod = 1.0
    for r in period:
        prod *= 1 + r[col]
    return prod - 1, len(period)


def make_figure(cum):
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    for col, label, color, ls, lw in SERIES:
        ax.plot(cum["_date"], cum[col], color=color, linestyle=ls,
                linewidth=lw, label=label, zorder=3)

    ax.set_yscale("log")
    yticks = [80, 100, 150, 200, 300, 400, 600]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{v - 100:+d}%" for v in yticks])
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    ax.axhline(100, color="black", linewidth=0.6, zorder=1)

    ymin, ymax = ax.get_ylim()
    for date, label, hfrac in EVENTS:
        ax.axvline(date, color="#999999", linewidth=0.9, linestyle="--", zorder=2)
        ax.text(date, ymin * (ymax / ymin) ** hfrac, "  " + label, rotation=90,
                va="top", ha="left", fontsize=7.5, color="#555555", zorder=4)

    ax.set_ylabel("Cumulative return (log scale)", fontsize=10)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=30, ha="right", fontsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    fig.tight_layout()
    return fig


def main():
    rows = load(DATA_PATH)

    # Print the Joint Resolution event-window raw returns for all 4 series.
    (s, e) = JR_WINDOW
    print(f"Joint Resolution window {s} -> {e} (raw compounded returns):")
    print(f"  {'series':<28}{'return':>9}{'ndays':>7}")
    for col, label, *_ in SERIES:
        ret, n = compound(rows, s, e, col)
        print(f"  {label:<28}{ret*100:>8.2f}%{n:>7}")
    print()

    cum = cumulative(rows, ANCHOR, WINDOW_END)
    fig = make_figure(cum)
    for p in OUT_PATHS:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        fig.savefig(p, bbox_inches="tight", dpi=150)
        print(f"Saved: {p}")
    plt.close(fig)


if __name__ == "__main__":
    main()
