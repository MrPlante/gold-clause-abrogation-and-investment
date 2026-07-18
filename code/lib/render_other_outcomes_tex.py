"""LaTeX rendering for Table 4 other-outcomes regressions."""

from __future__ import annotations

from config import OMITTED_YEAR, SAMPLE_YEARS
from lib.latex import fmt_coef, fmt_se, model_pvalue, model_se
from lib.other_outcomes import MODEL_ORDER
from lib.render_investment_reg_tex import CoefCell, _cell, _coef_row, _fmt_n

TABLE4_NOTES = (
    r"\scriptsize{\textit{Notes.} This table reports results from panel regressions of "
    r"various firm outcomes on $Q$, gold clause exposure $\tilde{d}$ (as defined in equation "
    r"(\ref{eq:tilde_d})), and year $\times$ $\tilde{d}$ interactions, where 1932 is the "
    r"omitted category. Columns 1--3 test the debt overhang prediction that firms with gold "
    r"exposure should increase payouts during the litigation period: Payout is total annual "
    r"equity payout, Dividend is cash dividends, and Net rep.\ is net share repurchases, all "
    r"normalized by the book value of common stock. Columns 4--6 examine whether gold exposure "
    r"is associated with changes in profitability, cash holdings, or leverage that might "
    r"confound the payout results: Profits is net income; Cash includes cash and marketable "
    r"securities (both normalized by fixed capital); and Leverage is book leverage. All "
    r"regressions include firm and year fixed effects. All variables are winsorized at the "
    r"0.5\% and 99.5\% levels within each year. Standard errors in parentheses are two-way "
    r"clustered by firm and year. $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.}"
)

COLUMN_HEADERS = [
    ("Payout", "(1)"),
    ("Dividend", "(2)"),
    ("Net rep.", "(3)"),
    ("Profits", "(4)"),
    ("Cash", "(5)"),
    ("Leverage", "(6)"),
]

INTERACTION_YEARS = [y for y in range(SAMPLE_YEARS[0], SAMPLE_YEARS[1] + 1) if y != OMITTED_YEAR]


def render_table4_latex(models: dict[str, object]) -> str:
    ordered = [models[k] for k in MODEL_ORDER]

    q_coef, q_se = _coef_row("Q", [_cell(m, "var_Q") for m in ordered])
    d_coef, d_se = _coef_row(
        r"\ensuremath{\tilde{d}}",
        [_cell(m, "d") for m in ordered],
    )

    year_rows: list[tuple[str, str]] = []
    for year in INTERACTION_YEARS:
        label = rf"\ensuremath{{\text{{{year}}} \times \tilde{{d}}}}"
        cells = [_cell(m, f"d_year_{year}") for m in ordered]
        year_rows.append(_coef_row(label, cells))

    header1 = " & ".join(
        [""] + [rf"\multicolumn{{1}}{{c}}{{{name}}}" for name, _ in COLUMN_HEADERS]
    )
    header2 = " & ".join(
        [""] + [rf"\multicolumn{{1}}{{c}}{{{num}}}" for _, num in COLUMN_HEADERS]
    )
    fe_row = " & ".join(["Firm FE"] + [r"\multicolumn{1}{c}{Yes}"] * len(COLUMN_HEADERS))
    year_fe_row = " & ".join(["Year FE"] + [r"\multicolumn{1}{c}{Yes}"] * len(COLUMN_HEADERS))
    r2_row = " & ".join([r"\ensuremath{R^2}"] + [f"{m._r2:.3f}" for m in ordered])
    n_row = " & ".join(
        ["Observations"]
        + [rf"\multicolumn{{1}}{{r}}{{{_fmt_n(int(m._N))}}}" for m in ordered]
    )

    lines = [
        r"\begin{table}[p]\centering",
        r"\caption{\\ Gold clause exposure and other outcomes}",
        r"\scriptsize",
        r"\label{tab:other_outcomes}",
        r"\renewcommand{\arraystretch}{1.2}{",
        r"    \def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"    \begin{tabular}{l*{6}{D{.}{.}{-1}}}",
        r"        \toprule",
        f"        {header1} \\\\",
        f"        {header2} \\\\",
        r"        \midrule",
        f"        {q_coef}",
        f"        {q_se}",
        f"        {d_coef}",
        f"        {d_se}",
    ]
    for coef_line, se_line in year_rows:
        lines.extend([f"        {coef_line}", f"        {se_line}"])
    lines.extend(
        [
            r"        \midrule",
            f"        {fe_row} \\\\",
            f"        {year_fe_row} \\\\",
            f"        {r2_row} \\\\",
            f"        {n_row} \\\\",
            r"        \bottomrule",
            r"    \end{tabular}",
            r"}\\",
            r"",
            r"\vspace*{3mm} \justifying \noindent",
            TABLE4_NOTES,
            r"\end{table}",
        ]
    )
    return "\n".join(lines)
