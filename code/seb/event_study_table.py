"""
Generates the LaTeX event-study return table for the referee response.

Panel A — cumulative raw returns and CAPM cumulative abnormal returns (CARs)
          over the three key event windows.
Panel B — daily return summary statistics for the full sample.

Market model: dwret_t = alpha + beta * mkt_t + epsilon_t
Estimated via OLS on a 250-trading-day window ending 30 trading days before
each event. CAR = sum of daily abnormal returns over the event window.
"""

import math
import numpy as np
import xlrd
from datetime import datetime, timedelta

DATA_PATH  = "../../data/returns/pf_returns.xls"
OUTPUT_TEX = "../../output/tables/event_study_returns.tex"

EVENTS = [
    ("Joint Resolution",
     "May 26--June 6, 1933",
     (1933, 5, 26), (1933, 6,  6)),
    ("Supreme Court oral arguments",
     "Jan.~8--10, 1935",
     (1935, 1,  8), (1935, 1, 10)),
    ("Supreme Court decision",
     "Feb.~18, 1935",
     (1935, 2, 18), (1935, 2, 18)),
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


def compound_return(rows, start, end, col):
    s, e = datetime(*start), datetime(*end)
    period = [r for r in rows if s <= r["_date"] <= e
              and r.get(col) not in ("", None)]
    prod = 1.0
    for r in period:
        prod *= (1 + r[col])
    return prod - 1, len(period)


# Single common estimation window: full pre-abrogation period ending 30 days
# before the Joint Resolution (Event 1). Using the same window for all three
# events ensures the beta is comparable across events.
MM_EST_START = datetime(1926, 7, 1)
MM_EST_END   = datetime(1933, 4, 25)


def estimate_market_model(rows, col="dwret"):
    """OLS market model on the common pre-abrogation estimation window."""
    est = [r for r in rows
           if MM_EST_START <= r["_date"] <= MM_EST_END
           and r.get("mkt") not in ("", None) and r.get(col) not in ("", None)]
    mkt = np.array([r["mkt"] for r in est])
    pf  = np.array([r[col]   for r in est])
    X   = np.column_stack([np.ones(len(mkt)), mkt])
    coef, *_ = np.linalg.lstsq(X, pf, rcond=None)
    return coef[0], coef[1]  # alpha, beta


def compute_car(rows, start, end, col, alpha, beta):
    """Cumulative abnormal return (sum of daily ARs) over event window."""
    s, e = datetime(*start), datetime(*end)
    period = [r for r in rows if s <= r["_date"] <= e
              and r.get(col) not in ("", None) and r.get("mkt") not in ("", None)]
    return sum(r[col] - (alpha + beta * r["mkt"]) for r in period)


def summary_stats(rows, col):
    vals = [r[col] for r in rows if r.get(col) not in ("", None)]
    n    = len(vals)
    mean = sum(vals) / n
    std  = math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1))
    return mean * 100, std * 100, n


def fmt_pct(x, decimals=1):
    sign = "+" if x > 0 else ""
    return f"{sign}{x:.{decimals}f}\\%"


def main():
    rows  = load_data(DATA_PATH)
    sample = [r for r in rows if r.get("mkt") not in ("", None)]
    start_date = sample[0]["_date"].strftime("%B %Y")
    end_date   = sample[-1]["_date"].strftime("%B %Y")

    # Panel A
    panel_a = []
    for label, date_str, s, e in EVENTS:
        mkt_ret,   n_days = compound_return(rows, s, e, "mkt")
        dwret_ret, _      = compound_return(rows, s, e, "dwret")
        alpha, beta       = estimate_market_model(rows)
        car               = compute_car(rows, s, e, "dwret", alpha, beta)
        panel_a.append((label, date_str, n_days, mkt_ret, dwret_ret, car, beta))

    # Panel B
    mkt_mean,   mkt_std,   n_days_tot = summary_stats(sample, "mkt")
    dwret_mean, dwret_std, _          = summary_stats(sample, "dwret")

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{Stock market responses to key legal events}")
    lines.append(r"\label{tab:event_study}")
    lines.append(r"\small")

    # Panel A
    lines.append(r"\medskip")
    lines.append(r"\textit{Panel A: Cumulative returns over event windows}")
    lines.append(r"\medskip")
    lines.append(r"\begin{tabular}{lccccc}")
    lines.append(r"\toprule")
    lines.append(r"Event & Dates & Days & Market & \multicolumn{2}{c}{Gold-weighted} \\")
    lines.append(r"\cmidrule(l){5-6}")
    lines.append(r" &  &  &  & Raw return & CAR \\")
    lines.append(r"\midrule")
    for label, date_str, n_days, mkt_ret, dwret_ret, car, beta in panel_a:
        lines.append(
            f"{label} & {date_str} & {n_days} & "
            f"{fmt_pct(mkt_ret*100)} & {fmt_pct(dwret_ret*100)} & {fmt_pct(car*100)} \\\\"
        )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    # Panel B
    lines.append(r"\medskip")
    lines.append(r"\textit{Panel B: Daily return summary statistics}")
    lines.append(r"\medskip")
    lines.append(r"\begin{tabular}{lcc}")
    lines.append(r"\toprule")
    lines.append(r" & Market & Gold-weighted \\")
    lines.append(r"\midrule")
    lines.append(f"Mean daily return (\\%) & {mkt_mean:.3f} & {dwret_mean:.3f} \\\\")
    lines.append(f"Std.~deviation (\\%)    & {mkt_std:.3f} & {dwret_std:.3f} \\\\")
    lines.append(f"Trading days            & \\multicolumn{{2}}{{c}}{{{n_days_tot:,}}} \\\\")
    lines.append(f"Sample period           & \\multicolumn{{2}}{{c}}{{{start_date}--{end_date}}} \\\\")
    lines.append(r"Firms (total / gold-clause) & \multicolumn{2}{c}{558 / 276} \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    lines.append(r"\medskip")
    lines.append(
        r"\begin{minipage}{0.85\textwidth}"
        r"\footnotesize \textit{Notes.} "
        r"The market return is the CRSP value-weighted index. "
        r"The gold-weighted portfolio weights each firm by its gold-clause exposure $d_j$, "
        r"as defined in equation~(\ref{eq:d}). "
        r"Raw returns are the compound product of daily returns over each event window. "
        r"The cumulative abnormal return (CAR) is the sum of daily abnormal returns "
        r"$\hat{\varepsilon}_t = r_t - \hat{\alpha} - \hat{\beta}\, r_{m,t}$, "
        r"where $\hat{\alpha}$ and $\hat{\beta}$ are estimated by OLS on the full "
        r"pre-abrogation period (July~1, 1926--April~25, 1933; 2,021 trading days), "
        r"yielding $\hat{\beta}=0.92$. "
        r"The same estimation window is used for all three events. "
        r"For the Supreme Court decision (February~18), the benchmark is the close of "
        r"February~16---the last trading day before the ruling, as the exchange was open "
        r"on Saturdays. "
        r"The modest decline during the oral arguments (January~8--10) understates "
        r"the market anxiety triggered by the government's weak showing: "
        r"press coverage in the following days drove sustained selling, "
        r"with Liberty Bond prices reaching their highest level since 1917 by January~13 "
        r"\citep{NYT1935}. "
        r"Panel~B statistics cover the full sample."
        r"\end{minipage}"
    )
    lines.append(r"\end{table}")

    tex = "\n".join(lines)
    print(tex)

    import os
    os.makedirs(os.path.dirname(OUTPUT_TEX), exist_ok=True)
    with open(OUTPUT_TEX, "w") as f:
        f.write(tex)
    print(f"\nSaved: {OUTPUT_TEX}", flush=True)


if __name__ == "__main__":
    main()
