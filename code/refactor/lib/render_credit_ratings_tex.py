"""LaTeX rendering for Table 5 credit-ratings regressions."""

from __future__ import annotations

from lib.credit_ratings import MODEL_ORDER
from lib.render_investment_reg_tex import CoefCell, _cell, _coef_row, _fmt_n

TABLE5_NOTES = (
    r"\scriptsize{\textit{Notes.} This table reports results from panel regressions testing "
    r"whether debt overhang effects are more severe for firms closer to default. It regresses "
    r"net investment (column 1) and cash dividends (column 2) on $Q$, gold clause exposure "
    r"$\tilde{d}$ (as defined in equation (\ref{eq:tilde_d})), year $\times$ $\tilde{d}$ "
    r"interactions, and triple interactions with a low credit rating indicator. Low rating "
    r"equals one if a firm's bond rating is Ba or below in 1930 (the median rating among bond "
    r"issuers). To ease interpretation, $\tilde{d}$ is normalized by subtracting its median "
    r"value among firms with positive exposure. All regressions include firm and year fixed "
    r"effects. Only 1933 and 1934 interaction terms are reported; see Internet Appendix Table "
    r"\ref{tabapp:credit_rating} for the full list of coefficients. All variables are winsorized "
    r"at the 0.5\% and 99.5\% levels within each year. Standard errors in parentheses are "
    r"two-way clustered by firm and year. $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.}"
)

COLUMN_HEADERS = [
    ("Net investment", "(1)"),
    ("Dividend", "(2)"),
]

DISPLAY_ROWS: list[tuple[str, str]] = [
    (r"\ensuremath{\text{1933} \times \tilde{d}}", "d_year_1933"),
    (r"\ensuremath{\text{1934} \times \tilde{d}}", "d_year_1934"),
    (r"\ensuremath{\text{1933} \times \text{Low rating}}", "year_1933_Low"),
    (r"\ensuremath{\text{1934} \times \text{Low rating}}", "year_1934_Low"),
    (
        r"\ensuremath{\text{1933} \times \tilde{d} \times \text{Low rating}}",
        "d_year_1933_Low",
    ),
    (
        r"\ensuremath{\text{1934} \times \tilde{d} \times \text{Low rating}}",
        "d_year_1934_Low",
    ),
]


def render_table5_latex(models: dict[str, object]) -> str:
    ordered = [models[k] for k in MODEL_ORDER]

    coef_rows: list[tuple[str, str]] = []
    for label, term in DISPLAY_ROWS:
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
        r"    \centering",
        r"    \caption{\\ Gold clause exposure, investment, and payout by credit rating}",
        r"    \scriptsize",
        r"    \label{tab:credit_rating}",
        r"",
        r"    \renewcommand{\arraystretch}{1.2}{",
        r"        \def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"        \begin{tabular}{l*{2}{D{.}{.}{-1}}}",
        r"        \toprule",
        f"													                    &{header1.split('&', 1)[1]} \\\\",
        f"													                    &{header2.split('&', 1)[1]} \\\\",
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
            r"        \end{tabular}",
            r"        }",
            r"",
            r"    \vspace*{3mm} \justifying \noindent",
            TABLE5_NOTES,
            r"\end{table}",
        ]
    )
    return "\n".join(lines)
