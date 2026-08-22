"""Shared paths and constants for pipeline/ (data wrangling) and analysis/."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Pipeline outputs (data/processed/): the merged panel plus the bond-level
# panel that Table 3 reads directly (bond-level rows never reach A4). The
# other source stages are held in memory by pipeline/build.py, not persisted.
PANEL_PATH = PROCESSED_DIR / "firm_year_panel.dta"
BOND_PANEL_PATH = PROCESSED_DIR / "bond_panel.dta"

# Source inputs with external provenance (never regenerated; data/raw/)
MONTHLY_DIV_PATH = RAW_DIR / "monthly_div.dta"
CHARS_ANNUAL_PATH = RAW_DIR / "chars_annual.dta"
CRSP_MONTHLY_PATH = RAW_DIR / "crsp_monthly.dta"
NETINCOME_PATH = RAW_DIR / "netincome.dta"
ACCOUNTING_CSV = RAW_DIR / "accounting_data.csv"
GOLD_CLAUSES_XLSX = RAW_DIR / "gold_clauses.xlsx"

# Analysis outputs: generated tables/figures go straight into the manuscript
MANUSCRIPT_BODY_TABLES = REPO_ROOT / "manuscript" / "tables" / "body"
MANUSCRIPT_APPENDIX_TABLES = REPO_ROOT / "manuscript" / "tables" / "online-appendix"
MANUSCRIPT_BODY_FIGURES = REPO_ROOT / "manuscript" / "figures" / "body"
MANUSCRIPT_APPENDIX_FIGURES = REPO_ROOT / "manuscript" / "figures" / "online-appendix"

SAMPLE_YEARS = (1926, 1940)
OMITTED_YEAR = 1932
WINSOR_BY = "year"
WINSOR_CUTS = (0.005, 0.995)  # Stata cuts(0.5 99.5)

UNRELIABLE_PERMNO = {11631, 15093, 15528, 24475, 13063, 14250}

CLUSTER = {"CRV1": "permno + year"}

# Printed standard errors come from the per-table reghdfe do-files in
# analysis/stata/ (batch stata-mp, engine version pinned per table; see
# DISCREPANCIES.md D-023). The former USE_STATA_VCOV in-process bridge is gone;
# pyfixest (CGM fix) remains only for coefficient-only consumers (T8/IA.18).

COEF_TOLERANCE = 0.001
