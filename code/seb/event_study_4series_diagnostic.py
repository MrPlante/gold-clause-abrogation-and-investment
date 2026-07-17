"""
4-series event-study figures, built from gold_claude.crsp (research DB).

This is the figure R2 asked for (round 2): time series of cumulative returns
for (a) the market, (b) gold-exposed firms equal-weighted, (c) gold-exposed
firms gold-exposure-weighted, (d) firms without gold exposure, with event
lines. Produces the full-period overview plus a 4-series zoom for each of the
three key events.

All four series are constructed here from raw CRSP daily data rather than
read from data/returns/pf_returns.xls: the ewret_yes/ewret_no columns in that
file are SWAPPED (verified 2026-07-16 — his "yes" matches the rebuilt d=0
portfolio at corr 0.9993 over 5,963 days and vice versa). The rebuilt series
reproduce the file's mkt/dwret to within a few bp.

Series:
  mkt      — value-weighted market (prev-day cap weights, CRSP convention)
  ew_yes   — equal-weighted, firms with gold exposure (fixed d > 0, 175 firms)
  ew_no    — equal-weighted, firms without gold exposure (fixed d = 0, 378)
  dwret    — d-weighted gold portfolio (daily rebalanced, weights = fixed d)

Fixed exposure d = the paper's treatment variable from A4_merged (constant
within firm from 1931 on: 1930 gold-clause debt / 1930 LT liabilities).

Requires a valid Kerberos ticket (klist). Reads the DB via psql (the local
psycopg2 wheel has no GSSAPI support).

Outputs (output/figures/event-study/):
  event_overview_4series.{pdf,png}
  event1_4series.{pdf,png}, event2_4series.{pdf,png}, event3_4series.{pdf,png}
"""

import io
import os
import subprocess
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

DB = ("postgresql://splante%40ads.ssc.wisc.edu@researchdb.ssc.wisc.edu/splante"
      "?sslmode=require&gssencmode=require")
A4_PATH = "../../data/A4_merged.dta"
OUT_DIR = "../../output/figures/event-study"

PULL_START, PULL_END = "1933-03-01", "1935-04-30"
ANCHOR = datetime(1933, 3, 31)

SERIES = [
    ("mkt",    "Market (CRSP VW)",                 "#333333", "-",  1.8),
    ("ew_no",  "No gold exposure (equal-wt.)",     "#d62728", ":",  2.0),
    ("ew_yes", "Gold exposure (equal-wt.)",        "#2ca02c", "-.", 2.0),
    ("dwret",  "Gold exposure (exposure-wt.)",     "#1f77b4", "--", 2.2),
]

OVERVIEW_EVENTS = [
    (datetime(1933, 4, 19), "Gold standard suspended", 0.55),
    (datetime(1933, 6, 5),  "Joint Resolution (abrogation)", 0.98),
    (datetime(1935, 1, 8),  "Supreme Court oral arguments", 0.55),
    (datetime(1935, 2, 18), "Supreme Court decision", 0.98),
]

EVENTS = [
    ("event1_4series", "Joint Resolution (May 26–June 6, 1933)",
     datetime(1933, 5, 26), datetime(1933, 6, 6)),
    ("event2_4series", "Supreme Court Arguments (Jan. 8–10, 1935)",
     datetime(1935, 1, 8), datetime(1935, 1, 10)),
    ("event3_4series", "Supreme Court Decision (Feb. 18, 1935)",
     datetime(1935, 2, 18), datetime(1935, 2, 18)),
    # Exploratory: cert grant in Bankers Trust (Nov 5) + Democratic midterm
    # landslide (Nov 6, market closed; results traded Nov 7). Anchor = Nov 3
    # close (Saturday), i.e. the value going into the election weekend.
    ("midterm_1934_4series", "Cert. Grant & Midterm Election (Nov. 5–7, 1934)",
     datetime(1934, 11, 5), datetime(1934, 11, 7)),
]
EVENT_BUFFER = 5  # trading days before anchor / after event end


def build_series():
    """Daily returns for the four portfolios, from gold_claude.crsp + A4 d."""
    a4 = pd.read_stata(A4_PATH)
    post = a4[a4.year >= 1931]
    d_fix = post.groupby(post.permno.astype(int))["d"].max()

    sql = f"""
    with lagged as (
      select permno, date, ret,
             lag(cap) over (partition by permno order by date) as prevcap
      from gold_claude.crsp
      where date between '{PULL_START}'::date - interval '7 days' and '{PULL_END}'
    )
    select permno, date, ret, prevcap from lagged
    where ret is not null and date between '{PULL_START}' and '{PULL_END}'
    """
    out = subprocess.run(["psql", DB, "-Atc", sql, "-F", ","],
                         capture_output=True, text=True, check=True)
    fd = pd.read_csv(io.StringIO(out.stdout),
                     names=["permno", "date", "ret", "prevcap"])
    fd["date"] = pd.to_datetime(fd.date)
    fd["d"] = fd.permno.map(d_fix)

    vw = fd.dropna(subset=["prevcap"])
    mkt = vw.groupby("date").apply(
        lambda g: (g.prevcap * g.ret).sum() / g.prevcap.sum(), include_groups=False)
    ew_yes = fd[fd.d > 0].groupby("date")["ret"].mean()
    ew_no = fd[fd.d == 0].groupby("date")["ret"].mean()
    gold = fd[fd.d > 0]
    dwret = gold.groupby("date").apply(
        lambda g: (g.d * g.ret).sum() / g.d.sum(), include_groups=False)

    return pd.DataFrame({"mkt": mkt, "ew_yes": ew_yes,
                         "ew_no": ew_no, "dwret": dwret}).sort_index()


def cum_index(df, anchor):
    """Cumulative index = 100 at the last trading day <= anchor."""
    cum = (1 + df.fillna(0)).cumprod()
    base = cum[cum.index <= anchor].iloc[-1]
    return cum / base * 100


def make_overview(df):
    cum = cum_index(df[df.index >= ANCHOR], ANCHOR)
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    for col, label, color, ls, lw in SERIES:
        ax.plot(cum.index, cum[col], color=color, linestyle=ls,
                linewidth=lw, label=label, zorder=3)

    ax.set_yscale("log")
    yticks = [80, 100, 150, 200, 300, 400, 600]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{v - 100:+d}%" for v in yticks])
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    ax.axhline(100, color="black", linewidth=0.6, zorder=1)

    ymin, ymax = ax.get_ylim()
    for date, label, hfrac in OVERVIEW_EVENTS:
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


def make_event_zoom(df, title, start, end):
    dates = df.index
    pre_pool = dates[dates < start]
    anchor = pre_pool[-1]
    lo = pre_pool[-(EVENT_BUFFER + 1)]
    post_pool = dates[dates > end]
    hi = post_pool[min(EVENT_BUFFER, len(post_pool)) - 1] if len(post_pool) else dates[-1]

    win = df.loc[lo:hi]
    cum = (1 + win.fillna(0)).cumprod()
    cum = (cum / cum.loc[anchor] - 1) * 100

    fig, ax = plt.subplots(figsize=(7, 3.5))
    shade_end = end if start != end else start
    ax.axvspan(anchor, shade_end, color="#f0f0f0", zorder=0)
    ax.axhline(0, color="black", linewidth=0.6, zorder=1)
    ax.axvline(anchor, color="#888888", linewidth=0.8, linestyle="--", zorder=2)
    ax.axvline(shade_end, color="#888888", linewidth=0.8, linestyle="--", zorder=2)

    for col, label, color, ls, lw in SERIES:
        ax.plot(cum.index, cum[col], color=color, linestyle=ls,
                linewidth=lw, label=label, zorder=3)

    ax.set_title(title, fontsize=11, pad=8)
    ax.set_ylabel("Cumulative return (%)", fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.set_xticks([mdates.date2num(anchor), mdates.date2num(shade_end)])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    plt.xticks(rotation=30, ha="right", fontsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=8, frameon=False, loc="best")
    fig.tight_layout()
    return fig


def save(fig, stem):
    for ext in ("pdf", "png"):
        path = os.path.join(OUT_DIR, f"{stem}.{ext}")
        fig.savefig(path, bbox_inches="tight", dpi=150)
        print(f"Saved: {path}")
    plt.close(fig)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = build_series()
    print(f"Built series: {len(df)} trading days "
          f"({df.index[0].date()} to {df.index[-1].date()})")

    # JR-window sanity print
    jr = df.loc["1933-05-26":"1933-06-06"]
    for col, label, *_ in SERIES:
        print(f"  JR window {label:<32}{((1+jr[col]).prod()-1)*100:+7.2f}%")

    save(make_overview(df), "event_overview_4series")
    for stem, title, start, end in EVENTS:
        save(make_event_zoom(df, title, start, end), stem)


if __name__ == "__main__":
    main()
