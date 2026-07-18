"""LaTeX rendering for IA Table 16 heterogeneous aggregate effects."""

from __future__ import annotations

from lib.aggregate import PeriodValues
from lib.aggregate_hetero import HeteroGoldEffects

TABLE16_NOTES = (
    r"\footnotesize{\textit{Notes.} This table extends the aggregation in Table \ref{tab:agg} "
    r"by allowing for heterogeneous marginal effects of gold clause exposure across firm "
    r"subgroups. Rows labeled ``with rating'' allow the marginal effect to differ between "
    r"high-rated and low-rated firms (Ba or below in 1930), using coefficients from Table "
    r"\ref{tab:credit_rating}. Rows labeled ``with size'' allow the marginal effect to differ "
    r"between large and small firms (above and below median assets). The baseline row reproduces "
    r"the uniform-effect estimates from Table \ref{tab:agg} for comparison. ``After'' denotes "
    r"the post-resolution period (1935--1940). See Section \ref{sec:agg} for details.}"
)


def _fmt_pct(value: float) -> str:
    return f"{value:.2f}"


def _data_row(label: str, values: PeriodValues) -> str:
    return (
        f"    {label}      & {_fmt_pct(values.y1933)} & "
        f"{_fmt_pct(values.y1934)} & {_fmt_pct(values.after)} \\\\"
    )


def render_aggregate_hetero_table(panels: dict[str, HeteroGoldEffects]) -> str:
    all_firms = panels["all_firms"]
    d_pos = panels["d_positive"]

    lines = [
        r"\begin{table}[p]\centering",
        r"    \caption{\\Aggregated investment effects with heterogeneous marginal effects}\footnotesize",
        r"    \label{tabapp:agg_het}",
        r"    \begin{tabular}{lrrr}",
        r"    \toprule",
        r"    & 1933 & 1934 & After \\",
        r"    \midrule",
        r"    \multicolumn{4}{c}{\textit{Panel A: All firms}}\\",
        r"    \midrule",
        _data_row("Gold clause effect in \\% (baseline)", all_firms.baseline),
        _data_row("Gold clause effect in \\% (with rating)", all_firms.rating),
        _data_row("Gold clause effect in \\% (with size)", all_firms.size),
        r"    \midrule",
        r"    \multicolumn{4}{c}{\textit{Panel B: $\tilde{d}>0$ firms}}\\",
        r"    \midrule",
        _data_row("Gold clause effect in \\% (baseline)", d_pos.baseline),
        _data_row("Gold clause effect in \\% (with rating)", d_pos.rating),
        _data_row("Gold clause effect in \\% (with size)", d_pos.size),
        r"    \bottomrule",
        r"",
        r"    \end{tabular}\\",
        r"",
        r"    \vspace*{3mm} \justifying \noindent",
        TABLE16_NOTES,
        r"\end{table}",
    ]
    return "\n".join(lines)
