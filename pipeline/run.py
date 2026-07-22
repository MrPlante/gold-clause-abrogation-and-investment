#!/usr/bin/env python3
"""Run the data pipeline: data/raw/ sources -> data/processed/firm_year_panel.dta.

Usage (from the repo root):
    .venv/bin/python pipeline/run.py

The A0-A3 stages run in memory (nothing is persisted besides the final
panel). The rebuilt panel matches the manuscript panel exactly (7,074 x 845,
to float32 storage precision); see DISCREPANCIES.md D-016/D-018.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> None:
    from pipeline.build import build_all

    path = build_all()
    print(f"Built merged panel: {path}")


if __name__ == "__main__":
    main()
