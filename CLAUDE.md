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
| `manuscript/` | Main LaTeX paper (compiled via `pdflatex Manuscript.tex`) |
| `manuscript/sections/` | One `.tex` file per section |
| `manuscript/tables/` | Body and online-appendix tables |
| `manuscript/figures/` | Body and online-appendix figures |
| `rfs-responses/round-2/` | Round-2 referee responses (R2, R6, editor) |
| `code/refactor/` | Python replication of Stata pipeline (pyfixest) |
| `code/mete/` | Original Stata `.do` files |
| `data/` | Panel data (not versioned); key file: `A4_merged.dta` |
| `output/` | Generated tables and figures (versioned) |

---

## How to run things

### Python pipeline (tables and figures)

```bash
cd code/refactor
python run.py
```

This regenerates all body and IA tables into `code/refactor/output/` and also
copies them to `manuscript/tables/`. Run this after any change to the Python
table builders.

To control whether pyfixest uses Stata's variance-covariance matrix:

```bash
USE_STATA_VCOV=1 python run.py   # use Stata vcov (default behaviour)
USE_STATA_VCOV=0 python run.py   # use pyfixest CGM fix instead
```

### Stata regressions (when needed for exact SEs)

Run do-files directly from the project root, e.g.:

```bash
cd /project7/splante/git/gold-clause-abrogation-and-investment
stata-mp -b do code/mete/A12_controls_indyear.do
```

Logs land in `logs/` (gitignored). Stata must be in PATH.

### Compiling the manuscript

```bash
cd manuscript
pdflatex Manuscript.tex
bibtex Manuscript
pdflatex Manuscript.tex
pdflatex Manuscript.tex
```

### Compiling a referee response PDF

Each referee response is a standalone document. To compile R6:

```bash
cd rfs-responses/round-2/referee-responses/r6
pdflatex response-r6.tex
bibtex response-r6
pdflatex response-r6.tex
pdflatex response-r6.tex
```

Same pattern for `r2/response-r2.tex` and `editor/response-editor.tex`.

---

## Table and figure mapping (post-round-2 renumbering)

The tables were renumbered between round 1 and round 2. When reading old notes
or Opus reviews, check which version is being referenced.

| Manuscript label | Contents | Old number |
|---|---|---|
| Table 1 | Summary statistics | — (new) |
| Table 2 | Event study | — (new) |
| Table 3 | Firm characteristics by gold exposure | — (new) |
| Table 4 | Main investment panel (baseline) | Table 1 |
| Table 5 | Dividends | Table 2 |
| Table 6 | Other outcomes | Table 3 |
| Table 7 | Controls robustness | Table 6 |
| Table 8 | Heterogeneous effects | Table 7 |

Online appendix tables follow `IA.N` numbering, sequenced by their `\input`
order in `manuscript/sections/11_online_appendix.tex`:

| IA label | LaTeX file | Contents |
|---|---|---|
| IA.17 | `15_controls_extra.tex` | Stock market controls |
| IA.18 | `16_aggregate_heterogeneous.tex` | Heterogeneous effects |
| IA.19 | `17_controls_indyear.tex` | Cols 2-10 of Table 7 with industry×year FEs |

---

## Referee response structure

Round-2 responses live under `rfs-responses/round-2/referee-responses/`.

```
referee-responses/
  r2/
    response-r2.tex          ← root document (inputs preamble + sections)
    sections/
      comment-1.tex          ← event study figures and table
      comment-2.tex          ← Liberty bond sentence + NYT citation
  r6/
    response-r6.tex
    sections/
      comment-1.tex          ← preferred share concern
      comment-2.tex          ← industry×year FEs in cols 2-10
      comment-3.tex          ← parallel trends / 1930 coefficient
      comment-4.tex          ← repurchases
      cover-letter-comment.tex ← cover letter point
  editor/
    response-editor.tex
```

All three root documents `\input{../../preamble.tex}` and
`\input{../../revision-summary.tex}` for shared boilerplate.

---

## Known gotchas

1. **Stata crash (rc=-11) for portfolio decile + sic2_year specs.** When the
   Python vcov framework tries to call Stata for these combinations it crashes.
   Work around by writing a standalone do-file (see `A12_controls_indyear.do`)
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

5. **Table number collisions in the online appendix.** The IA table counter
   resets to 1 at `\setcounter{table}{0}` in `11_online_appendix.tex`. Table
   numbers are determined by the order of `\input` calls in that file. Inserting
   a new table in the middle renumbers all subsequent tables. Always check the
   full appendix sequence after adding a table.

6. **`output/` is versioned; `data/` is not.** Never commit anything under
   `data/`. Generated artefacts (CSVs, PDFs, LaTeX tables) go in `output/` or
   `manuscript/tables/` and are committed.

7. **Collinearity in all_controls_linear + sic2_year.** The after-period
   interactions of all 8 characteristics are dropped for perfect collinearity
   when both firm FEs and industry-year FEs are absorbed simultaneously
   (partition-of-unity property: the four period indicators sum to 1, so after
   firm-FE demeaning the after-period column is linearly determined). This is
   expected behaviour, not a bug.

---

## Key conventions

- Two-way cluster SEs: firm (`permno`) and year
- The Python refactor matches Stata reghdfe coefficients; SEs use CGM fix or
  Stata vcov depending on `USE_STATA_VCOV` env var
- Regressions that require exact Stata SEs use `code/mete/` do-files directly
- Do not edit files under `manuscript/tables/` directly; they are generated by
  `code/refactor/tables/` scripts

---

## What NOT to do

- Do not use `eststo` or `esttab` — not installed.
- Do not commit files under `data/`.
- Do not edit generated `.tex` table files directly; edit the Python builder
  that generates them and re-run.
- Do not assume table numbers are stable; always verify against the `\input`
  order in `11_online_appendix.tex` and the main `Manuscript.tex`.
- Do not use old table numbers (Table 1 = main, Table 6 = controls) in referee
  responses; the current numbering is Table 4 = main, Table 7 = controls.
- Do not reference IA.17 for the industry-year robustness table; it is IA.19.
