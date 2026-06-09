# Gold Clause Abrogation and Investment

Academic research project — RFS submission (currently in round-2 revision).

## Session handoff

At the end of any session where significant work was done, update the memory
system so the next session can pick up without re-deriving context:

1. **What changed** — update or create a `project` memory entry summarising
   what was completed (files changed, regressions run, responses written).
2. **What is outstanding** — note any items explicitly left unfinished
   (e.g. "cover letter response still to be written").
3. **Any decisions made** — record non-obvious choices (e.g. why a particular
   specification was preferred, why a table was renumbered) that would
   otherwise need to be re-argued next session.

Memory files live in:
`~/.claude/projects/-project7-splante-git-gold-clause-abrogation-and-investment/memory/`

## Project layout

| Path | Contents |
|---|---|
| `manuscript/` | Main LaTeX paper (compiled via `pdflatex Manuscript.tex`) |
| `manuscript/sections/` | One `.tex` file per section |
| `manuscript/tables/` | Body and online-appendix tables |
| `manuscript/figures/` | Body and online-appendix figures |
| `rfs-responses/round-2/` | Round-2 referee responses (R2, R6, editor) |
| `code/refactor/` | Python replication of Stata pipeline (pyfixest) |
| `code/mete/` | Original Stata `.do` files |
| `data/` | Panel data (not versioned); key file: `A4_merged.dta` |
| `output/` | Generated tables and figures (versioned) |

## Key conventions

- Tables are compiled by running `python run.py` from `code/refactor/`
- Regressions that require exact Stata SEs use `code/mete/` do-files directly
- Two-way cluster: firm (`permno`) and year
- The Python refactor matches Stata reghdfe coefficients; SEs use CGM fix or
  Stata vcov depending on `USE_STATA_VCOV` env var
