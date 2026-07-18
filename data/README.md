# data/ — layout and provenance

Nothing in this folder is versioned except this README. There is **no git
safety net here**: treat `raw/` and `intermediates/` as irreplaceable.

```
data/
  A4_merged.dta      ← THE panel. Everything downstream reads this one file
                       (all tables, the event-study pipeline, the IA.19
                       Stata do-file). Rebuild: python3 code/run.py
                       --stage data --skip-raw  (verified byte-exact).
  raw/               ← source inputs, external provenance, never regenerated
    crsp_monthly.dta        CRSP monthly extract (feeds A2 marcap, A3 dividends)
    monthly_div.dta         coauthor's monthly dividend data (feeds IA.12)
    chars_annual.dta        1930 firm characteristics & betas (feeds IA.17)
    netincome.dta           net income series (feeds the A4 merge)
    figures/monthly_macro.csv   FRED cache for manuscript Figures 1-2
    accounting_data.csv     [MISSING on this machine — from Mete]
    gold_clauses.xlsx       [MISSING on this machine — from Mete]
  intermediates/     ← A0-A3 pipeline stages (June 2026 build, N=6,768 vintage)
    A0_accounting_data.dta, A1_bond_data_{bondlevel,firmlevel}.dta,
    A2_marcap.dta, A3_dividend_{annual,monthly}.dta
                       Regenerable from raw/ ONLY if the two missing raw
                       files are restored — until then these are precious.
  attic/             ← retired; kept because data/ has no git history
    pf_returns.xls          coauthor's return export; ewret_yes/ewret_no
                            columns are SWAPPED (verified 2026-07-16). Kept
                            as evidence for the coauthor conversation. Do
                            not use; returns come from gold_claude.crsp.
    ff_factors_daily.csv    orphan Fama-French download (superseded)
    denom_div.dta           legacy Stata input, nothing reads it
    VAR_IN~4, "var_inv_rate ..." files   Stata/Windows filename mishaps
```

**Data-vintage warning (2026-07-17):** the manuscript's regression tables
were produced from an older A4 vintage with N=7,074 that is NOT on this
machine. The current raw/ + intermediates/ chain produces N=6,768. See
`code/DISCREPANCIES.md` and the project memory before regenerating any
manuscript table.
