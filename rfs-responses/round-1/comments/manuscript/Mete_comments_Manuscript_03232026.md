# Mete's Comments on Manuscript (March 23, 2026)

Comments extracted from `Mete_comments_Manuscript_03232026.pdf`. Each comment is classified by theme, assessed for accuracy against the LaTeX source files, and accompanied by recommended actions.

---

## Theme 1: Typos and Grammar

### ~~Comment 1 — Name typo: "Ramodorai" → "Ramadorai" (Page 1, Title Page)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** Highlighted "Ramodorai" in the acknowledgments with comment: "Ramadorai."~~

~~**Assessment:** Valid. In `0_title_page.tex` (line 3), the acknowledgments list "Tarun Ramodorai." The correct spelling of the surname is "Ramadorai."~~

~~**Action:** In `0_title_page.tex` line 3, change "Tarun Ramodorai" to "Tarun Ramadorai."~~

---

### ~~Comment 2 — Grammar: "use" → "uses" (Page 8, Literature)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** Highlighted "use" in "Wittry (2020) use variation" with comment: "uses."~~

~~**Assessment:** Valid. In `2_literature.tex` (line 8), the sentence reads "Wittry (2020) use variation in mining reclamation liabilities across states." Since Wittry (2020) is a singular citation, the verb should be "uses."~~

~~**Action:** In `2_literature.tex` line 8, change "Wittry (2020) use" to "Wittry (2020) uses."~~

---

### ~~Comment 3 — Grammar: "show" → "shows" (Page 20, Main Results)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** Highlighted "show" in "Hennessy (2004) show that the standard investment regression" with comment: "shows."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 19), the sentence reads "Hennessy (2004) show that the standard investment regression must be modified as follows." Since Hennessy (2004) is a singular citation, the verb should be "shows." Note: Line 14 of the same file correctly uses "shows" for an earlier reference to the same paper; this occurrence on line 19 is the inconsistent one.~~

~~**Action:** In `5_main_results.tex` line 19, change "Hennessy (2004) show that" to "Hennessy (2004) shows that."~~

---

### ~~Comment 4 — Grammar: "are" → "is" (Page 27, Main Results / Credit Ratings)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** Highlighted "are" in "The interpretation of the coefficients γ_t and κ_t are unaffected by the normalization" with comment: "is."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 84), the subject is "The interpretation" (singular), so the verb should be "is unaffected."~~

~~**Action:** In `5_main_results.tex` line 84, change "are unaffected" to "is unaffected."~~

---

## Theme 2: Incorrect Variable Definition

### ~~Comment 5 — $\tilde{d}$ definition: "total assets" → "long-term liabilities" (Page 37, Appendix A)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** Highlighted "total assets" in the definition of $\tilde{d}$ with comment: "long-term liabilities."~~

~~**Assessment:** Valid and important. In `7_appendix.tex` (line 49), $\tilde{d}$ is defined as "the ratio of bond amount outstanding with gold clauses to total assets." This is incorrect—$\tilde{d}$ is the frozen (1930) version of $d$, which is defined as the ratio of gold-denominated long-term liabilities to total long-term liabilities (equation 1 in `4_data.tex`). The Appendix definition for $d$ on line 45 correctly says "long-term liabilities (LTL)," so the $\tilde{d}$ entry should match.~~

~~**Action:** In `7_appendix.tex` line 49, change "to total assets" to "to long-term liabilities (LTL)."~~

---

## Theme 3: Table Notes Follow-Up

### ~~Comment 6 — Table 4: Normalization note follow-up (Page 48, Table 4)~~

~~**Annotation type:** Highlight with comment~~

~~**What Mete flagged:** Highlighted text in the Table 4 notes near "normalized by total assets" with comment: "from last revision: 'these are normalized by fixed capital in 1930, the Appendix description is correct. Maybe no need to mention 1930 here.'"~~

~~**Assessment:** This is a follow-up on Comment 5 from the March 16 batch. The Table 4 notes state that Profits and Cash are "both normalized by total assets," while the Appendix A definition (`7_appendix.tex` line 53) states these are "normalized by fixed capital in 1930." The Appendix is correct. The Table 4 notes were updated to say "both normalized by fixed capital in 1930." No other tables had this incorrect normalization description—Table IA.15 (`13_dividend_additional.tex`) and the Appendix already correctly referenced "fixed capital in 1930."~~

~~**Action:** In `4_other_outcomes.tex` line 54, change "(both normalized by total assets)" to "(both normalized by fixed capital in 1930)."~~

---

## Summary of Actions

| # | Section | File(s) | Type | Effort |
|---|---------|---------|------|--------|
| 1 | Title Page | `0_title_page.tex` | Name typo: "Ramodorai" → "Ramadorai" | Quick fix |
| 2 | Literature | `2_literature.tex` | Grammar: "use" → "uses" | Quick fix |
| 3 | Main Results | `5_main_results.tex` | Grammar: "show" → "shows" | Quick fix |
| 4 | Main Results | `5_main_results.tex` | Grammar: "are" → "is" | Quick fix |
| 5 | Appendix A | `7_appendix.tex` | Incorrect definition: "total assets" → "long-term liabilities" | Quick fix |
| 6 | Table 4 | `4_other_outcomes.tex` | Normalization: "total assets" → "fixed capital in 1930" | Quick fix |
