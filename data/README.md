# data/ — layout and provenance

Nothing in this folder is versioned except this README. There is **no git
safety net here**: treat `raw/` as irreplaceable.

```
data/
  processed/         ← pipeline outputs (rebuild: .venv/bin/python pipeline/run.py;
                       the source stages run in memory and are not persisted)
    firm_year_panel.dta ← THE panel (7,074 x 845 — the manuscript vintage,
                       verified against every manuscript table). Everything
                       downstream reads this file (all tables, the
                       event-study pipeline, the IA.19 Stata do-file).
    bond_panel.dta   ← bond-level panel; read directly by the Table 3
                       builder (bond-level rows never reach the firm-year
                       panel). Matches the retired Mete intermediate to
                       float32 precision (row order within permno-year
                       differs).
  raw/               ← source inputs, external provenance, never regenerated
    crsp_monthly.dta        CRSP monthly extract (feeds sources/marcap + dividends)
    monthly_div.dta         coauthor's monthly dividend data (feeds IA.12)
    chars_annual.dta        1930 firm characteristics & betas (feeds IA.17)
    netincome.dta           net income series (feeds pipeline/merge.py)
    accounting_data.csv     hand-collected accounting panel (restored
                            2026-07-21 from "GKP Analysis Feb 2025/data/" —
                            the vintage Mete's A0 do-file cd's into;
                            NOT the corrections/ copy)
    gold_clauses.xlsx       hand-collected bond/gold-clause data (same
                            provenance; sheet "REAL ENTRY")
    crsp_daily.dta          local dump of researchdb gold_claude.crsp
                            (2026-07-22): CRSP daily returns 1925-12-31 to
                            1945-12-31, 4,396,736 rows, 1,146 permnos, dates
                            stored %td. THE CRSP daily source: the
                            event-study pipeline reads this file (offline,
                            no Kerberos); the DB is used only to regenerate
                            the dump when the extract changes.
    crsp_daily_names.dta    companion dump of gold_claude.crsp_names
                            (1,624 spells, 1,146 permnos -> 1,123 permcos):
                            names/share class/ticker/SIC/delisting history.
```

The two `crsp_daily*` files live in `raw/` (not `processed/`) because
`processed/` is reserved for what `pipeline/run.py` can rebuild from `raw/`
alone; the CRSP dump is licensed external data, rebuildable only with
researchdb/WRDS access (`pipeline/sql/build_gold_claude_crsp.sql`) — same
status as `crsp_monthly.dta`. CRSP is licensed: share only with coauthors
whose institutions hold a CRSP/WRDS subscription, and do not include these
files in any public replication package.

**Renamed 2026-07-22** (Stata stage prefixes dropped from on-disk artifacts):
`A4_merged.dta` → `firm_year_panel.dta`, `A1_bond_data_bondlevel.dta` →
`bond_panel.dta`. Older notes, `DISCREPANCIES.md`, and git history use the
old names; they refer to the same files.

The former `attic/` (retired material from the 2026-07-21 cleanup) was moved
on 2026-07-21 to `tmp/2026-07/21/attic/` — see `tmp/README.md` for the item
inventory and the caution about which parts are the only copy outside the
coauthors' Dropbox.

The three "GKP Analysis *" Dropbox snapshots were deleted from the repo
root on 2026-07-21 after everything load-bearing was extracted (raw files
-> data/raw/, panel -> data/processed/firm_year_panel.dta, do-files verified identical to
git history, round-1 reports + as-submitted PDFs -> rfs-responses/,
unique research material -> the attic, now `tmp/2026-07/21/attic/`). The
originals remain in the coauthors' Dropbox.

**Vintage note (resolved 2026-07-21):** the long-standing "N=7,074 vs
N=6,768 data vintage mismatch" was not a data problem. The upstream inputs
were always identical to Mete's; the old on-disk A4 was a deviant merge
(now in `tmp/2026-07/21/attic/`). `DISCREPANCIES.md` D-016 has the full story.
The published Table 4 columns 4-5 samples were later shown unrecoverable and
replaced by documented reconstructions (D-017); nothing about the data is
outstanding.
