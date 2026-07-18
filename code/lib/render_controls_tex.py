"""LaTeX rendering for Table 6 controls regressions."""

from __future__ import annotations

from lib.controls import CORE_TERMS, MODEL_ORDER
from lib.render_investment_reg_tex import _cell, _coef_row, _fmt_n

TABLE6_NOTES = (
    r"\scriptsize{\textit{Notes.} This table examines whether the effect of gold clause "
    r"exposure on investment is robust to controlling for industry-level shocks (e.g., "
    r"New Deal policies, agricultural shocks) and firm-level heterogeneity. It reports "
    r"results from panel regressions of net investment on $Q$, gold clause exposure "
    r"$\tilde{d}$ (as defined in equation (\ref{eq:tilde_d})), and period $\times$ "
    r"$\tilde{d}$ interactions, where the pre-abrogation period (1926--1932) is the "
    r"omitted category. Column 1 includes SIC2 industry-year fixed effects to absorb "
    r"industry-specific shocks. Column 2 includes all firm characteristics (measured in "
    r"1930) interacted with year indicators as linear controls. Columns 3--10 use a "
    r"non-parametric approach: each column includes decile dummies for a single 1930 "
    r"characteristic interacted with year indicators. The characteristics are: (3) $Q$, "
    r"(4) log assets, (5) net income/assets, (6) cash/assets, (7) payout/common stock, "
    r"(8) book leverage, (9) market leverage, and (10) log long-term liabilities. All "
    r"regressions include firm fixed effects. All variables are winsorized at the 0.5\% "
    r"and 99.5\% levels within each year. Standard errors in parentheses are two-way "
    r"clustered by firm and year. $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.}"
)

COLUMN_HEADERS_ROW1 = [
    "Industry-year FE",
    "All controls",
    "Q",
    "Assets",
    "NI/assets",
    "Cash/assets",
    "Payout",
    "Book leverage",
    "Market leverage",
    "LT lia.",
]

COLUMN_HEADERS_ROW2 = [
    "",
    "linear",
    "deciles",
    "deciles",
    "deciles",
    "deciles",
    "deciles",
    "deciles",
    "deciles",
    "deciles",
]

DISPLAY_TERMS: list[tuple[str, str]] = [
    ("Q", "var_Q"),
    (r"\ensuremath{\tilde{d}}", "d"),
    (r"\ensuremath{\text{1933} \times \tilde{d}}", "d_1933"),
    (r"\ensuremath{\text{1934} \times \tilde{d}}", "d_1934"),
    (r"\ensuremath{\text{After} \times \tilde{d}}", "d_After"),
]


def render_table6_latex(models: dict[str, object]) -> str:
    ordered = [models[k] for k in MODEL_ORDER]
    n_cols = len(COLUMN_HEADERS_ROW1)

    coef_rows: list[tuple[str, str]] = []
    for label, term in DISPLAY_TERMS:
        cells = [_cell(m, term) for m in ordered]
        coef_rows.append(_coef_row(label, cells))

    header1 = " & ".join(
        [""] + [rf"\multicolumn{{1}}{{c}}{{{name}}}" for name in COLUMN_HEADERS_ROW1]
    )
    header2 = " & ".join(
        [""]
        + [
            rf"\multicolumn{{1}}{{c}}{{{sub}}}" if sub else ""
            for sub in COLUMN_HEADERS_ROW2
        ]
    )
    header3 = " & ".join([""] + [rf"\multicolumn{{1}}{{c}}{{({i})}}" for i in range(1, n_cols + 1)])

    year_fe = ["No"] + ["Yes"] * (n_cols - 1)
    ind_year_fe = ["Yes"] + ["No"] * (n_cols - 1)

    fe_row = " & ".join(["Firm FE"] + [r"\multicolumn{1}{c}{Yes}"] * n_cols)
    year_fe_row = " & ".join(["Year FE"] + [rf"\multicolumn{{1}}{{c}}{{{v}}}" for v in year_fe])
    ind_fe_row = " & ".join(
        ["Industry-year FE"] + [rf"\multicolumn{{1}}{{c}}{{{v}}}" for v in ind_year_fe]
    )
    r2_row = " & ".join([r"\ensuremath{R^2}"] + [f"{m._r2:.3f}" for m in ordered])
    n_row = " & ".join(
        ["Observations"]
        + [rf"\multicolumn{{1}}{{r}}{{{_fmt_n(int(m._N))}}}" for m in ordered]
    )

    lines = [
        r"\begin{landscape}",
        r"\begin{table}[t!]\centering",
        r"\caption{\\ Gold clause exposure and net investment with controls}",
        r"\scriptsize",
        r"\label{tab:controls}",
        r"\renewcommand{\arraystretch}{1.2}{",
        r"    \def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"    \resizebox{\linewidth}{!}{",
        r"    \begin{tabular}{l*{10}{D{.}{.}{-1}}}",
        r"        \toprule",
        f"        {header1} \\\\",
        f"        {header2} \\\\",
        f"        {header3} \\\\",
        r"        \midrule",
    ]
    for coef_line, se_line in coef_rows:
        lines.extend([f"        {coef_line}", f"        {se_line}"])
    lines.extend(
        [
            r"        \midrule",
            f"        {fe_row} \\\\",
            f"        {year_fe_row} \\\\",
            f"        {ind_fe_row} \\\\",
            f"        {r2_row} \\\\",
            f"        {n_row} \\\\",
            r"        \bottomrule",
            r"    \end{tabular}",
            r"    }",
            r"}\\",
            r"\justifying \noindent",
            TABLE6_NOTES,
            r"\end{table}",
            r"\end{landscape}",
        ]
    )
    return "\n".join(lines)
