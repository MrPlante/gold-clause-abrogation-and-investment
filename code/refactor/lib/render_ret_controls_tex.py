"""LaTeX rendering for IA Table 15 return-control regressions."""

from __future__ import annotations

from lib.render_controls_tex import DISPLAY_TERMS
from lib.render_investment_reg_tex import _cell, _coef_row, _fmt_n
from lib.ret_controls import MODEL_ORDER

TABLE15_NOTES = (
    r"\scriptsize{\textit{Notes.} This table tests whether the effect of gold clause exposure "
    r"on investment is robust to controlling for equity return characteristics. It reports "
    r"results from panel regressions of net investment on $Q$, gold clause exposure "
    r"$\tilde{d}$, and period $\times$ $\tilde{d}$ interactions, where the pre-abrogation "
    r"period (1926--1932) is the omitted category. Column 1 includes all controls from Column "
    r"2 of Table \ref{tab:controls} as well as equity return average and volatility, and "
    r"Fama-French betas from the three-factor model computed using daily data. Columns 2--6 "
    r"use a non-parametric approach: each column includes decile dummies for a return-based "
    r"characteristic measured in 1930 interacted with year indicators, along with SIC2 "
    r"industry-year fixed effects. All regressions include firm fixed effects. All variables "
    r"are winsorized at the 0.5\% and 99.5\% levels within each year. Standard errors in "
    r"parentheses are two-way clustered by firm and year. $^{*}p<0.10$, $^{**}p<0.05$, "
    r"$^{***}p<0.01$.}"
)


def render_ret_controls_table(models: dict[str, object]) -> str:
    ordered = [models[k] for k in MODEL_ORDER]
    n_cols = len(MODEL_ORDER)

    coef_rows: list[tuple[str, str]] = []
    for label, term in DISPLAY_TERMS:
        cells = [_cell(m, term) for m in ordered]
        coef_rows.append(_coef_row(label, cells))

    header = " & ".join([""] + [rf"\multicolumn{{1}}{{c}}{{({i + 1})}}" for i in range(n_cols)])
    fe_row = " & ".join(["Firm FE"] + [r"\multicolumn{1}{c}{Yes}"] * n_cols)
    year_fe_row = " & ".join(["Year FE"] + [r"\multicolumn{1}{c}{Yes}"] * n_cols)
    ind_fe = ["No"] + ["Yes"] * (n_cols - 1)
    ind_fe_row = " & ".join(["Industry-year FE"] + [rf"\multicolumn{{1}}{{c}}{{{v}}}" for v in ind_fe])
    r2_row = " & ".join([r"\ensuremath{R^2}"] + [f"{m._r2:.3f}" for m in ordered])
    n_row = " & ".join(
        ["Observations"]
        + [rf"\multicolumn{{1}}{{r}}{{{_fmt_n(int(m._N))}}}" for m in ordered]
    )

    lines = [
        r"\begin{table}[p]\centering",
        r"\caption{\\ Gold clause exposure and investment with return-based controls}",
        r"\scriptsize \label{tabapp:retcontrol}",
        r"\renewcommand{\arraystretch}{1.2}",
        r"{",
        r"\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        rf"\begin{{tabular}}{{l*{{{n_cols}}}{{D{{.}}{{.}}{{-1}}}}}}",
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
            f"{ind_fe_row} \\\\",
            f"{r2_row} \\\\",
            f"{n_row} \\\\",
            r"\bottomrule",
            r"\end{tabular}",
            r"}",
            r"",
            r"\vspace*{3mm} \justifying \noindent",
            TABLE15_NOTES,
            r"\end{table}",
        ]
    )
    return "\n".join(lines)
