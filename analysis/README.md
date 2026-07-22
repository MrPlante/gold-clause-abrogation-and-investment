# analysis/ — everything that produces the numbers in the paper

Replicates all manuscript tables and figures from `data/processed/A4_merged.dta` (built
by `pipeline/`; the original Stata pipeline is in git history at
`d54b0c3:code/legacy`) with Stata-matched econometrics (two-way clustered SEs,
same sample windows, winsorization). Generated tables and figures are written
DIRECTLY into `manuscript/tables/` and `manuscript/figures/`.

## Layout

```
analysis/
├── run.py              # CLI entry point (stages; see --help)
├── eventstudy/         # Table 1, Figs 3–5, IA.2/IA.3, Table IA.20 (research DB)
│   ├── pipeline.py     #   the production event-study pipeline
│   └── vw.py           #   exploratory value-weighted variant (root output/ only)
├── stata/              # production do-files (IA.19 exact SEs) + run_stata_do.sh
├── lib/                # shared infrastructure: regressions, vcov, latex, validation
├── tables/
│   ├── body/           # manuscript Tables 1–8 builders
│   ├── appendix/       # Internet Appendix table builders
│   ├── models/         # shared per-table computations (controls, aggregate, …)
│   └── render/         # LaTeX renderers for each table
├── figures/
│   └── source-data/    # versioned primary-source transcriptions (Figs 1-2, 7)
├── tests/              # auto-check vs manuscript .tex (tol=0.001)
└── compare/            # Stata vs Python regression diff (see compare/README.md)

(shared: ../config.py — paths; ../pipeline/ — data wrangling + io/sample/winsor
primitives; ../.venv — interpreter; non-manuscript artifacts -> ../output/)
```

## Event study (Table 1, Figures 3–5, IA.2, IA.3, Table IA.20)

```bash
python3 analysis/run.py --stage eventstudy
```

Builds the four daily portfolio return series (VW market, equal-weighted
d>0 / d=0, and d-weighted) from `gold_claude.crsp` on the research DB plus
`data/processed/A4_merged.dta`, and writes all event figures and tables directly into
`manuscript/`. **Not part of `--stage all`**: it needs a valid Kerberos
ticket for `researchdb.ssc.wisc.edu` (check with `klist`). The DB extract
itself is built by `sql/build_gold_claude_crsp.sql` (run instructions in the
file header). Uses only numpy/pandas/matplotlib + `psql`, so the system
`python3` works — no venv needed for this stage.

## IA.19 (industry-year robustness): known Stata dependency

Table IA.19's coefficients and standard errors come from
`stata/A12_controls_indyear.do` (run with
`stata-mp -b do analysis/stata/A12_controls_indyear.do` from the repo
root), which writes `output/tables/t6_indyear_robustness.csv`;
`--stage ia17` then renders that CSV to LaTeX. This is deliberate: the
portfolio-decile + industry×year specifications crash the in-process
Stata vcov bridge, and the pure-Python CGM standard errors are close but
not identical to `reghdfe`. The CSV is versioned, so `--stage ia17` (and
`--stage all`) work without Stata; rerun the do-file only if the underlying
data changes.

## Stata vs Python comparison

Run the same `reghdfe` specifications in Mete’s Stata `.do` files and in the Python refactor, then diff coefficients:

```bash
bash analysis/compare/run_compare.sh
```

Or:

```bash
.venv/bin/python analysis/run.py --stage compare
```

**Requirements:** Stata on the machine (`STATA_BIN`, default `/usr/local/stata/stata-mp`), `data/processed/A4_merged.dta`, and user packages `require`, `ftools`, `reghdfe`, `winsor2` (installed automatically on first run).

**Outputs:** `compare/output/stata_regressions.csv`, `python_regressions.csv`, `comparison_report.md`.

On a full run (Tables 3–5 subset): **221/221** matched coefficient cells agree within `1e-3`; standard errors match when Python uses Stata `reghdfe` vcov (`USE_STATA_VCOV=auto`). See `compare/README.md`. Stata batch logs go to `logs/stata/` (`analysis/stata/run_stata_do.sh`).

## Figures

```bash
.venv/bin/python analysis/run.py --stage figures
```

Writes PDFs under `manuscript/figures/body/` (parallel-trend plot from Table 3 col. 2; macro series from FRED). See `figures/README.md` for Hickman bond-issuance CSV and the static appendix scan.

## Setup (virtual environment)

One-time setup (from repo root):

```bash
bash setup.sh   # from the repo root
```

Or manually:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Run commands from the repo root using the venv Python:

```bash
.venv/bin/python analysis/run.py --stage table1
```

Or activate the venv first:

```bash
source .venv/bin/activate
python analysis/run.py --stage all
```

## Data

See `data/README.md` for the full layout and provenance of every file.
In short: source inputs live in `data/raw/` (including the not-yet-present
`accounting_data.csv` and `gold_clauses.xlsx`), the A0-A3 intermediates in
`data/intermediates/`, and the merged panel at `data/processed/A4_merged.dta`.

Build merged panel:

```bash
.venv/bin/python analysis/run.py --stage data --skip-raw   # use existing A0–A3
.venv/bin/python analysis/run.py --stage data              # full rebuild from raw
```

## Table 1 (implemented)

```bash
.venv/bin/python analysis/run.py --stage table1
.venv/bin/python analysis/tests/test_table1.py
```

Summary stats by `dind_orig` (original gold exposure indicator) split into $d=0$ vs $d>0$
within each period panel. Panel C pools all firm-years 1935–1940. Uses unequal-variance
$t$-tests (Stata `ttest, uneq`). Stata reference: `A7_differences.do` (manuscript adds N/SD).

Generate LaTeX table:

```bash
.venv/bin/python analysis/run.py --stage table1
```

Writes `(removed mirror) output/tables/body/1_sum_stats_d.tex` (full `\begin{table}...\end{table}` environment).

See **`DISCREPANCIES.md`** for a running log of differences vs the published manuscript and Mete’s Stata output.

## Table 2 (implemented)

```bash
.venv/bin/python analysis/run.py --stage table2
.venv/bin/python analysis/tests/test_table2.py
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

Writes `(removed mirror) output/tables/body/2_bond_stats.tex`.

## Table 3 (implemented)

```bash
.venv/bin/python analysis/run.py --stage table3
.venv/bin/python analysis/tests/test_table3.py
```

Writes `(removed mirror) output/tables/body/3_investment_reg.tex` (full `\begin{table}...\end{table}` environment).

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
.venv/bin/python analysis/run.py --stage table4
.venv/bin/python analysis/tests/test_table4.py
```

Six overhang regressions (Stata `A10_otheroutcomes.do`) with dependent variables:
Payout (`var_payout`), Dividend (`cashrat`), Net rep. (`netrep`), Profits (`nippe`),
Cash (`cashppe`), Leverage (`var_booklev`).

**Validated:** cols 1 (Payout) and 6 (Leverage) — all 32 coefficient checks pass at tol 0.001.
Cols 2–5 have winsorization / sample gaps (see `DISCREPANCIES.md` D-010).

Writes `(removed mirror) output/tables/body/4_other_outcomes.tex`.

## Table 5 (implemented — partial)

```bash
.venv/bin/python analysis/run.py --stage table5
.venv/bin/python analysis/tests/test_table5.py
```

Credit-rating heterogeneity regressions (Stata `A21_ratings_yearbyyear.do`, not `A11_ratings.do`).
Demean `d` among firms with positive exposure, then estimate year × `d̃` and triple
interactions with low rating (Ba or below in 1930).

**Validated:** col 1 (Net investment) — all 6 displayed coefficient checks pass at tol 0.001.
Col 2 (Dividend) has `cashrat` winsor gaps (see `DISCREPANCIES.md` D-011).

Writes `(removed mirror) output/tables/body/5_credit_ratings.tex`.

## Table 6 (implemented)

```bash
.venv/bin/python analysis/run.py --stage table6
.venv/bin/python analysis/tests/test_table6.py
```

Robustness regressions with industry-year FE (col 1), linear 1930 firm controls
(col 2), and decile portfolio controls (cols 3–10). Stata `A12_controls.do`.

**Validated:** all 50 coefficient checks (5 terms × 10 columns) pass at tol 0.001.

Writes `(removed mirror) output/tables/body/6_controls.tex`.

## Table 7 (implemented)

```bash
.venv/bin/python analysis/run.py --stage table7
.venv/bin/python analysis/tests/test_table7.py
```

Aggregated investment effects (Stata `A13_aggregation.do`, `A13_aggregationd1.do`).
Capital-weighted gold-clause effects use baseline Table 3 year × `d` coefficients.

**Validated:** all 15 percentage checks pass at tol 0.011 (2-decimal display).

Writes `(removed mirror) output/tables/body/7_aggregate.tex`.

## Internet Appendix (in progress)

Appendix tables mirror `manuscript/tables/online-appendix/` and write to
`(removed mirror) output/tables/online-appendix/`.

### Table 0a — Summary stats for $d>0$ firms (implemented)

```bash
.venv/bin/python analysis/run.py --stage ia0a
.venv/bin/python analysis/tests/test_ia_0a_summary_d_1.py
```

Stata reference: `A14_summary_stats_IA.do` (first block). Uses **`d_orig > 0`**
(contemporaneous exposure) to match the manuscript; Mete's export filters on
`d > 0` and includes extra $\tilde{d}$ rows.

**Validated:** 216 checks (Panels A & B), tol 0.011.

Writes `(removed mirror) output/tables/online-appendix/0a_summary_d_1.tex`.

### Table 0b — Summary stats for $d=0$ firms (implemented)

```bash
.venv/bin/python analysis/run.py --stage ia0b
.venv/bin/python analysis/tests/test_ia_0b_summary_d_0.py
```

Uses **`d_orig == 0`**, Panels A–C (Panel C omits $d$ rows).

**Validated:** 324 checks, tol 0.011.

Writes `(removed mirror) output/tables/online-appendix/0b_summary_d_0.tex`.

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
.venv/bin/python analysis/tests/test_table1.py
.venv/bin/python analysis/tests/test_table2.py
.venv/bin/python analysis/tests/test_table3.py
.venv/bin/python analysis/tests/test_table4.py
.venv/bin/python analysis/tests/test_table5.py
.venv/bin/python analysis/tests/test_table6.py
.venv/bin/python analysis/tests/test_table7.py
```
