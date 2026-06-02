# Mete's Comments on Draft (March 4, 2026)

Comments extracted from `Mete_comments_03042026.pdf`. Each comment is classified by theme, assessed for accuracy against the LaTeX source files, and accompanied by recommended actions.

---

## Theme 1: Citation Formatting

### ~~Comment 1 — Double parentheses in citation (Page 4, Introduction)~~ DONE

~~**Annotation type:** StrikeOut~~

~~**What Mete flagged:** The citation `(e.g., (Giroud et al., 2011; Wittry, 2020; Bennett et al., 2025))` has double parentheses. Mete struck out the outer opening `(G` and closing `))`.~~

~~**Assessment:** Correct. In `1_intro.tex` (line 18), the code reads `(e.g., \citep{Giroud2012, Wittry2018, Bennett2025})`. Since `\citep` already wraps its output in parentheses, the surrounding `(...)` produces double nesting.~~

~~**Action:** Replace with `\citep[e.g.,][]{Giroud2012, Wittry2018, Bennett2025}` to produce `(e.g., Giroud et al., 2011; Wittry, 2020; Bennett et al., 2025)` with a single set of parentheses.~~

---

### ~~Comment 2 — Bernanke (1983) citation format (Page 6, Introduction)~~ DONE

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "Great Depression Bernanke (1983)" should be "(Bernanke, 1983)".~~

~~**Assessment:** Correct. In `1_intro.tex` (line 30), the code reads `\cite{Bernanke1983}`, which renders as an in-text citation ("Bernanke (1983)") rather than a parenthetical one. The sentence requires a parenthetical citation since "Bernanke" is not the grammatical subject.~~

~~**Action:** Change `\cite{Bernanke1983}` to `\citep{Bernanke1983}` in `1_intro.tex` line 30.~~

---

## Theme 2: Typos and Grammar

### ~~Comment 3 — Missing possessive apostrophe (Page 7, Literature)~~ DONE

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "firms inability" should be "firms' inability".~~

~~**Assessment:** Correct. In `2_literature.tex` (line 4), the text reads "firms inability to rollover maturing debt."~~

~~**Action:** Change "firms inability" to "firms' inability" in `2_literature.tex` line 4.~~

---

### ~~Comment 4 — Duplicate "term" (Page 16, Data)~~ DONE

~~**Annotation type:** StrikeOut~~

~~**What Mete flagged:** Struck out "m term l" in "long-term term liabilities", flagging the duplicate word "term".~~

~~**Assessment:** Correct. In `4_data.tex` (line 12), the text reads "firms without long-term term liabilities".~~

~~**Action:** Change "long-term term liabilities" to "long-term liabilities" in `4_data.tex` line 12.~~

---

### ~~Comment 5 — "Beside" vs. "Besides" (Page 16, Data)~~ DONE

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "Beside the main variables" should be "Besides".~~

~~**Assessment:** Correct. "Besides" (with the trailing "s") is the correct adverb meaning "in addition to." In `4_data.tex` (line 14), the text reads "Beside the main variables described above".~~

~~**Action:** Change "Beside" to "Besides" in `4_data.tex` line 14.~~

---

### ~~Comment 6 — Double "s" in table notes (Page 49, Table 5)~~ DONE

~~**Annotation type:** StrikeOut~~

~~**What Mete flagged:** "interaction termss" has a double "s" in the notes of Table 5 (credit ratings).~~

~~**Assessment:** Correct. In `5_credit_ratings.tex` (line 36), the note reads "Only 1933 and 1934 interaction termss are reported".~~

~~**Action:** Change "termss" to "terms" in `5_credit_ratings.tex` line 36.~~

---

## Theme 3: Incorrect Cross-References

### ~~Comment 7 — Figure 3 note references wrong column (Page 43, Figure 3)~~ DONE

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** The figure note says "Column 3 of Table 3" but Mete says it should be "2".~~

~~**Assessment:** Correct. The main text in `5_main_results.tex` (line 40) states: "Figure 3 plots the yearly interaction coefficients reported in column 2 of Table 3." However, the figure note in `9_figures.tex` (line 39) reads "Column 3 of Table \ref{tab:inv_main}."~~

~~**Action:** Change "Column 3" to "Column 2" in `9_figures.tex` line 39. Also, the figure note uses "$d$" where it should use "$\tilde{d}$" (consistent with the Theme 4 issue below).~~

---

### ~~Comment 8 — Footnote 12 references same table twice (Page 17, Data)~~ DONE

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** The PDF shows "Tables IA.4 and IA.4" — Mete asks whether this should be "IA.3 and IA.4".~~

~~**Assessment:** Correct. In `4_data.tex` (line 18), the footnote references `\ref{tabapp:summary_I_1}` twice (the same label), producing "IA.4 and IA.4." The first reference should be `\ref{tabapp:summary_I_0}` (which resolves to IA.3, the table for $\tilde{d} > 0$ firms).~~

~~**Action:** Change the first `\ref{tabapp:summary_I_1}` to `\ref{tabapp:summary_I_0}` in the footnote on line 18 of `4_data.tex`, so it reads "Tables IA.3 and IA.4".~~

---

## Theme 4: $d$ vs. $\tilde{d}$ Consistency

This is the most pervasive issue Mete identified. Multiple places in the manuscript and Internet Appendix use $d_{j,t}$ (the contemporaneous exposure measure) when the analysis actually uses $\tilde{d}_{j,t}$ (the 1930-frozen measure). Several related comments address this.

### ~~Comment 9 — Footnote 12 uses $d$ instead of $\tilde{d}$ (Page 17, Data)~~ DONE

~~**Annotation type:** Highlight with comment (multiple highlights on the same footnote)~~

~~**What Mete flagged:** Three overlapping highlights on footnote 12, noting: (a) "I think these tables are about dtilde right now, not d. We recently made d versions of these"; (b) "These tables are also based on dtilde, not d. Probably dtilde needs to be defined earlier"; (c) "We did not do any analysis based on d, so all these tables are based on dtilde. Some other IA tables also still say d, e.g. IA.8."~~

~~**Assessment:** Correct. In `4_data.tex` (line 18), footnote 12 consistently references $d_{j,t}$ (e.g., "$d_{j,t} > 0$ and $d_{j,t} = 0$ firms"), but the IA tables it references (IA.3 through IA.6) are all based on $\tilde{d}_{j,t}$, as confirmed by their captions and notes. The footnote should use $\tilde{d}_{j,t}$ to match the tables. One exception: IA.7 (correlations) does use $d$, which is correct since it reports correlations of the contemporaneous measure.~~

~~**Action:** In `4_data.tex` footnote 12 (line 18):~~
~~- Change all instances of `$d_{j,t}$` to `$\tilde{d}_{j,t}$` except for the reference to IA.7 (correlations), which correctly uses $d_{j,t}$.~~
~~- Alternatively, if new $d$-based versions of IA.3-IA.6 have been created, consider referencing those instead.~~
~~- Additionally, consider defining $\tilde{d}_{j,t}$ earlier in the Data section (it is currently introduced later, in the paragraph around line 26), or restructure the section so the footnote appears after $\tilde{d}$ is defined.~~

---

### ~~Comment 10 — IA Table 8 (credit ratings, full) uses $d$ instead of $\tilde{d}$ (Page 17 / IA)~~ DONE

~~**Annotation type:** Part of the broader comment on footnote 12~~

~~**What Mete flagged:** "Some other IA tables also still say d, e.g. IA.8."~~

~~**Assessment:** Correct. In `7_credit_ratings_full_table.tex` (line 31), the table note says "with $d$ where Before is the omitted category" and all variable labels use `\ensuremath{d}` and `\ensuremath{\times d}`. However, the body Table 5 (`5_credit_ratings.tex`) correctly uses $\tilde{d}$ throughout. The IA table should match.~~

~~**Action:** Update `7_credit_ratings_full_table.tex` to use $\tilde{d}$ in the table notes and variable labels, consistent with the body Table 5.~~

---

### ~~Comment 11 — Table 6 (controls) uses $d$ on 1934 row (Page 50, Table 6)~~ DONE

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** A single "$d$" should be "$\tilde{d}$" (dtilde).~~

~~**Assessment:** Correct. In `6_controls.tex` (line 21), the 1934 interaction row reads `\ensuremath{\text{1934} \times d}`, while the 1933 row (line 19) correctly reads `\ensuremath{\text{1933} \times \tilde{d}}` and the After row (line 23) also correctly uses `\tilde{d}`.~~

~~**Action:** Change `\ensuremath{\text{1934} \times d}` to `\ensuremath{\text{1934} \times \tilde{d}}` in `6_controls.tex` line 21.~~

---

### ~~Comment 12 — Figure 3 note uses $d$ instead of $\tilde{d}$ (Page 43, Figure 3)~~ DONE

~~**Annotation type:** (Related to Comment 7 above)~~

~~**Assessment:** The figure note in `9_figures.tex` (line 39) says "$d$ interacted with Year." Since the regression uses $\tilde{d}$, this should be updated.~~

~~**Action:** Change "$d$" to "$\tilde{d}$" in the Figure 3 note in `9_figures.tex` line 39.~~

---

## Theme 5: Substantive / Clarification Issues

### ~~Comment 13 — Clarify data collection period for security-level gold clause information (Page 16, Data)~~ DONE

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "Do we say anywhere that we collected this information from 1930 to 1935, and the numbers from before 1930 are book value of corporate bonds."~~

~~**Assessment:** Valid concern. The current text in `4_data.tex` (line 12) says "we collect individual security-level information on the presence of the gold clause" but does not specify the period over which security-level data were collected (1930-1935) or clarify that pre-1930 gold clause exposure is approximated using book value of corporate bonds. Neither does Appendix A (`7_appendix.tex`), which defines $d$ simply as "the ratio of bond amount outstanding with gold clauses to long-term liabilities."~~

~~**Action:** Add a clarification in `4_data.tex` (around line 12) or in Appendix A (`7_appendix.tex`) explaining (a) that security-level gold clause information was collected for the period 1930-1935, and (b) how pre-1930 exposure is measured (e.g., using book value of corporate bonds as a proxy).~~

---

### ~~Comment 14 — Payout denominator is fixed at 1930 value (Page 25, Payouts section)~~ DONE

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "The denominator is fixed at its 1930 value (or the first available year after 1930 if 1930 is not available). We can mention it in the Appendix A too."~~

~~**Assessment:** Valid concern. The formula in `5_main_results.tex` (lines 60-61) shows the denominator as "Book value of common stocks$_{j,t-1}$", which implies a time-varying denominator. If the actual implementation uses a fixed 1930 value, the formula and Appendix A should be corrected to match.~~

~~**Action:**~~
~~1. In `5_main_results.tex` (line 61), update the formula denominator to reflect the 1930 value (e.g., "Book value of common stocks$_{j,1930}$" or an appropriate notation).~~
~~2. In `7_appendix.tex`, update the description of "Payout/common stock" to specify that the denominator is fixed at the 1930 value (or the first available year after 1930).~~

---

### ~~Comment 15 — Reorder IA tables to match text order (Page 16, Data)~~ DONE

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** "maybe put the tables in IA in the order they are mentioned in the text? It is a bit hard to follow."~~

~~**Assessment:** Valid suggestion. The current IA table order in `11_online_appendix.tex` is: IA.1 (sum stats by $\tilde{d}$), IA.2 (full sample), IA.3 ($\tilde{d}>0$ firms), IA.4 ($\tilde{d}=0$ firms), IA.5 (low $\tilde{d}$), IA.6 (high $\tilde{d}$), IA.7 (correlations), IA.8 (credit ratings full), IA.9-17 (others). This ordering may not match the order in which the tables are first referenced in the main text. Reordering the IA tables to align with the order of first mention would improve readability.~~

~~**Action:** Review the order in which each IA table is first cited in the main text and reorder the `\input` statements in `11_online_appendix.tex` accordingly. (Note: this will change all IA table numbers, so all cross-references will need to be verified after reordering.)~~

---

### ~~Comment 16 — Empty sticky note (Page 17)~~ DONE

~~**Annotation type:** Text (sticky note), no content~~

~~**Assessment:** This appears to be a marker placed near footnote 12, likely related to the $d$ vs. $\tilde{d}$ comments (Comments 8-10) on the same page. No separate action is required.~~

~~**Action:** None beyond addressing Comments 8-10 above.~~

---

## Summary of Actions

| # | File | Type | Effort |
|---|------|------|--------|
| 1 | `1_intro.tex` | Fix double parentheses in citation | Quick fix |
| 2 | `1_intro.tex` | Change `\cite` to `\citep` for Bernanke (1983) | Quick fix |
| 3 | `2_literature.tex` | Add possessive apostrophe ("firms'") | Quick fix |
| 4 | `4_data.tex` | Remove duplicate "term" | Quick fix |
| 5 | `4_data.tex` | Change "Beside" to "Besides" | Quick fix |
| 6 | `5_credit_ratings.tex` | Fix "termss" typo | Quick fix |
| 7 | `9_figures.tex` | Fix column reference (3 -> 2) and $d$ -> $\tilde{d}$ | Quick fix |
| 8 | `4_data.tex` | Fix duplicate table reference in footnote 12 | Quick fix |
| 9 | `4_data.tex` | Change $d$ to $\tilde{d}$ in footnote 12 | Moderate |
| 10 | `7_credit_ratings_full_table.tex` | Change $d$ to $\tilde{d}$ in labels and notes | Moderate |
| 11 | `6_controls.tex` | Fix $d$ -> $\tilde{d}$ on 1934 row | Quick fix |
| 12 | `4_data.tex`, `7_appendix.tex` | Clarify gold clause data collection period | Requires discussion |
| 13 | `5_main_results.tex`, `7_appendix.tex` | Fix payout denominator to reflect 1930 value | Requires discussion |
| 14 | `11_online_appendix.tex` | Reorder IA tables to match text order | Moderate (changes all IA numbers) |
