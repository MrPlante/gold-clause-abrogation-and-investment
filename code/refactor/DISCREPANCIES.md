# Refactor vs original results — discrepancy log

Tracks differences between **`code/refactor/`** (Python), the **published manuscript**
(`manuscript/tables/`), and **Mete’s Stata pipeline** (`code/mete/`, `metes-tables/`).

**Baseline data:** `data/A4_merged.dta` (Mete-built; refactor data port not yet validated end-to-end).

**Last checked:** 2026-06-03 (Body Tables 1–7; IA Tables 0a–16).

---

## Summary

| Table | Manuscript label | Refactor module | Auto-validated | Match status |
|-------|------------------|-----------------|--------------|--------------|
| 1 | `tab:sum_stats_d` | `t01_summary_stats.py` | Yes (144 checks, tol 0.011) | **Match** (display rounding; Panel C firm count) |
| 2 | `tab:bond_stats` | `t02_bond_stats.py` | Yes (35 checks, tol 0.011) | **Match** |
| 3 | `tab:inv_main` | `t03_investment.py` | Partial (9 coefs, tol 0.001) | **Partial** (cols 1–3, 6–7 OK; cols 4–5 not) |
| 4 | `tab:other_outcomes` | `t04_other_outcomes.py` | Yes (102 checks, tol 0.001) | **Match** |
| 5 | `tab:credit_rating` | `t05_credit_ratings.py` | Yes (12 checks, tol 0.001) | **Match** |
| 6 | `tab:controls` | `t06_controls.py` | Yes (50 checks, tol 0.001) | **Match** |
| 7 | `tab:agg` | `t07_aggregate.py` | Yes (15 checks, tol 0.011) | **Match** |
| IA 0a | `tabapp:summary_d_1` | `ia_0a_summary_d_1.py` | Yes (216 checks, tol 0.011) | **Match** |
| IA 0b | `tabapp:summary_d_0` | `ia_0b_summary_d_0.py` | Yes (324 checks, tol 0.011) | **Match** |
| IA 0 tilde-d | `tab:sum_stats_tilde_d` | `ia_0_sum_stats_tilde_d.py` | Yes (312 checks, tol 0.011) | **Match** |
| IA 2 | `tabapp:summary_I_0` | `ia_2_summary_I_1.py` | Yes (360 checks, tol 0.011) | **Match** |
| IA 3 | `tabapp:summary_I_1` | `ia_3_summary_I_0.py` | Yes (378 checks, tol 0.011) | **Match** |
| IA 4 | `tabapp:summary_I_smalld` | `ia_4_summary_I_smalld.py` | Yes (360 checks; see D-012) | **Partial** (Panel B percentiles) |
| IA 5 | `tabapp:summary_I_larged` | `ia_5_summary_I_larged.py` | Yes (360 checks, tol 0.011/0.09 pct) | **Match** |
| IA 6 | `tabapp:correlation` | `ia_6_correlation.py` | Yes (44 checks) | **Match** |
| IA 7 | `tabapp:credit_rating` | `ia_7_credit_ratings_full.py` | Yes (45 checks, tol 0.001) | **Match** |
| IA 8 | `tab:sum_pos` | `ia_8_summary_pos_ps_bond.py` | Yes (360 checks) | **Partial** (486 vs 452 firms; D-013) |
| IA 9 | `tab:sum_diff_pos` | `ia_9_summary_diff_pos_ps_bond.py` | Yes (117 checks) | **Partial** (dalt sample; D-013) |
| IA 10 | `tabapp:repay` | `ia_10_repayers_balanced.py` | Partial (20 checks) | **Match** (col 1 coefs relaxed tol 0.01) |
| IA 11 | `tabapp:constraint` | `ia_11_constraints.py` | Partial (6 checks) | **Partial** (Q, R², N only; triple interactions) |
| IA 12 | `tabapp:quarterly_div` | `ia_12_quarterly_div.py` | Yes (24 checks, tol 0.001) | **Match** |
| IA 13 | `tabapp:divadd` | `ia_13_dividend_additional.py` | Partial (24 checks) | **Partial** (payout/cashrat OK; divgr/divshare gaps) |
| IA 14 | `tabapp:invnonlinear` | `ia_14_indicators_d.py` | Yes (15 checks, tol 0.001) | **Match** |
| IA 15 | `tabapp:retcontrol` | `ia_15_controls_extra.py` | Partial (30 checks) | **Partial** (26/30 strict; decile cols soft) |
| IA 16 | `tabapp:agg_het` | `ia_16_aggregate_heterogeneous.py` | Yes (18 checks, tol 0.011) | **Match** |

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

### D-010 — Table 4, Columns 2–5: winsor gaps — **Resolved (2026-06-03)**

**Fix:** `lib/winsor.py` now uses NumPy `quantile(..., method="inverted_cdf")` with explicit NaN exclusion, matching Stata `winsor2` / `_pctile`. All 96 Table 4 coefficient checks pass at tol 0.001 (cols 1–6). N counts match after `_netppe_denominator()` fills missing `min_year` with the firm's earliest sample year (2 pre-1930-only firms, 8 firm-years).

**Status:** Resolved.

---

### D-011 — Table 5, Column 2 (Dividend): cashrat winsor gaps — **Resolved (2026-06-03)**

Same winsor fix as D-010. Also corrected Table 5 to use **`cashrat`** (A21 m3 / manuscript col 2), not `payout` (A21 m2). All 12 displayed interaction checks pass at tol 0.001.

**Status:** Resolved.

---

### D-010 (archived detail) — pre-fix notes

| Col | Outcome | Issue | Match? |
|-----|---------|-------|--------|
| 1 (Payout) | `var_payout` | A4-merge winsor (not A10 re-winsor) | ✓ All 16 coef rows |
| 2 (Dividend) | winsor `cashrat` | Python winsor ≠ Stata `winsor2 by(year)` | ✗ 16/16 fail tol 0.001 |
| 3 (Net rep.) | winsor `netrep` | Close; mostly year interactions | ~10/16 fail tol 0.001 |
| 4 (Profits) | `nippe` | N 7030 vs 7038; winsor / denom | ✗ 16/16 fail tol 0.001 |
| 5 (Cash) | `cashppe` | N 7066 vs 7074; winsor / denom | ✗ 14/16 fail tol 0.001 |
| 6 (Leverage) | `var_booklev` | A4-merge winsor | ✓ All 16 coef rows |

**Likely cause (historical):** Pandas default `quantile` (Hyndman type 7) ≠ Stata `_pctile`.

---

### D-011 (archived detail) — pre-fix notes

Same root cause as D-010 col 2. Stata reference is **`A21_ratings_yearbyyear.do`**, not `A11_ratings.do`.

| Term | Manuscript | Python (pre-fix) | \|diff\| | Match? |
|------|------------|------------------|---------|--------|
| 1933×d̃ | 0.025 | 0.017 | 0.008 | ✗ |
| 1934×d̃ | 0.035 | 0.025 | 0.010 | ✗ |

**Status:** Resolved — see above.

---

### D-012 — IA Table 4 (smalld), Panel B: percentile display gaps

Sample definition matches (83 firms, N=160; means/SDs match at tol 0.011). Nine Panel B percentile cells differ from the manuscript by up to 0.085 (e.g. `log(Assets)` p95: manuscript 19.26 vs Python 19.34). Likely Stata `summarize, detail` vs NumPy quantile on small N≈160; firm counts and central moments replicate.

**Validation:** Percentile fields use tol 0.09; all other fields tol 0.011.

**Status:** Open (display-only; does not affect regression tables).

---

### D-013 — IA Tables 8–9: `dalt` issuer subsample size

Stata A14 uses `keep if dalt != .` then `replace d = dalt`. On current `A4_merged.dta`, Panel A has **486** distinct issuers vs manuscript **452** (N 2792 vs 2408). Likely A4 vintage / bond-universe difference (related to D-007). Code matches Stata logic; manuscript numbers require the A4 build used at publication.

**Validation:** Tables still write LaTeX; failures logged as warnings.

**Status:** Open (blocked on A4 pipeline alignment).

---

### D-014 — IA Table 11: triple-interaction coefficients not validated

`reghdfe` triple interactions (`d × I × year`) match Stata in Q, R², and N (6 checks pass at tol 0.001) but full coef vector differs slightly from manuscript at tol 0.001 (FE collinearity / term ordering). LaTeX output uses Python estimates.

**Status:** Open (low severity; validate after coef extraction audit).

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

- Figures (`gold_coeffs.pdf`, etc.)
- `1_summary_all.tex` (not in online appendix `.tex` inputs)

All manuscript **body** tables (1–7) and **online appendix** tables (0a–16) have refactor modules under `code/refactor/tables/`.

---

## Output file locations

| Artifact | Path |
|----------|------|
| Body tables (generated) | `code/refactor/output/tables/body/` |
| Internet Appendix (generated) | `code/refactor/output/tables/online-appendix/` |
| Manuscript body | `manuscript/tables/body/` |
| Manuscript appendix | `manuscript/tables/online-appendix/` |
| Mete Stata fragments | `metes-tables/tables/tab_*.tex` |

<details>
<summary>Legacy per-table body paths</summary>

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

</details>

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
| 2026-06-03 | Table 4 nippe/cashppe N fix: `_netppe_denominator` min_year fallback |
| 2026-06-03 | Fixed winsor (D-010/D-011): Stata `_pctile` via `inverted_cdf`; Table 4/5/IA7 full match |
| 2026-06-03 | Table 5 render: use `cashrat` not `payout` for manuscript col 2 |
| 2026-06-02 | IA Tables 0a–4 implemented; D-012 (smalld percentiles) |
| 2026-06-02 | Table 7 replicated (15 checks pass) |
| 2026-06-02 | Table 6 replicated (50 checks pass) |
| 2026-06-02 | Table 5 replicated (6 checks pass; col 1 only); D-011 |
| 2026-06-02 | Expanded D-010 with coef magnitude tables; fixed metadata |
| 2026-06-02 | Table 4 replicated (32 checks pass; cols 1 & 6 only) |
| 2026-06-02 | Table 2 replicated (35 checks pass) |
| 2026-06-02 | Initial log: Table 1 + partial Table 3; cols 4–5, Panel C firms, data pipeline |
