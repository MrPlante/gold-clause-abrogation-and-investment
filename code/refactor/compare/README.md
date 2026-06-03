# Stata vs Python regression comparison

Runs the **same regressions** in Mete’s Stata pipeline (`code/mete/`) and the Python refactor (`code/refactor/`), exports coefficients / SE / N / R², and writes a diff report.

## Prerequisites

1. **Stata** (MP/SE/BE) on `PATH`, or set `STATA_BIN`:
   ```bash
   export STATA_BIN=/usr/local/stata/stata-mp
   ```
2. **User packages** (installed automatically on first run if missing; or manually):
   ```stata
   ssc install require ftools reghdfe winsor2, replace
   ftools, compile
   ```
3. **Data:** `data/A4_merged.dta` (Mete-built panel).
4. **Python venv:** `code/refactor/.venv` with refactor dependencies.

**Standard errors:** Python export uses `reghdfe` vcov via Stata when `stata-mp` is available (`USE_STATA_VCOV=auto`, default). Set `USE_STATA_VCOV=0` to use pyfixest with a Cameron–Gelbach–Miller PSD fix only (may differ slightly on some year interactions).

## Quick start

From the repository root:

```bash
bash code/refactor/compare/run_compare.sh
```

Outputs:

| File | Description |
|------|-------------|
| `output/stata_regressions.csv` | Coefficients from `export_regressions.do` |
| `output/python_regressions.csv` | Coefficients from `export_python.py` |
| `output/comparison_report.md` | Summary and largest differences |
| `output/comparison_merged.csv` | Full outer join with diffs |

Fail CI-style if any coefficient differs:

```bash
bash code/refactor/compare/run_compare.sh --fail-on-mismatch
```

## What is compared

| Table | Stata source | Python module |
|-------|--------------|---------------|
| 3 (subset) | `A9_inv_results.do` | `t03_investment.py` |
| 4 | `A10_otheroutcomes.do` | `lib/other_outcomes.py` |
| 5 | `A21_ratings_yearbyyear.do` | `lib/credit_ratings.py` |

**Table 3:** Stata export includes `classic`, `overhang`, `no_maturity`, `dalt`, `pref_shares`, `bank_debt`. Python also has `no_redemption` and `positive_ltl` (not in the Stata export script); those appear as Python-only rows.

**Table 4:** Stata follows literal `A10` (`denom2 = netppe_bs if year <= min_year`). Python uses a `min_year` fallback for pre-1930-only firms, so **N** for `nippe` / `cashppe` may differ even when coefficients match on the overlapping sample.

**Table 5:** Both use demeaned `d` and `cashrat` for the dividend column (manuscript col 2).

## Manual steps

```bash
cd /path/to/gold-clause-abrogation-and-investment
bash code/refactor/scripts/run_stata_do.sh code/refactor/compare/export_regressions.do
code/refactor/.venv/bin/python code/refactor/compare/export_python.py
code/refactor/.venv/bin/python code/refactor/compare/compare_results.py
```

Stata batch logs are written to `logs/stata/` (see `logs/README.md`).

## Tolerances

Default in `compare_results.py`:

- Coefficients: `1e-3`
- SE: `1e-3`
- R²: `1e-3`
- N: exact match

Adjust constants at the top of `compare_results.py` if needed.

## Extending

Add regressions to **both**:

1. `export_regressions.do` — mirror the Stata `.do` logic, call `_post_reghdfe`.
2. `export_python.py` — call the matching `run_models` / `fit_*` helper.

Use consistent `table` and `model` keys so rows align on merge.
