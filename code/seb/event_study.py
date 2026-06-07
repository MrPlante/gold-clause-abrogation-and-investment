"""
Event study figures for the three key legal events around gold clause abrogation.
Outputs one PDF per event to code/output/figures/event-study/.

Series shown in each panel:
  mkt       — CRSP value-weighted market
  dwret     — gold-exposure-weighted portfolio (d_j weights)
  ewret_yes — gold-clause firms (equal-weighted)
  ewret_no  — non-gold-clause firms (equal-weighted)

Cumulative returns are indexed to 0 at the close of the last trading day
before the event window opens (the anchor). The left dashed line and shaded
area begin at the anchor so the 0% level aligns exactly with the left edge.
"""

import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import xlrd

DATA_PATH  = "../../data/returns/pf_returns.xls"
OUTPUT_DIR = "../../output/figures/event-study"

EVENTS = [
    {
        "filename": "event1_joint_resolution.pdf",
        "title":    "Joint Resolution (May 26–June 6, 1933)",
        "start":    datetime(1933, 5, 26),
        "end":      datetime(1933, 6, 6),
        "pre":      5,
        "post":     5,
    },
    {
        "filename": "event2_weak_showing.pdf",
        "title":    "Supreme Court Arguments (Jan. 8–10, 1935)",
        "start":    datetime(1935, 1, 8),
        "end":      datetime(1935, 1, 10),
        "pre":      5,
        "post":     5,
    },
    {
        "filename": "event3_sc_decision.pdf",
        "title":    "Supreme Court Decision (Feb. 18, 1935)",
        "start":    datetime(1935, 2, 18),
        "end":      datetime(1935, 2, 18),
        "pre":      5,
        "post":     5,
    },
]

SERIES = [
    ("mkt",   "Market",                 "#333333", "-",  2.0),
    ("dwret", "Gold-weighted portfolio","#1f77b4", "--", 2.0),
]


def load_data(path):
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
    return rows


def build_window(rows, event):
    start, end = event["start"], event["end"]

    all_near = [r for r in rows
                if start - timedelta(days=90) <= r["_date"] <= end + timedelta(days=90)]

    pre_pool  = [r for r in all_near if r["_date"] < start]
    evt_pool  = [r for r in all_near if start <= r["_date"] <= end]
    post_pool = [r for r in all_near if r["_date"] > end]

    if not pre_pool:
        raise ValueError("Not enough pre-event data")

    # Anchor: last trading day before event start. Series is indexed to 0 here.
    anchor = pre_pool[-1]

    # Pre-buffer: event["pre"] trading days strictly before the anchor.
    # Anchor itself is included as an explicit 0% point — not part of the buffer.
    pre_buffer = pre_pool[-(event["pre"] + 1):-1]
    post_buffer = post_pool[:event["post"]]

    # Full chronological sequence: [pre_buffer..., anchor (=0%), event..., post...]
    all_rows = pre_buffer + [anchor] + evt_pool + post_buffer
    dates = [r["_date"] for r in all_rows]
    anchor_idx = len(pre_buffer)  # index of anchor in all_rows

    cum = {}
    for col, *_ in SERIES:
        # Forward cumulative product through all rows from a common dummy origin
        running = 1.0
        products = []
        for r in all_rows:
            val = r.get(col)
            if val in ("", None):
                products.append(running)
            else:
                running *= (1 + val)
                products.append(running)

        # Normalise so anchor = 0%
        P_base = products[anchor_idx]
        cum[col] = [(p / P_base - 1) * 100 for p in products]

    # Return anchor date so make_figure can align the 0-line and shaded area
    return dates, cum, anchor["_date"], end


def make_figure(event, dates, cum, anchor_date, evt_end):
    fig, ax = plt.subplots(figsize=(7, 3.5))

    # Shade from anchor to event end (single-day: anchor to event start)
    shade_end = evt_end if event["start"] != event["end"] else event["start"]
    ax.axvspan(anchor_date, shade_end, color="#f0f0f0", zorder=0, label="_nolegend_")

    # Zero line
    ax.axhline(0, color="black", linewidth=0.6, linestyle="-", zorder=1)

    # Dashed boundaries at anchor and event end (or event start for single-day)
    ax.axvline(anchor_date, color="#888888", linewidth=0.8, linestyle="--", zorder=2)
    ax.axvline(shade_end, color="#888888", linewidth=0.8, linestyle="--", zorder=2)

    # Plot each series
    for col, label, color, ls, lw in SERIES:
        vals = cum[col]
        plot_dates = [d for d, v in zip(dates, vals) if v is not None]
        plot_vals  = [v for v in vals if v is not None]
        ax.plot(plot_dates, plot_vals, color=color, linestyle=ls,
                linewidth=lw, label=label, zorder=3)

    # Axes formatting
    ax.set_title(event["title"], fontsize=11, pad=8)
    ax.set_ylabel("Cumulative return (%)", fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))

    # Date format on x-axis
    span = (dates[-1] - dates[0]).days
    if span <= 30:
        # Only the event boundary dates
        tick_dates = [anchor_date, shade_end]
        ax.set_xticks([mdates.date2num(d) for d in tick_dates])
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    else:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=0, interval=2))

    plt.xticks(rotation=30, ha="right", fontsize=8)
    ax.tick_params(axis="y", labelsize=8)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(fontsize=8, frameon=False, loc="best")

    fig.tight_layout()
    return fig


def main():
    rows = load_data(DATA_PATH)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for event in EVENTS:
        dates, cum, anchor_date, evt_end = build_window(rows, event)
        fig = make_figure(event, dates, cum, anchor_date, evt_end)
        out_path = os.path.join(OUTPUT_DIR, event["filename"])
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
