"""LaTeX rendering for Internet Appendix distribution summary tables."""

from __future__ import annotations

import math

from lib.summary_stats_ia import DistributionPanel, DistributionRow

LATEX_ROW_LABELS: dict[str, str] = {
    "Corp. bonds/LTL": r"Corp. bonds/LTL",
    "Pref. share/LTL": r"Pref. share/LTL",
    r"\ensuremath{d}": r"\ensuremath{d}",
    r"\ensuremath{I_{d>0}}": r"\ensuremath{I_{d>0}}",
    r"\ensuremath{\tilde{d}}": r"\ensuremath{\tilde{d}}",
    r"\ensuremath{I_{\tilde{d}>0}}": r"\ensuremath{I_{\tilde{d}>0}}",
}


def _tex_label(label: str) -> str:
    return LATEX_ROW_LABELS.get(label, label)


def _fmt_int(n: int) -> str:
    return f"{n:,}"


def _fmt_num(x: float, decimals: int = 2) -> str:
    if math.isnan(x):
        return ""
    rounded = round(x, decimals)
    if rounded < 0:
        return f"$-${abs(rounded):.{decimals}f}"
    return f"{rounded:.{decimals}f}"


def _row_line(row: DistributionRow) -> str:
    s = row.stats
    return " & ".join(
        [
            _tex_label(row.label),
            _fmt_int(s.n_firms),
            _fmt_int(s.n_obs),
            _fmt_num(s.mean),
            _fmt_num(s.std),
            _fmt_num(s.p5),
            _fmt_num(s.p25),
            _fmt_num(s.p50),
            _fmt_num(s.p75),
            _fmt_num(s.p95),
        ]
    )


def _panel_lines(panel: DistributionPanel) -> list[str]:
    title = f"Panel {panel.panel}: {panel.year_lo}--{panel.year_hi}"
    lines = [
        r"            \midrule",
        rf"            \multicolumn{{10}}{{c}}{{\textit{{{title}}}}} \\",
        r"            \midrule",
    ]
    for row in panel.rows:
        lines.append(f"            {_row_line(row)} \\\\")
    return lines


def render_distribution_table(
    panels: dict[str, DistributionPanel],
    *,
    caption: str,
    label: str,
    notes: str,
    panel_order: list[str],
) -> str:
    lines = [
        r"\begin{table}[p]\centering",
        rf"    \caption{{\\ {caption}}}\scriptsize",
        rf"    \label{{{label}}}",
        r"    \begin{threeparttable}",
        r"        \begin{tabular}{lrrrrrrrrr}",
        r"            \toprule",
        r"            Variable & Firms & N & Mean & SD & 5\% & 25\% & 50\% & 75\% & 95\% \\",
    ]
    for idx, key in enumerate(panel_order):
        lines.extend(_panel_lines(panels[key]))
    lines.extend(
        [
            r"            \bottomrule",
            r"        \end{tabular}",
            r"    \end{threeparttable}",
            r"",
            r"    \vspace*{3mm} \justifying \noindent",
            notes,
            r"\end{table}",
        ]
    )
    return "\n".join(lines)
