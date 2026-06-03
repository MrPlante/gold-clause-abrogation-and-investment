"""LaTeX table formatting."""

from __future__ import annotations

import numpy as np

from lib.vcov import fix_vcov, model_pvalue, model_se

__all__ = [
    "stars_tex",
    "fmt_coef",
    "fmt_se",
    "fix_vcov",
    "model_se",
    "model_pvalue",
]


def stars_tex(p: float) -> str:
    if np.isnan(p):
        return ""
    if p < 0.01:
        return "\\sym{***}"
    if p < 0.05:
        return "\\sym{**}"
    if p < 0.1:
        return "\\sym{*}"
    return ""


def fmt_coef(value: float, p: float, decimals: int = 3) -> str:
    return f"{value:.{decimals}f}{stars_tex(p)}"


def fmt_se(value: float, decimals: int = 3) -> str:
    return f"({value:.{decimals}f})"
