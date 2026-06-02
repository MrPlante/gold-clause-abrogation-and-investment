"""
Table 1 — Summary statistics by gold clause exposure (tab:sum_stats_d).

Splits panels A/B by dind_orig (I{d_orig>0}), matching the published manuscript.
Stata A7_differences.do is similar but uses dind and reports means only; A5 is pooled.
"""

from __future__ import annotations

import re
from pathlib import Path

from config import A4_PATH, COEF_TOLERANCE, MANUSCRIPT_BODY_TABLES, REFACTOR_OUTPUT_TABLES_BODY
from lib.io import read_dta
from lib.render_sum_stats_tex import render_table1_latex
from lib.summary_stats import PANELS, compute_all_panels


def load_panel():
    return read_dta(A4_PATH)


def _parse_manuscript_table(tex_path: Path) -> dict[str, list[dict]]:
    """Parse panel rows from 1_sum_stats_d.tex into structured dicts."""
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
        if current is None or "&" not in line or line.strip().startswith("\\"):
            continue
        if line.strip().startswith("Net investment") is False and not any(
            line.strip().startswith(p)
            for p in (
                "Net investment",
                "Tobin's Q",
                "log(Assets)",
                "Net income",
                "Cash/assets",
                "Payout",
                "Book leverage",
                "Market leverage",
                "log(LTL)",
                "Corp.",
                "Pref.",
                "Bank debt",
                "\\ensuremath",
            )
        ):
            continue

        parts = [p.strip() for p in line.split("&")]
        if len(parts) < 4:
            continue

        label = parts[0].replace("\\ensuremath{d}", "d").strip()
        label = re.sub(r"\\ensuremath\{([^}]+)\}", r"\1", label)

        def _num(s: str) -> float | None:
            s = s.strip().replace("$-$", "-").replace("{", "").replace("}", "")
            if not s:
                return None
            try:
                return float(s)
            except ValueError:
                return None

        if current in ("A", "B"):
            panels[current].append(
                {
                    "label": label,
                    "n0": _num(parts[1]),
                    "mean0": _num(parts[2]),
                    "sd0": _num(parts[3]),
                    "n1": _num(parts[4]) if len(parts) > 4 else None,
                    "mean1": _num(parts[5]) if len(parts) > 5 else None,
                    "sd1": _num(parts[6]) if len(parts) > 6 else None,
                    "delta": _num(parts[7]) if len(parts) > 7 else None,
                    "p": _num(parts[8]) if len(parts) > 8 else None,
                }
            )
        else:
            panels["C"].append(
                {
                    "label": label,
                    "n0": _num(parts[1]),
                    "mean0": _num(parts[2]),
                    "sd0": _num(parts[3]),
                }
            )

    return panels


def _label_key(label: str) -> str:
    return label.replace("\\", "").strip()


def validate_against_manuscript(panels: dict) -> list[tuple[str, float, float]]:
    parsed = _parse_manuscript_table(MANUSCRIPT_BODY_TABLES / "1_sum_stats_d.tex")
    checks: list[tuple[str, float, float]] = []
    tol = max(COEF_TOLERANCE, 0.011)  # manuscript rounds to 2 decimals

    for panel_key in ("A", "B"):
        computed = { _label_key(r.label): r for r in panels[panel_key].rows }
        for exp in parsed[panel_key]:
            key = _label_key(exp["label"])
            row = computed.get(key) or computed.get(exp["label"])
            if row is None:
                continue
            for field, comp_attr, grp in [
                ("n0", "n_obs", 0),
                ("mean0", "mean", 0),
                ("sd0", "std", 0),
                ("n1", "n_obs", 1),
                ("mean1", "mean", 1),
                ("sd1", "std", 1),
                ("delta", "delta_mean", None),
                ("p", "p_value", None),
            ]:
                expected = exp.get(field)
                if expected is None:
                    continue
                if grp == 0:
                    actual = getattr(row.group0, comp_attr)
                elif grp == 1:
                    actual = getattr(row.group1, comp_attr)
                elif comp_attr == "delta_mean":
                    actual = row.delta_mean
                else:
                    actual = row.p_value
                if actual is None:
                    continue
                checks.append((f"panel{panel_key}.{key}.{field}", expected, float(actual)))

    for exp in parsed["C"]:
        key = _label_key(exp["label"])
        row = next((r for r in panels["C"].rows if _label_key(r.label) == key), None)
        if row is None or exp["n0"] is None:
            continue
        checks.append((f"panelC.{key}.n0", exp["n0"], float(row.group0.n_obs)))
        checks.append((f"panelC.{key}.mean0", exp["mean0"], row.group0.mean))
        checks.append((f"panelC.{key}.sd0", exp["sd0"], row.group0.std))

    return checks


def write_latex_table(panels: dict, path: Path | None = None) -> Path:
    """Write full table environment to refactor output (and return path)."""
    out = path or (REFACTOR_OUTPUT_TABLES_BODY / "1_sum_stats_d.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_table1_latex(panels), encoding="utf-8")
    return out


def main() -> dict:
    df = load_panel()
    panels = compute_all_panels(df)
    checks = validate_against_manuscript(panels)

    failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in checks
        if abs(exp - act) > max(COEF_TOLERANCE, 0.011)
    ]
    if failures:
        raise AssertionError(
            "Table 1 validation failed "
            f"({len(failures)}/{len(checks)} checks):\n" + "\n".join(failures[:20])
        )

    print(f"Table 1 — all {len(checks)} manuscript checks passed")
    for key, p in panels.items():
        cfg = PANELS[key]
        if cfg["split"]:
            r0 = p.rows[0].group0
            r1 = p.rows[0].group1
            print(
                f"  Panel {key} ({cfg['year_lo']}–{cfg['year_hi']}): "
                f"firms {r0.n_firms}/{r1.n_firms}, "
                f"N {r0.n_obs}/{r1.n_obs}"
            )
        else:
            print(
                f"  Panel {key} ({cfg['year_lo']}–{cfg['year_hi']}): "
                f"N={p.rows[0].group0.n_obs}, firms={p.rows[0].group0.n_firms}"
            )

    out_path = write_latex_table(panels)
    print(f"  Wrote LaTeX table -> {out_path}")

    return panels


if __name__ == "__main__":
    main()
