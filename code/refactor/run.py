#!/usr/bin/env python3
"""Run refactor pipeline stages."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REFACTOR_ROOT = Path(__file__).resolve().parent
if str(REFACTOR_ROOT) not in sys.path:
    sys.path.insert(0, str(REFACTOR_ROOT))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Gold clause Python refactor pipeline")
    parser.add_argument(
        "--stage",
        choices=["data", "table1", "table2", "table3", "table4", "table5", "table6", "table7", "all"],
        default="table3",
        help="Pipeline stage to run",
    )
    parser.add_argument(
        "--skip-raw",
        action="store_true",
        help="Build A4 from existing A0–A3 .dta (skip raw CSV/XLSX)",
    )
    args = parser.parse_args(argv)

    if args.stage in ("data", "all"):
        from data.build import build_all

        path = build_all(skip_raw=args.skip_raw)
        print(f"Built merged panel: {path}")

    if args.stage in ("table1", "all"):
        from tables.body.t01_summary_stats import main as run_table1

        run_table1()

    if args.stage in ("table2", "all"):
        from tables.body.t02_bond_stats import main as run_table2

        run_table2()

    if args.stage in ("table3", "all"):
        from tables.body.t03_investment import main as run_table3

        run_table3()

    if args.stage in ("table4", "all"):
        from tables.body.t04_other_outcomes import main as run_table4

        run_table4()

    if args.stage in ("table5", "all"):
        from tables.body.t05_credit_ratings import main as run_table5

        run_table5()

    if args.stage in ("table6", "all"):
        from tables.body.t06_controls import main as run_table6

        run_table6()

    if args.stage in ("table7", "all"):
        from tables.body.t07_aggregate import main as run_table7

        run_table7()


if __name__ == "__main__":
    main()
