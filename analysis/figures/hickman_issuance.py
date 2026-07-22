"""Figure — industrial corporate bond offerings (Hickman 1953).

Data: ``figures/data/hickman_industrial_bonds.csv`` (versioned), transcribed
from Hickman (1953), Appendix A, Table A-2 (straight corporate bonds),
Industrials panel, column "Offered during year", 1920-1940, millions of
dollars par value. Verified 2026-07-17 against the NBER chapter scan
(nber.org/chapters/c3090) and against a calibrated pixel extraction of the
original manuscript figure (max deviation 4.5 USDm, within rendering error).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from config import MANUSCRIPT_BODY_FIGURES

HICKMAN_CSV = Path(__file__).resolve().parent / "source-data" / "hickman_industrial_bonds.csv"


def build_hickman_issuance_plot(*, out_dir: Path | None = None) -> Path | None:
    if not HICKMAN_CSV.is_file():
        return None

    frame = pd.read_csv(HICKMAN_CSV)
    if not {"year", "par_millions"}.issubset(frame.columns):
        raise ValueError(f"{HICKMAN_CSV} must have columns year, par_millions")

    dest = Path(out_dir) if out_dir is not None else MANUSCRIPT_BODY_FIGURES
    out_path = dest / "industrial_corp_bond_issuance.pdf"

    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=150)
    ax.bar(frame["year"], frame["par_millions"], color="black", width=0.7)
    ax.set_xlabel("Year")
    ax.set_ylabel("New offerings (par, millions USD)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)

    return out_path


def main() -> None:
    path = build_hickman_issuance_plot()
    if path is None:
        print(f"Skip Hickman figure — add {HICKMAN_CSV}")
    else:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
