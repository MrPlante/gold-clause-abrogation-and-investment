---
name: graft
description: Fuse several drafts of the SAME thing into one coherent whole — keep the strongest part for each job across the drafts, stitch them with the fewest cuts, then re-check every new seam. A general, domain-agnostic synthesis primitive: give it N drafts (of prose, code, a plan, anything) and the criteria to judge against, and it returns one merged version. Used by `duel` (and `forge` in its origin project), and callable standalone. Use e.g. "/graft these two drafts".
---

# graft

**Many drafts, one result.** Given two or more drafts of the *same* artifact, `graft` produces a single coherent version that keeps the best part for each job and reads/works as one piece — not a stitched-together patchwork. It is a **general-purpose** primitive: it knows about *merging candidates*, not about any one domain. Whatever quality criteria apply (a style guide, a test suite, the task's own success conditions) are **supplied by the caller**; `graft` defaults to the artifact's own evident purpose when none are given.

Synthesis beats selection: picking one whole draft throws away every good part in the losers. `graft` harvests the strongest part wherever it appears.

## Inputs

- **The drafts** — two or more versions of the same artifact.
- **The criteria** *(optional)* — what "best" means here (a standard, a rubric, tests, the prompt's success conditions). If omitted, infer from the artifact's purpose.

## How it runs

1. **Map the winners, part by part.** Decompose the artifact into its jobs (for prose: opener, each beat, the close; for code: each function/branch; for a plan: each step) and, for each, identify which draft does it best and *why*, tied to the criteria. State which draft each chosen part came from.
2. **Fuse with the fewest cuts, into ONE coherent whole.** Stitch the chosen parts together and rewrite the joins so the result reads/works as a single piece in one consistent voice/style — never a Frankenstein of mismatched registers. De-dupe parts that overlap across drafts; keep the artifact's size on target.
3. **Re-check every seam — the load-bearing step.** Each graft point is a *new* join that can break things even when both source parts were fine. Re-validate the joins against the criteria (for prose: coherence, information flow, references resolve; for code: it still compiles/passes; for a plan: steps still follow). A graft can introduce a fault neither parent had — a doubled idea, a broken reference across the stitch, an inconsistency. Fix what you find.
4. **Return** the fused artifact and the part-by-part sources (which draft won each).

## Rules

- **One coherent whole, not a patchwork.** If a grafted part can't be made to fit the surrounding piece, rewrite it — don't ship the seam.
- **Fewest cuts.** Prefer the smallest number of grafts that captures the best parts; every cut is a seam you now have to defend.
- **The fused result is re-judged, not assumed.** You just stitched it, so you're blind to its new seams — step 3's fresh check is not optional.
- **Single pen.** Grafting is one act by one editor; any reviewers only assess.

## Domain bindings (how callers specialize it)

`graft` stays general by taking criteria as input. Callers bind it to their domain:

- **In KLPW2:** the criteria are the artifact's success conditions (e.g. `PLAN.md` verify targets / the paper for analysis, the validation harness for table builds); re-check seams against those criteria (graft's own step 3) and run whatever cheap check the artifact has. `duel` calls `graft` this way. (Origin-project callers used a `validate` skill + prose standards that were not imported.)
- **Other domains:** pass whatever rubric/tests/spec applies; the procedure is identical.

## Boundary

- `duel` (and origin-project `forge`) — *generate* the candidate drafts, then call `graft` to fuse them.
- A pure *assessment* of one artifact is not `graft` (that's a review/validate pass, not a merge); `graft` specifically merges several into one.
