"""Figure — industrial corporate bond offerings (Hickman 1953).

Place annual par amounts (millions USD) in ``data/raw/figures/hickman_industrial_bonds.csv``
with columns ``year,par_millions``. The manuscript cites Hickman (1953); this file is not
built from A4/A1 and must be supplied from the NBER volume or Mete's original figure data.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from config import MANUSCRIPT_BODY_FIGURES, RAW_DIR, REFACTOR_OUTPUT_FIGURES

HICKMAN_CSV = RAW_DIR / "figures" / "hickman_industrial_bonds.csv"


def build_hickman_issuance_plot(*, out_dir: Path | None = None) -> Path | None:
    if not HICKMAN_CSV.is_file():
        return None

    frame = pd.read_csv(HICKMAN_CSV)
    if not {"year", "par_millions"}.issubset(frame.columns):
        raise ValueError(f"{HICKMAN_CSV} must have columns year, par_millions")

    dest = Path(out_dir) if out_dir is not None else REFACTOR_OUTPUT_FIGURES
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

    MANUSCRIPT_BODY_FIGURES.mkdir(parents=True, exist_ok=True)
    manuscript_path = MANUSCRIPT_BODY_FIGURES / out_path.name
    manuscript_path.write_bytes(out_path.read_bytes())
    return manuscript_path


def main() -> None:
    path = build_hickman_issuance_plot()
    if path is None:
        print(f"Skip Hickman figure — add {HICKMAN_CSV}")
    else:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
