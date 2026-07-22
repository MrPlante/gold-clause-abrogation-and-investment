# pipeline/ — data wrangling (data/raw/ -> data/processed/)

Builds the firm-year panel the whole paper runs on:

```
data/raw/accounting_data.csv ─ a0_accounting ─> (in memory)
data/raw/gold_clauses.xlsx  ─ a1_bonds      ─> (in memory) + data/processed/bond_panel.dta
data/raw/crsp_monthly.dta   ─ a2_marcap     ─> (in memory)
data/raw/crsp_monthly.dta   ─ a3_dividend   ─> (in memory)
A0-A3 + data/raw/netincome.dta ─ a4_merge   ─> data/processed/firm_year_panel.dta  (7,074 x 845)
```

```bash
.venv/bin/python pipeline/run.py    # full raw -> processed build
```

Only the two consumed outputs are persisted: the merged panel and the
bond-level panel (read directly by the Table 3 builder). The other A0-A3
stage frames stay in memory; each is round-tripped through the .dta format
in an in-memory buffer (`io.roundtrip_dta`) before the merge, so dtypes
match the historical on-disk intermediates and the build stays
verified-exact.

Every stage is a faithful port of Mete's Stata do-files (git history:
`d54b0c3:code/legacy/mete/`) and reproduces the manuscript panel exactly,
to float32 storage precision (DISCREPANCIES.md D-016/D-018; Mete's Oct 2025
intermediates are retired to `tmp/2026-07/21/intermediates/`). `io.py`,
`sample.py`, and `winsor.py` are the shared data primitives, also imported
by `analysis/`.

`sql/build_gold_claude_crsp.sql` builds the `gold_claude.crsp` daily-returns
table on researchdb (licensed CRSP data; needed only by the event-study stage).
