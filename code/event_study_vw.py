"""Value-weighted variant of the event-study portfolios (exploratory).

Builds VALUE-weighted (previous-day-cap, like the market index) portfolios of
gold-exposed (d > 0) and non-exposed (d = 0) firms and produces the three
event-window figures plus the key numbers, using the same data, estimation
window, and CAR methodology as event_study_pipeline.py.

Outputs go ONLY to output/figures/event-study/ (files prefixed vw_) — nothing
is written into manuscript/. Run: python3 code/event_study_vw.py
"""

import io
import subprocess

import numpy as np
import pandas as pd

from event_study_pipeline import (
    DB, SAMPLE_START, SAMPLE_END, EST_START, EST_END, EVENTS,
    load_exposure, make_event_zoom, save, window_days, raw_ret,
)

SERIES_VW = [
    ("mkt",    "Market (CRSP value-weighted)",   "#333333", "-",  1.8),
    ("vw_no",  "No gold exposure (value-wt.)",   "#d62728", ":",  2.0),
    ("vw_yes", "Gold exposure (value-wt.)",      "#2ca02c", "-.", 2.0),
]


def build_series_vw(gold, zero):
    gold_p = ",".join(str(p) for p in gold.index)
    zero_p = ",".join(str(p) for p in zero.index)
    sql = f"""
    with gold(permno) as (select unnest(array[{gold_p}]::int[])),
    zer(permno) as (select unnest(array[{zero_p}]::int[])),
    lagged as (
      select permno, date, ret,
             lag(cap) over (partition by permno order by date) as prevcap
      from gold_claude.crsp),
    base as (
      select l.date, l.ret, l.prevcap,
             (g.permno is not null) as is1,
             (z.permno is not null) as is0
      from lagged l
      left join gold g on g.permno = l.permno
      left join zer z on z.permno = l.permno
      where l.ret is not null
        and l.date between '{SAMPLE_START}' and '{SAMPLE_END}')
    select date,
      sum(prevcap*ret) filter (where prevcap > 0)
        / nullif(sum(prevcap) filter (where prevcap > 0), 0)          as mkt,
      sum(prevcap*ret) filter (where is1 and prevcap > 0)
        / nullif(sum(prevcap) filter (where is1 and prevcap > 0), 0)  as vw_yes,
      sum(prevcap*ret) filter (where is0 and prevcap > 0)
        / nullif(sum(prevcap) filter (where is0 and prevcap > 0), 0)  as vw_no
    from base group by date order by date
    """
    out = subprocess.run(["psql", DB, "-Atc", sql, "-F", ","],
                         capture_output=True, text=True, check=True)
    df = pd.read_csv(io.StringIO(out.stdout),
                     names=["date", "mkt", "vw_yes", "vw_no"])
    df["date"] = pd.to_datetime(df.date)
    return df.set_index("date").astype(float)


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
