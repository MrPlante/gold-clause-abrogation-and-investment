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
        choices=[
            "data",
            "table1",
            "table2",
            "table3",
            "table4",
            "table5",
            "table6",
            "table7",
            "ia0a",
            "ia0b",
            "ia0tilde",
            "ia2",
            "ia3",
            "ia4",
            "ia5",
            "ia6",
            "ia7",
            "ia8",
            "ia9",
            "ia10",
            "ia11",
            "ia12",
            "ia13",
            "ia14",
            "ia15",
            "ia16",
            "compare",
            "figures",
            "all",
        ],
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

    if args.stage in ("ia0a", "all"):
        from tables.appendix.ia_0a_summary_d_1 import main as run_ia0a

        run_ia0a()

    if args.stage in ("ia0b", "all"):
        from tables.appendix.ia_0b_summary_d_0 import main as run_ia0b

        run_ia0b()

    if args.stage in ("ia0tilde", "all"):
        from tables.appendix.ia_0_sum_stats_tilde_d import main as run_ia0tilde

        run_ia0tilde()

    if args.stage in ("ia2", "all"):
        from tables.appendix.ia_2_summary_I_1 import main as run_ia2

        run_ia2()

    if args.stage in ("ia3", "all"):
        from tables.appendix.ia_3_summary_I_0 import main as run_ia3

        run_ia3()

    if args.stage in ("ia4", "all"):
        from tables.appendix.ia_4_summary_I_smalld import main as run_ia4

        run_ia4()

    if args.stage in ("ia5", "all"):
        from tables.appendix.ia_5_summary_I_larged import main as run_ia5

        run_ia5()

    if args.stage in ("ia6", "all"):
        from tables.appendix.ia_6_correlation import main as run_ia6

        run_ia6()

    if args.stage in ("ia7", "all"):
        from tables.appendix.ia_7_credit_ratings_full import main as run_ia7

        run_ia7()

    if args.stage in ("ia8", "all"):
        from tables.appendix.ia_8_summary_pos_ps_bond import main as run_ia8

        run_ia8()

    if args.stage in ("ia9", "all"):
        from tables.appendix.ia_9_summary_diff_pos_ps_bond import main as run_ia9

        run_ia9()

    if args.stage in ("ia10", "all"):
        from tables.appendix.ia_10_repayers_balanced import main as run_ia10

        run_ia10()

    if args.stage in ("ia11", "all"):
        from tables.appendix.ia_11_constraints import main as run_ia11

        run_ia11()

    if args.stage in ("ia12", "all"):
        from tables.appendix.ia_12_quarterly_div import main as run_ia12

        run_ia12()

    if args.stage in ("ia13", "all"):
        from tables.appendix.ia_13_dividend_additional import main as run_ia13

        run_ia13()

    if args.stage in ("ia14", "all"):
        from tables.appendix.ia_14_indicators_d import main as run_ia14

        run_ia14()

    if args.stage in ("ia15", "all"):
        from tables.appendix.ia_15_controls_extra import main as run_ia15

        run_ia15()

    if args.stage in ("ia16", "all"):
        from tables.appendix.ia_16_aggregate_heterogeneous import main as run_ia16

        run_ia16()

    if args.stage in ("figures", "all"):
        from figures.build import main as run_figures

        run_figures()

    if args.stage == "compare":
        import subprocess

        repo = REFACTOR_ROOT.parents[1]
        script = REFACTOR_ROOT / "compare" / "run_compare.sh"
        result = subprocess.run(["bash", str(script)], cwd=repo, check=False)
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
