# Python refactor of Mete's Stata pipeline

Replicates all manuscript tables from `code/mete/` with Stata-matched econometrics
(two-way clustered SEs, same sample windows, winsorization).

## Layout

```
code/refactor/
├── config.py           # paths, constants
├── run.py              # CLI entry point
├── setup.sh            # create .venv and install dependencies
├── data/               # A0–A4 data build (Stata A0_accounting … A4_merge)
├── lib/                # regressions, winsorization, LaTeX, validation
├── tables/
│   ├── body/           # manuscript Tables 1–7
│   └── appendix/       # Internet Appendix tables
├── output/
│   ├── tables/
│   │   ├── body/       # generated body .tex
│   │   └── online-appendix/
│   └── figure/
└── tests/              # auto-check vs manuscript .tex (tol=0.001)
```

## Setup (virtual environment)

One-time setup (from repo root):

```bash
bash code/refactor/setup.sh
```

Or manually:

```bash
python3 -m venv code/refactor/.venv
code/refactor/.venv/bin/pip install -r code/refactor/requirements.txt
```

Run commands from the repo root using the venv Python:

```bash
code/refactor/.venv/bin/python code/refactor/run.py --stage table1
```

Or activate the venv first:

```bash
source code/refactor/.venv/bin/activate
python code/refactor/run.py --stage all
```

## Data

Place raw files (not in git) under `data/raw/`:

- `accounting_data.csv`
- `gold_clauses.xlsx`

Intermediate `.dta` files live in `data/` (same as Mete's Stata `Data/` folder).

Build merged panel:

```bash
code/refactor/.venv/bin/python code/refactor/run.py --stage data --skip-raw   # use existing A0–A3
code/refactor/.venv/bin/python code/refactor/run.py --stage data              # full rebuild from raw
```

## Table 1 (implemented)

```bash
code/refactor/.venv/bin/python code/refactor/run.py --stage table1
code/refactor/.venv/bin/python code/refactor/tests/test_table1.py
```

Summary stats by `dind_orig` (original gold exposure indicator) split into $d=0$ vs $d>0$
within each period panel. Panel C pools all firm-years 1935–1940. Uses unequal-variance
$t$-tests (Stata `ttest, uneq`). Stata reference: `A7_differences.do` (manuscript adds N/SD).

Generate LaTeX table:

```bash
code/refactor/.venv/bin/python code/refactor/run.py --stage table1
```

Writes `code/refactor/output/tables/body/1_sum_stats_d.tex` (full `\begin{table}...\end{table}` environment).

See **`DISCREPANCIES.md`** for a running log of differences vs the published manuscript and Mete’s Stata output.

## Table 2 (implemented)

```bash
code/refactor/.venv/bin/python code/refactor/run.py --stage table2
code/refactor/.venv/bin/python code/refactor/tests/test_table2.py
```

Balanced panel of 157 firms with bonds in 1930 and investment data in 1935 (Stata `A6_bondstats.do`).
Merges firm-year panel with bond-level counts from `A1_bond_data_bondlevel.dta`.

| Stat | Definition |
|------|------------|
| N firms | Distinct permnos with `fd_amount > 0` in year |
| N firms (gold) | Firms with `d_year > 0` (`fd_amount_g1 / ll_bs_new`, capped at 1) |
| N bonds | Bond-level rows after merge (pre dedup) |
| Mean / Median $d$ | Over all firms in year (Stata `summarize d_year`; matches manuscript at 2 decimals) |
| $\rho$ | Corr(`d_year`, `d_1930`) across firms |

Writes `code/refactor/output/tables/body/2_bond_stats.tex`.

## Table 3 (implemented)

```bash
code/refactor/.venv/bin/python code/refactor/run.py --stage table3
code/refactor/.venv/bin/python code/refactor/tests/test_table3.py
```

Writes `code/refactor/output/tables/body/3_investment_reg.tex` (full `\begin{table}...\end{table}` environment).

Regression spec (all columns with exposure):

```
var_inv_rate ~ var_Q + exposure + exposure×year | permno + year
vcov: cluster permno × year
```

| Col | Manuscript label        | Sample / exposure        | Stata reference |
|-----|-------------------------|--------------------------|-----------------|
| 1   | Classic                 | `var_Q` only             | A9 m1           |
| 2   | Overhang                | baseline `d`             | A9 m2           |
| 3   | No maturity             | `ind_3134_max != 1`      | A9 m6           |
| 4   | No redemption           | exclude 1933–34 repayers | manuscript §5 (sample TBD) |
| 5   | With LT liabilities     | `ll_bs_new > 0`          | manuscript §5 (sample TBD) |
| 6   | Pref. shares placebo    | `ps` exposure            | A9 m4           |
| 7   | Bank debt placebo       | `bd` exposure            | A9 m5           |

## Table 4 (implemented — partial)

```bash
code/refactor/.venv/bin/python code/refactor/run.py --stage table4
code/refactor/.venv/bin/python code/refactor/tests/test_table4.py
```

Six overhang regressions (Stata `A10_otheroutcomes.do`) with dependent variables:
Payout (`var_payout`), Dividend (`cashrat`), Net rep. (`netrep`), Profits (`nippe`),
Cash (`cashppe`), Leverage (`var_booklev`).

**Validated:** cols 1 (Payout) and 6 (Leverage) — all 32 coefficient checks pass at tol 0.001.
Cols 2–5 have winsorization / sample gaps (see `DISCREPANCIES.md` D-010).

Writes `code/refactor/output/tables/body/4_other_outcomes.tex`.

## Table 5 (implemented — partial)

```bash
code/refactor/.venv/bin/python code/refactor/run.py --stage table5
code/refactor/.venv/bin/python code/refactor/tests/test_table5.py
```

Credit-rating heterogeneity regressions (Stata `A21_ratings_yearbyyear.do`, not `A11_ratings.do`).
Demean `d` among firms with positive exposure, then estimate year × `d̃` and triple
interactions with low rating (Ba or below in 1930).

**Validated:** col 1 (Net investment) — all 6 displayed coefficient checks pass at tol 0.001.
Col 2 (Dividend) has `cashrat` winsor gaps (see `DISCREPANCIES.md` D-011).

Writes `code/refactor/output/tables/body/5_credit_ratings.tex`.

## Table 6 (implemented)

```bash
code/refactor/.venv/bin/python code/refactor/run.py --stage table6
code/refactor/.venv/bin/python code/refactor/tests/test_table6.py
```

Robustness regressions with industry-year FE (col 1), linear 1930 firm controls
(col 2), and decile portfolio controls (cols 3–10). Stata `A12_controls.do`.

**Validated:** all 50 coefficient checks (5 terms × 10 columns) pass at tol 0.001.

Writes `code/refactor/output/tables/body/6_controls.tex`.

## Table 7 (implemented)

```bash
code/refactor/.venv/bin/python code/refactor/run.py --stage table7
code/refactor/.venv/bin/python code/refactor/tests/test_table7.py
```

Aggregated investment effects (Stata `A13_aggregation.do`, `A13_aggregationd1.do`).
Capital-weighted gold-clause effects use baseline Table 3 year × `d` coefficients.

**Validated:** all 15 percentage checks pass at tol 0.011 (2-decimal display).

Writes `code/refactor/output/tables/body/7_aggregate.tex`.

## Table map (remaining — stubs)

| Manuscript | Stata | Module |
|------------|-------|--------|
| `1_sum_stats_d.tex` | A7 (manuscript format) | `tables/body/t01_summary_stats.py` ✅ |
| `2_bond_stats.tex` | A6 | `tables/body/t02_bond_stats.py` ✅ |
| `4_other_outcomes.tex` | A10 | `tables/body/t04_other_outcomes.py` ✅ (partial) |
| `5_credit_ratings.tex` | A21 | `tables/body/t05_credit_ratings.py` ✅ (partial) |
| `6_controls.tex` | A12 | `tables/body/t06_controls.py` ✅ |
| `7_aggregate.tex` | A13 | `tables/body/t07_aggregate.py` ✅ |
| IA tables | A14–A21 | `tables/appendix/ia*.py` |

## Validation

Each table module compares key coefficients to the published manuscript
`.tex` in `manuscript/tables/` with tolerance `0.001` (see `config.COEF_TOLERANCE`).

Run all implemented tests:

```bash
code/refactor/.venv/bin/python code/refactor/tests/test_table1.py
code/refactor/.venv/bin/python code/refactor/tests/test_table2.py
code/refactor/.venv/bin/python code/refactor/tests/test_table3.py
code/refactor/.venv/bin/python code/refactor/tests/test_table4.py
code/refactor/.venv/bin/python code/refactor/tests/test_table5.py
code/refactor/.venv/bin/python code/refactor/tests/test_table6.py
code/refactor/.venv/bin/python code/refactor/tests/test_table7.py
```
