"""
IA Table 17 — Table 6 columns 2-10 re-estimated with industry-year FEs.

Reads Stata output from output/tables/t6_indyear_robustness.csv (produced by
code/mete/A12_controls_indyear.do) and renders a landscape LaTeX table.
"""

from __future__ import annotations

import csv
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config import REFACTOR_OUTPUT_TABLES_APPENDIX

CSV_PATH = (
    Path(__file__).resolve().parents[4]
    / "output" / "tables" / "t6_indyear_robustness.csv"
)

MANUSCRIPT_APPENDIX = (
    Path(__file__).resolve().parents[4]
    / "manuscript" / "tables" / "online-appendix"
)

COL_ORDER = [
    "all_controls_linear",
    "q_deciles",
    "logasset_deciles",
    "netinc_deciles",
    "cash_deciles",
    "payout_deciles",
    "booklev_deciles",
    "marketlev_deciles",
    "logltl_deciles",
]

DISPLAY_TERMS: list[tuple[str, str]] = [
    ("Q", "var_Q"),
    (r"\ensuremath{\tilde{d}}", "d"),
    (r"\ensuremath{\text{1933} \times \tilde{d}}", "d_1933"),
    (r"\ensuremath{\text{1934} \times \tilde{d}}", "d_1934"),
    (r"\ensuremath{\text{After} \times \tilde{d}}", "d_After"),
]

COLUMN_HEADERS_ROW1 = [
    "All controls",
    "Q",
    "Assets",
    "NI/assets",
    "Cash/assets",
    "Payout",
    "Book leverage",
    "Market leverage",
    "LT lia.",
]

COLUMN_HEADERS_ROW2 = [
    "linear",
    "deciles",
    "deciles",
    "deciles",
    "deciles",
    "deciles",
    "deciles",
    "deciles",
    "deciles",
]

TABLE_NOTES = (
    r"\scriptsize{\textit{Notes.} This table replicates columns 2--10 of Table~\ref{tab:controls} "
    r"replacing firm and year fixed effects (\texttt{absorb(permno year)}) with firm and "
    r"industry-year fixed effects (\texttt{absorb(permno sic2\_year)}), so that all specifications "
    r"share the same fixed-effect structure as column 1 of Table~\ref{tab:controls}. The "
    r"characteristic-interacted controls are identical to those in Table~\ref{tab:controls}: "
    r"column (1) includes all 1930 firm characteristics interacted with year indicators as linear "
    r"controls; columns (2)--(9) each include decile dummies for a single 1930 characteristic "
    r"interacted with year indicators. All regressions include firm and SIC2 industry-year fixed "
    r"effects. All variables are winsorized at the 0.5\% and 99.5\% levels within each year. "
    r"Standard errors in parentheses are two-way clustered by firm and year. "
    r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.}"
)


def _stars(p: float) -> str:
    if p < 0.01: return r"\sym{***}"
    if p < 0.05: return r"\sym{**}"
    if p < 0.10: return r"\sym{*}"
    return ""


def load_csv() -> dict[str, dict[str, dict]]:
    data: dict[str, dict[str, dict]] = {}
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            col, term = row["col"], row["term"]
            data.setdefault(col, {})[term] = {
                "coef": float(row["coef"]),
                "se":   float(row["se"]),
                "pval": float(row["pval"]),
                "N":    int(row["N"]),
            }
    return data


def render(data: dict) -> str:
    n_cols = len(COL_ORDER)

    header1 = " & ".join(
        [""] + [rf"\multicolumn{{1}}{{c}}{{{h}}}" for h in COLUMN_HEADERS_ROW1]
    )
    header2 = " & ".join(
        [""] + [rf"\multicolumn{{1}}{{c}}{{{h}}}" for h in COLUMN_HEADERS_ROW2]
    )
    header3 = " & ".join(
        [""] + [rf"\multicolumn{{1}}{{c}}{{({i})}}" for i in range(1, n_cols + 1)]
    )

    lines = [
        r"\begin{landscape}",
        r"\begin{table}[t!]\centering",
        r"\caption{\\ Gold clause exposure and net investment with controls: industry-year fixed effects}",
        r"\scriptsize",
        r"\label{tabapp:controls_indyear}",
        r"\renewcommand{\arraystretch}{1.2}{",
        r"    \def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"    \resizebox{\linewidth}{!}{",
        rf"    \begin{{tabular}}{{l*{{{n_cols}}}{{D{{.}}{{.}}{{-1}}}}}}",
        r"        \toprule",
        f"        {header1} \\\\",
        f"        {header2} \\\\",
        f"        {header3} \\\\",
        r"        \midrule",
    ]

    for label, term in DISPLAY_TERMS:
        coef_cells = []
        se_cells   = []
        for col in COL_ORDER:
            r = data[col][term]
            coef_cells.append(f"{r['coef']:.3f}{_stars(r['pval'])}")
            se_cells.append(f"({r['se']:.3f})")
        coef_row = f"{label:<52} & " + " & ".join(
            rf"     {c:<18}" for c in coef_cells
        ) + r"\\"
        se_row = " " * 52 + " & " + " & ".join(
            rf"     {s:<18}" for s in se_cells
        ) + r"\\"
        lines.append(f"        {coef_row}")
        lines.append(f"        {se_row}")

    # FE rows — all columns have firm + industry-year FE
    fe_row     = " & ".join(["Firm FE"]          + [r"\multicolumn{1}{c}{Yes}"] * n_cols)
    year_fe    = " & ".join(["Year FE"]           + [r"\multicolumn{1}{c}{No}"]  * n_cols)
    ind_fe     = " & ".join(["Industry-year FE"]  + [r"\multicolumn{1}{c}{Yes}"] * n_cols)

    # R2: not directly available from CSV — omit for this table
    n_vals = [data[col]["var_Q"]["N"] for col in COL_ORDER]
    n_row = " & ".join(
        ["Observations"]
        + [rf"\multicolumn{{1}}{{r}}{{{n:,}\phantom{{0}}}}" for n in n_vals]
    )

    lines.extend([
        r"        \midrule",
        f"        {fe_row} \\\\",
        f"        {year_fe} \\\\",
        f"        {ind_fe} \\\\",
        f"        {n_row} \\\\",
        r"        \bottomrule",
        r"    \end{tabular}",
        r"    }",
        r"}\\",
        r"\justifying \noindent",
        TABLE_NOTES,
        r"\end{table}",
        r"\end{landscape}",
    ])

    return "\n".join(lines)


def main() -> Path:
    data = load_csv()
    tex = render(data)

    for out_dir in [REFACTOR_OUTPUT_TABLES_APPENDIX, MANUSCRIPT_APPENDIX]:
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / "17_controls_indyear.tex"
        out.write_text(tex, encoding="utf-8")
        print(f"Wrote -> {out}")

    return MANUSCRIPT_APPENDIX / "17_controls_indyear.tex"


if __name__ == "__main__":
    main()
