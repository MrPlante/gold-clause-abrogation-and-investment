# Python refactor of Mete's Stata pipeline

Replicates all manuscript tables from `code/mete/` with Stata-matched econometrics
(two-way clustered SEs, same sample windows, winsorization).

## Layout

```
code/refactor/
├── config.py           # paths, constants
├── run.py              # CLI entry point
├── data/               # A0–A4 data build (Stata A0_accounting … A4_merge)
├── lib/                # regressions, winsorization, LaTeX, validation
├── tables/
│   ├── body/           # manuscript Tables 1–7
│   └── appendix/       # Internet Appendix tables
└── tests/              # auto-check vs manuscript .tex (tol=0.001)
```

## Requirements

```bash
pip install -r code/refactor/requirements.txt
```

## Data

Place raw files (not in git) under `data/raw/`:

- `accounting_data.csv`
- `gold_clauses.xlsx`

Intermediate `.dta` files live in `data/` (same as Mete's Stata `Data/` folder).

Build merged panel:

```bash
python code/refactor/run.py --stage data --skip-raw   # use existing A0–A3
python code/refactor/run.py --stage data              # full rebuild from raw
```

## Table 3 (implemented)

```bash
python code/refactor/run.py --stage table3
python code/refactor/tests/test_table3.py
```

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

## Table map (remaining — stubs)

| Manuscript | Stata | Module |
|------------|-------|--------|
| `1_sum_stats_d.tex` | A5 | `tables/body/t01_summary_stats.py` |
| `2_bond_stats.tex` | A6 | `tables/body/t02_bond_stats.py` |
| `4_other_outcomes.tex` | A10 | `tables/body/t04_other_outcomes.py` |
| `5_credit_ratings.tex` | A11 | `tables/body/t05_credit_ratings.py` |
| `6_controls.tex` | A12 | `tables/body/t06_controls.py` |
| `7_aggregate.tex` | A13 | `tables/body/t07_aggregate.py` |
| IA tables | A14–A21 | `tables/appendix/ia*.py` |

## Validation

Each table module compares key coefficients to the published manuscript
`.tex` in `manuscript/tables/` with tolerance `0.001` (see `config.COEF_TOLERANCE`).
