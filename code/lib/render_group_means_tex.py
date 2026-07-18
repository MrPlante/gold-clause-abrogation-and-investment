"""LaTeX rendering for 4-column group-mean comparison tables."""

from __future__ import annotations

import math

from lib.summary_stats import PanelStats, VariableRow

LATEX_ROW_LABELS: dict[str, str] = {
    "Corp. bonds/LTL": r"Corp.\ bonds/LTL",
    "Pref. share/LTL": r"Pref.\ share/LTL",
    r"\ensuremath{\tilde{d}}": r"\ensuremath{\tilde{d}}",
}


def _tex_label(label: str) -> str:
    return LATEX_ROW_LABELS.get(label, label)


def _fmt_mean(x: float) -> str:
    if math.isnan(x):
        return ""
    rounded = round(x, 2)
    if rounded < 0:
        return f"$-${abs(rounded):.2f}"
    return f"{rounded:.2f}"


def _fmt_p(p: float) -> str:
    if math.isnan(p):
        return ""
    return f"{p:.2f}"


def _row_line(row: VariableRow) -> str:
    g0, g1 = row.group0, row.group1
    assert g0 is not None and g1 is not None
    return " & ".join(
        [
            _tex_label(row.label),
            _fmt_mean(g0.mean),
            _fmt_mean(g1.mean),
            _fmt_p(row.p_value),  # type: ignore[arg-type]
        ]
    )


def render_group_means_table(
    panels: dict[str, PanelStats],
    *,
    caption: str,
    label: str,
    notes: str,
    panel_order: tuple[str, ...] = ("A", "B", "C"),
    panel_periods: dict[str, tuple[int, int]],
) -> str:
    lines = [
        r"\begin{table}[p]",
        r"\centering",
        rf"\caption{{\\ {caption}}} \scriptsize \label{{{label}}}",
        r"    \begin{threeparttable}",
        r"        \begin{tabular}{lrrr}",
        r"            \toprule",
        r"            Variable & \ensuremath{\tilde{d}=0} & \ensuremath{\tilde{d}>0} & p-val. \\",
    ]
    for panel_key in panel_order:
        lo, hi = panel_periods[panel_key]
        if panel_key != panel_order[0]:
            lines.append(r"            \midrule")
        lines.append(
            rf"            \multicolumn{{4}}{{c}}{{\textit{{Panel {panel_key}: {lo}--{hi}}}}} \\"
        )
        lines.append(r"            \midrule")
        for row in panels[panel_key].rows:
            lines.append(f"            {_row_line(row)} \\\\")
    lines.extend(
        [
            r"            \bottomrule",
            r"        \end{tabular}",
            r"    \end{threeparttable}",
            r"    ",
            r"    \vspace*{3mm} \justifying \noindent",
            notes,
            r"\end{table}",
        ]
    )
    return "\n".join(lines)
