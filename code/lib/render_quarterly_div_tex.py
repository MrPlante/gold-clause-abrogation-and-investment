"""LaTeX rendering for IA Table 12 quarter-specific dividend regressions."""

from __future__ import annotations

from config import OMITTED_YEAR, SAMPLE_YEARS
from lib.quarterly_dividends import MODEL_ORDER
from lib.render_investment_reg_tex import _cell, _coef_row, _fmt_n

TABLE12_NOTES = (
    r"\scriptsize{\textit{Notes.} This table reports results from panel regressions of cash "
    r"dividends on $Q$, gold clause exposure $\tilde{d}$, and year $\times$ $\tilde{d}$ "
    r"interactions, where 1932 is the omitted category. Column 1 replicates the annual "
    r"dividend specification (Table \ref{tab:other_outcomes}, column 2). Columns 2--5 use "
    r"the same specification but restrict the sample to firm-years with data from Q1, Q2, Q3, "
    r"or Q4 only; the dependent variable is quarterly cash dividend (sum of monthly dividends "
    r"in that quarter) normalized by book common stock. All regressions include firm and year "
    r"fixed effects. Standard errors in parentheses are clustered by firm. "
    r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.}"
)

COLUMN_HEADERS = [
    ("Annual", "(1)"),
    ("Q1", "(2)"),
    ("Q2", "(3)"),
    ("Q3", "(4)"),
    ("Q4", "(5)"),
]

INTERACTION_YEARS = [y for y in range(SAMPLE_YEARS[0], SAMPLE_YEARS[1] + 1) if y != OMITTED_YEAR]


def render_quarterly_div_table(models: dict[str, object]) -> str:
    ordered = [models[k] for k in MODEL_ORDER]

    q_coef, q_se = _coef_row("Q", [_cell(m, "var_Q") for m in ordered])
    d_coef, d_se = _coef_row(r"\ensuremath{\tilde{d}}", [_cell(m, "d") for m in ordered])

    year_rows: list[tuple[str, str]] = []
    for year in INTERACTION_YEARS:
        label = rf"\ensuremath{{\text{{{year}}} \times \tilde{{d}}}}"
        term = None if year == OMITTED_YEAR else f"d_year_{year}"
        cells = [_cell(m, term) for m in ordered]
        year_rows.append(_coef_row(label, cells))

    header1 = " & ".join(
        [""] + [rf"\multicolumn{{1}}{{c}}{{{name}}}" for name, _ in COLUMN_HEADERS]
    )
    header2 = " & ".join([""] + [rf"\multicolumn{{1}}{{c}}{{{num}}}" for _, num in COLUMN_HEADERS])
    fe_row = " & ".join(["Firm FE"] + [r"\multicolumn{1}{c}{Yes}"] * len(COLUMN_HEADERS))
    year_fe_row = " & ".join(["Year FE"] + [r"\multicolumn{1}{c}{Yes}"] * len(COLUMN_HEADERS))
    r2_row = " & ".join([r"\ensuremath{R^2}"] + [f"{m._r2:.3f}" for m in ordered])
    n_row = " & ".join(
        ["Observations"]
        + [rf"\multicolumn{{1}}{{r}}{{{_fmt_n(int(m._N))}}}" for m in ordered]
    )

    lines = [
        r"\begin{table}[p]\centering",
        r"\caption{\\ Quarter-specific dividend regressions (annual specification)}",
        r"\scriptsize",
        r"\label{tabapp:quarterly_div}",
        r"\renewcommand{\arraystretch}{1.2}{",
        r"    \def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"    \begin{tabular}{l*{5}{D{.}{.}{-1}}}",
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
            TABLE12_NOTES,
            r"\end{table}",
        ]
    )
    return "\n".join(lines)
