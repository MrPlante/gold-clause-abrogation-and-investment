"""Validate regression output against manuscript .tex tables."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from config import COEF_TOLERANCE


@dataclass
class CoefCheck:
    name: str
    expected: float
    actual: float
    column: int

    @property
    def ok(self) -> bool:
        return abs(self.expected - self.actual) <= COEF_TOLERANCE


def parse_manuscript_table(tex_path: Path) -> dict[str, list[float]]:
    """
    Parse coefficient rows from a manuscript table .tex file.

    Returns {row_label: [col1, col2, ...]} for numeric coefficient lines
    (not SE lines in parentheses).
    """
    text = tex_path.read_text(encoding="utf-8")
    rows: dict[str, list[float]] = {}
    current_label: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%"):
            continue
        if line.startswith("\\"):
            label_match = re.match(r"\\ensuremath\{([^}]+)\}|^Q\s", line)
            if line.startswith("Q ") or line.startswith("Q\\"):
                current_label = "Q"
            elif "\\ensuremath" in line:
                inner = re.search(r"\\ensuremath\{([^}]+)\}", line)
                if inner:
                    current_label = inner.group(1).replace("\\tilde{d}", "d").replace("\\text{", "").replace("}", "")
            elif line.startswith("\\midrule") or line.startswith("\\bottomrule"):
                current_label = None
            continue

        if line.startswith("(") and line.endswith(")"):
            continue

        if "&" not in line:
            continue

        parts = [p.strip() for p in line.split("&")]
        if not parts:
            continue

        label = parts[0] if parts[0] else current_label
        if label is None:
            continue

        nums: list[float] = []
        for cell in parts[1:]:
            cell = re.sub(r"\\sym\{[*]+\}", "", cell)
            cell = cell.strip()
            if not cell:
                nums.append(float("nan"))
                continue
            try:
                nums.append(float(cell))
            except ValueError:
                nums.append(float("nan"))

        if any(not np.isnan(x) for x in nums for np in [__import__("numpy")]):
            import numpy as np

            if any(not np.isnan(x) for x in nums):
                rows[label] = nums
                current_label = label

    return rows


def compare_to_manuscript(
    checks: list[tuple[str, int, float]],
    tex_path: Path,
) -> list[CoefCheck]:
    """checks: list of (coef_name, column_index_0based, actual_value)."""
    parsed = parse_manuscript_table(tex_path)
    results: list[CoefCheck] = []

    label_map = {
        "var_Q": "Q",
        "d": "d",
        "ps": "d",
        "bd": "d",
    }

    for coef_name, col, actual in checks:
        label = label_map.get(coef_name, coef_name)
        if coef_name.startswith("d_year_") or coef_name.startswith("ps_year_") or coef_name.startswith("bd_year_"):
            yr = coef_name.split("_")[-1]
            label = f"\\text{{{yr}}} \\times \\tilde{{d}}"
            # parser may simplify differently; match by year in parsed keys
            for key, vals in parsed.items():
                if yr in key and col < len(vals):
                    expected = vals[col]
                    results.append(CoefCheck(coef_name, expected, actual, col))
                    break
            continue

        if label not in parsed:
            continue
        expected = parsed[label][col]
        results.append(CoefCheck(coef_name, expected, actual, col))

    return results


def assert_checks(results: list[CoefCheck]) -> None:
    import numpy as np

    failures = [r for r in results if not r.ok and not (np.isnan(r.expected) and np.isnan(r.actual))]
    if failures:
        lines = [
            f"  {f.name} col {f.column + 1}: expected {f.expected:.4f}, got {f.actual:.4f}"
            for f in failures
        ]
        raise AssertionError("Coefficient validation failed:\n" + "\n".join(lines))
