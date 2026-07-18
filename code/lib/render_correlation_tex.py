"""LaTeX rendering for IA correlation table."""

from __future__ import annotations

import math

from lib.correlation import CORRELATION_VARIABLES, CorrelationRow

CORRELATION_NOTES = (
    r"\footnotesize{\textit{Notes.} This table examines correlations between gold "
    r"clause exposure $\tilde{d}$ (as defined in equation (\ref{eq:tilde_d})) and firm "
    r"characteristics. The first column reports correlations using firm-year observations "
    r"from the pre-abrogation period (1926--1932). The second column reports correlations "
    r"using only 1932 observations, the last year before abrogation. All variables are "
    r"winsorized at the 0.5\% and 99.5\% levels within each year. $p$-values are in "
    r"parentheses.}"
)


def _fmt_rho(x: float) -> str:
    if math.isnan(x):
        return ""
    return f"{x:.3f}"


def _fmt_p(x: float) -> str:
    if math.isnan(x):
        return ""
    return f"({x:.4f})"


def render_correlation_table(rows: list[CorrelationRow]) -> str:
    lines = [
        r"\begin{table}[p]\centering",
        r"\caption{\\ Correlations of firm characteristics with $\tilde{d}$}",
        r"\label{tabapp:correlation} \scriptsize",
        r"\renewcommand{\arraystretch}{1.2}",
        r"    \begin{threeparttable}",
        r"        \begin{tabular}{lcc}",
        r"            \toprule",
        r"            & 1926--1932 & 1932 \\",
        r"            \midrule",
    ]
    for row in rows:
        lines.append(f"            {row.label} & {_fmt_rho(row.rho_1926_32)} & {_fmt_rho(row.rho_1932)} \\\\")
        lines.append(
            f"            & {_fmt_p(row.p_1926_32)} & {_fmt_p(row.p_1932)} \\\\"
        )
    lines.extend(
        [
            r"            \bottomrule",
            r"        \end{tabular}",
            r"    \end{threeparttable}",
            r"",
            r"\vspace*{3mm} \justifying \noindent",
            CORRELATION_NOTES,
            r"\end{table}",
        ]
    )
    return "\n".join(lines)
