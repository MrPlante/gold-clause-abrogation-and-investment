# Mete's Comments on Manuscript (March 16, 2026)

Comments extracted from `Mete_comments_Manuscript__03162026.pdf`. Each comment is classified by theme, assessed for accuracy against the LaTeX source files, and accompanied by recommended actions.

---

## Theme 1: Typos and Grammar

### ~~Comment 1 — Missing space before citation (Page 12, Historical Background)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "missing space" — the text reads `gold"(Hoover, 1932)` with no space between the closing quotation mark and the parenthetical citation.~~

~~**Assessment:** Correct. In `3_historical_background.tex` (line 33), the code reads `gold''\citep{Hoover1932}`. Since `\citep` does not automatically insert a leading space, the rendered output produces `gold"(Hoover, 1932)` with no space.~~

~~**Action:** Insert a space before `\citep`: change `gold''\citep{Hoover1932}` to `gold'' \citep{Hoover1932}` in `3_historical_background.tex` line 33.~~

---

### ~~Comment 2 — Grammar: missing "which" (Page 29, Main Results / Credit Ratings)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "which is?" — the sentence reads "The negative signs suggest that the marginal effect of gold exposure on dividends diminishes with the degree of exposure is inconsistent with the prediction that low-rated firms should exhibit a stronger response for a given degree of exposure."~~

~~**Assessment:** Correct. The sentence is ungrammatical — it is missing a relative pronoun or conjunction to connect the two clauses.~~

~~**Action:** In `5_main_results.tex` (around line 93–94), change "diminishes with the degree of exposure is inconsistent" to "diminishes with the degree of exposure, which is inconsistent" (relative clause).~~

---

### ~~Comment 3 — "Gold clauses" should be "Gold clause" in IA table title (Page 73, Table IA.17)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "clause" — the table title reads "Gold clauses exposure and investment with return-based controls" with an incorrect plural "clauses."~~

~~**Assessment:** Correct. All other tables in the manuscript use the singular "Gold clause exposure." In `15_controls_extra.tex` (line 2), the caption reads `Gold clauses exposure and investment with return-based controls`.~~

~~**Action:** Change "Gold clauses exposure" to "Gold clause exposure" in the `\caption` of `15_controls_extra.tex` line 2.~~

---

## Theme 2: Unreferenced Figure

### ~~Comment 4 — Figure 2 not referenced in text (Page 42, Figures)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "This figure is not referred to in the text. I am okay with what you decide whether we drop it or mention it somewhere."~~

~~**Assessment:** Correct. Figure 2 ("Gold price and inflation in 1933 and 1934") has label `\label{fig:F3}` in `9_figures.tex` (line 23), and `\ref{fig:F3}` does not appear anywhere in the manuscript text sections.~~

~~**Action:** Added a reference to Figure 2 in `3_historical_background.tex` line 51, where the text discusses both the gold price ($35/oz) and modest inflation — the two variables the figure plots.~~

---

## Theme 3: Table Notes Issues

### ~~Comment 5 — Table 4 normalization note (Page 48, Table 4)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "these are normalized by fixed capital in 1930, the Appendix description is correct. Maybe no need to mention 1930 here."~~

~~**Assessment:** The table note in `4_other_outcomes.tex` (line 54–55) states that Payout, Dividend, and Net rep. are "all normalized by the book value of common stock." Mete is noting that the actual normalization uses a denominator fixed at 1930 values. The Appendix A description is consistent with this. Mete suggests that mentioning "in 1930" explicitly in the table note may be unnecessary if the Appendix already provides the detail.~~

~~**Action:** No change. Keeping the table note as-is; the Appendix provides sufficient detail.~~

---

### ~~Comment 6 — Table 6 notes incorrectly claim industry-year FEs in Columns 3–10 (Page 50, Table 6)~~

~~**Annotation type:** StrikeOut + Highlight with comment~~

~~**What Mete flagged:** Mete struck out content in the table and highlighted text in the notes with the comment "No."~~

~~**Assessment:** The table notes in `6_controls.tex` state that Columns 3–10 include decile dummies "along with industry-year fixed effects." However, the table body shows `Industry-year FE: No` for Columns 2–10 (only Column 1 has `Yes`). This is a contradiction between the notes and the table contents.~~

~~**Action:** Removed "along with industry-year fixed effects" from the Columns 3–10 description in the table notes. Also changed Year FE for Column 1 from Yes to No (since Column 1 uses industry-year FE, which subsumes year FE).~~

---

## Theme 4: $d$ vs. $\tilde{d}$ Consistency

### ~~Comment 7 — Table IA.12 notes use $d$ instead of $\tilde{d}$ (Page 68, Table IA.12)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "dtilde" — the table notes read "gold clause exposure $d$, and year $\times$ $d$ interactions" but should use $\tilde{d}$.~~

~~**Assessment:** Correct. In `10_repayers_balanced.tex` (line 55), the notes use `$d$` while the table body uses `\ensuremath{\tilde{d}}`. The notes should be consistent with the table body and with the rest of the manuscript.~~

~~**Action:** Changed `$d$` to `$\tilde{d}$` and `$d$ interactions` to `$\tilde{d}$ interactions` in the table notes of `10_repayers_balanced.tex`.~~

---

## Theme 5: Incorrect Cross-References

### ~~Comment 8 — Table IA.14 notes reference wrong table (Page 70, Table IA.14)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "Table 4?" — the table notes read "Column 1 replicates the annual dividend specification (Table 5, column 2)" but Mete believes the reference should be to Table 4.~~

~~**Assessment:** Correct. Table 4 ("Gold clause exposure and other outcomes") contains the annual dividend specification in Column 2. Table 5 ("Credit ratings and debt overhang") contains a different specification. In `12_quarterly_div.tex` (line 54), the note should reference Table 4, not Table 5.~~

~~**Action:** Changed hardcoded "Table 5" to `\ref{tab:other_outcomes}` in `12_quarterly_div.tex`, which resolves to Table 4.~~

---

## Summary of Actions

| # | File | Type | Effort |
|---|------|------|--------|
| 1 | `3_historical_background.tex` | Add space before `\citep{Hoover1932}` | Quick fix |
| 2 | `5_main_results.tex` | Fix grammar: add "which" or restructure sentence | Quick fix |
| 3 | `15_controls_extra.tex` | Change "clauses" to "clause" in table title | Quick fix |
| 4 | `9_figures.tex` / text sections | Reference Figure 2 in text or remove it | Requires discussion |
| 5 | `4_other_outcomes.tex` | Review normalization note (1930 mention) | Requires discussion |
| 6 | `6_controls.tex` | Fix note re: industry-year FEs in Cols 3–10 | Requires verification |
| 7 | `10_repayers_balanced.tex` | Change $d$ to $\tilde{d}$ in table notes | Quick fix |
| 8 | `12_quarterly_div.tex` | Change "Table 5" to "Table 4" in notes | Quick fix |
