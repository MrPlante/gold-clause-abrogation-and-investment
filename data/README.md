# data/ — layout and provenance

Nothing in this folder is versioned except this README. There is **no git
safety net here**: treat `raw/` and `intermediates/` as irreplaceable.

```
data/
  A4_merged.dta      ← THE panel (7,074 x 845 — the manuscript vintage,
                       adopted 2026-07-21 from Mete's Dropbox and verified
                       against every manuscript table). Everything
                       downstream reads this one file (all tables, the
                       event-study pipeline, the IA.19 Stata do-file).
                       Rebuild (both verified exact vs this file):
                         python3 code/run.py --stage data --skip-raw
                       or Mete's A4_merge.do from git history
                       (d54b0c3:code/legacy/mete/A4_merge.do).
  raw/               ← source inputs, external provenance, never regenerated
    crsp_monthly.dta        CRSP monthly extract (feeds A2 marcap, A3 dividends)
    monthly_div.dta         coauthor's monthly dividend data (feeds IA.12)
    chars_annual.dta        1930 firm characteristics & betas (feeds IA.17)
    netincome.dta           net income series (feeds the A4 merge)
    figures/monthly_macro.csv   retired FRED cache (Figures 1-2 now build
                            from versioned code/figures/data/macro_monthly.csv)
    accounting_data.csv     [MISSING on this machine — from Mete]
    gold_clauses.xlsx       [MISSING on this machine — from Mete]
  intermediates/     ← A0-A3 pipeline stages (June 2026 build; byte-identical
    A0_accounting_data.dta, A1_bond_data_{bondlevel,firmlevel}.dta,     to
    A2_marcap.dta, A3_dividend_{annual,monthly}.dta      Mete's Oct 2025 set)
                       Regenerable from raw/ ONLY if the two missing raw
                       files are restored — until then these are precious.
  attic/             ← retired; kept because data/ has no git history
    A4_merged_6768x831_deviant.dta  the pre-2026-07-21 on-disk panel. A
                            deviant build (lags recomputed after row drops,
                            losing 306 firm-years — see DISCREPANCIES
                            D-016), NOT an older data vintage. Superseded.
    pf_returns.xls          coauthor's return export; ewret_yes/ewret_no
                            columns are SWAPPED (verified 2026-07-16). Kept
                            as evidence for the coauthor conversation. Do
                            not use; returns come from gold_claude.crsp.
    ff_factors_daily.csv    orphan Fama-French download (superseded)
    denom_div.dta           legacy Stata input, nothing reads it
    VAR_IN~4, "var_inv_rate ..." files   Stata/Windows filename mishaps
```

**Vintage note (resolved 2026-07-21):** the long-standing "N=7,074 vs
N=6,768 data vintage mismatch" was not a data problem. The upstream inputs
were always identical to Mete's; the old on-disk A4 was a deviant merge
(now in attic/). `code/DISCREPANCIES.md` D-016 has the full story. The
only remaining ask for Mete is the RFS-era `A9_inv_results.do` (published
Table 4 columns 4-5 sample definitions).

The untracked `GKP Analysis *` folders at the repo root are Mete's Dropbox
snapshots (Apr 2024, Feb 2025, Oct 2025) — the source of the adopted A4
and of the original referee reports and submitted PDFs. Not versioned.
