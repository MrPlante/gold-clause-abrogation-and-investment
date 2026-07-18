"""LaTeX rendering for IA constraints regressions."""

from __future__ import annotations

from lib.constraints import DISPLAY_TERMS, MODEL_ORDER, TERM_LABELS
from lib.render_investment_reg_tex import _cell, _coef_row, _fmt_n

CONSTRAINTS_NOTES = (
    r"\scriptsize{\textit{Notes.} This table tests whether debt overhang effects vary by firm "
    r"characteristics. It reports results from panel regressions of net investment on $Q$, "
    r"gold clause exposure $\tilde{d}$, period $\times$ $\tilde{d}$ interactions, and triple "
    r"interactions with a firm characteristic indicator $I$, where the pre-abrogation period "
    r"(1926--1932) is the omitted category. In column 1, $I$ equals one if a firm has "
    r"below-median asset size among $\tilde{d} > 0$ firms in 1930. In column 2, $I$ equals "
    r"one if a firm has below-median cash/assets among $\tilde{d} > 0$ firms in 1930. In "
    r"column 3, $I$ equals one if a firm has above-median book leverage among $\tilde{d} > 0$ "
    r"firms in 1930. All regressions include firm and year fixed effects. All variables are "
    r"winsorized at the 0.5\% and 99.5\% levels within each year. Standard errors in "
    r"parentheses are two-way clustered by firm and year. $^{*}p<0.10$, $^{**}p<0.05$, "
    r"$^{***}p<0.01$.}"
)

COLUMN_HEADERS = [
    ("Small", "(1)"),
    ("Low cash", "(2)"),
    ("High leverage", "(3)"),
]


def render_constraints_table(models: dict[str, object]) -> str:
    ordered = [models[k] for k in MODEL_ORDER]

    coef_rows: list[tuple[str, str]] = []
    for term in DISPLAY_TERMS:
        label = TERM_LABELS[term]
        cells = [_cell(m, term) for m in ordered]
        coef_rows.append(_coef_row(label, cells))

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
        r"\begin{table}[p]",
        r"\centering",
        r"\caption{\\ Gold clause exposure and investment by firm size, cash, and book leverage } "
        r"\scriptsize \renewcommand{\arraystretch}{1.15}",
        r"",
        r"\label{tabapp:constraint}",
        r"{",
        r"    \def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"    \begin{tabular}{l*{3}{D{.}{.}{-1}}}",
        r"        \toprule",
        f"                            &{header1.split('&', 1)[1]} \\\\",
        f"                            &{header2.split('&', 1)[1]} \\\\",
        r"        \midrule",
    ]
    for coef_line, se_line in coef_rows:
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
            r"}",
            r"",
            r"\vspace*{3mm} \justifying \noindent",
            CONSTRAINTS_NOTES,
            r"\end{table}",
        ]
    )
    return "\n".join(lines)
