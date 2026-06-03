"""LaTeX rendering for IA Table 14 indicator investment regressions."""

from __future__ import annotations

from lib.indicator_investment import DISPLAY_TERMS, MODEL_ORDER, TERM_LABELS
from lib.render_investment_reg_tex import _cell, _coef_row, _fmt_n

TABLE14_NOTES = (
    r"\scriptsize{\textit{Notes.} This table tests whether debt overhang effects operate at the "
    r"extensive margin (any gold clause exposure versus none) and whether effects vary with "
    r"exposure intensity. It reports results from panel regressions of net investment on $Q$, "
    r"indicator variables for gold clause exposure, and period $\times$ indicator interactions, "
    r"where the pre-abrogation period (1926--1932) is the omitted category. Column 1 uses a "
    r"single indicator $(\tilde{d} > 0)$. Column 2 adds an indicator for above-median exposure "
    r"$(\tilde{d} > \tilde{d}_{0.50})$. Column 3 further adds an indicator for the top quartile "
    r"$(\tilde{d} > \tilde{d}_{0.75})$, where $\tilde{d}_{0.50}$ and $\tilde{d}_{0.75}$ are the "
    r"50th and 75th percentiles of $\tilde{d}$ among firms with positive exposure. All "
    r"regressions include firm and year fixed effects. All variables are winsorized at the "
    r"0.5\% and 99.5\% levels within each year. Standard errors in parentheses are two-way "
    r"clustered by firm and year. $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.}"
)

COLUMN_HEADERS = ["(1)", "(2)", "(3)"]


def render_indicators_d_table(models: dict[str, object]) -> str:
    ordered = [models[k] for k in MODEL_ORDER]

    coef_rows: list[tuple[str, str]] = []
    for term in DISPLAY_TERMS:
        cells = [_cell(m, term) for m in ordered]
        coef_rows.append(_coef_row(TERM_LABELS[term], cells))

    header = " & ".join([""] + [rf"\multicolumn{{1}}{{c}}{{{h}}}" for h in COLUMN_HEADERS])
    fe_row = " & ".join(["Firm FE"] + [r"\multicolumn{1}{c}{Yes}"] * 3)
    year_fe_row = " & ".join(["Year FE"] + [r"\multicolumn{1}{c}{Yes}"] * 3)
    r2_row = " & ".join([r"\ensuremath{R^2}"] + [f"{m._r2:.3f}" for m in ordered])
    n_row = " & ".join(
        ["Observations"]
        + [rf"\multicolumn{{1}}{{r}}{{{_fmt_n(int(m._N))}}}" for m in ordered]
    )

    lines = [
        r"\begin{table}[p]\centering",
        r"\scriptsize",
        r"\renewcommand{\arraystretch}{1.2}",
        r"\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"\caption{\\ Gold clause exposure at the extensive margin and investment} "
        r"\label{tabapp:invnonlinear}",
        r"{",
        r"\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"\begin{tabular}{l*{3}{D{.}{.}{-1}}}",
        r"\toprule",
        f"                    &{header.split('&', 1)[1].strip()} \\",
        r"\midrule",
    ]
    for coef_line, se_line in coef_rows:
        lines.extend([coef_line, se_line])
    lines.extend(
        [
            r"\midrule",
            f"{fe_row} \\\\",
            f"{year_fe_row} \\\\",
            f"{r2_row} \\\\",
            f"{n_row} \\\\",
            r"\bottomrule",
            r"\end{tabular}",
            r"}",
            r"",
            r"\vspace*{3mm} \justifying \noindent",
            TABLE14_NOTES,
            r"\end{table}",
        ]
    )
    return "\n".join(lines)
