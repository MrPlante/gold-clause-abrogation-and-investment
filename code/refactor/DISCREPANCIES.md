# Refactor vs original results — discrepancy log

Tracks differences between **`code/refactor/`** (Python), the **published manuscript**
(`manuscript/tables/`), and **Mete’s Stata pipeline** (`code/mete/`, `metes-tables/`).

**Baseline data:** `data/A4_merged.dta` (Mete-built; refactor data port not yet validated end-to-end).

**Last checked:** 2026-06-02 (Tables 1–7 implemented; Tables 3–5 partial).

---

## Summary

| Table | Manuscript label | Refactor module | Auto-validated | Match status |
|-------|------------------|-----------------|--------------|--------------|
| 1 | `tab:sum_stats_d` | `t01_summary_stats.py` | Yes (144 checks, tol 0.011) | **Match** (display rounding; Panel C firm count) |
| 2 | `tab:bond_stats` | `t02_bond_stats.py` | Yes (35 checks, tol 0.011) | **Match** |
| 3 | `tab:inv_main` | `t03_investment.py` | Partial (9 coefs, tol 0.001) | **Partial** (cols 1–3, 6–7 OK; cols 4–5 not) |
| 4 | `tab:other_outcomes` | `t04_other_outcomes.py` | Partial (32 checks, tol 0.001) | **Partial** (cols 1 & 6 OK; cols 2–5 gaps) |
| 5 | `tab:credit_rating` | `t05_credit_ratings.py` | Partial (6 checks, tol 0.001) | **Partial** (col 1 OK; col 2 dividend gaps) |
| 6 | `tab:controls` | `t06_controls.py` | Yes (50 checks, tol 0.001) | **Match** |
| 7 | `tab:agg` | `t07_aggregate.py` | Yes (15 checks, tol 0.011) | **Match** |
| IA tables | `tabapp:*` | — | No | **Not implemented** |

---

## Validation tolerances

| Check type | Tolerance | Notes |
|------------|-----------|--------|
| Regression coefficients (Tables 3–6) | 0.001 | vs manuscript `.tex`; Table 4 validates cols 1 & 6 only (32 checks); Table 5 validates col 1 only (6 checks); Table 6 validates all 50 checks |
| Summary stats (Table 1) | 0.011 | Manuscript rounds to 2 decimals; stricter tol fails on all panels |
| Bond stats (Table 2) | 0.011 | Manuscript rounds to 2 decimals |
| LaTeX Δ Mean (Table 1) | Display | Rendered as `round(mean1,2) − round(mean0,2)` to match printed columns |
| Aggregate percentages (Table 7) | 0.011 | Manuscript rounds to 2 decimals |

---

## Open discrepancies

### D-001 — Table 3, Column 4 (No redemption): wrong sample definition

| | Manuscript | Refactor (current) |
|---|------------|-------------------|
| **Rule** | Exclude **firms** that **repurchased bond issues** in 1933 or 1934 | Exclude firms with any drop in **aggregate gold debt** (`fd_amount_g1`) vs prior year |
| **N** | 5,572 | 5,178 |
| **Q** | 0.085 | 0.083 |
| **1933 × d̃** | −0.068 | −0.105 |
| **1934 × d̃** | −0.032 | −0.035 |

**Severity:** High (coefficients and N off).

**Likely cause:** Repurchaser flag should be built from **bond-level** Moody's data (`A1_bond_data_bondlevel.dta` — specific issues retired), not firm-level gold-debt totals. Exact Stata code for the manuscript table is **not in the repo** (`A9_inv_results.do` exports a different 6-column table).

**Status:** Open.

**Next step:** Recover Mete’s col-4 sample code or reverse-engineer bond-issue repurchase indicator to hit N = 5,572.

---

### D-002 — Table 3, Column 5 (Positive LTL): wrong sample definition

| | Manuscript / R6 response | Refactor (current) |
|---|--------------------------|-------------------|
| **Rule** | Restrict to firms with **positive long-term liabilities in 1930**; keep **all years** for those firms | Firm-**year** filter `ll_bs_new > 0` |
| **N** | 6,048 | 5,207 |
| **Q** | 0.123 | 0.138 |

**Severity:** High.

**Likely cause:** Firm-level 1930 LTL filter vs observation-level filter. Even with the firm-level rule on current `A4_merged.dta`, N ≈ 5,098–5,360 — still below 6,048 → possible **data version** difference vs manuscript run.

**Status:** Open.

**Next step:** Confirm 1930 vs `min_year` rule with Mete; rebuild `A4_merged.dta` via `code/refactor/data/` and re-check N.

---

### D-003 — Table 1, Panel C: firm count in header

| | Manuscript | Refactor |
|---|------------|----------|
| **Firms (header)** | 594 | 503 |
| **N (all rows)** | 2,867 | 2,867 ✓ |
| **Means / SDs** | (e.g. inv 0.01, Q 1.25) | Match at 2-decimal display ✓ |

**Severity:** Low (statistics match; header count only).

**Likely cause:** Manuscript used a slightly different merge or firm-universe when finalizing the paper; observation-level panel is identical.

**Status:** Open (documented in generated `output/tables/body/1_sum_stats_d.tex`).

---

### D-004 — Table 1: raw vs printed values (rounding)

All 144 automated checks pass at **tol = 0.011**; **106 fail** at tol = 0.001 because the manuscript stores **2-decimal rounded** values.

**Examples (Panel A, full precision vs manuscript):**

| Field | Manuscript | Refactor (raw) |
|-------|------------|----------------|
| Net investment Δ mean | 0.02 | 0.012 |
| Net investment mean (d>0) | 0.05 | 0.046 |
| Tobin's Q mean (d=0) | 1.33 | 1.332 |

**Severity:** None for replication (display-only).

**Status:** Accepted — LaTeX output rounds means/SDs to 2 decimals; Δ uses difference of rounded means.

---

### D-005 — Table 1: split variable vs Mete `A7_differences.do`

| | Manuscript / refactor | Mete `A7` (`tab_d_groups.tex`) |
|---|----------------------|--------------------------------|
| **Split** | `dind_orig` (`d_orig > 0`) | `dind` (`d > 0`) |
| **Panel A firms** | 415 / 338 | 410 / 330 |
| **Panel A inv p-val** | 0.25 | 0.19 |

**Severity:** None for manuscript replication (refactor follows manuscript).

**Status:** Closed (intentional; manuscript ≠ raw Mete export).

---

### D-006 — Table 3: manuscript vs Mete `A9` column layout

| Manuscript Table 3 (7 cols) | Mete `tab_reghdfe_main.tex` (6 cols) |
|----------------------------|--------------------------------------|
| Classic, Overhang, No maturity, No redemption, Positive LTL, PS placebo, BD placebo | Classic, Overhang, dalt, ps, bd, no ind_3134 |

**Severity:** Informational.

**Status:** Closed — refactor targets **manuscript**, not Mete Overleaf fragment.

---

### D-007 — Data pipeline (A0–A4): not validated end-to-end

| Item | Status |
|------|--------|
| Python ports `a0_accounting.py` … `a4_merge.py` | Written, not run against raw CSV/XLSX |
| Raw inputs in repo | Missing (`data/raw/accounting_data.csv`, `gold_clauses.xlsx`) |
| Rebuilt `A4_merged.dta` vs reference | Not compared |

**Severity:** Medium (all tables currently depend on Mete’s existing `.dta`).

**Status:** Open.

---

### D-008 — pyfixest warnings during regression estimation

Singleton fixed effects dropped; occasional `RuntimeWarning` on `sqrt` of vcov diagonal (Tables 3–4). Table 3 LaTeX uses eigenvalue-clamped vcov when SEs are NaN (1933–1935 interactions).

**Severity:** Low (validated columns still match manuscript).

**Status:** Monitor.

---

### D-010 — Table 4, Columns 2–5: outcome construction / winsor gaps

| Col | Outcome | Issue | Match? |
|-----|---------|-------|--------|
| 1 (Payout) | `var_payout` | A4-merge winsor (not A10 re-winsor) | ✓ All 16 coef rows |
| 2 (Dividend) | winsor `cashrat` | Python winsor ≠ Stata `winsor2 by(year)` | ✗ 16/16 fail tol 0.001 |
| 3 (Net rep.) | winsor `netrep` | Close; mostly year interactions | ~10/16 fail tol 0.001 |
| 4 (Profits) | `nippe` | N 7030 vs 7038; winsor / denom | ✗ 16/16 fail tol 0.001 |
| 5 (Cash) | `cashppe` | N 7066 vs 7074; winsor / denom | ✗ 14/16 fail tol 0.001 |
| 6 (Leverage) | `var_booklev` | A4-merge winsor | ✓ All 16 coef rows |

**Magnitude (max \|diff\| across 16 coef rows, Python − manuscript):**

| Col | Max \|diff\| | Mean \|diff\| | Notes |
|-----|-------------|-------------|-------|
| 2 Dividend | 0.012 | 0.009 | Litigation interactions ~25–30% smaller |
| 3 Net rep. | 0.008 | 0.002 | Headline Q, d, 1933×d within 0.001 |
| 4 Profits | 0.040 | 0.009 | Worst: 1927×d (+0.040); Q off 0.017 |
| 5 Cash | 0.064 | 0.011 | Worst: 1929×d (+0.064); main d near zero |

**Headline coefficients (litigation period):**

| Col | Term | Manuscript | Python | \|diff\| |
|-----|------|------------|--------|---------|
| 2 | 1933×d | 0.028 | 0.020 | 0.008 |
| 2 | 1934×d | 0.036 | 0.027 | 0.009 |
| 3 | 1933×d | 0.017 | 0.016 | 0.001 |
| 3 | 1934×d | 0.006 | 0.002 | 0.004 |
| 4 | 1933×d | 0.012 | 0.003 | 0.009 |
| 4 | 1934×d | 0.011 | 0.004 | 0.007 |
| 5 | 1933×d | 0.047 | 0.060 | 0.013 |
| 5 | 1934×d | 0.035 | 0.050 | 0.015 |

Col 1 (Payout) matches exactly — including 1933×d = 0.038, 1934×d = 0.054 (the main debt-overhang payout result).

**Severity:** Medium (cols 1 & 6 replicate exactly; col 3 close; cols 2/4/5 are robustness).

**Likely cause:** Col 1 uses merge-time `var_payout`; cols 2–3 need Stata-exact `winsor2 by(year)` on raw `cashrat`/`netrep`. Cols 4–5 use `nippe`/`cashppe` with `netppe_bs` denominator — 8 obs dropped (missing denom) and winsor mismatch.

**Status:** Open.

**Next step:** Match Stata winsor2 algorithm; confirm nippe N=7038 handling for missing `ni_is` / `denom`.

---

### D-011 — Table 5, Column 2 (Dividend): cashrat winsor gaps

Same root cause as D-010 col 2. Stata reference is **`A21_ratings_yearbyyear.do`**, not `A11_ratings.do` (A11 uses bucketed year interactions and includes `rating_ind` as a regressor).

| Term | Manuscript | Python | \|diff\| | Match? |
|------|------------|--------|---------|--------|
| 1933×d̃ | 0.025 | 0.017 | 0.008 | ✗ |
| 1934×d̃ | 0.035 | 0.025 | 0.010 | ✗ |
| 1933×Low rating | 0.013 | 0.012 | 0.001 | ✓ |
| 1934×Low rating | 0.011 | 0.009 | 0.002 | ✗ |
| 1933×d̃×Low | −0.025 | −0.016 | 0.009 | ✗ |
| 1934×d̃×Low | −0.037 | −0.026 | 0.011 | ✗ |

Col 1 (Net investment): all 6 displayed terms match at tol 0.001. R² = 0.244, N = 7,074.

**Severity:** Medium (col 1 replicates; col 2 is secondary outcome).

**Status:** Open (blocked on D-010 winsor fix).

---

## Resolved / accepted

| ID | Item | Resolution |
|----|------|------------|
| D-004 | Table 1 rounding | Accepted; 2-decimal display policy |
| D-005 | Table 1 uses `dind_orig` | Discovered and implemented; matches manuscript |
| D-006 | Table 3 follows manuscript not A9 | By design |
| D-009 | Table 2 vs Mete `tab_bonds_1930_1935.tex` | Manuscript uses gold bond counts (1930–1934); Mete export uses % gold bonds and includes 1935 — refactor targets manuscript |

---

## Not yet replicated (no discrepancies logged)

- Table 2 (`2_bond_stats.tex`) — Stata `A6_bondstats.do` ✅
- Table 4 (`4_other_outcomes.tex`) — `A10_otheroutcomes.do` ✅ (partial: cols 1 & 6)
- Table 5 (`5_credit_ratings.tex`) — `A21_ratings_yearbyyear.do` ✅ (partial: col 1)
- Table 6 (`6_controls.tex`) — `A12_controls.do` ✅
- Table 7 (`7_aggregate.tex`) — `A13_aggregation.do` / `A13_aggregationd1.do` ✅
- Internet Appendix tables — `A14`–`A21`
- Figures (`gold_coeffs.pdf`, etc.)
- Seb quarterly dividend table — still in `code/seb/quarterly-div.py`

---

## Output file locations

| Artifact | Path |
|----------|------|
| Table 1 LaTeX (generated) | `code/refactor/output/tables/body/1_sum_stats_d.tex` |
| Table 1 LaTeX (manuscript) | `manuscript/tables/body/1_sum_stats_d.tex` |
| Table 2 LaTeX (generated) | `code/refactor/output/tables/body/2_bond_stats.tex` |
| Table 2 LaTeX (manuscript) | `manuscript/tables/body/2_bond_stats.tex` |
| Table 3 LaTeX (generated) | `code/refactor/output/tables/body/3_investment_reg.tex` |
| Table 3 LaTeX (manuscript) | `manuscript/tables/body/3_investment_reg.tex` |
| Table 4 LaTeX (generated) | `code/refactor/output/tables/body/4_other_outcomes.tex` |
| Table 4 LaTeX (manuscript) | `manuscript/tables/body/4_other_outcomes.tex` |
| Table 5 LaTeX (generated) | `code/refactor/output/tables/body/5_credit_ratings.tex` |
| Table 5 LaTeX (manuscript) | `manuscript/tables/body/5_credit_ratings.tex` |
| Table 6 LaTeX (generated) | `code/refactor/output/tables/body/6_controls.tex` |
| Table 6 LaTeX (manuscript) | `manuscript/tables/body/6_controls.tex` |
| Table 7 LaTeX (generated) | `code/refactor/output/tables/body/7_aggregate.tex` |
| Table 7 LaTeX (manuscript) | `manuscript/tables/body/7_aggregate.tex` |
| Mete Stata fragments | `metes-tables/tables/tab_*.tex` |

---

## How to update this log

1. Run validations:
   ```bash
   code/refactor/.venv/bin/python code/refactor/run.py --stage table1
   code/refactor/.venv/bin/python code/refactor/run.py --stage table2
   code/refactor/.venv/bin/python code/refactor/run.py --stage table3
   code/refactor/.venv/bin/python code/refactor/run.py --stage table4
   code/refactor/.venv/bin/python code/refactor/run.py --stage table5
   code/refactor/.venv/bin/python code/refactor/run.py --stage table6
   code/refactor/.venv/bin/python code/refactor/run.py --stage table7
   code/refactor/.venv/bin/python code/refactor/tests/test_table1.py
   code/refactor/.venv/bin/python code/refactor/tests/test_table2.py
   code/refactor/.venv/bin/python code/refactor/tests/test_table3.py
   code/refactor/.venv/bin/python code/refactor/tests/test_table4.py
   code/refactor/.venv/bin/python code/refactor/tests/test_table5.py
   code/refactor/.venv/bin/python code/refactor/tests/test_table6.py
   code/refactor/.venv/bin/python code/refactor/tests/test_table7.py
   ```
2. For new tables, add a row to the summary table and open/close discrepancy entries.
3. When a discrepancy is fixed, move it to **Resolved** with date and commit hash.

---

## Change history

| Date | Change |
|------|--------|
| 2026-06-02 | Table 7 replicated (15 checks pass) |
| 2026-06-02 | Table 6 replicated (50 checks pass) |
| 2026-06-02 | Table 5 replicated (6 checks pass; col 1 only); D-011 |
| 2026-06-02 | Expanded D-010 with coef magnitude tables; fixed metadata |
| 2026-06-02 | Table 4 replicated (32 checks pass; cols 1 & 6 only) |
| 2026-06-02 | Table 2 replicated (35 checks pass) |
| 2026-06-02 | Initial log: Table 1 + partial Table 3; cols 4–5, Panel C firms, data pipeline |
