#!/usr/bin/env python3
"""Run the data pipeline: raw sources -> A0-A3 intermediates -> A4_merged.dta.

Usage (from the repo root):
    .venv/bin/python pipeline/run.py             # full raw -> A4 build
    .venv/bin/python pipeline/run.py --skip-raw  # rebuild A4 from existing A0-A3

The rebuilt panel matches the manuscript panel exactly (7,074 x 845, to
float32 storage precision); see DISCREPANCIES.md D-016/D-018.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Gold clause data pipeline (raw -> A4)")
    parser.add_argument(
        "--skip-raw",
        action="store_true",
        help="Build A4 from existing A0-A3 .dta (skip the raw CSV/XLSX stages)",
    )
    args = parser.parse_args(argv)

    from pipeline.build import build_all

    path = build_all(skip_raw=args.skip_raw)
    print(f"Built merged panel: {path}")


if __name__ == "__main__":
    main()
