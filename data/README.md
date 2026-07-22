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
                         .venv/bin/python pipeline/run.py --skip-raw
                       or Mete's A4_merge.do from git history
                       (d54b0c3:code/legacy/mete/A4_merge.do).
  raw/               ← source inputs, external provenance, never regenerated
    crsp_monthly.dta        CRSP monthly extract (feeds A2 marcap, A3 dividends)
    monthly_div.dta         coauthor's monthly dividend data (feeds IA.12)
    chars_annual.dta        1930 firm characteristics & betas (feeds IA.17)
    netincome.dta           net income series (feeds the A4 merge)
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
                       chain was verified 2026-07-21 (.venv/bin/python
                       pipeline/run.py rebuilds the manuscript panel exactly,
                       to float32 storage precision).
```

The former `attic/` (retired material from the 2026-07-21 cleanup) was moved
on 2026-07-21 to `tmp/2026-07/21/attic/` — see `tmp/README.md` for the item
inventory and the caution about which parts are the only copy outside the
coauthors' Dropbox.

The three "GKP Analysis *" Dropbox snapshots were deleted from the repo
root on 2026-07-21 after everything load-bearing was extracted (raw files
-> data/raw/, panel -> data/A4_merged.dta, do-files verified identical to
git history, round-1 reports + as-submitted PDFs -> rfs-responses/,
unique research material -> the attic, now `tmp/2026-07/21/attic/`). The
originals remain in the coauthors' Dropbox.

**Vintage note (resolved 2026-07-21):** the long-standing "N=7,074 vs
N=6,768 data vintage mismatch" was not a data problem. The upstream inputs
were always identical to Mete's; the old on-disk A4 was a deviant merge
(now in `tmp/2026-07/21/attic/`). `DISCREPANCIES.md` D-016 has the full story. The
only remaining ask for Mete is the RFS-era `A9_inv_results.do` (published
Table 4 columns 4-5 sample definitions).
