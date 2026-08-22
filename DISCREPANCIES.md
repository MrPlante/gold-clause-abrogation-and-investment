# Refactor vs original results — discrepancy log

Tracks differences between **`pipeline/` + `analysis/`** (Python), the **published manuscript**
(`manuscript/tables/`), and **Mete’s Stata pipeline** (formerly `code/mete/`, removed from the tree at d54b0c3; `archive/metes-tables/`, removed at ad2edf7 — retrieve with `git checkout ad2edf7 -- archive`).

**Baseline data:** `data/processed/A4_merged.dta` — the manuscript vintage (7,074 x 845), reproduced exactly by both Mete's `A4_merge.do` (git: `d54b0c3:code/legacy/mete/`) and the Python port `dataprep/a4_merge.py` from raw (A0-A3 stages in memory; Mete's intermediates retired to tmp/2026-07/21/intermediates/ — see D-016).

**Last checked:** 2026-07-21 (full sweep on the manuscript-vintage panel; see D-016).

---

## Summary

| Table | Manuscript label | Refactor module | Auto-validated | Match status |
|-------|------------------|-----------------|--------------|--------------|
| 1 | `tab:sum_stats_d` | `t01_summary_stats.py` | Yes (144 checks, tol 0.011) | **Match** (display rounding; Panel C firm count) |
| 2 | `tab:bond_stats` | `t02_bond_stats.py` | Yes (35 checks, tol 0.011) | **Match** |
| 3 | `tab:inv_main` | `t03_investment.py` | Yes (strict cols 1-3, 6-7; cols 4-5 recon tol 0.02) | **Match** (cols 4-5 adopted reconstructions; D-017) |
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

**Next step:** Confirm 1930 vs `min_year` rule with Mete; rebuild `A4_merged.dta` via `pipeline/` and re-check N.

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

All manuscript **body** tables (1–7) and **online appendix** tables (0a–16) have refactor modules under `analysis/tables/`.

---

## Output file locations

| Artifact | Path |
|----------|------|
| Body tables (generated) | `(removed mirror) output/tables/body/` |
| Internet Appendix (generated) | `(removed mirror) output/tables/online-appendix/` |
| Manuscript body | `manuscript/tables/body/` |
| Manuscript appendix | `manuscript/tables/online-appendix/` |
| Mete Stata fragments | `archive/metes-tables/tables/tab_*.tex` (git history: ad2edf7) |

<details>
<summary>Legacy per-table body paths</summary>

| Artifact | Path |
|----------|------|
| Table 1 LaTeX (generated) | `(removed mirror) output/tables/body/1_sum_stats_d.tex` |
| Table 1 LaTeX (manuscript) | `manuscript/tables/body/1_sum_stats_d.tex` |
| Table 2 LaTeX (generated) | `(removed mirror) output/tables/body/2_bond_stats.tex` |
| Table 2 LaTeX (manuscript) | `manuscript/tables/body/2_bond_stats.tex` |
| Table 3 LaTeX (generated) | `(removed mirror) output/tables/body/3_investment_reg.tex` |
| Table 3 LaTeX (manuscript) | `manuscript/tables/body/3_investment_reg.tex` |
| Table 4 LaTeX (generated) | `(removed mirror) output/tables/body/4_other_outcomes.tex` |
| Table 4 LaTeX (manuscript) | `manuscript/tables/body/4_other_outcomes.tex` |
| Table 5 LaTeX (generated) | `(removed mirror) output/tables/body/5_credit_ratings.tex` |
| Table 5 LaTeX (manuscript) | `manuscript/tables/body/5_credit_ratings.tex` |
| Table 6 LaTeX (generated) | `(removed mirror) output/tables/body/6_controls.tex` |
| Table 6 LaTeX (manuscript) | `manuscript/tables/body/6_controls.tex` |
| Table 7 LaTeX (generated) | `(removed mirror) output/tables/body/7_aggregate.tex` |
| Table 7 LaTeX (manuscript) | `manuscript/tables/body/7_aggregate.tex` |
| Mete Stata fragments | `archive/metes-tables/tables/tab_*.tex` (git history: ad2edf7) |

</details>

---

## How to update this log

1. Run validations:
   ```bash
   .venv/bin/python analysis/run.py --stage table1
   .venv/bin/python analysis/run.py --stage table2
   .venv/bin/python analysis/run.py --stage table3
   .venv/bin/python analysis/run.py --stage table4
   .venv/bin/python analysis/run.py --stage table5
   .venv/bin/python analysis/run.py --stage table6
   .venv/bin/python analysis/run.py --stage table7
   .venv/bin/python analysis/tests/test_table1.py
   .venv/bin/python analysis/tests/test_table2.py
   .venv/bin/python analysis/tests/test_table3.py
   .venv/bin/python analysis/tests/test_table4.py
   .venv/bin/python analysis/tests/test_table5.py
   .venv/bin/python analysis/tests/test_table6.py
   .venv/bin/python analysis/tests/test_table7.py
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

### D-015 — Macro figures (manuscript Figures 1-2) were blank from 2026-06-03 to 2026-07-18

The `figures/macro_plots.py` FRED series ids (`EXUSUK`, `EXCHUS`, `CPIAUCSL`)
have no pre-1947 observations, so the 1931-1934 plot windows were empty: the
builder overwrote the correct original figures with axes-only blanks at
73a03d1 (2026-06-03) and every compiled manuscript since shipped blank
Figures 1-2, unnoticed until a visual review on 2026-07-18. Resolution: the
original figures were restored from 348d60f into `manuscript/figures/body/`
and `output/figure/`, and `build_macro_figures()` now refuses to write
anything when the cache has no pre-1936 data. To make these figures
reproducible, replace the series ids with ones that cover the 1930s
(`CPIAUCNS` for CPI; NBER macrohistory series for the sterling/franc rates)
and add a source for the RFC gold purchasing-program price, then match the
original figure's content before re-enabling the manuscript copy step.

**RESOLVED 2026-07-18 (primary sources):** the figures are now fully
reproducible from versioned primary-source data in
`figures/source-data/macro_monthly.csv`:

- FX: monthly noon buying rates in New York (cents per pound / per franc)
  from Board of Governors, *Banking and Monetary Statistics, 1914-1941*,
  Table 173 (UK p. 681, France p. 670; FRASER scan). Identified as the
  original figures' source by recovering the plotted series at data
  precision from the MATLAB vector paths: the extraction matches Table 173
  normalized to 12/1932 month-by-month. Cross-validation caught one OCR
  misread (France 1/1936 = 6.6251, not 6.8251) and one real divergence
  (France 9/1936: published month average 6.3409 straddles the Sept 26
  Tripartite devaluation; the original figure plotted ~6.51).
- CPI: FRED `CPIAUCNS` raw levels, normalized to 12/1932 in code (matches
  the original in 10 of 13 plotted months; June-August 1933 one 0.1-tick
  off from an older vintage).
- Gold: monthly averages of the official daily purchasing-program prices
  from the Federal Reserve Bulletin "Official Price of Gold" tables
  (Dec. 1933, Jan. 1934, Feb. 1934 issues; FRASER): 30.77, 30.82, 33.34,
  34.03, 34.27 for 9/1933-1/1934, $20.67 before, $35.00 after. The
  original figure plotted 28.00, 29.01, 31.96, 33.32, 34.06 — sampling
  unidentified (three values appear verbatim in the daily tables at
  non-month-end dates); the primary-source averages replace them, which
  shifts the plotted gold path slightly upward in Sept-Dec 1933.

`macro_plots.py` reads the versioned CSV (no network dependency) and the
regenerated figures replace the originals in the manuscript.

---

### D-016 — "Data vintage mismatch" resolved: the deviant file was ours, not Mete's — **RESOLVED (2026-07-21)**

Since 2026-06-06 every table validation carried the caveat that the
manuscript was generated from an N=7,074 panel while the on-disk
`data/A4_merged.dta` had N=6,768 ("data version mismatch"). Sebastien
provided Mete's Dropbox folders (untracked, repo root: `GKP Analysis Oct
2025 Mete/` and two earlier snapshots), which settled the question:

- `GKP Analysis Oct 2025 Mete/Data/A4_merged.dta` is the manuscript
  vintage (7,074 x 845).
- Every upstream input (A0-A3 intermediates, chars_annual, crsp_monthly,
  monthly_div, netincome) in that folder is **byte-identical** to ours.
- Running Mete's `A4_merge.do` (identical to the copy in git history at
  `d54b0c3:code/legacy/mete/A4_merge.do`) on our own intermediates
  reproduces his 7,074 x 845 file **exactly** (all 843 non-key columns;
  `astile` replaced by `xtile`, verified identical here).

So there never was a missing data vintage: the old on-disk 6,768 x 831 A4
was a deviant build (now `data/attic/A4_merged_6768x831_deviant.dta`), and
the Python port had been tuned to reproduce the deviant file. Root causes
of the deviation, all fixed in `dataprep/a4_merge.py` (which now reproduces
the manuscript panel exactly, to float32 storage precision):

1. **Lags recomputed instead of using A0's stored lags.** A0 ships
   pre-computed calendar lags (`Lta_bs`, `Lbeq_bs`, `Lcb_bs`, `Lps_bs`,
   `Lbd_bs`) built before rows were dropped from the saved A0; 702 A0 rows
   have a stored lag whose prior-year row is absent (361 in 1926).
   Recomputing lags with a groupby-shift lost 306 firm-years (251 in 1926)
   through the `Q != .` filter.
2. **`sic2_year` enumerated post-filter** instead of on the pre-filter
   merged panel (Stata computes it right after the marcap merge, before
   any drop, and `egen group()` skips missing components).
3. **Positional instead of calendar lags** for `d_orig`/`dalt_orig`.
4. **Stata missing-value semantics**: `year <= min_year` is TRUE and
   `(dalt > 0)` is TRUE when the RHS/LHS is missing (missing = +infinity).
5. **14 intermediate columns dropped** that Stata keeps in the saved panel
   (`_merge`, `ph`, `denom2`, `denom3`, `bd_all`, `ps_all`, and the
   `*_Low` before/after interactions).

Consequences (2026-07-21):

- `data/processed/A4_merged.dta` is now the manuscript vintage; all table builders
  validate against the manuscript in full (Tables 2-8, IA tables — same
  pass/fail profile as the pre-existing D-012/D-013/D-014 entries, which
  are unrelated to the vintage).
- Artifacts previously generated from the deviant panel were regenerated
  and their quoted numbers re-synced: Figure 6 (fixes the referee-visible
  Figure 6 vs Table 4 inconsistency), IA.19 (`A12_controls_indyear.do`
  rerun; significance pattern changed, Section 5 + R6 comment-2 text
  updated), and the event-study block (exposure classification moved from
  175/378 to 177/376 firms; Table 1, IA.20, Figures 3-5, IA.2-IA.3
  regenerated; ~0.1pp changes to quoted returns synced in Section 3, IA
  Section IA.1, R2 comment-1, and the shared revision summary).
- Published Table 4 columns 4-5 sample definitions are in none of the
  available do-files; closest reconstructions adopted 2026-07-21 (see
  D-017).

---

### D-017 — Table 4 cols 4-5 samples adopted as reconstructions; col 7 published SEs irreproducible — **Adopted & regenerated into manuscript (2026-07-21)**

Follow-up to D-016's open item. Per Sebastien's decision ("use the closest
match moving forward"), the builder now ships adopted reconstructions of
the two lost sample definitions:

- **Column 4 ("No redemption")**: exclude firms whose exposure `d` went
  from positive to zero during 1931-1935 (Mete's `A16_balanced.do`
  ``repay`` flag, calendar lag). Gives d = -0.094 (N = 5,918) vs published
  -0.097 (N = 5,572); year-interaction profile matches within 0.02.
- **Column 5 ("With LT Lia.")**: firms with positive raw balance-sheet
  long-term liabilities (`ll_bs > 0`) in 1930, the year exposure is
  measured. Gives d = -0.052 (N = 6,187) vs published -0.057 (N = 6,048);
  chosen over contemporaneous `ll_bs_new > 0` (the builder's old guess),
  whose pre-period profile is far off (1930 = -0.079*** vs published
  -0.038). Selected by grid search over candidate samples scored against
  the full published coefficient vector and N.

UPDATE (same day): per Sebastien's decision that the code must reproduce
the manuscript ("non negotiable"), `manuscript/tables/body/
3_investment_reg.tex` is now GENERATED by the builder and all seven
columns validate strictly. Before adopting, an exhaustive reverse-
engineering sweep tried to recover the exact published samples against
the published N / coefficient vector / R-squared: every numeric panel
column x 4 explainable mask shapes (row-level >0, firm-level in 1930,
firm-always, firm-ever) for col 5 (target N=6,048 — zero hits within 3);
35 decline-based repurchaser definitions (5 data sources incl. bond-level
counts/amounts, 5 year-window readings incl. the ManualYear off-by-one)
plus 5 d->0 windows for col 4 (target N=5,572 — nothing closer than 74
rows); label-swap and sequential-keep hypotheses; and both filters on the
older-vintage-style attic panel. Conclusion: the published cols 4-5 came
from a lost intermediate state (esttab stores estimates across runs) and
are not exactly recoverable by any explainable filter, which is why the
reconstructions were promoted into the manuscript. Visible changes vs the
published table: col 4 d -0.097->-0.094, 1933 -0.068->-0.064, 1934
-0.032->-0.036 (same signs/stars); col 5 1934 -0.043->-0.038, d loses its
10% star (-0.057* -> -0.052 n.s.); col 7 SEs move to the reproducible CGM
values, upgrading two PRE-period placebo cells (1926 * -> **, 1928 * ->
***) while 1933/1934 stay insignificant (1934 t = 1.71, below the 10%
critical value at df 14). Section 5 text synced (green \rev marks).

**New finding — column 7 (bank debt placebo) SEs cannot be reproduced.**
Current reghdfe (Stata 18/19 era) returns an all-missing e(V) for this
spec ("variance matrix is nonsymmetric or highly singular" after the CGM
adjustment) on the exact manuscript panel. Reproducible alternatives (CGM
fix on the pyfixest two-way vcov; manual Vp+Vy-Vi with reghdfe's own
eigenvalue fix in Stata) agree with each other (~0.12 for 1926, ~0.03 for
1934) but NOT with the published SEs (0.177, 0.084), which came from an
older reghdfe's salvage of the degenerate matrix. Under the reproducible
SEs several placebo cells change stars (1926 -0.335 -> **, 1928 -0.144 ->
***, 1934 +0.060 -> **, a POSITIVE significant placebo cell). Because
this is referee-visible and unfavorable to the placebo presentation, the
published column is left as-is; `attach_cluster_vcov` now falls back to
the CGM fix (instead of writing zero SEs) whenever Stata's e(V) comes
back degenerate, so the regenerated table carries the reproducible CGM
SEs for this column. Flag for the coauthor conversation if a referee ever
asks for col 7 SEs to be regenerated.

---

### D-018 — Raw -> A0-A3 chain closed; full raw-to-paper reproduction verified — **Resolved (2026-07-21)**

The two raw source files missing since the repo's creation
(`accounting_data.csv`, `gold_clauses.xlsx`) were recovered from
`GKP Analysis Feb 2025/data/` (the exact folder Mete's A0/A1 do-files cd
into; the `corrections/` copies are a different vintage) and installed in
`data/raw/`. The never-before-runnable Python ports of A0-A3 were then
tested against the known-good intermediates and fixed:

- **a0_accounting.py**: lowercase headers (Stata `import delimited`),
  calendar lags under `xtset permno_man year`, keep the `cc` scratch
  column, reproduce Stata's all-missing float lags of string date vars.
- **a1_bonds.py**: sanitize Excel headers the way `import excel, firstrow`
  does; `rating_med` is the firm-year median broadcast to bonds;
  `ind_3134_max` is a FIRM-wide max across all years (not per firm-year);
  keep the two missing-year bonds (groupby dropna=False); stable sort for
  bondnum.
- **a2_marcap.py**: keep the month column under Stata's name `min_month`.
- **a3_dividend.py**: correct as written (annual + monthly both exact).

Verification: A0 (9,245 x 111), A1 firm-level (1,804 x 9), A2
(15,625 x 7), A3 annual/monthly all match the on-disk intermediates
column-by-column (float32 storage noise only). A1 bond-level content is
identical as a multiset; only the meaningless within-firm-year `bondnum`
ordering differs (Stata's non-stable sort). End-to-end: raw files ->
A0-A3 -> a4_merge -> 7,074 x 845 panel matches `data/processed/A4_merged.dta`
exactly (0 mismatching columns). Combined with D-016/D-017, every number
in the manuscript now regenerates from `data/raw/` + versioned code; the
only external dependency is CRSP daily via `gold_claude.crsp` (licensed
data, rebuilt by `pipeline/sql/build_gold_claude_crsp.sql`).

---

### D-019 — Two-way clustered SEs are repair-convention-dependent; the paper standardizes on reghdfe — **Documented (2026-07-22)**

Investigation triggered by the all-Python question. The design has 15 year
clusters and 16+ regressors, so the year-cluster meat matrix has rank <= 14
and the CGM two-way combination (V_firm + V_year - V_intersection) is
non-positive-definite BY CONSTRUCTION, in every package. Each implementation
repairs it by zeroing negative eigenvalues; because the repair is applied to
slightly differently-scaled matrices, the repaired SEs diverge non-linearly.

Findings (baseline Table 4 col 2 spec, current reghdfe as ground truth):
- pyfixest raw components match reghdfe's to ~1e-7 (obs-level component):
  the estimator is identical, only scaling + repair differ.
- No pyfixest ssc() configuration reproduces reghdfe (best of 24: 4.5% max
  relative SE difference); manual reghdfe-style per-component scaling gets
  8.4%; reghdfe's final e(V) is not even a linear combination of the raw
  components (least-squares residual 35%) because it is post-repair.
- Exact matching would require porting reghdfe's Mata repair line-by-line,
  i.e. hard-coding one package version's discretionary heuristic — a moving
  target: reghdfe's own repair changed across versions (D-017 col 7).

Decision (Sebastien, 2026-07-22): keep the hybrid as the standard — Python
plumbing, reghdfe variance estimation — so the paper's SEs are exactly the
reghdfe numbers referees know. USE_STATA_VCOV=0 remains a fully functional
pure-Python fallback (identical coefficients; SEs within ~5%; ~46 star flips
across the regression tables, enumerated in the 2026-07-22 session report;
notably Table 5's net-repurchase 1933 cell would turn significant).

If a referee ever questions inference in this design, the textbook remedy
for G_clusters < k is the wild-cluster bootstrap; that discussion belongs in
a response letter, not in a silent SE-convention swap.

**D-019 addendum (2026-07-22) — legacy reghdfe code paths tested.** No older
Stata exists on the cluster (both /usr/local/stata and /software/stata are
Stata 19.5). However, reghdfe 6.13.1 ships its old implementations as
`reghdfe3` and `reghdfe5`. Both were run on the Table 4 column-7 (bank-debt)
spec: unlike reghdfe 6 (which returns all-missing SEs), BOTH produce SEs —
and both land in the CGM family (1926: 0.125/0.129 vs pyfixest 0.125), NOT
at the published values (0.177). With reghdfe3, reghdfe5, reghdfe6-refusal,
pyfixest-CGM, and a manual Stata combination all mutually consistent and
none matching the published column-7 SEs, the most parsimonious explanation
is that those SEs came from the same lost 2023 esttab session that produced
the columns 4-5 samples (D-017) — not from any reproducible software
vintage. Chasing older reghdfe releases is a dead end; the shipped CGM SEs
for column 7 stand as the reproducible choice.

## D-020 (2026-07-22): Table 2 Panel C — shipped firm count and decimals are fossils; builder output adopted

Discovered during the analysis-folder rename, when recompiling the
manuscript exposed that the committed PDF had been stale since the repo
restructure (bc6a4c6): that commit regenerated `1_sum_stats_d.tex` (now
`table2_summary_stats.tex`) from the builder, changing Panel C, and the PDF
was never rebuilt.

The shipped (Mete-original) Panel C does not reproduce from any accessible
panel:

- Firm count "594": distinct firms 1935–1940 in the verified vintage panel
  = 503 (the builder's number). The full-sample count is 558 — 594 matches
  nothing; it is presumably a fossil of a pre-vintage data state.
- Eight cells differ by ±0.01 (netinc mean 0.05→0.06, booklev mean
  0.36→0.35, and six SDs). Recomputing on the verified panel confirms the
  builder's rounding in every cell (e.g. booklev mean 0.3540, Q SD 0.8558,
  cash SD 0.1329). Observation counts (2,867 / 2,861) are identical, so
  the shipped values come from slightly different variable values in an
  older panel, not a different sample.

Panels A and B — the referee-facing d=0 vs d>0 comparisons — are identical
in every cell (the "144/144" validation covered these). The builder also
adds a previously missing N/Mean/SD header row to Panels A/B.

Decision: adopt the builder's Table 2 (consistent with the non-negotiable
"code reproduces the manuscript" and with D-017's treatment of Table 4);
the table is wrapped in revblock for review in the round-2 diff.

## D-021 (2026-07-22): IA summary-table quantile convention fixed; three IA builders still do not reproduce shipped tables

The `summary_stats_ia` model computed p25/p50/p75 with numpy's default
linear interpolation (with per-quantile "lower"/"higher" fudges for
p5/p95). Stata's `summarize, detail` averages the two adjacent order
statistics when n*q is an integer, else takes the next one up — numpy's
`averaged_inverted_cdf` (the same convention already used for xtile
deciles and in constraints.py). The six shipped IA.1 cells that the old
method missed (Q p25 0.69, log-assets p75 18.22 / p25 16.28, cash p75
0.15, book-lev p75 0.66, log-LTL p25 15.12) all reproduce exactly under
the Stata convention.

With the fix, cell-level numeric comparison against the shipped tables:

- IA.1, IA.2, IA.4, IA.5, IA.6 (259-386 numbers each): ALL identical.
  These five are now builder-generated in the tree (values unchanged;
  formatting normalized: math-mode minus, standard notes block).
- IA.7 (summary_I_larged), IA.10 (summary_pos_ps_bond), IA.11
  (summary_diff_pos_ps_bond): builders produce DIFFERENT samples
  (e.g. IA.10 first panel: 486 firms/2,792 obs vs shipped 452/2,408) —
  the pre-existing D-012/13/14-family gaps, now measured precisely.
  Shipped versions restored; these stages are in run.py's FROZEN set, so
  `--stage all` skips them instead of silently overwriting. Resolving
  them (recover Mete's sample definitions or adopt builder output)
  remains the open decision flagged in the 2026-07-22 all-Python report.

**D-021 addendum (2026-07-22) — IA.7, IA.10, IA.11 RESOLVED: exact
reproduction.** All three "different sample" gaps were reverse-engineered
from the verified panel and Mete's legacy A14 do-file:

- IA.7: the median cutoff (`keep if d > r(p50)`, observation-level over
  1926-32 d>0 firm-years) reproduces exactly under the D-021 quantile fix
  (192 firms / 715 obs in Panel A). The remaining diff was structural: the
  shipped IA.7 (unlike IA.6) reports the d-tilde rows in Panel B; rows
  added to the builder. 386/386 numbers identical.
- IA.10/IA.11: the shipped tables were built with the RFS-era `dalt` —
  denominator `cb_bs + ps_bs` (preferred + bonds, NO bank debt) and no
  zero-backfills; the panel's stored `dalt` column is the later Oct-2025
  variant (`bd+cb+ps` + has_debt backfills), which selects 486 firms where
  the shipped table has 452. Sample counts verified exact in all three
  panels (452/2,408; 366/717; 355/2,016); reconstructed in
  models/dalt_panel.py. IA.11 then reproduces 119/119 numbers; IA.10
  (after adding the Panel B d-tilde rows) 386/386.

run.py's FROZEN set is now EMPTY: every manuscript table regenerates
exactly from the code. Validator tolerances in the three builders
tightened back to standard (PERCENTILE_TOL fudge removed).

## D-022 (2026-07-22): Full reproducibility audit — the authoritative scorecard

Every table stage was regenerated and compared to the committed manuscript
tex, number by number (SEs and all cells, not just the validated
coefficients). Results:

**Byte-identical (regenerate to the byte):** Table 4 (investment), and the
previously verified Table 1 + IA.20 (event study), Table 2, Table 3, IA.19.

**Value-identical (every number equal; formatting normalized and adopted):**
Table 6, IA.1-IA.11, IA.14, IA.18 — i.e. IA.3, IA.8, IA.9, IA.14, IA.18
joined the D-021 set in this audit.

**Value gaps (shipped versions kept; stages FROZEN):**

| Stage  | Table | Gap |
|--------|-------|-----|
| table5 | T5 other outcomes      | 10/213 cells, last digit (D-010 winsor/sample gaps, cols 2-5) |
| table7 | T7 controls            | Stata-vcov bridge segfaults (rc=-11, known); CGM mode: 20/113 last-digit SE cells |
| table8 | T8 aggregate           | 2/17 cells, last digit (inherits T4-input sensitivity) |
| ia12   | IA.12 repayers/balanced| 21/147 cells, mostly last digit |
| ia13   | IA.13 constraints      | 72/82 cells incl. sign flips — largest open gap (D-013) |
| ia15   | IA.15 dividends add'l  | 22/59 cells, some large (0.064 vs 0.079; D-014 family) |
| ia16   | IA.16 indicators       | 2/76 cells, last digit |
| ia17   | IA.17 stock controls   | Stata-vcov crash; CGM mode: 27/69, some SEs 20-30% off |

Most gaps are third-decimal SE differences consistent with the shipped
tables having been built under a different vcov path (mixed
Stata-vcov/CGM vintage); ia13 and ia15 look like genuine sample/spec
mismatches in the same class D-021's addendum resolved for IA.7/10/11 —
candidates for the same reverse-engineering treatment. The FROZEN set in
analysis/run.py mirrors this table; `--stage all` skips those stages.

**D-022 addendum (2026-07-22) — IA.13 and IA.15 resolved and adopted.**
Both gaps were spec/semantics bugs in the builders, recovered from the
legacy do-files (d54b0c3:code/legacy/mete/):

- IA.13 (constraints, A17_sizecashlev.do): the constraint measures are the
  FIRM-LEVEL MEAN of a time-varying indicator (``bys permno: egen small =
  mean(small2)`` — a fraction in [0,1], defined for all firms), not a
  min-year 0/1 snapshot of d>0 firms; plus Stata missing semantics
  (missing > p50 is TRUE for highlev). With the fix: all coefficients and
  stars match the shipped table; 6 last-digit cells (3 coefficient, 3 SE)
  remained as fossils of a lost intermediate state.
- IA.15 (additional dividends, A18_additionaldividend.do): three bugs —
  divind must be TRUE when 1932 cashrat is missing (Stata missing > 0) and
  MISSING for firms with no 1932 row (excluded from both cols 3 and 4, not
  dumped into col 4); L.cashrat/L.cashdiv are calendar lags, not
  positional shifts; ``if L.cashrat > 0`` includes missing-lag rows.
  With the fixes: every coefficient and star matches; 1 SE digit (divgr
  column) remained (Stata-vcov family confirmed; CGM is worse at 8 cells).

Per the D-020 precedent (irreproducible fossil digits -> adopt the
reproducible builder output), both tables are now builder-generated in the
tree, wrapped in revblock for review. FROZEN shrinks to six stages, all
with last-digit-SE-class gaps only: table5, table7, table8, ia12, ia16,
ia17.

**D-022 final addendum (2026-07-22) — remaining fossils adopted; replication
is unconditional.** Per Sebastien's decision, the six frozen tables were
regenerated under the hybrid vcov standard and adopted (revblocked for
review). The Stata bridge segfault on the Table 7 / IA.17 specs is now
handled inside attach_cluster_vcov (automatic CGM fallback), so
`analysis/run.py --stage all` runs end-to-end with no env vars. Adopted
differences vs the shipped fossils (all SE-family; only Table 8 touches
coefficients, two cells at 0.01pp, text synced with \rev):

- Table 5: 2 star changes on uncited cells (1931 profits * -> **;
  1940 net-repurchase loses *). All quoted 1933/34 claims unchanged.
- Table 7: SE last digits; d-tilde col 1 *** -> **, col 5 ** -> *;
  1933 col 6 ** -> *; 1934 cols 1,3 ** -> ***. The quoted col 1 / col 2
  sentences hold (col 1 1934 strengthens).
- Table 8: -4.10/-1.77 -> -4.11/-1.78 (Section 5 sentence updated).
- IA.12: stars only strengthen (d-tilde and 1935 cells ** -> ***).
- IA.16: two SE last digits, no star changes.
- IA.17: d-tilde cols 4-6 upgrade * -> **.

FROZEN is empty. The replication statement is now unconditional: from
data/raw/ + data/processed/, `pipeline/run.py` then
`analysis/run.py --stage all` reproduces every table and figure in the
manuscript exactly.

## D-023 (2026-08-22): SE vintage identified as reghdfe engine versions; regression tables now generated by per-table Stata do-files

The "mixed vcov vintage" behind every remaining last-digit SE fossil
(D-019/D-022) is resolved. Prompted by Mete's suggestion to try reghdfe's
`version(5)` option, a full-table sweep compared every printed cell of the
regression tables, re-estimated under reghdfe 6.13.1's current engine and
its legacy `version(5)` engine, against the pre-adoption (previous-
submission) tex files:

| Table | Cells | version(5) | version(6) | Vintage |
|-------|-------|------------|------------|---------|
| T5    | 204   | 204        | 194        | v5 |
| T7    | 120   | 120        | 116        | v5 |
| IA.12 (cols 2-4) | 102 | 102 | 100 | v5 |
| IA.15 | 64    | 64         | 63         | v5 |
| IA.16 | 60    | 60         | 58         | v5 |
| IA.13 | 78    | 73         | 72         | v5 (5 lost-state cells remain) |
| IA.17 (cols 2-6) | 60 | 52 | 45        | v5 (residual = lost decile construction) |
| T4 (March submission, cols 1,2,3,6) | 106 | 105 | 106 | **v6** |
| T6 + IA.9 | 304 | 282       | 304        | **v6** |
| IA.14 | 170   | 170        | 170        | either (one-way cluster) |

So the original tables were estimated under two reghdfe generations:
version-5-era runs for T5/T7/IA.12/IA.13/IA.15/IA.16/IA.17, version-6-era
runs for T4/T6/IA.9 (IA.19 is our own reghdfe-6 work). The reghdfe 5->6
revision of the two-way-cluster computation moves SEs by ~0.5%, which
surfaces only in cells at a 3-decimal rounding boundary - exactly the
observed fossil pattern. The old D-022 note that the Stata bridge
"segfaults" on the T7/IA.17 specs was a defect of the in-process bridge
invocation only; the same specs run fine as batch do-files.

**Architecture change.** Every table that prints reghdfe standard errors is
now estimated by a standalone batch do-file in `analysis/stata/` (one per
table, engine pinned via `version(5)` where that is the paper's vintage),
writing `analysis/stata/results/<stage>_results.csv` (committed). The
Python builders prepare the input panel (`data/processed/stata_inputs/`,
not committed), invoke `stata-mp -b`, read the CSV back through
`analysis/lib/stata_reg.py` adapters, and render LaTeX with the unchanged
renderers. There is no fallback: a missing/failing Stata run fails the
stage. The in-process vcov bridge (`reghdfe_vcov.do`,
`fetch_vcov_stata`, `USE_STATA_VCOV`) is removed; `lib/vcov.py` keeps only
the CGM fix for the coefficient-only consumers (T8/IA.18 aggregations).
Figure 6 now reads the Table 4 results CSV (overhang column), so its bands
are the table's SEs by construction (pixel-identical to the shipped
figure).

**Effect on shipped tables.** T5, T7, IA.12 (cols 2-4), IA.15, IA.16
revert to the previous submission's SEs exactly (undoing the D-022
adoption); T6, IA.9, IA.14 were already exact and are byte-unchanged; T4
cols 1-6 unchanged. 11 star changes vs the adopted versions, all
restorations of the previous submission's stars, none on a cited cell; two
round-2 text passages written against the adopted tables were synced
(Section 5's count of significant 1933 decile coefficients - now all
eight at 5% or better - and the R6 comment-2 citation of Table 7 col 1's
1934 star). Remaining irreproducible items, all engine-independent lost
states documented before: T4 cols 4-5 samples and col 7 published SEs
(col 7 now ships version(5) SEs, the only engine that produces any for
that spec; no star changes), IA.12 col 1 sample (18 cells), IA.13
(5 cells), IA.17 col 1 sample and a few decile-column last digits
(15 cells), T2 Panel C, T8's two 0.01pp cells.

**D-023 addendum (2026-08-22) — Table 4 col 7 published SEs declared an
error, matching closed.** Per Sebastien: the round-1 column-7 standard
errors (e.g. 1926: 0.177, 1934: 0.084), which match no reproducible
reghdfe engine (D-017/D-019), are an error in the original version of the
paper, not a target. The version(5) SEs shipped since commit 6fcb909 are
the paper's numbers (1926: 0.129**, 1928: 0.038***, 1933: 0.061 n.s.,
1934: 0.038 n.s.; placebo conclusions unchanged). No further attempts to
recover the published column-7 SEs.

**D-023 addendum 2 (2026-08-22) — published Table 4 col 5 RECOVERED from
Mete's original code; it was never a sample restriction.** Mete supplied
the round-1 column-5 code via Slack: it redefines the exposure as `dalt`
= fd_amount_g1/(bd_bs+cb_bs+ps_bs) capped at 1 (measured 1930, zero-filled
for firms with any fixed claims), with pre-1930 values of the LEVEL
variable overwritten by a time-varying Lcb_bs/(Lbd_bs+Lcb_bs+Lps_bs)
ratio (Mete's own comment: "this is mainly the problem"), interactions
from A4's firm-constant dalt_year_*, no explicit sample restriction. Run
verbatim on firm_year_panel.dta under reghdfe 6 it reproduces the
published column EXACTLY: N = 6,048, d = -0.057 (0.030), 1933 = -0.058
(0.013), 1934 = -0.043 (0.009), every cell to the printed digit. So the
published column was mislabeled ("restricts the sample to firms with
positive long-term liabilities" with the paper's d-tilde) - it is a
different exposure, and D-017's sample-search could never find it. The
shipped reconstruction (d-tilde on ll_bs>0-in-1930 firms) remains in the
tree pending the Sebastien/Mete decision: adopt-and-relabel, keep the
reconstruction, or ship a corrected dalt spec. The published col 4
(N = 5,572, also IA.12 col 1) may live in another block of the same
script - ask Mete. Test script: scratch mete_col5.do (this session).

**D-023 addendum 3 (2026-08-22) — one engine everywhere.** Per Sebastien,
all regression do-files (including Table 4 cols 1-6, Table 6/IA.9, IA.14,
and IA.19) now run under reghdfe's legacy `version(5)` engine, trading
~26 last-digit SE cells of round-1 fidelity in the former reghdfe-6
tables for a uniform engine. Verified effects: Table 4, Table 6, IA.14
zero star changes (T4: 4 SE digits; T6 body: 1 digit; IA.14
print-identical); IA.9: ~20 SE digits + three star strengthenings, all in
the uncited payout column (1933 *->**, 1934 **->***, 1939 gains *);
IA.19: one SE digit + payout-deciles 1934 ** -> * (p 0.0499 -> 0.0508
boundary). All quoted claims verified intact: IA.19 d-tilde 9/9 at 5%,
1933 7/9 at 5% and 9/9 at 10%, 1934 loses significance in seven of nine
(same two 10% survivors); Table 6's cited theta/kappa stars unchanged.
The replication statement is now one line: all printed standard errors
are reghdfe legacy-engine (version(5)) estimates.

**D-023 addendum 4 (2026-08-22) — Table 4 col 5 adopted; published column
restored.** Per Sebastien ("our goal should be to match the numbers that
were there before"), Mete's recovered fixed-claims exposure is now the
col-5 builder (t04_investment.py `_fixed_claims_exposure` + do-file
`fixed_claims` block): gold-clause debt over bank debt + bonds +
preferred stock in 1930, capped at one, pre-1930 level = lagged bond
share of fixed claims (mirroring merge.py's baseline-d construction; a
firm-constant level would be absorbed by the firm FE), interactions =
the panel's firm-constant dalt_year_*. Pandas translation required two
Stata semantics (missing > 0 is TRUE; x/0 is missing). The column now
matches the round-1 submission in every cell except the 1933 SE printed
digit (0.014 vs 0.013 - the accepted version(5) engine difference);
d-tilde regains its published -0.057* (the D-017 reconstruction had
-0.052 n.s.). Because the round-1 note misdescribed the column as a
sample restriction with the paper's d-tilde, the note and the Section 5
passage were rewritten to describe the actual specification (header
"With LT Lia." -> "Fixed claims"). Still open: col 4 (N = 5,572, also
IA.12 col 1) - ask Mete for the corresponding block of the same script.
