"""Build all manuscript figures that can be generated from this repo."""

from __future__ import annotations

from pathlib import Path

from config import MANUSCRIPT_APPENDIX_FIGURES
from figures.hickman_issuance import HICKMAN_CSV, build_hickman_issuance_plot
from figures.macro_plots import MONTHLY_MACRO_CSV, build_macro_figures
from figures.parallel_trend_plot import build_parallel_trend_plot


def build_all() -> dict[str, Path | None]:
    """Return map of figure name → output path (None if skipped)."""
    results: dict[str, Path | None] = {}

    pt_path, _ = build_parallel_trend_plot()
    results["parallel_trend_plot"] = pt_path

    try:
        macro = build_macro_figures()
        results.update(macro)
    except Exception as exc:
        print(f"Macro figures failed ({exc}); cache at {MONTHLY_MACRO_CSV}")

    hickman = build_hickman_issuance_plot()
    results["industrial_corp_bond_issuance"] = hickman
    if hickman is None:
        print(f"Hickman figure skipped — add {HICKMAN_CSV}")

    appendix_png = MANUSCRIPT_APPENDIX_FIGURES / "cfc_bond_quotes.png"
    if not appendix_png.is_file():
        print(
            "Appendix figure cfc_bond_quotes.png not regenerated "
            "(static scan; place file under manuscript/figures/online-appendix/)."
        )
        results["cfc_bond_quotes"] = None
    else:
        results["cfc_bond_quotes"] = appendix_png

    return results


def main() -> None:
    built = build_all()
    for name, path in built.items():
        status = path if path else "skipped"
        print(f"{name}: {status}")


if __name__ == "__main__":
    main()
