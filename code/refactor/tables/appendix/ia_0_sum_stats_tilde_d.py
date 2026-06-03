"""
Internet Appendix Table 0 — Summary statistics by tilde-d exposure (tab:sum_stats_tilde_d).

Splits all panels by dind (I{d>0}), matching manuscript 0_sum_stats_tilde_d.tex.
Stata reference: A14_summary_stats_IA.do (replace dind = (d > 0); ttest by dind).
"""

from __future__ import annotations

import re
from pathlib import Path

from config import (
    A4_PATH,
    COEF_TOLERANCE,
    MANUSCRIPT_APPENDIX_TABLES,
    REFACTOR_OUTPUT_TABLES_APPENDIX,
)
from lib.io import read_dta
from lib.render_sum_stats_tex import render_tilde_d_summary_latex
from lib.summary_stats import TILDE_D_PANELS, compute_tilde_d_panels

TOL = max(COEF_TOLERANCE, 0.011)


def load_panel():
    return read_dta(A4_PATH)


def _parse_manuscript_table(tex_path: Path) -> dict[str, list[dict]]:
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
        if not any(
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

        parts = [p.strip().rstrip("\\").strip() for p in line.split("&")]
        if len(parts) < 9:
            continue

        label = parts[0].replace(r"\ensuremath{\tilde{d}}", "tilde{d}").strip()
        label = re.sub(r"\\ensuremath\{([^}]+)\}", r"\1", label)

        def _num(s: str) -> float | None:
            s = (
                s.strip()
                .replace("$-$", "-")
                .replace("{", "")
                .replace("}", "")
                .replace(",", "")
            )
            if not s:
                return None
            try:
                return float(s)
            except ValueError:
                return None

        panels[current].append(
            {
                "label": label,
                "n0": _num(parts[1]),
                "mean0": _num(parts[2]),
                "sd0": _num(parts[3]),
                "n1": _num(parts[4]),
                "mean1": _num(parts[5]),
                "sd1": _num(parts[6]),
                "delta": _num(parts[7]),
                "p": _num(parts[8]),
            }
        )

    return panels


def _label_key(label: str) -> str:
    label = label.replace(r"\ensuremath{\tilde{d}}", "tilde{d}")
    label = re.sub(r"\\ensuremath\{([^}]+)\}", r"\1", label)
    return label.replace("\\", "").strip()


def validate_against_manuscript(panels: dict) -> list[tuple[str, float, float]]:
    parsed = _parse_manuscript_table(
        MANUSCRIPT_APPENDIX_TABLES / "0_sum_stats_tilde_d.tex"
    )
    checks: list[tuple[str, float, float]] = []

    for panel_key in ("A", "B", "C"):
        computed = {_label_key(r.label): r for r in panels[panel_key].rows}
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

    return checks


def write_latex_table(panels: dict, path: Path | None = None) -> Path:
    out = path or (REFACTOR_OUTPUT_TABLES_APPENDIX / "0_sum_stats_tilde_d.tex")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_tilde_d_summary_latex(panels), encoding="utf-8")
    return out


def main() -> dict:
    df = load_panel()
    panels = compute_tilde_d_panels(df)
    checks = validate_against_manuscript(panels)

    failures = [
        f"{name}: expected {exp:.4f}, got {act:.4f}"
        for name, exp, act in checks
        if abs(exp - act) > TOL
    ]
    if failures:
        raise AssertionError(
            "IA Table 0 (tilde-d) validation failed "
            f"({len(failures)}/{len(checks)} checks):\n" + "\n".join(failures[:20])
        )

    print(f"IA Table 0 (tilde-d) — all {len(checks)} manuscript checks passed")
    for key, p in panels.items():
        cfg = TILDE_D_PANELS[key]
        r0 = p.rows[0].group0
        r1 = p.rows[0].group1
        assert r0 is not None and r1 is not None
        print(
            f"  Panel {key} ({cfg['year_lo']}–{cfg['year_hi']}): "
            f"firms {r0.n_firms}/{r1.n_firms}, "
            f"N {r0.n_obs}/{r1.n_obs}"
        )

    out_path = write_latex_table(panels)
    print(f"  Wrote LaTeX table -> {out_path}")

    return panels


if __name__ == "__main__":
    main()
