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

---

## Project layout

| Path | Contents |
|---|---|
| `manuscript/` | Main LaTeX paper (`main.tex`, compiled via `latexmk main.tex` into `gold-clause.pdf`) |
| `manuscript/sections/` | One `.tex` file per section |
| `manuscript/tables/` | Body and online-appendix tables |
| `manuscript/figures/` | Body and online-appendix figures |
| `rfs-responses/round-2/` | Round-2 referee responses (R2, R6, editor) |
| `pipeline/` | Data wrangling: `data/raw/` -> `data/processed/firm_year_panel.dta` (sources/ run in memory, merge.py writes the panel; + researchdb SQL build) |
| `analysis/` | Everything that produces paper numbers: table/figure builders (pyfixest), event study, Stata do-files |
| *(no `code/legacy/`)* | The original Stata pipeline (`mete/`) and retired scripts (`seb/`) were removed from the tree; retrieve with `git checkout d54b0c3 -- code/legacy` |
| `data/` | Panel data (not versioned; see `data/README.md`): sources in `raw/`, the panel at `processed/firm_year_panel.dta` (retired attic material now in `tmp/2026-07/21/attic/`) |

---

## How to run things

### Data pipeline and analysis stages

```bash
.venv/bin/python pipeline/run.py                    # raw -> firm_year_panel.dta
.venv/bin/python analysis/run.py --stage table4     # one manuscript object
.venv/bin/python analysis/run.py --stage all        # everything (skips FROZEN)
```

Stage names match manuscript labels (`table2`..`table8`, `ia1`..`ia19`,
`figures`, `eventstudy`); builders write directly into
`manuscript/tables/` and `manuscript/figures/`. `--stage all` skips any
stage in run.py's `FROZEN` set (guard for builders that do not reproduce
the shipped tables; see the D-022 audit scorecard in DISCREPANCIES.md).
Run any builder after changing it.

To control whether pyfixest uses Stata's variance-covariance matrix:

```bash
USE_STATA_VCOV=1 ...   # reghdfe vcov (default behaviour, auto)
USE_STATA_VCOV=0 ...   # pyfixest CGM fix instead
```

### Stata regressions (when needed for exact SEs)

Run do-files directly from the project root, e.g.:

```bash
cd /project7/splante/git/gold-clause-abrogation-and-investment
stata-mp -b do analysis/stata/ia19_controls_indyear.do
```

Logs land in `logs/` (gitignored). Stata must be in PATH.

### Compiling the manuscript

```bash
cd manuscript
latexmk main.tex
```

That is the whole recipe: `manuscript/.latexmkrc` runs the full
pdflatex/bibtex cycle, routes build artifacts (`.aux`, `.bbl`, `.log`, …)
to the gitignored `manuscript/build/`, and writes `gold-clause.pdf` at the
manuscript root (versioned; the jobname is set in the rc file).
`latexmk -C` cleans all generated files.

### Compiling a referee response PDF

Each referee response is a standalone document following the same template as
the manuscript: the root file is `main.tex`, a local `.latexmkrc` routes
artifacts to a gitignored `build/` and names the PDF (e.g. `response-r6.pdf`).
To compile R6:

```bash
cd rfs-responses/round-2/referee-responses/r6
latexmk main.tex
```

Same pattern for every document directory under
`rfs-responses/round-{1,2}/referee-responses/` (round 1: editor, r1, r2, r6;
round 2: editor, r2, r6).

### CRSP daily data

Firm-level CRSP daily returns live locally in **`data/raw/crsp_daily.dta`**
(with the names history in `data/raw/crsp_daily_names.dta`) — 2026-07-22
dumps of the `gold_claude.crsp` / `.crsp_names` tables on the research
Postgres server (database `splante` on `researchdb.ssc.wisc.edu`, Kerberos
auth). Any script that needs CRSP daily data must read the local dump —
do **not** query the DB in analysis code, do **not** query
`crsp.daily_stock_returns`, and do **not** download from WRDS. The DB is
touched only to regenerate the dumps when the underlying extract changes:

```bash
kinit   # needs a valid Kerberos ticket (klist to check)
psql "postgresql://splante%40ads.ssc.wisc.edu@researchdb.ssc.wisc.edu/splante?sslmode=require&gssencmode=require" \
  -c "\copy (select * from gold_claude.crsp order by permno, date) to 'crsp.csv' with csv header"
```

Contents: 1925-12-31 to 1945-12-31, all stocks (4,396,736 rows, 1,146 permnos).
Columns: `permno, date, ret, retx, prc, close, cap, vol, facprc, orddivamt,
nonorddivamt` (CIZ format; delisting returns already integrated into `ret`).
The DB tables themselves are built/rebuilt by
`pipeline/sql/build_gold_claude_crsp.sql` (run instructions in the file
header).

The companion table **`gold_claude.crsp_names`** (same build script) holds the
CRSP security-info/names history for those 1,146 permnos: the permno→permco
map plus issuer/security names, share class, ticker, SIC, exchange, and
delisting fields, one row per validity spell (`secinfostartdt`–`secinfoenddt`).
All 1,146 permnos map to 1,123 permcos; only 21 permcos have multiple share
classes listed.

### Event-study figures and tables

All return series, event figures (manuscript Figures 3–5, IA.2, IA.3), and
tables (Table 1, IA.20) are generated by a single pipeline
(`analysis/eventstudy/pipeline.py`):

```bash
python3 analysis/run.py --stage eventstudy
```

The stage is fully offline (part of `--stage all` since 2026-07-22): it
builds four daily portfolio series (VW market, equal-weighted d>0, d=0,
and d-weighted) from `data/raw/crsp_daily.dta` + `firm_year_panel.dta` and writes
outputs directly into `manuscript/figures/` and `manuscript/tables/`
(verified 2026-07-22 to reproduce the researchdb-backed outputs
byte-identically). Do **not** use
`data/returns/pf_returns.xls` — its `ewret_yes`/`ewret_no` columns are
swapped (verified 2026-07-16).

---

## Table and figure naming

Since 2026-07-22, file names match manuscript labels end to end: manuscript
Table N is `manuscript/tables/body/tableN_<topic>.tex`, built by
`analysis/tables/body/t0N_<topic>.py` via `--stage tableN`; Table IA.N is
`manuscript/tables/online-appendix/iaNN_<topic>.tex`, built by
`analysis/tables/appendix/iaNN_<topic>.py` via `--stage iaN`. Table 1 and
IA.20 are built by the `eventstudy` stage. IA numbers are still ASSIGNED by
`\input` order in `manuscript/sections/11_online_appendix.tex` — if a table
is inserted mid-sequence, later tables renumber and their files must be
renamed to keep the invariant.

When reading old notes (pre-round-2 or pre-2026-07-22), beware two retired
numbering systems: the round-1 manuscript numbering (old Table 1 = main
investment panel, now Table 4; old Table 6 = controls, now Table 7) and the
old off-by-one/two file numbering (`3_investment_reg.tex` was Table 4;
`15_controls_extra.tex` was IA.17).

---

## Referee response structure

Round-2 responses live under `rfs-responses/round-2/`.

```
round-2/
  shared/                    ← material shared by all response documents
    referee-reports/         ← the incoming reports being responded to
    preamble.tex
    revision-summary.tex
    gold-bib.bib
    jf.bst
  referee-responses/
    r2/
      main.tex               ← root document (inputs shared/ + sections)
      .latexmkrc             ← jobname response-r2 → compiles to response-r2.pdf
      sections/
        comment-1.tex        ← event study figures and table
        comment-2.tex        ← Liberty bond sentence + NYT citation
    r6/
      main.tex               ← compiles to response-r6.pdf
      sections/
        comment-1.tex        ← preferred share concern
        comment-2.tex        ← industry×year FEs in cols 2-10
        comment-3.tex        ← parallel trends / 1930 coefficient
        comment-4.tex        ← repurchases
        cover-letter-comment.tex ← cover letter point
    editor/
      main.tex               ← compiles to response-editor.pdf
```

All three root documents `\input{../../shared/preamble.tex}` and
`\input{../../shared/revision-summary.tex}` for shared boilerplate, and take
their bibliography from `shared/gold-bib.bib` with `shared/jf.bst`. Round-1
under `rfs-responses/round-1/` follows the same layout (with an extra `r1/`
response).

---

## Known gotchas

1. **Stata crash (rc=-11) for portfolio decile + sic2_year specs.** When the
   Python vcov framework tries to call Stata for these combinations it crashes.
   Work around by writing a standalone do-file (see `ia19_controls_indyear.do`)
   that outputs results to CSV, then read the CSV in Python/LaTeX.

2. **Python vcov always passes `absorb=("permno", "year")` to Stata.** In
   `lib/vcov.py`, `attach_cluster_vcov()` hardcodes the absorb argument
   regardless of the regression formula. Any spec using `sic2_year` FEs will
   get the wrong Stata vcov. Use `USE_STATA_VCOV=0` or a standalone do-file
   for those specs.

3. **`eststo`/`esttab` are not installed in the Stata environment.** Do not
   use them. Use `_b[term]`, `_se[term]`, and `file write` to export results.

4. **`latexdiff` is not installed on the server.** It is available as a Perl
   script from CTAN but requires manual installation. Do not attempt to run it
   in a pipeline step without checking first.

5. **IA numbers are assigned by `\input` order.** The IA table counter
   resets at `\setcounter{table}{0}` in `11_online_appendix.tex`, so
   inserting a table mid-sequence renumbers all subsequent tables — and,
   under the naming invariant, requires renaming their files (tex +
   builders + stages) to match. Always check the full appendix sequence
   after adding a table.

6. **Nothing under `data/` is ever committed.** Generated paper objects go
   directly into `manuscript/tables/` and `manuscript/figures/` and are
   committed (the former `output/` mirror tree was removed 2026-07-22; the
   IA.19 Stata CSV now lives at `analysis/stata/ia19_controls_indyear.csv`).

7. **Collinearity in all_controls_linear + sic2_year.** The after-period
   interactions of all 8 characteristics are dropped for perfect collinearity
   when both firm FEs and industry-year FEs are absorbed simultaneously
   (partition-of-unity property: the four period indicators sum to 1, so after
   firm-FE demeaning the after-period column is linearly determined). This is
   expected behaviour, not a bug.

---

## Key conventions

- **Recompile after every change.** Any edit that affects a PDF (manuscript
  sections, response sections, shared/ files, or generators that write into
  `manuscript/`) must be followed by recompiling the affected document(s)
  before committing, and the fresh PDF goes into the same commit as the
  source change. Verify the compile actually ran (`cd` with an absolute
  path — the shell's working directory persists between commands and a
  failed `cd &&` chain silently skips the build).
- Two-way cluster SEs: firm (`permno`) and year
- The Python refactor matches Stata reghdfe coefficients; SEs use CGM fix or
  Stata vcov depending on `USE_STATA_VCOV` env var
- Regressions that require exact Stata SEs use `analysis/stata/` do-files
  directly (IA.19 = `ia19_controls_indyear.do`); the original Stata pipeline
  lives only in git history (`git checkout d54b0c3 -- code/legacy`)
- Do not edit files under `manuscript/tables/` directly; they are generated by
  `analysis/tables/` scripts

---

## What NOT to do

- Do not use `eststo` or `esttab` — not installed.
- Do not commit files under `data/`.
- Do not edit generated `.tex` table files directly; edit the Python builder
  that generates them and re-run.
- Do not assume table numbers are stable; they are assigned by `\input`
  order. File names carry the current labels — if you renumber, rename.
- Do not use round-1 table numbers (Table 1 = main, Table 6 = controls) in
  referee responses; currently Table 4 = main, Table 7 = controls.
- If a builder stops reproducing its shipped table, add its stage to
  run.py's `FROZEN` set (skipped by `--stage all`) and log it in
  DISCREPANCIES.md rather than committing mismatched output.
