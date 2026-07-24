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
  manuscript/figures/body/event{1,2,3}_*.pdf                  (Figures 3-5)
  manuscript/figures/online-appendix/event_overview.pdf       (Figure IA.2)
  manuscript/figures/online-appendix/midterm_1934.pdf         (Figure IA.3)
  manuscript/tables/body/table1_event_study.tex               (Table 1)
  manuscript/tables/online-appendix/ia20_other_events.tex     (Table IA.20)

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
EST_START, EST_END = "1926-07-01", "1933-04-25"   # pre-abrogation window

SERIES4 = [
    ("mkt",    "Market (CRSP value-weighted)",    "#333333", "-",  1.8),
    ("ew_no",  "No gold exposure (equal-wt.)",    "#d62728", ":",  2.0),
    ("ew_yes", "Gold exposure (equal-wt.)",       "#2ca02c", "-.", 2.0),
    ("dwret",  "Gold exposure (exposure-wt.)",    "#1f77b4", "--", 2.2),
]
SERIES2 = [SERIES4[0], SERIES4[3]]

# (stem, title, window start, window end) -- Table 1 / manuscript figures
EVENTS = [
    ("event1_joint_resolution", "Joint Resolution (May 26–June 6, 1933)",
     datetime(1933, 5, 26), datetime(1933, 6, 6)),
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

MIDTERM = ("midterm_1934", "Cert. Grant & Midterm Election (Nov. 5–7, 1934)",
           datetime(1934, 11, 5), datetime(1934, 11, 7))

OVERVIEW_ANCHOR = datetime(1933, 3, 31)
OVERVIEW_END = datetime(1935, 4, 30)
OVERVIEW_EVENTS = [
    (datetime(1933, 4, 19), "Gold standard suspended", 0.55),
    (datetime(1933, 6, 5),  "Joint Resolution (abrogation)", 0.98),
    (datetime(1935, 1, 8),  "Supreme Court oral arguments", 0.55),
    (datetime(1935, 2, 18), "Supreme Court decision", 0.98),
]


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


def estimate_capm(s):
    """alpha/beta of each portfolio vs mkt over the pre-abrogation window."""
    est = s.loc[EST_START:EST_END].dropna()
    out = {}
    for col in ("ew_yes", "ew_no", "dwret"):
        b, a = np.polyfit(est.mkt, est[col], 1)
        out[col] = (a, b)
    out["n_days"] = len(est)
    return out


def window_days(s, start, n):
    return s.loc[start:].head(n)


def raw_ret(s, start, n, col):
    return (1 + window_days(s, start, n)[col]).prod() - 1


def car(s, capm, start, n, col):
    a, b = capm[col]
    w = window_days(s, start, n)
    return (w[col] - a - b * w.mkt).sum()


def diff_car_se(s, capm):
    """Daily SD of the abnormal ew_yes-ew_no differential in calm 1934."""
    cal = s.loc["1934-01-01":"1934-12-31"]
    cal = cal[~(("1934-06-18" <= cal.index.strftime("%Y-%m-%d"))
                & (cal.index.strftime("%Y-%m-%d") <= "1934-07-10"))]
    cal = cal[cal.index.month != 11]
    ay, by = capm["ew_yes"]
    an, bn = capm["ew_no"]
    d = (cal.ew_yes - ay - by * cal.mkt) - (cal.ew_no - an - bn * cal.mkt)
    return d.std(ddof=1)


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


def make_overview(s, series):
    win = s.loc[OVERVIEW_ANCHOR:OVERVIEW_END]
    cum = (1 + win.fillna(0)).cumprod()
    cum = cum / cum.iloc[0] * 100

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    for col, label, color, ls, lw in series:
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


def save(fig, stem, target_dir):
    path = os.path.join(target_dir, f"{stem}.pdf")
    fig.savefig(path, bbox_inches="tight", dpi=150)
    print(f"Saved: {path}")
    plt.close(fig)


# ---------------------------------------------------------------- tables

def fmt_pct(x, dec=1):
    return f"{x*100:+.{dec}f}\\%"


def write_event_table(s, gold, zero):
    ev = []
    for stem, _, start, end in EVENTS:
        w = s.loc[start:end]
        ev.append((start, end, len(w)))

    rows_a = []
    meta = [("Joint Resolution", "May 26--June 6, 1933"),
            ("Supreme Court oral arguments", "Jan.~8--10, 1935"),
            ("Supreme Court decision", "Feb.~18, 1935")]
    for (label, dates), (start, end, nd) in zip(meta, ev):
        st = start.strftime("%Y-%m-%d")
        raw = [raw_ret(s, st, nd, c) for c in ("mkt", "ew_no", "ew_yes", "dwret")]
        rows_a.append(f"{label} & {dates} & {nd} & " +
                      " & ".join(fmt_pct(r) for r in raw) + r" \\")

    tex = rf"""\begin{{table}}[htbp]
\centering
\caption{{\\ Stock market responses to key legal events}}
\label{{tab:event_study}}
\small
\setlength{{\tabcolsep}}{{4pt}}
\medskip
\begin{{adjustbox}}{{max width=\textwidth}}
\begin{{tabular}}{{lcccccc}}
\toprule
Event & Dates & Days & Market & No gold & Gold & Gold \\
 & & & & (equal-wt.) & (equal-wt.) & (exposure-wt.) \\
\midrule
{chr(10).join(rows_a)}
\bottomrule
\end{{tabular}}
\end{{adjustbox}}
\medskip
\begin{{minipage}}{{0.95\textwidth}}\footnotesize \textit{{Notes.}} This table reports cumulative raw returns, the compound product of daily returns over each event window. All series are constructed from CRSP daily returns. The market return is value-weighted using previous-day market capitalization and reproduces the CRSP value-weighted index. Firms are classified by the gold-clause exposure measure $d_j$ defined in equation~(\ref{{eq:d}}): the two equal-weighted portfolios contain firms with $d_j>0$ ({len(gold)} firms) and $d_j=0$ ({len(zero)} firms), respectively, and the exposure-weighted portfolio weights firms with $d_j>0$ by $w_j = d_j/\sum_k d_k$. Portfolios are rebalanced daily over firms with a return on each day. For the Supreme Court decision (February~18), the benchmark is the close of February~16---the last trading day before the ruling, as the exchange was open on Saturdays. The modest decline during the oral arguments (January~8--10) understates the market anxiety triggered by the government's weak showing: press coverage in the following days drove sustained selling, with Liberty Bond prices reaching their highest level since 1917 by January~13 \citep{{NYT1935}}. Internet Appendix Section~\ref{{sec:ia_other_events}} examines the remaining legal and political events of the litigation period in a CAPM cumulative-abnormal-return framework.\end{{minipage}}
\end{{table}}
"""
    path = os.path.join(MS_BODY_TAB, "table1_event_study.tex")
    with open(path, "w") as f:
        f.write(tex)
    print(f"Saved: {path}")


def write_other_events_table(s, capm, sd_daily):
    rows = []
    for label, dates, start, nd in OTHER_EVENTS + [JR_ROW]:
        m = raw_ret(s, start, nd, "mkt")
        cy = car(s, capm, start, nd, "ew_yes")
        cn = car(s, capm, start, nd, "ew_no")
        diff = cy - cn
        t = diff / (sd_daily * np.sqrt(nd))
        rows.append(f"{label} & {dates} & {nd} & {fmt_pct(m)} & {fmt_pct(cy)} & "
                    f"{fmt_pct(cn)} & {fmt_pct(diff)} & {t:.1f} \\\\")
    body = chr(10).join(rows[:-1]) + chr(10) + r"\midrule" + chr(10) + rows[-1]

    tex = rf"""\begin{{table}}[htbp]
\centering
\caption{{\\ Stock market responses to other legal and political events}}
\label{{tab:other_events}}
\footnotesize
\setlength{{\tabcolsep}}{{4pt}}
\medskip
\begin{{adjustbox}}{{max width=\textwidth}}
\begin{{tabular}}{{lccccccc}}
\toprule
 & & & & \multicolumn{{2}}{{c}}{{CAR (equal-wt.)}} & & \\
\cmidrule(lr){{5-6}}
Event & Dates & Days & Market & Gold & No gold & Diff. & $t$ \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\end{{adjustbox}}
\medskip
\begin{{minipage}}{{0.95\textwidth}}\footnotesize \textit{{Notes.}} This table reports stock market responses to the intermediate legal and political events of the gold clause litigation, using the same portfolio construction as Table~\ref{{tab:event_study}} in the main text. The cumulative abnormal return (CAR) is the sum of daily abnormal returns $\hat{{\varepsilon}}_t = r_t - \hat{{\alpha}} - \hat{{\beta}}\, r_{{m,t}}$, where $\hat{{\alpha}}$ and $\hat{{\beta}}$ are estimated by OLS on the pre-abrogation period (July~1, 1926--April~25, 1933; {capm['n_days']:,} trading days); the estimated betas are {capm['ew_yes'][1]:.2f} for the gold-exposed and {capm['ew_no'][1]:.2f} for the non-exposed equal-weighted portfolio, with the same estimation window used for all events. ``Diff.''\ is the difference between the cumulative abnormal returns of the gold-exposed and non-exposed equal-weighted portfolios. The $t$-statistic scales this difference by $\hat\sigma\sqrt{{h}}$, where $h$ is the number of trading days in the window and $\hat\sigma = {sd_daily*100:.2f}$ percentage points is the standard deviation of the daily abnormal-return differential over calm trading days in 1934 (excluding the event windows in this table). The Irving Trust hearing (May~22--24, 1933) was the first court hearing on the enforceability of gold clauses. \textit{{In re Missouri Pacific}} (E.D.~Mo., June~20, 1934) was the first federal ruling upholding the constitutionality of the Joint Resolution; the New York Court of Appeals affirmed \textit{{Norman v.\ Baltimore \& Ohio R.~Co.}} on July~3, 1934. Certiorari was granted in \textit{{Norman}} on October~8, 1934 and in \textit{{United States v.\ Bankers Trust Co.}} on November~5, 1934; the New York Stock Exchange was closed on November~6, 1934 for the midterm election, so the November window mixes the certiorari grant with the election result. The Joint Resolution window from Table~\ref{{tab:event_study}} is repeated for reference.\end{{minipage}}
\end{{table}}
"""
    path = os.path.join(MS_IA_TAB, "ia20_other_events.tex")
    with open(path, "w") as f:
        f.write(tex)
    print(f"Saved: {path}")


# ---------------------------------------------------------------- main

def main():
    gold, zero = load_exposure()
    print(f"Exposure: {len(gold)} firms d>0, {len(zero)} firms d=0")

    s = build_series(gold, zero)
    print(f"Series: {len(s)} trading days ({s.index[0].date()} to {s.index[-1].date()})")

    capm = estimate_capm(s)
    sd_daily = diff_car_se(s, capm)
    print(f"Estimation window: {capm['n_days']} days; betas: "
          f"ew_yes {capm['ew_yes'][1]:.3f}, ew_no {capm['ew_no'][1]:.3f}, "
          f"dwret {capm['dwret'][1]:.3f}; calm-1934 daily diff SD {sd_daily*100:.2f}pp")

    # figures
    for stem, title, start, end in EVENTS:
        save(make_event_zoom(s, SERIES4, title, start, end), stem, MS_BODY_FIG)
    save(make_event_zoom(s, SERIES4, MIDTERM[1], MIDTERM[2], MIDTERM[3]),
         MIDTERM[0], MS_IA_FIG)
    save(make_overview(s, SERIES2), "event_overview", MS_IA_FIG)

    # tables
    write_event_table(s, gold, zero)
    write_other_events_table(s, capm, sd_daily)

    # ---------------- numbers for the text -----------------
    print("\n=== NUMBERS FOR TEXT ===")
    for stem, title, start, end in EVENTS + [MIDTERM]:
        st = start.strftime("%Y-%m-%d")
        nd = len(s.loc[start:end])
        raw = {c: raw_ret(s, st, nd, c) for c in ("mkt", "ew_no", "ew_yes", "dwret")}
        cars = {c: car(s, capm, st, nd, c) for c in ("ew_no", "ew_yes", "dwret")}
        diff = cars["ew_yes"] - cars["ew_no"]
        t = diff / (sd_daily * np.sqrt(nd))
        print(f"{title} [{nd}d]: raw mkt {raw['mkt']*100:+.2f} no {raw['ew_no']*100:+.2f} "
              f"yes {raw['ew_yes']*100:+.2f} dw {raw['dwret']*100:+.2f} | "
              f"CAR no {cars['ew_no']*100:+.2f} yes {cars['ew_yes']*100:+.2f} "
              f"dw {cars['dwret']*100:+.2f} | diff {diff*100:+.2f} (t {t:+.1f})")
    # oral-arguments aftermath (for section 3 / response letter)
    for lbl, st, nd in [("Jan 11-17, 1935 aftermath", "1935-01-11", 6),
                        ("Jan 8-17, 1935 cumulative", "1935-01-08", 9)]:
        print(f"{lbl}: mkt {raw_ret(s, st, nd, 'mkt')*100:+.2f} "
              f"dw {raw_ret(s, st, nd, 'dwret')*100:+.2f} "
              f"yes {raw_ret(s, st, nd, 'ew_yes')*100:+.2f} "
              f"no {raw_ret(s, st, nd, 'ew_no')*100:+.2f}")
    for label, dates, start, nd in OTHER_EVENTS:
        m = raw_ret(s, start, nd, "mkt")
        cy, cn = car(s, capm, start, nd, "ew_yes"), car(s, capm, start, nd, "ew_no")
        t = (cy - cn) / (sd_daily * np.sqrt(nd))
        print(f"{label}: mkt {m*100:+.2f} CARyes {cy*100:+.2f} CARno {cn*100:+.2f} "
              f"diff {(cy-cn)*100:+.2f} (t {t:+.1f})")


if __name__ == "__main__":
    main()
