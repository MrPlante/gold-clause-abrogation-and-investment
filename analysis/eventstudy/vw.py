"""Value-weighted variant of the event-study portfolios (exploratory).

Builds VALUE-weighted (previous-day-cap, like the market index) portfolios of
gold-exposed (d > 0) and non-exposed (d = 0) firms and produces the three
event-window figures plus the key numbers, using the same data, estimation
window, and CAR methodology as event_study_pipeline.py.

Outputs go ONLY to output/figures/event-study/ (files prefixed vw_) — nothing
is written into manuscript/. Run from the repo root:
    PYTHONPATH=code python3 -m eventstudy.vw
"""

import sys
from pathlib import Path

for _p in (str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[2])):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np
import pandas as pd

from eventstudy.pipeline import (
    EST_START, EST_END, EVENTS,
    load_crsp, load_exposure, make_event_zoom, save, window_days, raw_ret,
)

SERIES_VW = [
    ("mkt",    "Market (CRSP value-weighted)",   "#333333", "-",  1.8),
    ("vw_no",  "No gold exposure (value-wt.)",   "#d62728", ":",  2.0),
    ("vw_yes", "Gold exposure (value-wt.)",      "#2ca02c", "-.", 2.0),
]


def build_series_vw(gold, zero):
    base = load_crsp()
    date = base["date"]
    ret = base["ret"]
    pc = base["prevcap"].where(base["prevcap"] > 0)

    def vw(mask):
        p = pc.where(mask)
        return ((p * ret).groupby(date).sum(min_count=1)
                / p.groupby(date).sum(min_count=1))

    df = pd.DataFrame({
        "mkt": vw(pd.Series(True, index=base.index)),
        "vw_yes": vw(base["permno"].isin(gold.index)),
        "vw_no": vw(base["permno"].isin(zero.index)),
    })
    df.index.name = "date"
    return df.sort_index().astype(float)


def estimate_capm_vw(s):
    est = s.loc[EST_START:EST_END].dropna()
    out = {}
    for col in ("vw_yes", "vw_no"):
        b, a = np.polyfit(est.mkt, est[col], 1)
        out[col] = (a, b)
    out["n_days"] = len(est)
    return out


def car_vw(s, capm, start, n, col):
    a, b = capm[col]
    w = window_days(s, start, n)
    return (w[col] - a - b * w.mkt).sum()


def diff_car_se_vw(s, capm):
    cal = s.loc["1934-01-01":"1934-12-31"]
    cal = cal[~(("1934-06-18" <= cal.index.strftime("%Y-%m-%d"))
                & (cal.index.strftime("%Y-%m-%d") <= "1934-07-10"))]
    cal = cal[cal.index.month != 11]
    ay, by = capm["vw_yes"]
    an, bn = capm["vw_no"]
    d = (cal.vw_yes - ay - by * cal.mkt) - (cal.vw_no - an - bn * cal.mkt)
    return d.std(ddof=1)


def main():
    gold, zero = load_exposure()
    s = build_series_vw(gold, zero)
    capm = estimate_capm_vw(s)
    sd = diff_car_se_vw(s, capm)

    print(f"Estimation window: {capm['n_days']} days; "
          f"betas: vw_no {capm['vw_no'][1]:.2f}, vw_yes {capm['vw_yes'][1]:.2f}; "
          f"calm-1934 daily diff SD {sd*100:.2f}pp")
    print("\n=== VALUE-WEIGHTED NUMBERS ===")
    for stem, title, start, end in EVENTS:
        nd = len(s.loc[start:end])
        m = raw_ret(s, start, nd, "mkt")
        ry, rn = raw_ret(s, start, nd, "vw_yes"), raw_ret(s, start, nd, "vw_no")
        cy, cn = car_vw(s, capm, start, nd, "vw_yes"), car_vw(s, capm, start, nd, "vw_no")
        t = (cy - cn) / (sd * np.sqrt(nd))
        print(f"{title} [{nd}d]: raw mkt {m*100:+.2f} no {rn*100:+.2f} "
              f"yes {ry*100:+.2f} | CAR no {cn*100:+.2f} yes {cy*100:+.2f} "
              f"diff {(cy-cn)*100:+.2f} (t {t:+.1f})")
        save(make_event_zoom(s, SERIES_VW, title + " — value-weighted", start, end),
             f"vw_{stem}")


if __name__ == "__main__":
    main()
