"""LaTeX rendering for IA balanced-panel regressions."""

from __future__ import annotations

from config import OMITTED_YEAR, SAMPLE_YEARS
from lib.balanced import COLUMN_LABELS, COLUMN_ORDER
from lib.render_investment_reg_tex import CoefCell, _cell, _coef_row, _fmt_n

BALANCED_NOTES = (
    r"\scriptsize{\textit{Notes.} This table reports results from panel regressions of "
    r"net investment on $Q$, gold clause exposure $\tilde{d}$, and year $\times$ "
    r"$\tilde{d}$ interactions, where 1932 is the omitted category. Column 1 excludes "
    r"firms that repaid all of their gold clause debt anytime from 1931 to 1935. Columns "
    r"2--4 restrict the sample to balanced panels of firms with observations in each year "
    r"for 1930--1936, 1929--1940, and 1926--1940, respectively. All regressions include "
    r"firm and year fixed effects. All variables are winsorized at the 0.5\% and 99.5\% "
    r"levels within each year. Standard errors in parentheses are two-way clustered by firm "
    r"and year. $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.}"
)

INTERACTION_YEARS = [y for y in range(SAMPLE_YEARS[0], SAMPLE_YEARS[1] + 1) if y != OMITTED_YEAR]


def render_balanced_table(models: dict[str, object]) -> str:
    ordered = [models[k] for k in COLUMN_ORDER]

    q_coef, q_se = _coef_row("Q", [_cell(m, "var_Q") for m in ordered])
    d_coef, d_se = _coef_row(r"\ensuremath{\tilde{d}}", [_cell(m, "d") for m in ordered])

    year_rows: list[tuple[str, str]] = []
    for year in INTERACTION_YEARS:
        term = f"d_year_{year}"
        label = rf"\ensuremath{{\text{{{year}}} \times \tilde{{d}}}}"
        year_rows.append(_coef_row(label, [_cell(m, term) for m in ordered]))

    header1 = " & ".join(
        [""] + [rf"\multicolumn{{1}}{{c}}{{{name}}}" for name, _ in COLUMN_LABELS]
    )
    header2 = " & ".join([""] + [rf"\multicolumn{{1}}{{c}}{{{num}}}" for _, num in COLUMN_LABELS])
    fe_row = " & ".join(["Firm FE"] + [r"\multicolumn{1}{c}{Yes}"] * len(COLUMN_LABELS))
    year_fe_row = " & ".join(["Year FE"] + [r"\multicolumn{1}{c}{Yes}"] * len(COLUMN_LABELS))
    r2_row = " & ".join([r"\ensuremath{R^2}"] + [f"{m._r2:.3f}" for m in ordered])
    n_row = " & ".join(
        ["Observations"]
        + [rf"\multicolumn{{1}}{{r}}{{{_fmt_n(int(m._N))}}}" for m in ordered]
    )

    lines = [
        r"\begin{table}[p]",
        r"    \centering",
        r"    \caption{\\ Omitting repayers and balanced panels}",
        r"    \scriptsize",
        r"    \renewcommand{\arraystretch}{1.2}",
        r"    \label{tabapp:repay}",
        r"    {",
        r"        \def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"        \begin{tabular}{l*{4}{D{.}{.}{-1}}}",
        r"            \toprule",
        f"                                &{header1.split('&', 1)[1]} \\\\",
        f"                                &{header2.split('&', 1)[1]} \\\\",
        r"            \midrule",
        f"            {q_coef}",
        f"            {q_se}",
        f"            {d_coef}",
        f"            {d_se}",
    ]
    for coef_line, se_line in year_rows:
        lines.extend([f"            {coef_line}", f"            {se_line}"])
    lines.extend(
        [
            r"            \midrule",
            f"            {fe_row} \\\\",
            f"            {year_fe_row} \\\\",
            f"            {r2_row} \\\\",
            f"            {n_row} \\\\",
            r"            \bottomrule",
            r"        \end{tabular}",
            r"    }",
            r"",
            r"    \vspace*{3mm} \justifying \noindent",
            BALANCED_NOTES,
            r"\end{table}",
        ]
    )
    return "\n".join(lines)
