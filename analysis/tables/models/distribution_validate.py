"""Shared manuscript validation for IA distribution summary tables."""

from __future__ import annotations

import re
from pathlib import Path


def parse_distribution_table(tex_path: Path) -> dict[str, list[dict]]:
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
        if len(parts) != 10:
            continue

        label = parts[0]
        if not label or label.startswith("("):
            continue

        def _num(s: str) -> float | None:
            s = s.strip().replace("$-$", "-")
            if not s:
                return None
            try:
                return float(s)
            except ValueError:
                return None

        def _int(s: str) -> int | None:
            s = s.strip().replace(",", "")
            if not s:
                return None
            try:
                return int(s)
            except ValueError:
                return None

        panels[current].append(
            {
                "label": label,
                "firms": _int(parts[1]),
                "n": _int(parts[2]),
                "mean": _num(parts[3]),
                "sd": _num(parts[4]),
                "p5": _num(parts[5]),
                "p25": _num(parts[6]),
                "p50": _num(parts[7]),
                "p75": _num(parts[8]),
                "p95": _num(parts[9]),
            }
        )

    return panels


def label_key(label: str) -> str:
    label = re.sub(r"\\ensuremath\{([^}]+)\}", r"\1", label)
    return label.replace(r"\ ", " ").strip()


def validate_distribution_panels(
    panels: dict,
    parsed: dict[str, list[dict]],
    *,
    panel_order: tuple[str, ...] = ("A", "B", "C"),
    tol: float = 0.011,
    percentile_tol: float | None = None,
) -> list[tuple[str, float, float]]:
    pct_tol = percentile_tol if percentile_tol is not None else tol
    checks: list[tuple[str, float, float]] = []

    for panel_key in panel_order:
        if panel_key not in parsed:
            continue
        computed = {label_key(r.label): r for r in panels[panel_key].rows}
        for exp in parsed[panel_key]:
            key = label_key(exp["label"])
            row = computed.get(key)
            if row is None:
                continue
            s = row.stats
            mapping = {
                "firms": s.n_firms,
                "n": s.n_obs,
                "mean": s.mean,
                "sd": s.std,
                "p5": s.p5,
                "p25": s.p25,
                "p50": s.p50,
                "p75": s.p75,
                "p95": s.p95,
            }
            for field, actual in mapping.items():
                expected = exp.get(field)
                if expected is None:
                    continue
                field_tol = pct_tol if field.startswith("p") else tol
                checks.append((f"panel{panel_key}.{key}.{field}", float(expected), float(actual)))

    return checks


def check_failures(
    checks: list[tuple[str, float, float]],
    *,
    tol: float = 0.011,
    percentile_tol: float | None = None,
) -> list[str]:
    pct_tol = percentile_tol if percentile_tol is not None else tol
    failures: list[str] = []
    for name, exp, act in checks:
        field = name.split(".")[-1]
        field_tol = pct_tol if field.startswith("p") else tol
        if abs(exp - act) > field_tol:
            failures.append(f"{name}: expected {exp:.4f}, got {act:.4f}")
    return failures
