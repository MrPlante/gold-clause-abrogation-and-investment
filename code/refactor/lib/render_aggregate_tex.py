"""LaTeX rendering for Table 7 aggregate investment effects."""

from __future__ import annotations

from lib.aggregate import AggregatePanel, PeriodValues

TABLE7_NOTES = (
    r"\footnotesize{\textit{Notes.} This table aggregates firm-level estimates to assess "
    r"the total investment foregone due to gold clause uncertainty. Total net investment "
    r"is the aggregate change in fixed capital divided by lagged aggregate fixed capital, "
    r"for firms present in both years. The gold clause effect is the capital-weighted "
    r"average of each firm's foregone investment, calculated using the regression "
    r"coefficients from Table \ref{tab:inv_main} applied to each firm's gold clause "
    r"exposure $\tilde{d}$ (as defined in equation (\ref{eq:tilde_d})). Panel A reports "
    r"results for all firms; Panels B and C decompose by gold clause exposure. ``After'' "
    r"denotes the post-resolution period (1935--1940). See Section \ref{sec:agg} for details.}"
)


def _fmt_pct(value: float) -> str:
    return f"{value:.2f}"


def _data_row(label: str, values: PeriodValues) -> str:
    return (
        f"    {label}               & {_fmt_pct(values.y1933)} & "
        f"{_fmt_pct(values.y1934)} & {_fmt_pct(values.after)} \\\\"
    )


def render_table7_latex(panels: dict[str, AggregatePanel]) -> str:
    all_firms = panels["all_firms"]
    d_pos = panels["d_positive"]
    d_zero = panels["d_zero"]

    lines = [
        r"\begin{table}[p]\centering",
        r"    \caption{\\Aggregated investment effects}\footnotesize",
        r"    \label{tab:agg}",
        r"    \begin{tabular}{lrrr}",
        r"    \toprule",
        r"    & 1933 & 1934 & After \\",
        r"    \midrule",
        r"    \multicolumn{4}{c}{\textit{Panel A: All firms}}\\",
        r"    \midrule",
        _data_row("Total net investment in \\%", all_firms.total),
        _data_row("Gold clause effect in \\%", all_firms.gold_effect),
        r"    \midrule",
        r"    \multicolumn{4}{c}{\textit{Panel B: $\tilde{d}>0$ firms}}\\",
        r"    \midrule",
        _data_row("Total net investment in \\%", d_pos.total),
        _data_row("Gold clause effect in \\%", d_pos.gold_effect),
        r"    \midrule",
        r"    \multicolumn{4}{c}{\textit{Panel C: $\tilde{d}=0$ firms}}\\",
        r"    \midrule",
        _data_row("Total net investment in \\%", d_zero.total),
        r"    \bottomrule",
        r"",
        r"    \end{tabular}\\",
        r"",
        r"    \vspace*{3mm} \justifying \noindent",
        TABLE7_NOTES,
        r"\end{table}",
    ]
    return "\n".join(lines)
