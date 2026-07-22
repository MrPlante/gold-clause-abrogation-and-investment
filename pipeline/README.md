# pipeline/ — data wrangling (data/raw/ -> data/processed/)

Builds the firm-year panel the whole paper runs on:

```
sources/  (independent; any order)                          merge.py
  accounting.py  accounting_data.csv -> accounting panel ──────┐
  bonds.py       gold_clauses.xlsx   -> firm + bond panels ────┤
  marcap.py      crsp_monthly.dta    -> market caps ───────────┼─> data/processed/firm_year_panel.dta
  dividends.py   crsp_monthly.dta    -> dividend series ───────┤        (7,074 x 845)
                 data/raw/netincome.dta ───────────────────────┘
```

```bash
.venv/bin/python pipeline/run.py    # full raw -> processed build
```

Only the two consumed outputs are persisted: the merged panel and the
bond-level panel `data/processed/bond_panel.dta` (read directly by the
Table 3 builder). The other source frames stay in memory; each is
round-tripped through the .dta format in an in-memory buffer
(`lib/io.roundtrip_dta`) before the merge, so dtypes match the historical
on-disk intermediates and the build stays verified-exact.

## Layout

- `run.py` — entry point; `build.py` — orchestration + panel validation.
- `sources/` — one module per raw input, independent of each other.
- `merge.py` — the terminal stage: sources + netincome -> THE panel.
- `lib/` — shared data primitives (`io`, `sample`, `winsor`), also imported
  by `analysis/` (analysis depends on pipeline, never the reverse).
- `sql/build_gold_claude_crsp.sql` — builds the `gold_claude.crsp` daily
  CRSP table on researchdb (licensed), from which `data/raw/crsp_daily.dta`
  is dumped; see `data/README.md`.

## Provenance

Every stage is a faithful port of Mete's Stata do-files (git history:
`d54b0c3:code/legacy/mete/`) and reproduces the manuscript panel exactly,
to float32 storage precision (DISCREPANCIES.md D-016/D-018). Old -> new
module names (2026-07-22; the aN prefixes were the do-file numbers):

| Do-file | Old module | Now |
|---|---|---|
| A0_accounting.do | `a0_accounting.py` | `sources/accounting.py` |
| A1_bond_data.do | `a1_bonds.py` | `sources/bonds.py` |
| A2_marcap.do | `a2_marcap.py` | `sources/marcap.py` |
| A3_dividend.do | `a3_dividend.py` | `sources/dividends.py` |
| A4_merge.do | `a4_merge.py` | `merge.py` |
