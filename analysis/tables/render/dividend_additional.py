"""LaTeX rendering for IA Table 13 additional dividend regressions."""

from __future__ import annotations

from tables.models.dividend_additional import BUCKET_TERMS, MODEL_ORDER
from tables.render.regression_table import _cell, _coef_row, _fmt_n

TABLE13_NOTES = (
    r"\scriptsize{\textit{Notes.} This table tests the robustness of the dividend results to "
    r"sample restrictions and alternative dependent variable definitions. It reports results "
    r"from panel regressions of payout outcomes on $Q$, gold clause exposure $\tilde{d}$, and period "
    r"$\times$ $\tilde{d}$ interactions, where the pre-abrogation period (1926--1932) is the "
    r"omitted category. Columns 1--4 use cash dividends divided by the fixed base-period average "
    r"book-common-stock denominator used in Table \ref{tab:other_outcomes}: column 1 (2) includes "
    r"firm-year observations with a positive (zero) prior-year dividend measure, with firm-years "
    r"lacking a prior-year observation retained in the payer sample; column 3 (4) includes firms that "
    r"paid a positive (zero) amount of cash dividends in 1932. Column 5 uses annual dividend "
    r"growth (set to zero if dividends are zero in both years). Columns 6--8 use total equity "
    r"payout (cash dividends minus net share issuance): column 6 divides payout by lagged book "
    r"equity, column 7 divides it by market capitalization in 1930 (or the first available year "
    r"thereafter), and column 8 divides it by net income while restricting the sample to firm-years "
    r"in which net income exceeds cash dividends. All regressions include firm and year fixed "
    r"effects. Dependent variables are winsorized at the 0.5\% and 99.5\% levels within each "
    r"year. Standard errors in "
    r"parentheses are two-way clustered by firm and year. $^{*}p<0.10$, $^{**}p<0.05$, "
    r"$^{***}p<0.01$.}"
)

TERM_LABELS = {
    "d_1933": r"\ensuremath{\text{1933} \times \tilde{d}}",
    "d_1934": r"\ensuremath{\text{1934} \times \tilde{d}}",
    "d_After": r"\ensuremath{\text{After} \times \tilde{d}}",
}


def render_dividend_additional_table(models: dict[str, object]) -> str:
    ordered = [models[k] for k in MODEL_ORDER]
    n_cols = len(MODEL_ORDER)

    coef_rows: list[tuple[str, str]] = []
    for term in BUCKET_TERMS:
        cells = [_cell(m, term) for m in ordered]
        coef_rows.append(_coef_row(TERM_LABELS[term], cells))

    header = " & ".join([""] + [rf"\multicolumn{{1}}{{c}}{{({i + 1})}}" for i in range(n_cols)])
    fe_row = " & ".join(["Firm FE"] + [r"\multicolumn{1}{c}{Yes}"] * n_cols)
    year_fe_row = " & ".join(["Year FE"] + [r"\multicolumn{1}{c}{Yes}"] * n_cols)
    r2_row = " & ".join([r"\ensuremath{R^2}"] + [f"{m._r2:.3f}" for m in ordered])
    n_row = " & ".join(
        ["Observations"]
        + [rf"\multicolumn{{1}}{{r}}{{{_fmt_n(int(m._N))}}}" for m in ordered]
    )

    lines = [
        r"\begin{landscape}",
        r"\begin{table}[p]\centering",
        r"\caption{\\ Additional analysis on dividends}",
        r"\scriptsize \label{tabapp:divadd}",
        r"\renewcommand{\arraystretch}{1.2}",
        r"\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"{",
        r"\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"\begin{tabular}{l*{8}{D{.}{.}{-1}}}",
        r"\toprule",
        f"                    {header} \\\\",
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
            TABLE13_NOTES,
            r"\end{table}",
            r"\end{landscape}",
        ]
    )
    return "\n".join(lines)
