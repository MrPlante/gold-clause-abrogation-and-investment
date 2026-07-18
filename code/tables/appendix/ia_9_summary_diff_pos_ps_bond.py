"""
Internet Appendix Table 9 — Group means on dalt sample split by dind (Stata A14/A7).
"""

from __future__ import annotations

import re
from pathlib import Path

from config import (
    COEF_TOLERANCE,
    MANUSCRIPT_APPENDIX_TABLES,
    REFACTOR_OUTPUT_TABLES_APPENDIX,
)
from lib.dalt_panel import load_dalt_panel
from lib.render_group_means_tex import render_group_means_table
from lib.summary_stats import PANELS, _compute_panel_impl
from lib.summary_stats_ia import BASE_VARIABLES

TOL = max(COEF_TOLERANCE, 0.011)

GROUP_VARIABLES = BASE_VARIABLES + [("d", r"\ensuremath{\tilde{d}}")]
GROUP_PANELS = {key: {**cfg, "split": True} for key, cfg in PANELS.items()}

TABLE_NOTES = (
    r"\scriptsize{\textit{Notes.} This table reports average characteristics for preferred "
    r"equity and/or bond issuers, split by gold clause exposure ($\tilde{d} = 0$ vs. "
    r"$\tilde{d} > 0$). Panel A covers 1926--1932, Panel B covers 1933--1934, and Panel C "
    r"covers 1935--1940. $p$-values are from two-sample $t$-tests. All variables are "
    r"winsorized at the 0.5\% and 99.5\% levels within each year. See Appendix "
    r"\ref{secapp:vars} for variable definitions.}"
)


def load_panel():
    return load_dalt_panel()


def compute_group_panels(df):
    return {
        key: _compute_panel_impl(
            df,
            key,
            panels=GROUP_PANELS,
            split_col="dind",
            variables_split=GROUP_VARIABLES,
            variables_pooled=GROUP_VARIABLES,
        )
        for key in GROUP_PANELS
    }


def _parse_manuscript(tex_path: Path) -> dict[str, list[dict]]:
    text = tex_path.read_text(encoding="utf-8")
    panels: dict[str, list[dict]] = {"A": [], "B": [], "C": []}
    current: str | None = None

    for line in text.splitlines():
        if "Panel A:" in line:
            current = "A"
            continue
        if "Panel B:" in line:
            current = "B"
            continue
        if "Panel C:" in line:
            current = "C"
            continue
        if current is None or "&" not in line:
            continue
        stripped = line.strip()
        if stripped.startswith("\\") and not stripped.startswith(r"\ensuremath"):
            continue
        if stripped.startswith("Variable"):
            continue

        parts = [p.strip().rstrip("\\").strip() for p in line.split("&")]
        if len(parts) != 4:
            continue
        label = parts[0]
        if not label:
            continue

        def _num(s: str) -> float | None:
            s = s.strip().replace("$-$", "-")
            if not s:
                return None
            try:
                return float(s)
            except ValueError:
                return None

        panels[current].append(
            {
                "label": label,
                "mean0": _num(parts[1]),
                "mean1": _num(parts[2]),
                "p": _num(parts[3]),
            }
        )

    return panels


def _label_key(label: str) -> str:
    label = re.sub(r"\\ensuremath\{([^}]+)\}", r"\1", label)
    return label.replace(r"\ ", " ").strip()


def validate_against_manuscript(panels: dict) -> list[tuple[str, float, float]]:
    parsed = _parse_manuscript(
        MANUSCRIPT_APPENDIX_TABLES / "9_summary_diff_pos_ps_bond.tex"
    )
    checks: list[tuple[str, float, float]] = []

    for panel_key in ("A", "B", "C"):
        computed = {_label_key(r.label): r for r in panels[panel_key].rows}
        for exp in parsed[panel_key]:
            key = _label_key(exp["label"])
            row = computed.get(key)
            if row is None:
                continue
            g0, g1 = row.group0, row.group1
            assert g0 is not None and g1 is not None
            for field, actual in [
                ("mean0", g0.mean),
                ("mean1", g1.mean),
                ("p", row.p_value),
            ]:
                expected = exp.get(field)
                if expected is None or actual is None:
                    continue
                checks.append((f"panel{panel_key}.{key}.{field}", float(expected), float(actual)))

    return checks


def write_latex_table(panels: dict, path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "9_summary_diff_pos_ps_bond.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        render_group_means_table(
            panels,
            caption=(
                "Average characteristics for $\\tilde{d} = 0$ and $\\tilde{d} > 0$ "
                "among preferred equity and bond issuers"
            ),
            label="tab:sum_diff_pos",
            notes=TABLE_NOTES,
            panel_periods={k: (v["year_lo"], v["year_hi"]) for k, v in PANELS.items()},
        ),
        encoding="utf-8",
    )
    return out


def main() -> dict:
    panels = compute_group_panels(load_panel())
    checks = validate_against_manuscript(panels)

    failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in checks
        if abs(exp - act) > TOL
    ]

    out_path = write_latex_table(panels)
    if failures:
        print(
            f"IA Table 9 — {len(checks) - len(failures)}/{len(checks)} checks passed "
            f"(tol={TOL}; {len(failures)} failures — see DISCREPANCIES D-013)"
        )
        for line in failures[:5]:
            print(f"    {line}")
    else:
        print(f"IA Table 9 — all {len(checks)} manuscript checks passed (tol={TOL})")
    print(f"  Wrote LaTeX table -> {out_path}")
    return panels


if __name__ == "__main__":
    main()
