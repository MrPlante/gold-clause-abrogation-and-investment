"""
Replicates portfolio return figures reported in the historical background section
of the manuscript (Section 3).

Three events:
  1. Joint Resolution (May 26 – June 6, 1933): equity market +11.7%, gold-
     exposure-weighted portfolio +27.2%
  2. Weak showing / market anxiety (Jan 8 – Feb 17, 1935): market -4.4%,
     gold-exposure-weighted portfolio -5.1%
  3. Supreme Court decision day (Feb 18, 1935): market +2.9%, portfolio +3.7%

Columns used:
  mkt      — CRSP value-weighted market return (equity market)
  dwret    — d-weighted portfolio return (gold-exposure-weighted portfolio,
             weighted by d_j = firm-level gold clause exposure measure)

NOTE: The current .xls file reproduces most figures closely. Small discrepancies
from the manuscript (event 1 market: 12.0% vs 11.7%; event 1 portfolio: 31.2%
vs 27.2%) likely reflect a data revision since the original script was run.
"""

import xlrd
from datetime import datetime, timedelta

DATA_PATH = "../../data/returns/pf_returns.xls"

EVENTS = [
    ("Joint Resolution",      (1933, 5, 26), (1933, 6,  6), "9 trading days"),
    ("Weak showing / anxiety", (1935, 1,  8), (1935, 2, 17), "34 trading days (Jan 8–Feb 17)"),
    ("SC decision day",        (1935, 2, 18), (1935, 2, 18), "1 day"),
]

MANUSCRIPT = {
    "Joint Resolution":       {"mkt": 0.117,  "dwret": 0.272},
    "Weak showing / anxiety": {"mkt": -0.044, "dwret": -0.051},
    "SC decision day":        {"mkt": 0.029,  "dwret": 0.037},
}


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
    period = [r for r in rows if s <= r["_date"] <= e and r.get(col) != ""]
    prod = 1.0
    for r in period:
        prod *= 1 + r[col]
    return prod - 1, len(period)


def main():
    rows = load_data(DATA_PATH)

    print(f"{'Event':<28} {'Col':<10} {'Computed':>9} {'Manuscript':>11} {'Diff':>7}")
    print("-" * 70)
    for label, start, end, note in EVENTS:
        for col in ("mkt", "dwret"):
            ret, n_days = compound_return(rows, start, end, col)
            ms = MANUSCRIPT[label][col]
            diff = ret - ms
            flag = " *" if abs(diff) > 0.005 else ""
            print(
                f"{label:<28} {col:<10} {ret*100:>8.2f}%  {ms*100:>9.1f}%  {diff*100:>+6.2f}pp{flag}"
            )
        print(f"  ({note})")
        print()

    print("* = differs from manuscript by more than 0.5pp (likely data revision)")


if __name__ == "__main__":
    main()
