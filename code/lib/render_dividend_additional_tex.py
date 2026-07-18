"""LaTeX rendering for IA Table 13 additional dividend regressions."""

from __future__ import annotations

from lib.additional_dividends import BUCKET_TERMS, MODEL_ORDER
from lib.render_investment_reg_tex import _cell, _coef_row, _fmt_n

TABLE13_NOTES = (
    r"\scriptsize{\textit{Notes.} This table tests the robustness of the dividend results to "
    r"sample restrictions and alternative dependent variable definitions. It reports results "
    r"from panel regressions of dividends on gold clause exposure $\tilde{d}$, and period "
    r"$\times$ $\tilde{d}$ interactions, where the pre-abrogation period (1926--1932) is the "
    r"omitted category. Columns 1--4 use cash dividends normalized by fixed capital in 1930 as "
    r"the dependent variable: column 1 (2) includes firm-year observations where a firm paid a "
    r"positive (zero) amount of cash dividends in the previous year; column 3 (4) includes "
    r"firms that paid a positive (zero) amount of cash dividends in 1932. Columns 5--8 use the "
    r"full sample with alternative dependent variable definitions: column 5 uses annual dividend "
    r"growth (set to zero if dividends are zero in both years); column 6 uses dividends divided "
    r"by lagged book equity; column 7 uses dividends divided by market capitalization in 1930; "
    r"column 8 uses dividends as a share of net income for firms with positive net income "
    r"exceeding the dividend. All regressions include firm and year fixed effects. All variables "
    r"are winsorized at the 0.5\% and 99.5\% levels within each year. Standard errors in "
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
        f"                    {header} \\",
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
