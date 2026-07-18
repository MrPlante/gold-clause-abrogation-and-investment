"""LaTeX rendering for Table 2 bond statistics."""

from __future__ import annotations

from lib.bond_stats import BondYearStats

TABLE2_NOTES = (
    r"\scriptsize{\textit{Notes.} This table examines whether firms strategically "
    r"adjusted their gold clause exposure prior to the abrogation. The sample is a "
    r"balanced panel of 157 firms with corporate bonds outstanding at the end of "
    r"1930---the year before Britain's departure from the gold standard. For each year, "
    r"the table reports the number of the initial 157 firms that still have at least one "
    r"bond outstanding, the number of firms with gold clause bonds, total bond count "
    r"among the 157 firms, gold clause bond count, mean and median gold clause exposure "
    r"($d$, as defined in equation (\ref{eq:d})) among firms with positive exposure, and "
    r"the correlation between contemporaneous $d$ and its 1930 value.}"
)


def _fmt_int(n: int) -> str:
    return f"{n:,}"


def _fmt_float(x: float) -> str:
    return f"{x:.2f}"


def _row_tex(r: BondYearStats) -> str:
    cells = [
        str(r.year),
        _fmt_int(r.n_firms),
        _fmt_int(r.n_firms_gold),
        _fmt_int(r.n_bonds),
        _fmt_int(r.n_bonds_gold),
        _fmt_float(r.mean_d),
        _fmt_float(r.median_d),
        _fmt_float(r.rho_d1930),
    ]
    return "            " + " & ".join(cells) + r" \\"


def render_table2_latex(rows: list[BondYearStats]) -> str:
    body = "\n".join(_row_tex(r) for r in rows)
    lines = [
        r"\begin{table}[p]",
        r"    \centering",
        r"    \caption{\\ Bond statistics}",
        r"    \scriptsize",
        r"    \label{tab:bond_stats}",
        r"    ",
        r"    \begin{threeparttable}",
        r"        \begin{tabular}{lccccccc}",
        r"            \toprule",
        r"                 & N firms & N firms & N bonds & N bonds & Mean $d$ & Median $d$ & $\rho(d_{1930}, d_t)$ \\",
        r"            Year & (with bonds) & (with gold bonds) & (all) & (gold) & ($d>0$) & ($d>0$) & \\",
        r"            \midrule",
        body,
        r"            \bottomrule",
        r"        \end{tabular}",
        r"    \end{threeparttable}\\",
        r"    ",
        r"    \vspace*{3mm} \justifying \noindent",
        f"    {TABLE2_NOTES}",
        r"\end{table}",
    ]
    return "\n".join(lines)
