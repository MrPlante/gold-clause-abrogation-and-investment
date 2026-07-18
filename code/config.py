"""Paths and analysis constants for the Python refactor of Mete's Stata pipeline."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERMEDIATES_DIR = DATA_DIR / "intermediates"

# Pipeline intermediates, A0-A3 (regenerable from raw; see data/README.md)
A0_PATH = INTERMEDIATES_DIR / "A0_accounting_data.dta"
A1_BOND_PATH = INTERMEDIATES_DIR / "A1_bond_data_bondlevel.dta"
A1_FIRM_PATH = INTERMEDIATES_DIR / "A1_bond_data_firmlevel.dta"
A2_PATH = INTERMEDIATES_DIR / "A2_marcap.dta"
A3_MONTHLY_PATH = INTERMEDIATES_DIR / "A3_dividend_monthly.dta"
A3_ANNUAL_PATH = INTERMEDIATES_DIR / "A3_dividend_annual.dta"

# The merged panel (the one file everything downstream reads)
A4_PATH = DATA_DIR / "A4_merged.dta"

# Source inputs with external provenance (never regenerated; data/raw/)
MONTHLY_DIV_PATH = RAW_DIR / "monthly_div.dta"
CHARS_ANNUAL_PATH = RAW_DIR / "chars_annual.dta"
CRSP_MONTHLY_PATH = RAW_DIR / "crsp_monthly.dta"
NETINCOME_PATH = RAW_DIR / "netincome.dta"
ACCOUNTING_CSV = RAW_DIR / "accounting_data.csv"    # missing on this machine
GOLD_CLAUSES_XLSX = RAW_DIR / "gold_clauses.xlsx"   # missing on this machine

MANUSCRIPT_BODY_TABLES = REPO_ROOT / "manuscript" / "tables" / "body"
MANUSCRIPT_APPENDIX_TABLES = REPO_ROOT / "manuscript" / "tables" / "online-appendix"
MANUSCRIPT_BODY_FIGURES = REPO_ROOT / "manuscript" / "figures" / "body"
MANUSCRIPT_APPENDIX_FIGURES = REPO_ROOT / "manuscript" / "figures" / "online-appendix"

REFACTOR_OUTPUT = Path(__file__).resolve().parent / "output"
REFACTOR_OUTPUT_TABLES = REFACTOR_OUTPUT / "tables"
REFACTOR_OUTPUT_TABLES_BODY = REFACTOR_OUTPUT_TABLES / "body"
REFACTOR_OUTPUT_TABLES_APPENDIX = REFACTOR_OUTPUT_TABLES / "online-appendix"
REFACTOR_OUTPUT_FIGURES = REFACTOR_OUTPUT / "figure"

SAMPLE_YEARS = (1926, 1940)
OMITTED_YEAR = 1932
WINSOR_BY = "year"
WINSOR_CUTS = (0.005, 0.995)  # Stata cuts(0.5 99.5)

UNRELIABLE_PERMNO = {11631, 15093, 15528, 24475, 13063, 14250}

CLUSTER = {"CRV1": "permno + year"}

# Two-way cluster SEs: set USE_STATA_VCOV=1 to match reghdfe exactly (requires stata-mp).
# Default "auto" uses Stata when /usr/local/stata/stata-mp exists; else CGM fix on pyfixest vcov.

COEF_TOLERANCE = 0.001
