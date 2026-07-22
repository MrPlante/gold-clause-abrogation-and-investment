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
    accounting_data.csv     hand-collected accounting panel (restored
                            2026-07-21 from "GKP Analysis Feb 2025/data/" —
                            the vintage Mete's A0 do-file cd's into;
                            NOT the corrections/ copy)
    gold_clauses.xlsx       hand-collected bond/gold-clause data (same
                            provenance; sheet "REAL ENTRY")
  intermediates/     ← A0-A3 pipeline stages (June 2026 build; byte-identical
    A0_accounting_data.dta, A1_bond_data_{bondlevel,firmlevel}.dta,     to
    A2_marcap.dta, A3_dividend_{annual,monthly}.dta      Mete's Oct 2025 set)
                       Regenerable from raw/: the full raw -> A0-A3 -> A4
                       chain was verified 2026-07-21 (python3 code/run.py
                       --stage data rebuilds the manuscript panel exactly,
                       to float32 storage precision).
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
    bond_returns/           hand-made bond-CRSP link files (1926-1942) and
                            bond-return work from the Feb 2025 snapshot —
                            unused by the paper but irreplaceable hand work
    coauthor-notes/         Mete's notes, data-issue workbooks, CODE.pdf,
                            column documentation (Feb/Oct 2025 snapshots)
    corrections-vintage/    the corrections-era accounting_data.csv /
                            gold_clauses.xlsx (a DIFFERENT vintage from
                            data/raw/ — kept for provenance)
    apr2024-snapshot/       the Apr 2024 folder wholesale (ancient pipeline
                            data + a 2024 balance-sheet recollection)
    portfolio_returns_feb2025.xls   another coauthor return export
                            (differs from pf_returns.xls)
```

The three "GKP Analysis *" Dropbox snapshots were deleted from the repo
root on 2026-07-21 after everything load-bearing was extracted (raw files
-> data/raw/, panel -> data/A4_merged.dta, do-files verified identical to
git history, round-1 reports + as-submitted PDFs -> rfs-responses/,
unique research material -> attic/ as listed above). The originals remain
in the coauthors' Dropbox.

**Vintage note (resolved 2026-07-21):** the long-standing "N=7,074 vs
N=6,768 data vintage mismatch" was not a data problem. The upstream inputs
were always identical to Mete's; the old on-disk A4 was a deviant merge
(now in attic/). `code/DISCREPANCIES.md` D-016 has the full story. The
only remaining ask for Mete is the RFS-era `A9_inv_results.do` (published
Table 4 columns 4-5 sample definitions).

The untracked `GKP Analysis *` folders at the repo root are Mete's Dropbox
snapshots (Apr 2024, Feb 2025, Oct 2025) — the source of the adopted A4
and of the original referee reports and submitted PDFs. Not versioned.
