"""
Unified event-study pipeline: builds every return series, figure, and table
for the stock-market event-study evidence from data/raw/crsp_daily.dta (a
local dump of researchdb gold_claude.crsp; see data/README.md) and the
paper's exposure measure d (firm_year_panel.dta).

This is the single source for all return numbers in the paper. It replaces
the retired scripts event_study.py, event_study_overview.py,
event_study_table.py, and event_study_4series_diagnostic.py, which read
data/returns/pf_returns.xls -- a file whose ewret_yes/ewret_no columns are
swapped (verified 2026-07-16: rebuilt portfolios match the opposite labels at
corr 0.999 over 5,963 trading days).

Series (daily, July 1, 1926 - December 31, 1945):
  mkt    -- value-weighted market, previous-day-cap weights (CRSP convention;
            matches the CRSP VW index to ~2bp/day)
  ew_yes -- equal-weighted, firms with gold-clause exposure (fixed d > 0)
  ew_no  -- equal-weighted, firms without gold-clause exposure (fixed d = 0)
  dwret  -- gold portfolio weighted by exposure d, daily rebalanced

Fixed exposure d is the paper's treatment variable from firm_year_panel.dta (constant
within firm from 1931 on: 1930 gold-clause debt / 1930 LT liabilities).

Outputs (written directly into manuscript/):
  manuscript/figures/online-appendix/event*_*.pdf             (Figures IA.2-IA.5)
  manuscript/tables/body/table1_event_study.tex               (Table 1)

Fully offline: no researchdb access needed. The dump is regenerated from
the DB (Kerberos + psql) only when the underlying CRSP extract changes;
pipeline/sql/build_gold_claude_crsp.sql documents that build.
"""

import os
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]  # repo root, independent of cwd
PANEL_PATH = ROOT / "data" / "processed" / "firm_year_panel.dta"
CRSP_DAILY_PATH = ROOT / "data" / "raw" / "crsp_daily.dta"
MS_BODY_FIG = ROOT / "manuscript" / "figures" / "body"
MS_IA_FIG = ROOT / "manuscript" / "figures" / "online-appendix"
MS_BODY_TAB = ROOT / "manuscript" / "tables" / "body"
MS_IA_TAB = ROOT / "manuscript" / "tables" / "online-appendix"

SAMPLE_START, SAMPLE_END = "1926-07-01", "1945-12-31"

SERIES4 = [
    ("mkt",    "Market (CRSP value-weighted)",    "#333333", "-",  1.8),
    ("ew_no",  "No gold exposure (equal-wt.)",    "#d62728", ":",  2.0),
    ("ew_yes", "Gold exposure (equal-wt.)",       "#2ca02c", "-.", 2.0),
    ("dwret",  "Gold exposure (exposure-wt.)",    "#1f77b4", "--", 2.2),
]
# The paper's adopted representation: the market and the two equal-weighted
# portfolios, dropping only the redundant exposure-weighted series (the
# four-series versions are reproduced in the R2 response letter).
SERIES3 = [
    ("mkt",    "Market (CRSP value-weighted)",    "#333333", "-",  1.6),
    ("ew_yes", "Gold exposure (equal-wt.)",       "#2ca02c", "-",  2.2),
    ("ew_no",  "No gold exposure (equal-wt.)",    "#d62728", "--", 2.0),
]
# (stem, title, window start, window end) -- Table 1 / manuscript figures
EVENTS = [
    ("event1_joint_resolution", "Joint Resolution (May 26–June 6, 1933)",
     datetime(1933, 5, 26), datetime(1933, 6, 6)),
    ("event4_midterm", "Cert. Grant & Midterm Election (Nov. 5–8, 1934)",
     datetime(1934, 11, 5), datetime(1934, 11, 8)),
    ("event2_weak_showing", "Supreme Court Arguments (Jan. 8–10, 1935)",
     datetime(1935, 1, 8), datetime(1935, 1, 10)),
    ("event3_sc_decision", "Supreme Court Decision (Feb. 18, 1935)",
     datetime(1935, 2, 18), datetime(1935, 2, 18)),
]
EVENT_BUFFER = 5

# Other legal/political events (IA table): (label, start, n trading days)
OTHER_EVENTS = [
    ("First gold-clause hearing (Irving Trust)", "May 22--24, 1933", "1933-05-22", 3),
    ("\\textit{In re Missouri Pacific} ruling",  "June 20--22, 1934", "1934-06-20", 3),
    ("\\textit{Norman} affirmed (N.Y. Ct.\\ App.)", "July 3--6, 1934", "1934-07-03", 3),
    ("Cert.\\ granted, \\textit{Norman}",        "Oct.\\ 8--10, 1934", "1934-10-08", 3),
    ("Cert.\\ granted \\& midterm election",     "Nov.\\ 5--8, 1934", "1934-11-05", 3),
]
JR_ROW = ("Joint Resolution (reference)", "May 26--June 6, 1933", "1933-05-26", 9)

# ---------------------------------------------------------------- series

def load_exposure():
    a4 = pd.read_stata(PANEL_PATH)
    post = a4[a4.year >= 1931]
    d_fix = post.groupby(post.permno.astype(int))["d"].max()
    gold = d_fix[d_fix > 0]
    zero = d_fix[d_fix == 0]
    return gold, zero


def load_crsp():
    """CRSP daily rows with previous-day cap, restricted to the sample window.

    prevcap is the within-permno lag of cap over the FULL file (which starts
    1925-12-31), computed before the sample filter — so the first sample day
    already has a valid previous-day weight, exactly like the SQL window
    function the retired DB version of this pipeline used.
    """
    df = pd.read_stata(CRSP_DAILY_PATH, columns=["permno", "date", "ret", "cap"])
    df = df.sort_values(["permno", "date"], kind="stable")
    df["prevcap"] = df.groupby("permno")["cap"].shift(1)
    return df[df["ret"].notna()
              & df["date"].between(SAMPLE_START, SAMPLE_END)]


def build_series(gold, zero):
    base = load_crsp()
    date = base["date"]
    ret = base["ret"]
    dg = base["permno"].map(gold)            # fixed exposure d; NaN if not d>0 firm
    is0 = base["permno"].isin(zero.index)
    pc = base["prevcap"].where(base["prevcap"] > 0)

    df = pd.DataFrame({
        "mkt": (pc * ret).groupby(date).sum(min_count=1)
               / pc.groupby(date).sum(min_count=1),
        "ew_yes": ret.where(dg.notna()).groupby(date).mean(),
        "ew_no": ret.where(is0).groupby(date).mean(),
        "dwret": (dg * ret).groupby(date).sum(min_count=1)
                 / dg.groupby(date).sum(min_count=1),
    })
    df.index.name = "date"
    return df.sort_index().astype(float)


def window_days(s, start, n):
    return s.loc[start:].head(n)


def raw_ret(s, start, n, col):
    return (1 + window_days(s, start, n)[col]).prod() - 1


PRE_START, PRE_END = "1926-07-01", "1932-12-31"  # pre-abrogation period


def diff_se(s):
    """Daily SD of the raw ew_yes-ew_no differential over the pre-abrogation
    period (July 1926 - December 1932): every trading day before the
    treatment, with no selection."""
    pre = s.loc[PRE_START:PRE_END]
    return (pre.ew_yes - pre.ew_no).std(ddof=1)


# ---------------------------------------------------------------- figures

def make_event_zoom(s, series, title, start, end):
    dates = s.index
    pre_pool = dates[dates < start]
    anchor = pre_pool[-1]
    lo = pre_pool[-(EVENT_BUFFER + 1)]
    post_pool = dates[dates > end]
    hi = post_pool[min(EVENT_BUFFER, len(post_pool)) - 1] if len(post_pool) else dates[-1]

    win = s.loc[lo:hi]
    cum = (1 + win.fillna(0)).cumprod()
    cum = (cum / cum.loc[anchor] - 1) * 100

    fig, ax = plt.subplots(figsize=(7, 3.5))
    shade_end = end if start != end else start
    ax.axvspan(anchor, shade_end, color="#f0f0f0", zorder=0)
    ax.axhline(0, color="black", linewidth=0.6, zorder=1)
    ax.axvline(anchor, color="#888888", linewidth=0.8, linestyle="--", zorder=2)
    ax.axvline(shade_end, color="#888888", linewidth=0.8, linestyle="--", zorder=2)

    for col, label, color, ls, lw in series:
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


def save(fig, stem, target_dir):
    path = os.path.join(target_dir, f"{stem}.pdf")
    fig.savefig(path, bbox_inches="tight", dpi=150)
    print(f"Saved: {path}")
    plt.close(fig)


# ---------------------------------------------------------------- tables

def fmt_pct(x, dec=1):
    return f"{x*100:+.{dec}f}\\%"


# Table 1 is written by write_size_split_tables() below: the paper's single
# return table reports gold-minus-non-gold differentials (raw and
# beta-adjusted, pooled and within size terciles) for every main event
# window. The four-series levels representation the referee sketched lives
# in the R2 response letter and in the appendix figures, not in the body.


# ------------------------------------- size-split tables (Table 1 / IA.20)

SIZE_CAP_DATE = "1932-12-31"    # tercile formation: pre-litigation market caps
BETA_SAMPLE_END = "1940-12-31"  # full-sample firm-level market betas

SIZE_MAIN_EVENTS = [
    ("Panel A: Joint Resolution (May 26--June 6, 1933)", "1933-05-26", 9),
    ("Panel B: Certiorari Grant \\& Midterm Election (November 5--8, 1934)", "1934-11-05", 3),
    ("Panel C: Supreme Court Arguments (January 8--10, 1935)", "1935-01-08", 3),
    ("Panel D: Post-Argument Days (January 11--17, 1935)", "1935-01-11", 6),
    ("Panel E: Supreme Court Decision (February 18, 1935)", "1935-02-18", 1),
]
SIZE_INTERMEDIATE_EVENTS = [
    ("Panel A: First gold-clause hearing, \\textit{Irving Trust} (May 22--24, 1933)",
     "1933-05-22", 3),
    ("Panel B: \\textit{In re Missouri Pacific} ruling (June 20--22, 1934)",
     "1934-06-20", 3),
    ("Panel C: \\textit{Norman} affirmed, N.Y.\\ Ct.\\ App.\\ (July 3--6, 1934)",
     "1934-07-03", 3),
    ("Panel D: Certiorari granted, \\textit{Norman} (Oct.\\ 8--10, 1934)",
     "1934-10-08", 3),
]


def _calm_sd(x):
    """SD of a daily series over the pre-abrogation period (as diff_se)."""
    return x.loc[PRE_START:PRE_END].std(ddof=1)


def size_split_inputs(gold, zero):
    """Per-tercile EW gold / no-gold daily series, the market, and portfolio betas.

    Terciles are formed on the last observed market cap on or before
    SIZE_CAP_DATE (pre-litigation, so the classification cannot reflect the
    events). Portfolio betas are equal-weighted means of firm-level market
    betas (daily returns on the VW market through BETA_SAMPLE_END, >= 250
    obs); one vintage everywhere, reported in the table note.
    """
    base = load_crsp()
    members = set(gold.index) | set(zero.index)
    base = base[base["permno"].isin(members)]
    pc = base["prevcap"].where(base["prevcap"] > 0)
    mkt = ((pc * base["ret"]).groupby(base["date"]).sum(min_count=1)
           / pc.groupby(base["date"]).sum(min_count=1))

    caps = (base[base["date"] <= SIZE_CAP_DATE].sort_values("date")
            .groupby("permno")["cap"].last())
    caps = caps[caps > 0]
    cuts = caps.quantile([1 / 3, 2 / 3])
    grp = caps.map(lambda c: "Small" if c <= cuts.iloc[0]
                   else ("Medium" if c <= cuts.iloc[1] else "Large"))

    est = base[base["date"] <= BETA_SAMPLE_END].copy()
    est["m"] = est["date"].map(mkt)
    est = est.dropna(subset=["ret", "m"])
    betas = {}
    for p, g in est.groupby("permno"):
        if len(g) >= 250:
            c = np.cov(g["ret"], g["m"])
            betas[p] = c[0, 1] / c[1, 1]
    betas = pd.Series(betas)

    out = {}
    for gname in ("Pooled", "Small", "Medium", "Large"):
        if gname == "Pooled":
            gy, gn = set(gold.index), set(zero.index)
        else:
            mem = set(grp[grp == gname].index)
            gy, gn = mem & set(gold.index), mem & set(zero.index)
        y = base[base["permno"].isin(gy)].groupby("date")["ret"].mean()
        n = base[base["permno"].isin(gn)].groupby("date")["ret"].mean()
        idx = y.index.intersection(n.index)
        out[gname] = dict(y=y.loc[idx], n=n.loc[idx], m=mkt.loc[idx],
                          by=betas.reindex(list(gy)).mean(),
                          bn=betas.reindex(list(gn)).mean(),
                          ny=len(gy), nn=len(gn))
    return out


def _size_panel_body(inputs, events):
    """Panel layout follows the manuscript house style (Tables 2 and 8):
    centered panel titles between \midrule pairs, unindented row labels."""
    lines = []
    for i, (title, start, nd) in enumerate(events):
        if i:
            lines.append(r"\midrule")
        # zero-width box: long titles must not inflate the spanned columns
        lines.append(rf"\multicolumn{{7}}{{c}}{{\makebox[0pt][c]{{\textit{{{title}}}}}}} \\")
        lines.append(r"\midrule")
        for gname in ("Pooled", "Small", "Medium", "Large"):
            d = inputs[gname]
            wy = d["y"].loc[start:].head(nd)
            wn = d["n"].loc[start:].head(nd)
            wm = d["m"].loc[start:].head(nd)
            h = len(wy)
            ry = (1 + wy).prod() - 1
            rn = (1 + wn).prod() - 1
            rm = (1 + wm).prod() - 1
            raw = ry - rn
            adj = raw - (d["by"] - d["bn"]) * rm
            t_r = raw / (_calm_sd(d["y"] - d["n"]) * np.sqrt(h))
            t_a = adj / (_calm_sd((d["y"] - d["by"] * d["m"])
                                  - (d["n"] - d["bn"] * d["m"])) * np.sqrt(h))
            lines.append(rf"{gname} & {ry*100:.1f}\% & {rn*100:.1f}\% & "
                         rf"{raw*100:+.1f} & ({t_r:.1f}) & {adj*100:+.1f} & ({t_a:.1f}) \\")
    return chr(10).join(lines)


def _size_table_tex(body, caption, label, notes):
    return rf"""\begin{{table}}[htbp]
\centering
\caption{{\\ {caption}}}
\label{{{label}}}
\scriptsize
\setlength{{\tabcolsep}}{{10pt}}
\renewcommand{{\arraystretch}}{{1.2}}
\smallskip
\begin{{adjustbox}}{{max width=\textwidth}}
\begin{{tabular}}{{lcccccc}}
\toprule
 & \multicolumn{{2}}{{c}}{{Portfolio return}} & \multicolumn{{4}}{{c}}{{Differential (gold $-$ no gold)}} \\
\cmidrule(lr){{2-3}}\cmidrule(lr){{4-7}}
 & Gold & No gold & Raw & $t$ & $\beta$-adj. & $t$ \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\end{{adjustbox}}
\smallskip
\begin{{minipage}}{{\textwidth}}\scriptsize \textit{{Notes.}} {notes}\end{{minipage}}
\end{{table}}
"""


def write_size_split_tables(gold, zero):
    inputs = size_split_inputs(gold, zero)
    gs = inputs

    notes_main = (
        r"Cumulative raw returns, from daily CRSP returns, of equal-weighted portfolios of "
        r"firms with ($\tilde{d}_j>0$) and without ($\tilde{d}_j=0$) gold-clause exposure "
        r"(equation~(\ref{eq:tilde_d})) over each event window, pooled and within size "
        r"terciles formed on market capitalization at the end of 1932 (gold/non-gold firm "
        rf"counts: {gs['Pooled']['ny']}/{gs['Pooled']['nn']} pooled; "
        rf"{gs['Small']['ny']}/{gs['Small']['nn']}, {gs['Medium']['ny']}/{gs['Medium']['nn']}, "
        rf"{gs['Large']['ny']}/{gs['Large']['nn']} across terciles). "
        r"Differentials are gold minus non-gold, in percentage points; the beta-adjusted "
        r"differential subtracts $(\beta_G-\beta_N)\times R_m$, where $R_m$ is the market "
        r"return over the window and portfolio betas are estimated from daily returns over "
        rf"1926--1940 (pooled: $\beta_G={gs['Pooled']['by']:.2f}$, "
        rf"$\beta_N={gs['Pooled']['bn']:.2f}$). $t$-statistics (in parentheses) scale each "
        r"differential by $\hat\sigma\sqrt{h}$, where $h$ is the number of trading days in "
        r"the window and $\hat\sigma$ is the standard deviation of the daily differential "
        r"over the pre-abrogation period (July 1926--December 1932). The decision-day "
        r"benchmark is the close of Saturday, February~16, 1935. The November window "
        r"combines the certiorari grant in \textit{United States v.\ Bankers Trust Co.}\ "
        r"with the midterm election, for which the exchange was closed. Internet Appendix "
        r"Table~\ref{tabapp:size_split_intermediate} examines the intermediate legal events "
        r"in the same format.")
    notes_int = (
        r"Same portfolio construction, size terciles, and $t$-statistic convention as "
        r"Table~\ref{tab:event_study} in the main text; each window is three "
        r"trading days from the event date. The Irving Trust hearing (May~22--24, 1933) was "
        r"the first court hearing on the enforceability of gold clauses. \textit{In re "
        r"Missouri Pacific} (E.D.~Mo., June~20, 1934) was the first federal ruling upholding "
        r"the constitutionality of the Joint Resolution; the New York Court of Appeals "
        r"affirmed \textit{Norman v.\ Baltimore \& Ohio R.~Co.} on July~3, 1934. Certiorari "
        r"was granted in \textit{Norman} on October~8, 1934.")

    # Panel F: the full litigation episode, eve of the Joint Resolution
    # window through the Supreme Court decision, in the same format.
    nd_full = len(inputs["Pooled"]["y"].loc["1933-05-26":"1935-02-18"])
    main_events = SIZE_MAIN_EVENTS + [
        ("Panel F: Full Episode (May 26, 1933--February 18, 1935)",
         "1933-05-26", nd_full),
    ]

    for out_dir, fname, events, caption, label, notes in [
        (MS_BODY_TAB, "table1_event_study.tex", main_events,
         "Stock market responses to key legal events",
         "tab:event_study", notes_main),
        (MS_IA_TAB, "ia20_size_split_intermediate.tex", SIZE_INTERMEDIATE_EVENTS,
         "Intermediate legal events, by firm size",
         "tabapp:size_split_intermediate", notes_int),
    ]:
        body = _size_panel_body(inputs, events)
        path = os.path.join(out_dir, fname)
        with open(path, "w") as f:
            f.write(_size_table_tex(body, caption, label, notes))
        print(f"Saved: {path}")


# ---------------------------------------------------------------- main

def main():
    gold, zero = load_exposure()
    print(f"Exposure: {len(gold)} firms d>0, {len(zero)} firms d=0")

    s = build_series(gold, zero)
    print(f"Series: {len(s)} trading days ({s.index[0].date()} to {s.index[-1].date()})")

    sd_daily = diff_se(s)
    print(f"pre-abrogation daily raw diff SD {sd_daily*100:.2f}pp")

    # figures: IA versions show the adopted three-series representation; the
    # four-series versions (suffix _allseries) are embedded in the R2 letter
    for stem, title, start, end in EVENTS:
        save(make_event_zoom(s, SERIES3, title, start, end), stem, MS_IA_FIG)
        save(make_event_zoom(s, SERIES4, title, start, end),
             f"{stem}_allseries", MS_IA_FIG)

    # tables
    write_size_split_tables(gold, zero)

    # ---------------- numbers for the text -----------------
    print("\n=== NUMBERS FOR TEXT ===")
    for stem, title, start, end in EVENTS:
        st = start.strftime("%Y-%m-%d")
        nd = len(s.loc[start:end])
        raw = {c: raw_ret(s, st, nd, c) for c in ("mkt", "ew_no", "ew_yes", "dwret")}
        diff = raw["ew_yes"] - raw["ew_no"]
        t = diff / (sd_daily * np.sqrt(nd))
        print(f"{title} [{nd}d]: raw mkt {raw['mkt']*100:+.2f} no {raw['ew_no']*100:+.2f} "
              f"yes {raw['ew_yes']*100:+.2f} dw {raw['dwret']*100:+.2f} | "
              f"diff {diff*100:+.2f} (t {t:+.1f})")
    # oral-arguments aftermath (for section 3 / response letter)
    for lbl, st, nd in [("Jan 11-17, 1935 aftermath", "1935-01-11", 6),
                        ("Jan 8-17, 1935 cumulative", "1935-01-08", 9)]:
        print(f"{lbl}: mkt {raw_ret(s, st, nd, 'mkt')*100:+.2f} "
              f"dw {raw_ret(s, st, nd, 'dwret')*100:+.2f} "
              f"yes {raw_ret(s, st, nd, 'ew_yes')*100:+.2f} "
              f"no {raw_ret(s, st, nd, 'ew_no')*100:+.2f}")
    for label, dates, start, nd in OTHER_EVENTS:
        m = raw_ret(s, start, nd, "mkt")
        ry, rn = raw_ret(s, start, nd, "ew_yes"), raw_ret(s, start, nd, "ew_no")
        t = (ry - rn) / (sd_daily * np.sqrt(nd))
        print(f"{label}: mkt {m*100:+.2f} yes {ry*100:+.2f} no {rn*100:+.2f} "
              f"diff {(ry-rn)*100:+.2f} (t {t:+.1f})")


if __name__ == "__main__":
    main()
