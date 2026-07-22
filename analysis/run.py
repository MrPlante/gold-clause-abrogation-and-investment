#!/usr/bin/env python3
"""Run analysis stages (tables, figures, event study).

Data wrangling lives in pipeline/ (see pipeline/run.py); this runner only
produces the numbers in the paper from data/processed/firm_year_panel.dta.

Stage names match manuscript labels: --stage table4 builds manuscript
Table 4, --stage ia19 builds Internet Appendix Table IA.19. Manuscript
Table 1 and Table IA.20 are built by the eventstudy stage.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parent
REPO_ROOT = ANALYSIS_ROOT.parent
for _p in (str(ANALYSIS_ROOT), str(REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# stage name (= manuscript label) -> module whose main() builds it.
# "all" runs every entry in this order.
STAGES = {
    "table2": "tables.body.t02_summary_stats",
    "table3": "tables.body.t03_bond_stats",
    "table4": "tables.body.t04_investment",
    "table5": "tables.body.t05_other_outcomes",
    "table6": "tables.body.t06_credit_ratings",
    "table7": "tables.body.t07_controls",
    "table8": "tables.body.t08_aggregate",
    "ia1": "tables.appendix.ia01_summary_d_1",
    "ia2": "tables.appendix.ia02_summary_d_0",
    "ia3": "tables.appendix.ia03_sum_stats_tilde_d",
    "ia4": "tables.appendix.ia04_summary_I_1",
    "ia5": "tables.appendix.ia05_summary_I_0",
    "ia6": "tables.appendix.ia06_summary_I_smalld",
    "ia7": "tables.appendix.ia07_summary_I_larged",
    "ia8": "tables.appendix.ia08_correlation",
    "ia9": "tables.appendix.ia09_credit_ratings_full",
    "ia10": "tables.appendix.ia10_summary_pos_ps_bond",
    "ia11": "tables.appendix.ia11_summary_diff_pos_ps_bond",
    "ia12": "tables.appendix.ia12_repayers_balanced",
    "ia13": "tables.appendix.ia13_constraints",
    "ia14": "tables.appendix.ia14_quarterly_div",
    "ia15": "tables.appendix.ia15_dividend_additional",
    "ia16": "tables.appendix.ia16_indicators_d",
    "ia17": "tables.appendix.ia17_stock_controls",
    "ia18": "tables.appendix.ia18_aggregate_heterogeneous",
    "ia19": "tables.appendix.ia19_controls_indyear",
    "figures": "figures.build",
    # Reads data/raw/crsp_daily.dta (local dump of gold_claude.crsp; no
    # researchdb access needed). Builds Table 1, Figures 3-5, IA.2, IA.3,
    # and Table IA.20 directly into manuscript/.
    "eventstudy": "eventstudy.pipeline",
}


# Stages whose builders are KNOWN not to reproduce the shipped (Mete-original)
# manuscript tables. "all" skips them so a full run cannot silently overwrite
# a shipped table; run them explicitly with --stage to regenerate anyway.
# Empty since the D-021 addendum resolved ia7/ia10/ia11 (exact reproduction).
FROZEN: set[str] = set()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Gold clause analysis stages")
    parser.add_argument(
        "--stage",
        choices=[*STAGES, "compare", "all"],
        default="table4",
        help="Stage to run (names match manuscript labels; default: table4)",
    )
    args = parser.parse_args(argv)

    if args.stage == "compare":
        import subprocess

        script = ANALYSIS_ROOT / "compare" / "run_compare.sh"
        result = subprocess.run(["bash", str(script)], cwd=REPO_ROOT, check=False)
        raise SystemExit(result.returncode)

    for stage, module in STAGES.items():
        if args.stage == "all" and stage in FROZEN:
            print(f"[skip] {stage}: builder does not reproduce the shipped "
                  f"table (DISCREPANCIES.md); run --stage {stage} explicitly.")
            continue
        if args.stage in (stage, "all"):
            importlib.import_module(module).main()


if __name__ == "__main__":
    main()
