"""LaTeX longtable for IA full credit-ratings regressions."""

from __future__ import annotations

from config import OMITTED_YEAR, SAMPLE_YEARS
from lib.credit_ratings import MODEL_ORDER
from lib.render_investment_reg_tex import _cell, _coef_row, _fmt_n

FULL_TABLE_NOTES = (
    r"\scriptsize{\textit{Notes.} This table reports results from panel regressions of net "
    r"investment, equity payout rate, and cash dividends on interactions of individual year "
    r"indicators with $\tilde{d}$, where 1932 is the omitted year. The net investment "
    r"regression controls for $Q$. Low rating is a firm-level dummy variable that is 1 if a "
    r"firm's bond ratings are Ba or below in 1930. All regressions include firm and year fixed "
    r"effects. All variables are winsorized at the 0.5\% and 99.5\% levels within each year. "
    r"Standard errors in parentheses are two-way clustered by firm and year. $^{*}p<0.10$, "
    r"$^{**}p<0.05$, $^{***}p<0.01$.}"
)

COLUMN_HEADERS = [
    ("Net investment", "(1)"),
    ("Payout", "(2)"),
    ("Dividend", "(3)"),
]

INTERACTION_YEARS = [y for y in range(SAMPLE_YEARS[0], SAMPLE_YEARS[1] + 1) if y != OMITTED_YEAR]


def _display_rows() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = [
        ("Q", "var_Q"),
        (r"\ensuremath{\tilde{d}}", "d"),
        ("Low rating", "d_Low"),
    ]
    for year in INTERACTION_YEARS:
        rows.append((rf"\ensuremath{{\text{{{year}}} \times \tilde{{d}}}}", f"d_year_{year}"))
    for year in INTERACTION_YEARS:
        rows.append((rf"\ensuremath{{\text{{{year}}} \times}} Low rating", f"year_{year}_Low"))
    for year in INTERACTION_YEARS:
        rows.append(
            (
                rf"\ensuremath{{\text{{{year}}} \times \tilde{{d}} \times}} Low rating",
                f"d_year_{year}_Low",
            )
        )
    return rows


def render_credit_ratings_full_table(models: dict[str, object]) -> str:
    ordered = [models[k] for k in MODEL_ORDER]
    display_rows = _display_rows()

    header1 = (
        "                        &"
        + "&".join(rf"\multicolumn{{1}}{{c}}{{{name}}}" for name, _ in COLUMN_HEADERS)
    )
    header2 = (
        "                        &"
        + "&".join(rf"\multicolumn{{1}}{{c}}{{{num}}}" for _, num in COLUMN_HEADERS)
    )
    fe_row = "    Firm FE             &" + "&".join([r"\multicolumn{1}{c}{Yes}"] * 3)
    year_fe_row = "    Year FE             &" + "&".join([r"\multicolumn{1}{c}{Yes}"] * 3)
    r2_row = "    \\ensuremath{R^2}    &" + "&".join(f"       {m._r2:.3f}         " for m in ordered)
    n_row = (
        "    Observations        &"
        + "&".join(rf"\multicolumn{{1}}{{r}}{{{_fmt_n(int(m._N))}}}" for m in ordered)
    )

    body: list[str] = []
    for label, term in display_rows:
        c_line, s_line = _coef_row(label, [_cell(m, term) for m in ordered])
        body.append(f"    {c_line}")
        body.append(f"    {s_line}")

    lines = [
        r"\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}",
        r"\scriptsize",
        r"\begin{longtable}{l*{3}{D{.}{.}{-1}}}",
        r"    \caption{\\ Gold clause exposure, investment, and payout by credit rating}",
        r"    \label{tabapp:credit_rating} \\",
        r"    ",
        r"    \toprule",
        header1 + r" \\",
        header2 + r" \\",
        r"    \midrule",
        r"    \endfirsthead",
        r"    ",
        r"    \multicolumn{4}{l}{\textit{Table \ref{tabapp:credit_rating} continued from previous page}} \\",
        r"    \toprule",
        header1 + r" \\",
        header2 + r" \\",
        r"    \midrule",
        r"    \endhead",
        r"    ",
        r"    \midrule",
        r"    \multicolumn{4}{r}{\textit{Continued on next page}} \\",
        r"    \endfoot",
        r"    ",
        r"    \midrule",
        fe_row + r" \\",
        year_fe_row + r" \\",
        r2_row + r" \\",
        n_row + r" \\",
        r"    \bottomrule",
        r"    ",
        rf"    \multicolumn{{4}}{{p{{0.85\textwidth}}}}{{\vspace*{{3mm}} \justifying {FULL_TABLE_NOTES}}} \\",
        r"    \endlastfoot",
        r"    ",
    ]
    lines.extend(body)
    lines.append(r"\end{longtable}")
    return "\n".join(lines)
