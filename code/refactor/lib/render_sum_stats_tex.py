"""LaTeX rendering for summary-statistics tables."""

from __future__ import annotations

import math

from lib.summary_stats import PANELS, PanelStats, VariableRow

LATEX_ROW_LABELS: dict[str, str] = {
    "d": r"\ensuremath{d}",
    "Corp. bonds/LTL": r"Corp.\ bonds/LTL",
    "Pref. share/LTL": r"Pref.\ share/LTL",
}

TABLE1_NOTES = (
    r"\scriptsize{\textit{Notes.} This table reports summary statistics separately "
    r"for firms with no gold clause exposure ($d = 0$) and firms with positive gold "
    r"clause exposure ($d > 0$). The number of unique firms in each group is reported "
    r"in parentheses. $\Delta$ Mean is the difference in means ($d > 0$ minus $d = 0$), "
    r"and p-val is the $p$-value of the difference. Panel A covers 1926--1932, Panel B "
    r"covers 1933--1934, and Panel C covers 1935--1940. In Panel C, all firms have "
    r"$d = 0$ because the Supreme Court upheld the constitutionality of the abrogation "
    r"in February 1935; the reported statistics pool all observations. In Panels A and B, "
    r"$d$ can be slightly greater than Corp.\ bonds/LTL because $d$ is calculated using "
    r"the reported amount outstanding of each bond, whereas Corp.\ bonds/LTL is based on "
    r"balance sheet information. For most firms the two values coincide, but minor "
    r"discrepancies between the book value of corporate bonds and the reported amount "
    r"outstanding can arise. See Appendix \ref{secapp:vars} for variable definitions.}"
)


def _tex_label(label: str) -> str:
    return LATEX_ROW_LABELS.get(label, label)


def _fmt_int(n: int) -> str:
    return f"{n:,}"


def _fmt_signed(x: float, decimals: int = 2) -> str:
    if math.isnan(x):
        return ""
    rounded = round(x, decimals)
    if rounded < 0:
        return f"$-${abs(rounded):.{decimals}f}"
    return f"{rounded:.{decimals}f}"


def _fmt_p(p: float) -> str:
    if math.isnan(p):
        return ""
    return f"{p:.2f}"


def _row_split(row: VariableRow) -> str:
    g0, g1 = row.group0, row.group1
    assert g0 is not None and g1 is not None
    delta_tex = _fmt_signed(round(g1.mean, 2) - round(g0.mean, 2))
    return " & ".join(
        [
            _tex_label(row.label),
            _fmt_int(g0.n_obs),
            _fmt_signed(g0.mean),
            _fmt_signed(g0.std),
            _fmt_int(g1.n_obs),
            _fmt_signed(g1.mean),
            _fmt_signed(g1.std),
            delta_tex,
            _fmt_p(row.p_value),  # type: ignore[arg-type]
        ]
    )


def _row_pooled(row: VariableRow) -> str:
    g0 = row.group0
    assert g0 is not None
    return " & ".join(
        [
            _tex_label(row.label),
            _fmt_int(g0.n_obs),
            _fmt_signed(g0.mean),
            _fmt_signed(g0.std),
            "",
            "",
            "",
            "",
            "",
        ]
    )


def render_table1_latex(panels: dict[str, PanelStats]) -> str:
    lines: list[str] = [
        r"\begin{table}[p]\centering",
        r"    \caption{\\ Summary statistics by gold clause exposure}",
        r"    \scriptsize",
        r"    \label{tab:sum_stats_d}",
        r"    ",
        r"    \begin{threeparttable}",
        r"        \begin{tabular}{l rrr rrr rr}",
        r"            \toprule",
    ]

    for panel_key in ("A", "B", "C"):
        cfg = PANELS[panel_key]
        lo, hi = cfg["year_lo"], cfg["year_hi"]
        panel = panels[panel_key]

        if panel_key != "A":
            lines.append(r"            \midrule")

        lines.append(
            rf"            \multicolumn{{9}}{{c}}{{\textit{{Panel {panel_key}: {lo}--{hi}}}}} \\"
        )
        lines.append(r"            \midrule")

        if cfg["split"]:
            g0, g1 = panel.rows[0].group0, panel.rows[0].group1
            assert g0 is not None and g1 is not None
            lines.extend(
                [
                    rf"             & \multicolumn{{3}}{{c}}{{$d = 0$ ({g0.n_firms} firms)}} "
                    rf"& \multicolumn{{3}}{{c}}{{$d > 0$ ({g1.n_firms} firms)}} "
                    r"& \multicolumn{2}{c}{$\Delta$ Mean} \\",
                    r"            \cmidrule(lr){2-4} \cmidrule(lr){5-7} \cmidrule(lr){8-9}",
                    r"             & N & Mean & SD & N & Mean & SD & $\Delta$ & p-val \\",
                ]
            )
            for row in panel.rows:
                lines.append(f"            {_row_split(row)} \\\\")
        else:
            g0 = panel.rows[0].group0
            assert g0 is not None
            lines.extend(
                [
                    rf"             & \multicolumn{{3}}{{c}}{{$d = 0$ ({g0.n_firms} firms)}} "
                    r"& \multicolumn{3}{c}{} & \multicolumn{2}{c}{} \\",
                    r"            \cmidrule(lr){2-4}",
                ]
            )
            for row in panel.rows:
                lines.append(f"            {_row_pooled(row)} \\\\")

    lines.extend(
        [
            r"            \bottomrule",
            r"        \end{tabular}",
            r"    \end{threeparttable}\\",
            r"    ",
            r"    \vspace*{3mm} \justifying \noindent",
            f"    {TABLE1_NOTES}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)
