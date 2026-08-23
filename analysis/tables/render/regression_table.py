"""LaTeX rendering for Table 3 investment regressions."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from config import OMITTED_YEAR, SAMPLE_YEARS
from lib.latex import fmt_coef, fmt_se, model_pvalue, model_se

TABLE4_NOTES = (
    r"\scriptsize{\textit{Notes.} This table reports results from panel regressions of "
    r"net investment on $Q$, gold clause exposure $\tilde{d}$ (as defined in equation "
    r"(\ref{eq:tilde_d})), and year $\times$ $\tilde{d}$ interactions, where 1932 is the "
    r"omitted category. Column 1 presents the classical investment regression (equation "
    r"(\ref{eq:classic_inv_reg})) without gold clause exposure. Column 2 reports our "
    r"baseline debt overhang specification (equation (\ref{eq:parameterization})). Columns "
    r"3 and 4 report estimation results using the baseline specification on restricted "
    r"samples: Column 3 excludes firms with bonds maturing between 1931 and 1934, and Column 4 "
    r"excludes firms that retired their gold-clause debt between 1931 and 1935. Column 5 uses an "
    r"alternative exposure measure that scales gold-clause debt by the firm's total fixed "
    r"claims---bank debt, bonds, and preferred stock. The measure is frozen at its 1930 value "
    r"after 1930; before 1930, it uses the lagged bond share of fixed claims. It is defined only "
    r"for firms with fixed claims, which restricts the sample accordingly. Columns 6 and 7 "
    r"report results from placebo tests that replace the numerator of $\tilde{d}$ with "
    r"preferred shares and bank debt, respectively---securities that did not contain gold "
    r"clauses. All regressions include firm and year fixed effects. All variables are "
    r"winsorized at the 0.5\% and 99.5\% levels within each year. Standard errors in "
    r"parentheses are two-way clustered by firm and year. $^{*}p<0.10$, $^{**}p<0.05$, "
    r"$^{***}p<0.01$.}"
)

COLUMN_HEADERS = [
    ("Classic", "(1)"),
    ("Overhang", "(2)"),
    ("No maturity", "(3)"),
    ("No redemption", "(4)"),
    ("Fixed claims", "(5)"),
    ("Pref. shares", "(6)"),
    ("Bank Debt", "(7)"),
]

MODEL_ORDER = [
    "classic",
    "overhang",
    "no_maturity",
    "no_redemption",
    "fixed_claims",
    "pref_shares",
    "bank_debt",
]

EXPOSURE_BY_MODEL = {
    "classic": None,
    "overhang": "d",
    "no_maturity": "d",
    "no_redemption": "d",
    "fixed_claims": "dalt",
    "pref_shares": "ps",
    "bank_debt": "bd",
}

INTERACTION_YEARS = [y for y in range(SAMPLE_YEARS[0], SAMPLE_YEARS[1] + 1) if y != OMITTED_YEAR]


@dataclass
class CoefCell:
    coef: float | None
    se: float | None
    p: float | None


def _fmt_n(n: int) -> str:
    return f"{n:,}$\\phantom{{000}}$"


def _cell(model, term: str | None) -> CoefCell:
    if model is None or term is None:
        return CoefCell(None, None, None)
    coef = model.coef()
    if term not in coef.index:
        return CoefCell(None, None, None)
    se = model_se(model)
    p = model_pvalue(model)
    return CoefCell(
        float(coef[term]),
        float(se[term]) if not pd.isna(se[term]) else None,
        float(p[term]) if term in p.index and not pd.isna(p[term]) else None,
    )


def _coef_row(label: str, cells: list[CoefCell]) -> tuple[str, str]:
    coef_line = [label]
    se_line = [""]
    for cell in cells:
        if cell.coef is None:
            coef_line.append("")
            se_line.append("")
        else:
            coef_line.append(fmt_coef(cell.coef, cell.p if cell.p is not None else float("nan")))
            se_line.append(fmt_se(cell.se) if cell.se is not None else "")
    return " & ".join(coef_line) + r" \\", " & ".join(se_line) + r" \\"


def render_table3_latex(models: dict[str, object]) -> str:
    ordered = [models[k] for k in MODEL_ORDER]

    q_cells = [_cell(m, "var_Q") for m in ordered]
    q_coef, q_se = _coef_row("Q", q_cells)

    d_cells = [
        _cell(m, EXPOSURE_BY_MODEL[key]) if EXPOSURE_BY_MODEL[key] else CoefCell(None, None, None)
        for key, m in zip(MODEL_ORDER, ordered, strict=True)
    ]
    d_coef, d_se = _coef_row(r"\ensuremath{\tilde{d}}", d_cells)

    year_rows: list[tuple[str, str]] = []
    for year in INTERACTION_YEARS:
        cells = []
        for key, m in zip(MODEL_ORDER, ordered, strict=True):
            exposure = EXPOSURE_BY_MODEL[key]
            term = f"{exposure}_year_{year}" if exposure else None
            cells.append(_cell(m, term))
        label = rf"\ensuremath{{\text{{{year}}} \times \tilde{{d}}}}"
        year_rows.append(_coef_row(label, cells))

    header1 = " & ".join(
        [""]
        + [rf"\multicolumn{{1}}{{c}}{{{name}}}" for name, _ in COLUMN_HEADERS]
    )
    header2 = " & ".join([""] + [rf"\multicolumn{{1}}{{c}}{{{num}}}" for _, num in COLUMN_HEADERS])

    fe_row = " & ".join(
        ["Firm FE"] + [r"\multicolumn{1}{c}{Yes}"] * len(COLUMN_HEADERS)
    )
    year_fe_row = " & ".join(
        ["Year FE"] + [r"\multicolumn{1}{c}{Yes}"] * len(COLUMN_HEADERS)
    )
    r2_row = " & ".join(
        [r"\ensuremath{R^2}"]
        + [f"{m._r2:.3f}" for m in ordered]
    )
    n_row = " & ".join(
        ["Observations"]
        + [rf"\multicolumn{{1}}{{r}}{{{_fmt_n(int(m._N))}}}" for m in ordered]
    )

    lines = [
        r"\begin{table}[p]\centering",
        r"\caption{\\ Leverage and investment}",
        r"\scriptsize",
        r"\label{tab:inv_main}",
        r"\setlength{\tabcolsep}{3.5pt}",
        r"\renewcommand{\arraystretch}{1.2}{",
        r"    \def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"    \begin{tabular}{l*{7}{D{.}{.}{-1}}}",
        r"    \toprule",
        f"    {header1} \\\\",
        f"    {header2} \\\\",
        r"    \midrule",
        f"    {q_coef}",
        f"    {q_se}",
        f"    {d_coef}",
        f"    {d_se}",
    ]
    for coef_line, se_line in year_rows:
        lines.extend([f"    {coef_line}", f"    {se_line}"])
    lines.extend(
        [
            r"    \midrule",
            f"    {fe_row} \\\\",
            f"    {year_fe_row} \\\\",
            f"    {r2_row} \\\\",
            f"    {n_row} \\\\",
            r"    \bottomrule",
            r"    \end{tabular}",
            r"}\\",
            r"",
            r"\vspace*{3mm} \justifying \noindent",
            TABLE4_NOTES,
            r"\end{table}",
        ]
    )
    return "\n".join(lines)
