# Sébastien's Comments on Manuscript (March 22, 2026)

Comments extracted from `Sebastien_comments_Manuscript_03222026.pdf`. Each comment is assessed against the LaTeX source files and accompanied by recommended actions. Comments are organized by manuscript section.

---

## Section 1: Introduction (Pages 3–4)

### ~~Comment 1 — Word choice: "than unexposed firms" (Page 3)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "than unexposed" with comment: "than a similar unexposed firm."~~

~~**Assessment:** Valid. In `1_intro.tex` (line 14), the sentence reads "had investment rates 6.0 and 4.1 percentage points lower in 1933 and 1934, respectively, than unexposed firms." Adding "similar" tightens the counterfactual framing (consistent with regression logic). Switching to singular "firm" is optional but acceptable.~~

~~**Action:** In `1_intro.tex` line 14, change "than unexposed firms" to "than a similar unexposed firm" (or "than similar unexposed firms" to keep plural).~~

---

### ~~Comment 2 — Word choice: "might explain" → "might otherwise explain" (Page 4)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "might explain" with comment: "otherwise."~~

~~**Assessment:** Valid. In `1_intro.tex` (line 20), the sentence reads "potential confounding factors that might explain our findings." Adding "otherwise" clarifies these are rival/alternative explanations, which is the intended meaning.~~

~~**Action:** In `1_intro.tex` line 20, change "might explain" to "might otherwise explain."~~

---

## Section 2: Literature (Page 8)

### ~~Comment 3 — Add "in modern times" for contrast (Page 8)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "and its effects on corporate policies" with comment: "In modern times. This offers a better contrast with respect to what we are doing."~~

~~**Assessment:** Valid. In `2_literature.tex` (line 7), the sentence discusses Bennett (2025) extending Hassan et al. (2019)'s textual methodology. Since the paragraph contrasts modern settings with the Depression-era setting, adding "in modern times" (or "in contemporary settings") after the citation reinforces that contrast.~~

~~**Action:** In `2_literature.tex` line 7, add "in modern times" or "in contemporary settings" to the sentence describing Bennett (2025), e.g., "and its effects on corporate policies in modern times."~~

---

## Section 3: Historical Background (Pages 10–14)

### ~~Comment 4 — Transition word: "Regardless" (Page 10)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "Regardless of the specific factors behind this pattern," with comment: "Improve. I am not sure that Regardless is the right word to use for the transition."~~

~~**Assessment:** Valid. In `3_historical_background.tex` (line 15), "Regardless" follows a discussion of why gold clause adoption differed across securities, which "remains unclear." "Regardless" can read as dismissive. Alternatives like "Whatever the reasons for this pattern," or "Independently of why adoption differed," fit more naturally.~~

~~**Action:** In `3_historical_background.tex` line 15, replace "Regardless of the specific factors behind this pattern," with a softer transition.~~

---

### ~~Comment 5 — Break into two sentences (Page 10)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "By the onset of the Great Depression, most major economies were on the gold standard, but the crisis soon forced many to abandon it. The United Kingdom led the way, ending" with comment: "Break into two sentences."~~

~~**Assessment:** Valid. In `3_historical_background.tex` (lines 20–21), the second sentence joins "led the way" with a long participial phrase. Splitting into two sentences improves readability.~~

~~**Action:** In `3_historical_background.tex` lines 20–21, split the sentence about the UK (e.g., "The United Kingdom led the way. It ended convertibility on September 21, 1931, after…").~~

---

### ~~Comment 6 — Cite Friedman and Schwartz for gold hoarding (Page 10)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "In the United States, Britain's exit from the standard prompted widespread concern that the dollar might be next, leading depositors to withdraw funds and hoard gold." with comment: "Cite Friedman and Schwarz, if appropriate. I am thinking probably adding a footnote."~~

~~**Assessment:** Valid. In `3_historical_background.tex` (line 22), the claim about depositor behavior after Britain's exit is sourced from Friedman and Schwartz (1963). The citation currently only appears later in the paragraph (for bank failures). A footnote citation here would strengthen the claim.~~

~~**Action:** In `3_historical_background.tex` line 22, add a `\citep{Friedman1963}` footnote after "hoard gold."~~

---

### ~~Comment 7 — Cite Friedman and Schwartz for discount rate (Page 10)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "The Federal Reserve raised its discount rate, which swiftly stemmed gold outflows." with comment: "Reference. Probably Friedman and Schwarz, again. I am thinking probably a footnote."~~

~~**Assessment:** Valid. In `3_historical_background.tex` (line 22–23), the discount rate increase is a well-documented event in Friedman and Schwartz. Adding a footnote citation supports the claim.~~

~~**Action:** In `3_historical_background.tex` line 22–23, add a `\citep{Friedman1963}` footnote for the discount rate claim. **Resolved together with Comment 6 via a single footnote.**~~

---

### ~~Comment 8 — Add footnote with exact bank failure numbers (Page 10)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "forcing hundreds of banks to close that month alone (Friedman and Schwartz, 1963)." with comment: "Add a footnote with exact numbers as well."~~

~~**Assessment:** Valid. In `3_historical_background.tex` (line 23), "hundreds" is vague. A footnote with specific numbers from Friedman and Schwartz (e.g., exact monthly failure counts) would be more rigorous.~~

~~**Action:** In `3_historical_background.tex` line 23, add a footnote with exact bank failure numbers from Friedman and Schwartz (1963). Verify the specific figures against the source.~~

---

### ~~Comment 9 — Cite Edwards for gold redeposits (Page 11)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "partially reassured markets and restored confidence. However, gold redeposits fell short of the administration's expectations." with comment: "Cite Edwards."~~

~~**Assessment:** Valid. In `3_historical_background.tex` (line 28), the claim about gold redeposits falling short is unsourced. Edwards (2018 or 2015, already in the bibliography) covers this episode.~~

~~**Action:** In `3_historical_background.tex` line 28, add `\citep{Edwards2018}` (or the relevant Edwards reference) after "expectations."~~

---

### ~~Comment 10 — Reformulate Figure 1 description (Page 12)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "against currencies still tied to gold, such as the French franc. Figure 1 shows this decline against sterling and the franc between December 31, 1930, and March 31, 1934." with comment: "Reformulate. Figure 1 plots the exchange rate between the sterling and the franc between those two dates. It makes the decline apparent."~~

~~**Assessment:** Valid. In `3_historical_background.tex` (line 32), the current wording is imprecise about what Figure 1 actually plots. The sentence should be reformulated to match the figure's content more precisely.~~

~~**Action:** In `3_historical_background.tex` line 32, reformulate the sentence describing Figure 1 to accurately describe what the figure plots (e.g., "Figure 1 plots the dollar exchange rate against sterling and the franc between December 31, 1930, and March 31, 1934, making the decline apparent.").~~

---

### ~~Comment 11 — Phrasing: "gold clause enforceability" (Page 13)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "to gold clause enforceability." with comment: "to the enforceability of gold clauses?"~~

~~**Assessment:** Valid. In `3_historical_background.tex` (line 36), "the enforceability of gold clauses" is slightly clearer than the noun stack "gold clause enforceability."~~

~~**Action:** In `3_historical_background.tex` line 36, change "gold clause enforceability" to "the enforceability of gold clauses."~~

---

### ~~Comment 12 — Split long sentence about legal challenges (Page 14)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "about firms' future liabilities. For nearly two years, legal challenges to the abrogation accumulated as cases worked their way through the courts, until the Supreme Court's 1935 ruling ultimately removed the risk of higher debt burdens by upholding the abrogation. Moreover," with comment: "Rework that sentence. I feel like it might need to be split into two?"~~

~~**Assessment:** Valid. In `3_historical_background.tex` (line 53), the long sentence packs timeline, mechanism, and outcome into one clause. Splitting improves readability.~~

~~**Action:** In `3_historical_background.tex` line 53, split into two sentences (e.g., "For nearly two years, legal challenges to the abrogation accumulated as cases worked their way through the courts. The Supreme Court's 1935 ruling ultimately removed the risk of higher debt burdens by upholding the abrogation.").~~

---

## Section 4: Data (Pages 16–19)

### ~~Comment 13 — Verify numbers match Table 1 (Page 16)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "Table 1 reports summary" with comment: "Make sure these numbers match the content of Table 1."~~

~~**Assessment:** Valid verification request. In `4_data.tex` (line 16), the narrative numbers describing Table 1 should be cross-checked against `tables/body/1_sum_stats_d.tex`. Preliminary check shows no mismatches, but a thorough review is warranted.~~

~~**Action:** Cross-check all summary statistics quoted in `4_data.tex` (lines 16–18) against Table 1. Confirm or correct any discrepancies.~~

---

### ~~Comment 14 — Redundant leverage comparison (Page 17)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "Exposed firms also maintain substantially higher leverage throughout the litigation period (book leverage of 51% vs. 28%; market leverage of 67% vs. 37%)." with comment: "Is that necessary? It feels a bit redundant and interrupt the flow with the next sentence. What do you think, AI?"~~

~~**Assessment:** The sentence adds cross-sectional leverage detail (Panel B of Table 1) that goes beyond the investment-decline comparison. It is informative but does break the flow between the investment discussion and the caveat about pre-existing differences. Could be tightened or merged.~~

~~**Action:** Consider condensing or moving this sentence to avoid interrupting the narrative flow. Alternatively, integrate it into the preceding paragraph about summary statistics.~~

---

### ~~Comment 15 — Flag pre-existing differences caveat (Page 17)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "However, the pre-existing differences between exposed and unexposed firms may be correlated with investment decisions." with comment: "We must be careful when interpreting this heterogeneity since pre-existing...."~~

~~**Assessment:** Valid. In `4_data.tex` (line 18), the caveat about pre-existing differences is already present but could be strengthened by explicitly noting that descriptive heterogeneity should not be interpreted causally.~~

~~**Action:** Consider adding a phrase such as "We must be careful when interpreting this descriptive heterogeneity, since pre-existing differences…" to make the caveat more prominent.~~

---

### ~~Comment 16 — Add "For example" (Page 17)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "exposure. If only financially" with comment: "This is an example, so maybe we should start with 'For example,'?"~~

~~**Assessment:** Reasonable but optional. In `4_data.tex` (line 20), the "If only financially unconstrained firms…" is a conditional scenario illustrating a potential confound. "For example" would signal this is an illustration, though the "If…" structure already implies conditionality.~~

~~**Action:** Optional. In `4_data.tex` line 20, consider adding "For example, if only financially…" to signal the illustrative nature.~~

---

### ~~Comment 17 — Add "outstanding" before "gold-denominated bonds" (Page 17)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "of gold-denominated bonds" with comment: "outstanding gold-denominated bonds."~~

~~**Assessment:** Valid. In `4_data.tex` (line 22), adding "outstanding" before "gold-denominated bonds" parallels usage elsewhere and avoids ambiguity (number of issues vs. par value).~~

~~**Action:** In `4_data.tex` line 22, change "gold-denominated bonds" to "outstanding gold-denominated bonds."~~

---

### ~~Comment 18 — Reorder "prior to the abrogation in 1933" (Page 18)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "to the abrogation in 1933." with comment: "prior to the 1933 abrogation."~~

~~**Assessment:** Valid. In `4_data.tex` (line 22), "prior to the 1933 abrogation" is slightly more compact and reads better than "prior to the abrogation in 1933."~~

~~**Action:** In `4_data.tex` line 22, change "prior to the abrogation in 1933" to "prior to the 1933 abrogation."~~

---

### ~~Comment 19 — Add "apparent" before "bipartisan" (Page 18)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "This bipartisan" with comment: "apparent."~~

~~**Assessment:** Valid. In `4_data.tex` (line 24), "This apparent bipartisan commitment" signals that the perceived consensus (rather than a verified fact) mattered for firm managers' expectations.~~

~~**Action:** In `4_data.tex` line 24, change "This bipartisan" to "This apparent bipartisan."~~

---

### ~~Comment 20 — Soften "had no political" → "had little to no political" (Page 18)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "had no political" with comment: "little to no."~~

~~**Assessment:** Valid. In `4_data.tex` (line 24), "little to no political support" is more defensible than the absolute "no political support" for a historical claim.~~

~~**Action:** In `4_data.tex` line 24, change "had no political" to "had little to no political."~~

---

### ~~Comment 21 — Improve $\tilde{d}$ definition paragraph (Page 18)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "Nonetheless, to address potential endogeneity from post-1931 adjustments in gold exposure, we construct a modified measure that fixes each firm's exposure at its 1930 level—the" with comment: "Improve."~~

~~**Assessment:** Valid. In `4_data.tex` (line 26), the sentence is functional but could be tightened (see also Comment 22 which covers the same paragraph).~~

~~**Action:** See Comment 22 below for the combined rewrite.~~

---

### ~~Comment 22 — Reword the $\tilde{d}$ definition paragraph (Page 18)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the full "Nonetheless, to address potential endogeneity…We denote" passage with comment: "Reword the whole thing, actually. I feel like the writing here is a bit clumsy."~~

~~**Assessment:** Valid. In `4_data.tex` (line 26), the paragraph repeats context from earlier (Britain's departure, 1930 timing) and the em-dash explanation is heavy. Subsumes Comment 21.~~

~~**Action:** In `4_data.tex` line 26, rewrite the paragraph more concisely. Reduce repetition of context already introduced, and streamline the motivation for the 1930 freeze.~~

---

### ~~Comment 23 — "formally defined" (Page 18)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "defined as:" with comment: "formally defined."~~

~~**Assessment:** Valid minor addition. In `4_data.tex` (line 26), "formally defined as:" lends appropriate weight to the equation that follows.~~

~~**Action:** In `4_data.tex` line 26, change "defined as:" to "formally defined as:".~~

---

### ~~Comment 24 — IA tables report wider range of statistics (Page 19)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "Internet Appendix Tables IA.4 and IA.5 report the same statistics" with comment: "These two tables actually report a wider range of statistics for...."~~

~~**Assessment:** Valid if the IA tables include more variables than Table 1. In `4_data.tex` (line 36), "the same statistics" may understate what those tables contain.~~

~~**Action:** In `4_data.tex` line 36, verify whether IA.4 and IA.5 report additional statistics beyond Table 1. If so, change "the same statistics" to "a broader set of statistics" or describe the additional content.~~

---

### ~~Comment 25 — Tighten description of IA.8 (Page 19)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "reports correlations between $\tilde{d}_{j,t}$ and the firm characteristics in Table 1" with comment: "and firm characteristics."~~

~~**Assessment:** Ambiguous. The sentence already mentions firm characteristics. Possibly the suggestion is to tighten the phrasing (e.g., "between $\tilde{d}_{j,t}$ and firm characteristics listed in Table 1"). Needs author judgment.~~

~~**Action:** In `4_data.tex` line 36, consider tightening the description of Table IA.8.~~

---

### ~~Comment 26 — Remove or specify correlation claim (Page 19)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "these correlations are statistically significant in the pre-1933 sample." with comment: "Remove, or be more specific. What do we learn from those correlation coefficients?"~~

~~**Assessment:** Valid. In `4_data.tex` (line 36), noting significance without direction or magnitude is thin. Either remove the claim, or specify what the correlations reveal (e.g., which characteristics are most strongly correlated).~~

~~**Action:** In `4_data.tex` line 36, either remove "these correlations are statistically significant in the pre-1933 sample" or expand with direction/magnitude of key correlations.~~

---

### ~~Comment 27 — "from" vs. "of" (Page 19)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "from" with comment: "of?"~~

~~**Assessment:** Debatable. "Endogeneity from [source]" is standard usage; "endogeneity of [adjustments]" shifts emphasis slightly. Not clearly an error either way.~~

~~**Action:** Optional. In `4_data.tex` line 26, consider whether "endogeneity of" reads better in context than "endogeneity from."~~

---

### ~~Comment 28 — "behavior" → "decisions" or "policy" (Page 19)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "behavior" with comment: "decisions or policy instead?"~~

~~**Assessment:** The word "behavior" does not appear in `4_data.tex`. The closest match is "investment decisions" (line 18). Either the highlight refers to a different file or a rendering artifact. If the word appears elsewhere, "decisions" or "policy" is indeed more precise in an academic context.~~

~~**Action:** Locate the exact occurrence of "behavior" in the manuscript and evaluate whether "decisions" or "policy" is more appropriate.~~

---

## Section 5: Main Results (Pages 19–33)

### ~~Comment 29 — Reformulate baseline equation introduction (Page 19)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "As a baseline, consider the standard investment regression relating investment to average Q:" with comment: "Reformulate."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 7), the sentence is functional but flat. A reformulation such as "To motivate our empirical strategy, we begin with the standard investment regression…" would provide clearer framing.~~

~~**Action:** In `5_main_results.tex` line 7, reformulate the introductory sentence before the baseline equation.~~

---

### ~~Comment 30 — Define subscripts j and t (Page 20)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "where $i_{j,t} = I_{j,t}/K_{j,t-1}$…" with comment: "Mention somewhere what j and t correspond to (firm and year)."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 10–12), the subscripts j and t are used without being defined. Standard practice requires "where j indexes firms and t indexes years."~~

~~**Action:** In `5_main_results.tex` line 12, add "where $j$ indexes firms and $t$ indexes years" upon first use of the subscripts.~~

---

### ~~Comment 31 — "increase in the severity" (Page 20)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "providing cross-sectional variation in the severity of debt overhang during the litigation period." with comment: "it's about an increase in the severity of the debt overhang issue."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 25), the current phrasing is imprecise. The abrogation increased the debt overhang wedge, and this increase varied cross-sectionally. The text should reflect "variation in the increase in severity."~~

~~**Action:** In `5_main_results.tex` line 25, change "variation in the severity of debt overhang" to "variation in the increase in the severity of debt overhang" or similar.~~

---

### ~~Comment 32 — Commas around "under certain conditions" (Page 20)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "under certain conditions" with comment: "Should we put that between commas?"~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 12), enclosing in commas ("who show that, under certain conditions, average $Q$ is a sufficient statistic") improves readability.~~

~~**Action:** In `5_main_results.tex` line 12, add commas around "under certain conditions."~~

---

### ~~Comment 33 — "precisely" → "the years when" (Page 21)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "precisely" with comment: "the years when."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 38), "the years when" is clearer and more informative than "precisely" (e.g., "only in 1933 and 1934—the years when the gold clause was litigated—").~~

~~**Action:** In `5_main_results.tex` line 38, replace "precisely when" with "the years when."~~

---

### ~~Comment 34 — Verify numbers match Table 3 (Page 21)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "6.0 percentage points in 1933 and 4.1 percentage" with comment: "Do these numbers match what's in the table?"~~

~~**Assessment:** Verified. Table 3 (Column 2) reports: 1933 × $\tilde{d}$: −0.060*** and 1934 × $\tilde{d}$: −0.041***. The text's "6.0 and 4.1 percentage points" matches exactly.~~

~~**Action:** No change needed. Numbers are confirmed correct.~~

---

### ~~Comment 35 — Tense: "was" vs. "is" (Page 22)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "the investment decline was" with comment: "decline we document (is or was?)---I am not sure of the right tense here. Based on what is around, I think it should be present, but please correct me if I am wrong, AI."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 38), the surrounding text uses present tense to describe regression results (e.g., "The interaction coefficient in 1935 is…"). For consistency, "the investment decline is concentrated" or "the investment decline we document is concentrated" is preferable.~~

~~**Action:** In `5_main_results.tex` line 38, change "the investment decline was concentrated" to "the investment decline we document is concentrated" (present tense for consistency).~~

---

### ~~Comment 36 — Prevent line break before negative coefficients (Page 24)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "The interaction coefficients for 1933 and 1934 are -0.058 and -0.043" with comment: "Make sure the negative coefficients doesn't get stuck on the previous line."~~

~~**Assessment:** Valid typographic concern. In `5_main_results.tex` (line 50), plain hyphens `-` could become separated from the numbers at a line break. Wrapping in math mode (`$-0.058$`) prevents this.~~

~~**Action:** In `5_main_results.tex` line 50, wrap negative numbers in math mode (e.g., `$-0.058$` and `$-0.043$`) to prevent orphaned minus signs.~~

---

### ~~Comment 37 — "statistically insignificant" → "not statistically significantly different from zero" (Page 24, 1st occurrence)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "positive and statistically insignificant" with comment: "not statistically significant from zero."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 52), "statistically insignificant" is informal. "Not statistically significantly different from zero" is the precise econometric phrasing.~~

~~**Action:** In `5_main_results.tex` line 52, change "positive and statistically insignificant" to "positive and not statistically significantly different from zero" (first occurrence).~~

---

### ~~Comment 38 — Same fix, second occurrence (Page 24)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "positive and statistically insignificant" (second occurrence) with comment: "Not statistically significantly different from zero."~~

~~**Assessment:** Same as Comment 37.~~

~~**Action:** In `5_main_results.tex` line 52, apply the same change to the second occurrence of "positive and statistically insignificant."~~

---

### ~~Comment 39 — Move "respectively" to end of sentence (Page 25)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "the interaction coefficients for 1933 and 1934 are 0.038 and 0.054, respectively, both statistically significant at the 5% and 1% levels." with comment: "Should 'respectively' be written at the end of the sentence?"~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 63), moving "respectively" to the end resolves ambiguity about whether it maps to the coefficients or the significance levels: "…are 0.038 and 0.054, both statistically significant at the 5% and 1% levels, respectively."~~

~~**Action:** In `5_main_results.tex` line 63, move "respectively" to the end of the sentence.~~

---

### ~~Comment 40 — Capitalize "Column" consistently (Page 25)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "(Column 2)" with comment: "Make sure that the reference to table columns are consistent throughout the manuscript. Should they be capitalized as it is here, or should they be in lower case as I believe I have seen elsewhere."~~

~~**Assessment:** Valid. The manuscript inconsistently capitalizes "Column" mid-sentence (e.g., "(Column 2)" on line 65 vs. "column 4" on line 67). A consistent convention should be adopted—common practice in economics is lowercase "column" mid-sentence.~~

~~**Action:** Standardize all mid-sentence column references to lowercase "column" throughout the manuscript.~~

---

### ~~Comment 41 — Transition: "The payout effect" → "This pattern in the payout effect" (Page 25)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "The payout effect likely reflects that…" with comment: "This pattern in the payout effect..."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 65), the transition from the repurchase/dividend decomposition to the explanation is abrupt. "This pattern in the payout effect likely reflects…" creates a smoother link.~~

~~**Action:** In `5_main_results.tex` line 65, change "The payout effect likely reflects" to "This pattern in the payout effect likely reflects."~~

---

### ~~Comment 42 — Lowercase "column" example (Page 26)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "column 4" with comment: "here is an example of lower case column reference."~~

~~**Assessment:** Reinforces Comment 40. No separate action needed—covered by the consistency standardization.~~

~~**Action:** No separate action. See Comment 40.~~

---

### ~~Comment 43 — Verify dividend discussion matches IA tables (Page 26)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the paragraph discussing IA dividend robustness checks with comment: "Make sure that everything said here is consistent with the content of the tables."~~

~~**Assessment:** Valid verification request. In `5_main_results.tex` (lines 69–71), the claims about columns 1–4 (payers vs. non-payers), columns 6–7 (alternative normalizations), and quarterly results should be cross-checked against IA Tables IA.15 and IA.14.~~

~~**Action:** Cross-check all claims in `5_main_results.tex` lines 69–71 against IA Tables IA.14 and IA.15 for consistency.~~

---

### ~~Comment 44 — Remove mechanical introductory sentence (Page 27)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "The first column of Table 5 reports our estimation results of equation (7) with net investment as the dependent variable." with comment: "We can remove this part, I believe."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 86), the sentence is mechanical—the section heading and preceding paragraphs already establish the context. Removing it tightens the prose.~~

~~**Action:** In `5_main_results.tex` line 86, remove the introductory sentence "The first column of Table 5 reports our estimation results of equation (7) with net investment as the dependent variable."~~

---

### ~~Comment 45 — Flag that Table 5 only reports 1933/1934 coefficients (Page 27)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the coefficient discussion with comment: "Important edit: we need to flag the fact that, to save space, Table 5 only reports the coefficients for 1933 and 1934. The regression results for all years are presented in Table IA.9."~~

~~**Assessment:** Valid and important. In `5_main_results.tex` (line 86), the reader should be informed that Table 5 is an abbreviated version, with the full results in Table IA.9.~~

~~**Action:** In `5_main_results.tex` near line 86, add a sentence: "To conserve space, Table 5 reports only the 1933 and 1934 interaction coefficients; the full set of year-by-year results is available in Internet Appendix Table IA.9."~~

---

### ~~Comment 46 — Remove "rather than targeting individual firms" (Page 30)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "rather than targeting individual firms" with comment: "I think we can remove that."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 105), "rather than targeting individual firms" is redundant given "operated primarily at the industry level."~~

~~**Action:** In `5_main_results.tex` line 105, remove "rather than targeting individual firms."~~

---

### ~~Comment 47 — Better explain how industry-year FEs address the concern (Page 30)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the industry-year FE explanation with comment: "By absorbing, ... (explain how these industry-year fixed effects work to alleviate the concern.)"~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 105), the sentence describes what industry-year FEs do but not how this addresses the New Deal concern. A restructured explanation would better connect the methodological choice to the specific concern.~~

~~**Action:** In `5_main_results.tex` line 105, restructure to: "By absorbing time-varying, industry-specific shocks, industry-year fixed effects ensure that the gold exposure coefficient is identified solely from within-industry variation, thereby ruling out confounding from policies that operate at the industry level."~~

---

### ~~Comment 48 — "industry-level" → "industry-specific" (Page 30)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "industry-level" with comment: "industry-specific?"~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 107), "industry-specific" is marginally more precise and consistent with "industry-specific shocks" used two lines earlier.~~

~~**Action:** In `5_main_results.tex` line 107, change "industry-level" to "industry-specific."~~

---

### ~~Comment 49 — Verify numbers match Table 6 (Page 31)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "-0.035, while the 1934 coefficient is -0.026" with comment: "make sure these numbers are in line with what's in the table."~~

~~**Assessment:** Verified. Table 6 (Column 2) reports: 1933 × $\tilde{d}$: −0.035** and 1934 × $\tilde{d}$: −0.026 (no significance star). The text matches and correctly notes that 1934 loses significance.~~

~~**Action:** No change needed. Numbers are confirmed correct.~~

---

### ~~Comment 50 — Verify numbers match Table 7 (Page 33)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "the aggregate net investment rate was −5.47% in 1933 and −2.47% in 1934…" and "−1.79 and −1.23 percentage points" with comment: "Make sure these numbers match what is in Table 7."~~

~~**Assessment:** Verified. Table 7 (Panel A, first row): 1933: −5.47, 1934: −2.47. Gold clause effect: −1.79 and −1.23. All numbers match.~~

~~**Action:** No change needed. Numbers are confirmed correct.~~

---

### ~~Comment 51 — "Roughly half" may overstate for 1934 (Page 33)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "roughly half of these firms' total divestment" with comment: "Do we see that in the table? Should be clear what the last column is about (time interval)."~~

~~**Assessment:** Partially valid. Table 7 Panel B: gold clause effect is −3.27 in 1933 (out of −6.59 total, ~50%) and −2.18 in 1934 (out of −3.01 total, ~72%). "Roughly half" is accurate for 1933 but understates the fraction for 1934. Also, the "After" column header should be clarified in the text.~~

~~**Action:** In `5_main_results.tex` line 130, revise to differentiate 1933 (~half) from 1934 (~three-quarters). Also ensure the main text clearly defines the "After" period (1935–1940).~~

---

### ~~Comment 52 — Better motivate heterogeneous aggregation (Page 33)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "Because the baseline aggregation assumes a uniform marginal effect of gold exposure across all firms…" with comment: "Reformulate to better highlight what is the issue we are concerned about here and how what we are doing in the Appendix can help address it."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 132), the sentence is matter-of-fact. It should more clearly articulate why uniform marginal effects are a limitation and how heterogeneity addresses it.~~

~~**Action:** In `5_main_results.tex` line 132, reformulate to explain the concern (e.g., if investment responses vary by firm type, the aggregate effect could be over- or under-estimated) and how heterogeneous marginal effects address it.~~

---

### ~~Comment 53 — Split long sentence about heterogeneity results (Page 33)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "Accounting for credit rating heterogeneity leaves the estimates largely unchanged, while allowing for size heterogeneity yields similar results in 1933 but a somewhat smaller aggregate effect in 1934…" with comment: "Reword, and maybe even split into two sentences."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 132), the sentence packs two distinct findings. Splitting improves readability.~~

~~**Action:** In `5_main_results.tex` line 132, split into: (1) "Accounting for credit rating heterogeneity leaves the estimates largely unchanged." (2) "Allowing for size heterogeneity yields similar results in 1933 but a somewhat smaller aggregate effect in 1934, reflecting the concentration of capital among large firms that experienced more moderate gold clause effects."~~

---

## Section 6: Conclusion (Pages 34–35)

### ~~Comment 54 — "remain intact" → "remain the same" (Page 34)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "remain intact." with comment: "the same."~~

~~**Assessment:** Valid. In `5_main_results.tex` (line 132), "remain intact" is somewhat heavy. "Remain the same" or "are unchanged" is simpler.~~

~~**Action:** Change "remain intact" to "remain the same" (note: this text is in `5_main_results.tex`, not `6_conclusion.tex`).~~

---

### ~~Comment 55 — "firms" → "issuers" (Page 34)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "these firms as well" with comment: "issuers instead of firms."~~

~~**Assessment:** Valid. The preceding text discusses public utilities and railroads as issuers of gold-denominated bonds. "Issuers" is more precise.~~

~~**Action:** Change "these firms as well" to "these issuers as well" (note: this text is in `5_main_results.tex`).~~

---

### ~~Comment 56 — "the" → "our" (Page 34)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "the" with comment: "our."~~

~~**Assessment:** Valid. In `6_conclusion.tex` (line 8), "the evidence" should be "our evidence" to signal ownership of the findings, standard in conclusions.~~

~~**Action:** In `6_conclusion.tex` line 8, change "the evidence" to "our evidence."~~

---

### ~~Comment 57 — Rewrite clumsy opening sentence (Page 34)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "In this paper, we study the impact of the 1933 abrogation of gold clauses, and the ensuing leverage uncertainty until the Supreme Court's 1935 decision, on real investment in 1933 and 1934." with comment: "This sentence is clumsy. Improve."~~

~~**Assessment:** Valid. In `6_conclusion.tex` (line 4), the main clause is interrupted by a long parenthetical separating "impact of" from "on real investment."~~

~~**Action:** In `6_conclusion.tex` line 4, restructure, e.g., "In this paper, we study how the 1933 abrogation of gold clauses—and the ensuing leverage uncertainty that persisted until the Supreme Court's 1935 decision—affected real investment in 1933 and 1934."~~

---

### ~~Comment 58 — Avoid linking too closely to Q in conclusion (Page 34)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "legal uncertainty about the real value of outstanding bond liabilities increased the share of average $Q$ attributable to bondholders' recovery, widening the wedge between marginal and average $Q$ and depressing investment." with comment: "Be careful about linking this too closely to Q. We should just talk about debt overhang at a high level here."~~

~~**Assessment:** Valid. In `6_conclusion.tex` (line 4), the conclusion should summarize at a high level rather than repeat the technical Q-based mechanism.~~

~~**Action:** In `6_conclusion.tex` line 4, reformulate at a higher level, e.g., "legal uncertainty about the real value of outstanding bond liabilities increased the expected recovery value of debtholders, discouraging equity-value-maximizing investment."~~

---

### ~~Comment 59 — Reword placebo test summary (Page 35)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "bank debt and preferred equity show no comparable patterns." with comment: "exposure to.... does not generate a similar pattern."~~

~~**Assessment:** Valid. In `6_conclusion.tex` (line 6), the current phrasing is vague. "Exposure to bank debt and preferred equity does not generate a similar pattern" clarifies that the placebo test replaces gold clause exposure with other components.~~

~~**Action:** In `6_conclusion.tex` line 6, change "bank debt and preferred equity show no comparable patterns" to "exposure to bank debt and preferred equity does not generate a similar pattern."~~

---

## Appendix A (Pages 36–37)

### ~~Comment 60 — "The" → "This" appendix (Page 36)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "The appendix presents" with comment: "This."~~

~~**Assessment:** Valid. In `7_appendix.tex` (line 17), "This appendix" is more precise since the sentence is within the appendix itself.~~

~~**Action:** In `7_appendix.tex` line 17, change "The appendix" to "This appendix."~~

---

### ~~Comment 61 — Add footnote about coverage (Page 36)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "in year $t$ usually reports annual balance sheet and income statement data from year $t-7$ to $t-1$." with comment: "add a footnote to say that for some firms the coverage only includes the last 2 years."~~

~~**Assessment:** Valid. In `7_appendix.tex` (line 17), a footnote clarifying that some firms have shorter coverage (e.g., only 2 years) is important for transparency.~~

~~**Action:** In `7_appendix.tex` line 17, add a `\footnote{For some firms, the coverage includes only the last two years.}` after "$t-1$."~~

---

### ~~Comment 62 — Capitalize "log" (Page 36)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "lo" (beginning of "log") with comment: "L."~~

~~**Assessment:** Debatable. In `7_appendix.tex` (line 27), lowercase "log" is standard mathematical notation. However, if the table headers use "Log(Assets)" as a variable name, capitalization for consistency might be appropriate. Confirm with co-authors.~~

~~**Action:** Optional. In `7_appendix.tex` line 27, consider capitalizing "Log(Assets)" if that is the convention used in the tables.~~

---

### ~~Comment 63 — Add $\tilde{d}$ and $\mathbb{I}_{\tilde{d}>0}$ definitions (Page 37)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the definitions of $d$ and $\mathbb{I}_{d>0}$ with comment: "Add data definition of $\tilde{d}$ and the indicator variable for $\tilde{d}$. Refer to the equation in the main text that contains the definition."~~

~~**Assessment:** Valid and important. In `7_appendix.tex` (lines 45–47), $\tilde{d}$ and $\mathbb{I}_{\tilde{d}>0}$ appear throughout the tables and regressions but are missing from the variable definitions appendix.~~

~~**Action:** In `7_appendix.tex` after line 47, add definitions for $\tilde{d}$ (referencing equation in the main text) and $\mathbb{I}_{\tilde{d}>0}$.~~

---

## Figures (Page 43)

### ~~Comment 64 — Improve Figure 3 notes for clarity (Page 43)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "This figure plots the yearly $\tilde{d}$ interaction coefficients and 95% confidence bands…" with comment: "This sentence could be improved for clarity. Interaction coefficients should appear earlier in the sentence."~~

~~**Assessment:** Valid. In `9_figures.tex` (line 39), front-loading the key concept improves readability, e.g., "This figure plots the year × $\tilde{d}$ interaction coefficients and 95% confidence bands from…"~~

~~**Action:** In `9_figures.tex` line 39, restructure the sentence to place "interaction coefficients" earlier.~~

---

### ~~Comment 65 — "year" → "year dummies" (Page 43)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "year" in the figure notes with comment: "year dummies."~~

~~**Assessment:** Valid. In `9_figures.tex` (line 39), "year dummy × $\tilde{d}$" is more precise than "year × $\tilde{d}$" since the interactions use year indicator variables.~~

~~**Action:** In `9_figures.tex` line 39, change "year $\times$ $\tilde{d}$" to "year dummy $\times$ $\tilde{d}$."~~

---

## Table Notes — Body Tables (Pages 45–51)

### ~~Comment 66 — Table 1: Fix explanation for $d = 0$ in Panel C (Page 45)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "In Panel C, all firms have $d = 0$ because gold clauses were abrogated in June 1933" with comment: "It is because the Supreme Court upheld the constitutionality of the abrogation, not because of the abrogation itself."~~

~~**Assessment:** Valid and substantively important. In `1_sum_stats_d.tex` (line 67), the reason $d = 0$ in Panel C (1935–1940) is that the Supreme Court upheld the abrogation in February 1935, not the abrogation itself. During 1933–1934 (Panel B), firms still had $d > 0$ because the constitutionality was uncertain.~~

~~**Action:** In `1_sum_stats_d.tex` line 67, revise to: "In Panel C, all firms have $d = 0$ because the Supreme Court upheld the constitutionality of the abrogation in February 1935."~~

---

### ~~Comment 67 — Table 2: Clarify "initial 157 firms" (Page 46)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "the number of firms with any bonds outstanding" with comment: "should say that it is the number of the initial 157 firms which still have at least one bond outstanding."~~

~~**Assessment:** Valid. In `2_bond_stats.tex` (line 23), the table tracks a fixed panel of 157 firms, so the notes should clarify that the count refers to how many of the original 157 still have bonds.~~

~~**Action:** In `2_bond_stats.tex` line 23, change "the number of firms with any bonds outstanding" to "the number of the initial 157 firms that still have at least one bond outstanding."~~

---

### ~~Comment 68 — Table 2: "number with" → "number of firms with" (Page 46)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "number with" with comment: "The number of firms with."~~

~~**Assessment:** Valid. In `2_bond_stats.tex` (line 23), "the number of firms with gold clause bonds" is clearer.~~

~~**Action:** In `2_bond_stats.tex` line 23, change "number with" to "number of firms with."~~

---

### ~~Comment 69 — Table 2: Clarify "total bond count" (Page 46)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "total bond count" with comment: "that the 157 firms have."~~

~~**Assessment:** Valid. In `2_bond_stats.tex` (line 23), "total bond count" should clarify it is restricted to the tracked panel.~~

~~**Action:** In `2_bond_stats.tex` line 23, change "total bond count" to "total number of bonds that the 157 firms have" or "total bond count among the 157 firms."~~

---

### ~~Comment 70 — Table 3: Clarify absence of $\tilde{d}$ in Column 1 (Page 47)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the table notes with comment: "Be more specific and clear about the absence of $\tilde{d}$ in the regressions. Provide equation number."~~

~~**Assessment:** Valid. In `3_investment_reg.tex` (line 55), the opening describes the general specification (Q + $\tilde{d}$ + interactions) but Column 1 does not include $\tilde{d}$. The notes should clarify which columns include which variables.~~

~~**Action:** In `3_investment_reg.tex` line 55, revise the notes to specify which columns include $\tilde{d}$ and reference the relevant equation numbers.~~

---

### ~~Comment 71 — Table 3: Add equation reference for Column 2 (Page 47)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "Column 2 reports our baseline debt overhang specification." with comment: "Provide equation."~~

~~**Assessment:** Valid. In `3_investment_reg.tex` (line 55), referencing the equation number helps the reader locate the specification.~~

~~**Action:** In `3_investment_reg.tex` line 55, add equation reference: "Column 2 reports our baseline debt overhang specification (equation (X))."~~

---

### ~~Comment 72 — Table 3: Reword Column 3 description (Page 47)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "Column 3 excludes firms with bonds maturing between 1931 and 1934." with comment: "Column reports the estimation results using a restricted sample where firms with bonds maturing between 1931 and 1934 are excluded."~~

~~**Assessment:** Valid. In `3_investment_reg.tex` (line 55), "reports estimation results using a restricted sample" is more precise than "excludes firms."~~

~~**Action:** In `3_investment_reg.tex` line 55, reword: "Column 3 reports estimation results using a restricted sample that excludes firms with bonds maturing between 1931 and 1934."~~

---

### ~~Comment 73 — Table 3: Reword Column 4 description (Page 47)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "Column 4 excludes firms that repurchased their bond issues in 1933 or 1934." with comment: "Adapt the wording suggested in my previous comment."~~

~~**Assessment:** Valid. Same style as Comment 72.~~

~~**Action:** In `3_investment_reg.tex` line 55, reword: "Column 4 reports estimation results using a restricted sample that excludes firms that repurchased their bond issues in 1933 or 1934."~~

---

### ~~Comment 74 — Table 3: Improve wording for Columns 5–7 (Page 47)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted Columns 5–7 descriptions with comment: "Try to see if we can improve the wording here as well."~~

~~**Assessment:** Valid. Same style should be applied for consistency.~~

~~**Action:** In `3_investment_reg.tex` line 55, reword Columns 5–7 in the same style (e.g., "Column 5 restricts the sample to…", "Columns 6 and 7 report results from placebo tests that replace…").~~

---

### ~~Comment 75 — Table 4: Fix punctuation in notes (Page 48)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "the payout results: Profits is net income and Cash includes cash and marketable securities (both normalized by total assets), and Leverage is book leverage." with comment: "Should improve formulation. I think a comma might be missing. What do you think, AI?"~~

~~**Assessment:** Valid. In `4_other_outcomes.tex` (line 54), the coordination is awkward. Using semicolons would improve clarity: "Profits is net income; Cash includes cash and marketable securities (both normalized by total assets); and Leverage is book leverage."~~

~~**Action:** In `4_other_outcomes.tex` line 54, replace the commas with semicolons for the variable definitions list.~~

---

### ~~Comment 76 — Table 5: "table tests" → "table reports" + reorder (Page 49)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "This table tests whether debt overhang effects are more severe for firms closer to default." with comment: "The table doesn't test. It reports the results of the tests. Also: 'Only 1933 and 1934 interaction terms are reported; see Internet Appendix Table IA.9 for the full list of coefficients.' should be mentioned earlier in the Notes."~~

~~**Assessment:** Valid. In `5_credit_ratings.tex` (line 36), the table reports results, it doesn't "test." Also, the truncation note should appear early so readers know they're seeing a subset.~~

~~**Action:** In `5_credit_ratings.tex` line 36: (1) change "This table tests whether" to "This table reports results from regressions testing whether"; (2) move the sentence about "Only 1933 and 1934 interaction terms are reported…" to appear earlier in the notes.~~

---

### ~~Comment 77 — Table 6: Same "table tests" issue (Page 50)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "This table tests whether the effect of gold clause exposure" with comment: "Again, the table doesn't test."~~

~~**Assessment:** Valid. Same issue as Comment 76.~~

~~**Action:** In `6_controls.tex` line 36, change "This table tests whether" to "This table reports results testing whether" or "This table examines whether."~~

---

### Comment 78 — Table 7: Clarify "After" in main text (Page 51)

**Annotation type:** Highlight with comment

**What was flagged:** Highlighted the table notes with comment: "Make sure we are clear in the main text what After corresponds to and how to interpret the numbers."

**Assessment:** Valid. The table note defines "After" as 1935–1940, but the main text discussion should also clearly explain this.

**Action:** Verify that Section 5.6 in `5_main_results.tex` clearly defines and explains the "After" period and its interpretation.

---

## Table Notes — Internet Appendix (Pages 53–71)

### ~~Comment 79 — IA Figure: Add notes (Page 53)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "Industrial bond quotes. Commercial" with comment: "Add some notes."~~

~~**Assessment:** Valid. In `11_online_appendix.tex` (lines 55–61), the IA figure of bond quotes from the Commercial and Financial Chronicle has only a caption but no descriptive notes, unlike all other figures.~~

~~**Action:** In `11_online_appendix.tex` after the figure, add a `\textit{Notes.}` section explaining what the figure shows and why it is relevant.~~

---

### ~~Comment 80 — Table IA.1: Remove Panel C (Page 54)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "Panel C: 1935–1940" (entire panel) with comment: "Panel C should be entirely removed."~~

~~**Assessment:** Valid. In `1_summary_all.tex` (lines 49–66), Panel C should be removed.~~

~~**Action:** In `1_summary_all.tex`, remove all Panel C data rows (lines 49–66).~~

---

### ~~Comment 81 — Table IA.1: Remove Panel C from notes (Page 54)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted "and Panel C the post-resolution period (1935–1940)." with comment: "Panel C must be removed."~~

~~**Assessment:** Valid. Consistent with Comment 80.~~

~~**Action:** In `1_summary_all.tex` (line 72), remove the reference to Panel C from the notes.~~

---

### ~~Comment 82 — Table IA.1: Remove $d$/$\tilde{d}$ definitions from notes (Page 54)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the variable definitions in the notes with comment: "Remove this part as well."~~

~~**Assessment:** Valid. In `1_summary_all.tex` (line 72), remove the $d$ and $\tilde{d}$ variable definitions from the table notes (readers can refer to Appendix A for definitions).~~

~~**Action:** In `1_summary_all.tex` line 72, remove the sentences defining $d$, $\tilde{d}$, $I_{d>0}$, and $I_{\tilde{d}>0}$.~~

---

### ~~Comment 83 — IA Tables IA.2/IA.3: Remove same definitions (Page 55)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the $d$/$\tilde{d}$ definition text with comment: "Remove."~~

~~**Assessment:** Valid. Same $d$/$\tilde{d}$ definition text should be removed from IA table notes in `0a_summary_d_1.tex` and/or `2_summary_I_1.tex`, consistent with Comment 82.~~

~~**Action:** Remove the $d$/$\tilde{d}$ variable definitions from the notes of `0a_summary_d_1.tex` and `2_summary_I_1.tex`.~~

---

### ~~Comment 84 — Table IA.4: Add explanation for $d$ vs. Corp. bonds/LTL discrepancy (Page 56)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the table notes with comment: "Add the explanation we provided earlier in the text about why d may differ slightly from Corp. bond/LTL. It has to do with the way data source amt outstanding vs balance sheet. Also explain why in the post sample (Panel C) d can differ significantly from corp bond/LTL. This is because $\tilde{d}$ is frozen at 1930 value while corp bond / LTL is contemporaneous."~~

~~**Assessment:** Valid and important. In `0_sum_stats_tilde_d.tex` (line 68), the notes should explain: (1) $d$ may differ from Corp. bonds/LTL because $d$ uses amount outstanding from bond listings while LTL uses balance sheet data; (2) in Panel C, $\tilde{d}$ can differ significantly from Corp. bonds/LTL because $\tilde{d}$ is frozen at 1930 values while Corp. bonds/LTL is contemporaneous. This explanation already exists in Table 1's notes and should be adapted here.~~

~~**Action:** In `0_sum_stats_tilde_d.tex` line 68, add the discrepancy explanation adapted from Table 1's notes.~~

---

### ~~Comment 85 — Table IA.5: Update footnote (Page 57)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the table notes with comment: "Update this footnote in the same spirit as the notes of the previous table."~~

~~**Assessment:** Valid. Same treatment as Comment 84.~~

~~**Action:** In `0a_summary_d_1.tex` (line 62), update notes to include the same discrepancy explanation.~~

---

### ~~Comment 86 — Table IA.6: Update footnote (Page 58)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the table notes with comment: "Update the footnote along the same lines as before."~~

~~**Assessment:** Valid. Same treatment.~~

~~**Action:** In `0b_summary_d_0.tex` (line 62), update notes consistently.~~

---

### ~~Comment 87 — Table IA.7: Update footnote (Page 59)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the table notes with comment: "Update the footnote along the same lines as before."~~

~~**Assessment:** Valid. Same treatment.~~

~~**Action:** In `4_summary_I_smalld.tex` (line 63), update notes consistently.~~

---

### Comment 88 — Table IA.8: Update table notes (Page 60)

**Annotation type:** Highlight with comment

**What was flagged:** Highlighted the table notes with comment: "Update the table along the same lines as before."

**Assessment:** Valid. Same treatment.

**Action:** In `5_summary_I_larged.tex` (line 65), update notes consistently.

---

### ~~Comment 89 — Table IA.10: Add same explanatory text (Page 66)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted the table notes with comment: "Add the same element to the notes as in the many table notes we updated earlier."~~

~~**Assessment:** Valid. Note that this table uses a different $\tilde{d}$ definition (gold clause bonds / (pref. equity + bonds) in 1930), so the explanation needs to be adapted accordingly.~~

~~**Action:** In `8_summary_pos_ps_bond.tex` (line 64), add the adapted discrepancy explanation.~~

---

### ~~Comment 90 — Table IA.15: Fix alignment (Page 71)~~

~~**Annotation type:** Highlight with comment~~

~~**What was flagged:** Highlighted Table IA.15 with comment: "This table doesn't look good. The alignment is off."~~

~~**Assessment:** Valid. In `13_dividend_additional.tex`, the table formatting may be inconsistent with other tables (e.g., `1933 \ensuremath{\times \tilde{d}}` vs. `\ensuremath{\text{1933} \times \tilde{d}}`). The alignment issue likely stems from inconsistent LaTeX formatting of the first-column entries.~~

~~**Action:** In `13_dividend_additional.tex`, standardize the row label formatting to match other tables (e.g., use `\ensuremath{\text{1933} \times \tilde{d}}`). Investigate and fix the alignment issue.~~

---

## Summary of Actions

| # | Section | File(s) | Type | Effort |
|---|---------|---------|------|--------|
| 1 | Intro | `1_intro.tex` | Word choice: "similar unexposed firm" | Quick fix |
| 2 | Intro | `1_intro.tex` | Word choice: add "otherwise" | Quick fix |
| 3 | Literature | `2_literature.tex` | Add "in modern times" | Quick fix |
| 4 | Hist. Background | `3_historical_background.tex` | Improve transition word | Quick fix |
| 5 | Hist. Background | `3_historical_background.tex` | Split sentence | Quick fix |
| 6 | Hist. Background | `3_historical_background.tex` | Add Friedman & Schwartz cite | Quick fix |
| 7 | Hist. Background | `3_historical_background.tex` | Add Friedman & Schwartz cite | Quick fix |
| 8 | Hist. Background | `3_historical_background.tex` | Add footnote with bank failure numbers | Moderate |
| 9 | Hist. Background | `3_historical_background.tex` | Cite Edwards | Quick fix |
| 10 | Hist. Background | `3_historical_background.tex` | Reformulate Figure 1 description | Moderate |
| 11 | Hist. Background | `3_historical_background.tex` | Rephrase "gold clause enforceability" | Quick fix |
| 12 | Hist. Background | `3_historical_background.tex` | Split long sentence | Quick fix |
| 13 | Data | `4_data.tex` | Verify numbers match Table 1 | Verification |
| 14 | Data | `4_data.tex` | Evaluate redundancy of leverage sentence | Requires discussion |
| 15 | Data | `4_data.tex` | Strengthen pre-existing differences caveat | Moderate |
| 16 | Data | `4_data.tex` | Add "For example" | Optional |
| 17 | Data | `4_data.tex` | Add "outstanding" | Quick fix |
| 18 | Data | `4_data.tex` | Reorder "prior to the 1933 abrogation" | Quick fix |
| 19 | Data | `4_data.tex` | Add "apparent" | Quick fix |
| 20 | Data | `4_data.tex` | Soften "no" → "little to no" | Quick fix |
| 21–22 | Data | `4_data.tex` | Rewrite $\tilde{d}$ definition paragraph | Moderate |
| 23 | Data | `4_data.tex` | Add "formally" | Quick fix |
| 24 | Data | `4_data.tex` | Verify IA table descriptions | Verification |
| 25 | Data | `4_data.tex` | Tighten IA.8 description | Quick fix |
| 26 | Data | `4_data.tex` | Remove or specify correlation claim | Requires discussion |
| 27 | Data | `4_data.tex` | "from" vs. "of" | Optional |
| 28 | Data | Unknown | Locate "behavior" and evaluate | Needs investigation |
| 29 | Main Results | `5_main_results.tex` | Reformulate baseline intro | Moderate |
| 30 | Main Results | `5_main_results.tex` | Define j and t subscripts | Quick fix |
| 31 | Main Results | `5_main_results.tex` | "increase in severity" | Quick fix |
| 32 | Main Results | `5_main_results.tex` | Add commas | Quick fix |
| 33 | Main Results | `5_main_results.tex` | "precisely" → "the years when" | Quick fix |
| 34 | Main Results | `5_main_results.tex` | Numbers verified ✓ | No action |
| 35 | Main Results | `5_main_results.tex` | Fix tense ("was" → "is") | Quick fix |
| 36 | Main Results | `5_main_results.tex` | Prevent minus sign line breaks | Quick fix |
| 37–38 | Main Results | `5_main_results.tex` | "not statistically significantly different from zero" (×2) | Quick fix |
| 39 | Main Results | `5_main_results.tex` | Move "respectively" | Quick fix |
| 40, 42 | Main Results | `5_main_results.tex` | Standardize column capitalization | Moderate (global) |
| 41 | Main Results | `5_main_results.tex` | Improve transition | Quick fix |
| 43 | Main Results | `5_main_results.tex` | Verify IA table consistency | Verification |
| 44 | Main Results | `5_main_results.tex` | Remove mechanical sentence | Quick fix |
| 45 | Main Results | `5_main_results.tex` | Add Table 5 → IA.9 note | Quick fix |
| 46 | Main Results | `5_main_results.tex` | Remove redundant phrase | Quick fix |
| 47 | Main Results | `5_main_results.tex` | Better explain FE mechanism | Moderate |
| 48 | Main Results | `5_main_results.tex` | "industry-level" → "industry-specific" | Quick fix |
| 49 | Main Results | `5_main_results.tex` | Numbers verified ✓ | No action |
| 50 | Main Results | `5_main_results.tex` | Numbers verified ✓ | No action |
| 51 | Main Results | `5_main_results.tex` | Fix "roughly half" for 1934 | Moderate |
| 52 | Main Results | `5_main_results.tex` | Better motivate heterogeneity | Moderate |
| 53 | Main Results | `5_main_results.tex` | Split long sentence | Quick fix |
| 54 | Main Results | `5_main_results.tex` | "remain intact" → "remain the same" | Quick fix |
| 55 | Main Results | `5_main_results.tex` | "firms" → "issuers" | Quick fix |
| 56 | Conclusion | `6_conclusion.tex` | "the" → "our" | Quick fix |
| 57 | Conclusion | `6_conclusion.tex` | Rewrite clumsy sentence | Moderate |
| 58 | Conclusion | `6_conclusion.tex` | High-level debt overhang framing | Moderate |
| 59 | Conclusion | `6_conclusion.tex` | Reword placebo test summary | Quick fix |
| 60 | Appendix | `7_appendix.tex` | "The" → "This" | Quick fix |
| 61 | Appendix | `7_appendix.tex` | Add footnote on coverage | Quick fix |
| 62 | Appendix | `7_appendix.tex` | Capitalize "Log" | Optional |
| 63 | Appendix | `7_appendix.tex` | Add $\tilde{d}$ definitions | Moderate |
| 64 | Figures | `9_figures.tex` | Improve Figure 3 notes | Quick fix |
| 65 | Figures | `9_figures.tex` | "year" → "year dummy" | Quick fix |
| 66 | Table 1 | `1_sum_stats_d.tex` | Fix Panel C explanation | Quick fix |
| 67–69 | Table 2 | `2_bond_stats.tex` | Clarify "157 firms" wording | Quick fix |
| 70–74 | Table 3 | `3_investment_reg.tex` | Reword column descriptions + add equations | Moderate |
| 75 | Table 4 | `4_other_outcomes.tex` | Fix punctuation | Quick fix |
| 76 | Table 5 | `5_credit_ratings.tex` | "table tests" → "table reports" + reorder | Quick fix |
| 77 | Table 6 | `6_controls.tex` | Same as 76 | Quick fix |
| 78 | Table 7 | `7_aggregate.tex` | Clarify "After" in text | Moderate |
| 79 | IA Figure | `11_online_appendix.tex` | Add notes | Moderate |
| 80–82 | Table IA.1 | `1_summary_all.tex` | Remove Panel C + definitions | Moderate |
| 83 | IA Tables | `0a_summary_d_1.tex`, `2_summary_I_1.tex` | Remove definitions | Quick fix |
| 84–89 | IA Tables | Multiple summary tables | Add discrepancy explanation to notes | Moderate (×6 tables) |
| 90 | Table IA.15 | `13_dividend_additional.tex` | Fix alignment | Moderate |
