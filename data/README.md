# data/ — layout and provenance

Nothing in this folder is versioned except this README. There is **no git
safety net here**: treat `raw/` as irreplaceable.

```
data/
  processed/
    A4_merged.dta    ← THE panel (7,074 x 845 — the manuscript vintage,
                       verified against every manuscript table). Everything
                       downstream reads this one file (all tables, the
                       event-study pipeline, the IA.19 Stata do-file).
                       Rebuild: .venv/bin/python pipeline/run.py
                       (A0-A3 run in memory; nothing else is persisted).
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
