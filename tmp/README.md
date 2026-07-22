# tmp/ — session scratch

Everything here is untracked and disposable (see `.gitignore`); this README
and the `.gitignore` are the only tracked files.

## Convention (since 2026-07-21, mirrors KLPW2)

- One month directory containing one directory per working-session day:
  `tmp/YYYY-MM/DD/`. The day is the date the session **started** (overnight
  work stays in the starting day's directory).
- All session results — smoke outputs, diagnostics, draft notes, moved-aside
  material — go in that directory.
- At the end of the session, decide together what (if anything) gets
  promoted into the main project trees; the rest stays here as the session's
  paper trail and can be cleaned out later without ceremony.

## Contents

- `2026-07/21/intermediates/` — the former `data/intermediates/` (A0-A3
  stage files, byte-identical to Mete's Oct 2025 set), retired 2026-07-21
  when the pipeline moved to in-memory stages writing only
  `data/processed/`. The Python rebuild was verified against these to
  float32 precision before retiring them.
- `2026-07/21/A4_merged_adopted_backup.dta` — safety copy of the adopted
  manuscript panel taken before the pipeline-rebuild verification run
  (identical to `data/processed/A4_merged.dta`).
- `2026-07/21/attic/` — the former `data/attic/` (retired material from the
  2026-07-21 Dropbox-snapshot cleanup), moved here wholesale. **Caution:
  despite living under tmp/, parts of this are the only copy outside the
  coauthors' Dropbox** — `bond_returns/` (hand-made bond-CRSP links
  1926-1942), `coauthor-notes/` (Mete's notes and data-issue workbooks),
  `corrections-vintage/` (a different accounting_data/gold_clauses vintage
  than data/raw/), `apr2024-snapshot/`. Also: `pf_returns.xls` and
  `portfolio_returns_feb2025.xls` (evidence of the swapped
  ewret_yes/ewret_no columns — keep until Mete has been told),
  `A4_merged_6768x831_deviant.dta` (the deviant pre-2026-07-21 panel,
  see DISCREPANCIES D-016), and genuine junk (`ff_factors_daily.csv`,
  `denom_div.dta`, the `VAR_IN~4` / `var_inv_rate ...` filename mishaps).
