---
name: duel
description: General dual cross-model pipeline. Give it a prompt; both models draft an answer independently and blind; each draft is hardened by the OTHER model's review to convergence (two cross pairs); a fresh agent then grafts the two hardened drafts into one, and a cold adversary gate hardens the result. Domain-agnostic — works on any task, not just scripts. Uses `claudex` twice and `graft` once. Use e.g. "/duel <prompt>".
---

# duel

**Two models draft, each hardens the other's, then we graft both into one.** Where `claudex` has a single pen (one model writes, the other reviews), `duel` runs **two independent drafts** — one from each model — and hardens each against the *other* model's review before fusing. It maximizes both axes that make cross-model work pay: generative **diversity** (two models, not one) and review **independence** (each draft judged by the model that didn't write it).

`duel` is **general-purpose**: prompt in, one hardened answer out. It knows about *models and loops*, not any one domain. Quality criteria are supplied by the caller (a standard, a rubric, the prompt's own success conditions); with none given, each side works to the prompt's evident bar.

## Layering

`duel` is orchestration over primitives — it doesn't re-define the loop or the synthesis:

- **`claudex`** (×2) — each cross pair is a `claudex` loop (writer + the *other* model as reviewer), run to convergence. Drive Codex in DIRECT mode (`mcp__codex__codex`, read-only, `xhigh` effort — see `claudex` Step 2.5).
- **`graft`** (×1) — the final fuse of the two hardened drafts into one.

This is a textbook fit for the **Workflow tool** (deterministic agent fan-out), which needs explicit opt-in. Until then, drive it inline as the orchestrator.

## How it runs

1. **Two independent, blind drafts.** One model (Claude) and the other (Codex, a *fresh* `mcp__codex__codex` thread) each answer the prompt — **neither sees the other's draft.** Brief both identically: the task, the success criteria, any fixed constraints. Independence at generation is the point; don't let one writer anchor on the other.
2. **Two cross pairs, hardened to convergence** (two `claudex` loops, ideally in parallel):
   - **Draft A** (Claude's) is reviewed by **Codex**; Claude holds the pen on A and revises to Codex's located feedback until Codex signs off.
   - **Draft B** (Codex's) is reviewed by **Claude**; Codex holds the pen on B (revising via `codex-reply`) and revises to Claude's feedback until Claude signs off.
   - Each draft is edited by its *author* model and reviewed by the *other* — two pens, two separate drafts (no clobber), single-pen *per draft*.
3. **Fresh graft (the cold synthesis).** A **fresh** agent — not either warm reviewer — runs `graft` on the two hardened drafts, fusing the best parts of each into one. Fresh-and-cold is deliberate: a reviewer that just signed off has gone agreeable, so the most consequential step (what ships) gets new eyes. Synthesize, don't pick a winner.
4. **Cold adversary gate (standard).** Run `claudex`'s adversarial hardening on the grafted result — a *fresh* Codex adversary, blockers-only — then fix and re-confirm. The gate passes when a fresh adversary finds nothing new worth fixing.
5. **Return** the final artifact and what each draft contributed.

## Rules

- **Blind independent generation.** The two first drafts must not see each other — anchoring kills the diversity that justifies the workflow.
- **Each draft hardened by the other model.** Cross-review, not self-review; that's where independence pays.
- **The final synthesis is fresh and cold**, never one of the warm reviewers — and it *grafts*, it doesn't *select*.
- **Cold gate is standard**, not optional — `duel` always ends on a fresh adversary pass.
- **Calibration.** Weight specific, located catches high; treat sweeping gestalt verdicts (a bare "APPROVED") cautiously — a warm reviewer goes agreeable, so a clean verdict is weak evidence and a precise located catch is strong (`claudex`).
- **It's expensive — reserve it.** Two pipelines + Codex on both the writing and reviewing side. Use it for high-stakes, wide-open tasks; lighter work goes to `claudex`.

## Domain bindings

`duel` takes criteria as input. In KLPW2 (a research pipeline, not a script-writing repo) the criteria are the artifact's own success conditions — e.g. correctness against `analysis/PLAN.md` verify targets and the paper, plus the pipeline validation harness for table builds; run whatever cheap check the artifact has inside the `claudex` loops, and `graft` re-validates the seams. In other domains, pass the relevant rubric/tests; the pipeline is identical.

## Boundary

- `claudex` — one writer + one reviewer cross-model loop (the engine `duel` calls twice).
- `graft` — the synthesis step `duel` finishes with.
- `forge` (origin project, not imported here) — applies `duel`'s both-models philosophy to a *divergent, aspect-pinned* fan-out of rewrites; `duel` itself is the general two-best-effort-drafts pipeline.
