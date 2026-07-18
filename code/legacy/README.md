# Legacy code (archived)

Nothing in this directory is part of the active pipeline. It is kept for
provenance and as the reference implementation the Python refactor was
validated against. The active pipeline lives entirely in `code/refactor/`.

## `mete/` — original Stata pipeline

The original `.do` files (A0–A21 plus `main_code.do`) that built the panel
and produced every table of the round-1 manuscript. Superseded by
`code/refactor/`, which replicates it coefficient-for-coefficient
(221/221 matched cells; see `code/refactor/compare/`). Two pieces were
promoted out of here rather than archived:

- `A12_controls_indyear.do` → `code/refactor/stata/` (still the production
  source of IA.19's exact Stata standard errors)
- the compare harness runs its own `.do` files under
  `code/refactor/compare/`, so nothing here is executed anymore

## `seb/` — retired exploratory scripts

- `pf_returns.py` — read the coauthor's `data/returns/pf_returns.xls`
  export. Retired: that file's `ewret_yes`/`ewret_no` columns are swapped
  (verified 2026-07-16), and all return series are now rebuilt from raw
  CRSP by `code/refactor/event_study_pipeline.py`.
- `quarterly-div.py`, `quarterly-div-regtable.tex`,
  `quarterly-div-coefficients.{pdf,png}` — early quarterly-dividend
  analysis, superseded by `code/refactor/tables/appendix/ia_12_quarterly_div.py`
  (manuscript Table IA.12).
- `cursor.md` — working notes for the quarterly-dividend exploration.
