# Claudex Loop Protocol

Two AI agents iterate on **{{ARTIFACTS}}** to convergence: **Claude** (Anthropic, in Claude Code) and **Codex** (OpenAI CLI). This file is the shared contract — both agents read it first, every turn. Working folder: `{{LOOP_DIR}}`.

---

## Roles (asymmetric on purpose — to stay clobber-free)

- **Claude — Writer / pen-holder.** The *only* agent that edits the artifact files. Reads Codex's review, adjudicates **every** point (accept + apply / modify / reject + reason), and produces the next version.
- **Codex — Cross-model Reviewer.** Reads the artifacts + the log and appends critique entries to `loop.jsonl`. **Never edits the artifacts** — that is how two writers avoid clobbering one file. Every proposed change is a log entry for Claude to apply.

Roles are swappable by mutual note, but there is **only ever one pen-holder.**

---

## Files

- `{{LOOP_DIR}}/loop.jsonl` — the message bus + control channel. **Append-only, one compact JSON object per line** (no pretty-printing; no space after the colon in top-level keys, so `tail`/`grep` matching works). **Git-ignored.**
- `{{LOOP_DIR}}/PROTOCOL.md` — this contract.
- The artifact(s) under iteration — the work product Claude edits. Git-tracked.

---

## Turn protocol

1. On your turn, read the **last** entry in `loop.jsonl` (and anything appended since your previous turn).
2. Do your work — Claude: edit artifacts + adjudicate; Codex: review + critique.
3. Append **exactly one** entry, set `next_turn` to the other agent, then **stop and wait.**
4. **Strict alternation** — never take two turns in a row. If the last line's `author` is you, it is *not* your turn.

## Entry schema (one compact line each)

```json
{"ts":"<UTC ISO8601>","round":1,"author":"claude","role":"writer","status":"handoff","next_turn":"codex","artifacts":["paths the other should read"],"summary":"one line","points":[{"id":"P1","severity":"high","loc":"file:section","issue":"...","proposal":"..."}],"dispositions":[{"ref":"P1","action":"accepted","reason":"...","applied_to":"file"}],"requests":["..."]}
```

- **Reviewer (Codex)** fills `points` (id, severity, location, the issue, a concrete proposal) + a `status`.
- **Writer (Claude)** fills `dispositions` (how each prior point was handled — `accepted`/`modified`/`rejected` + reason) and names the version produced.
- Keep prose in `summary`/`issue`/`reason`; keep document content in the artifact files, not the log.

`status`: `handoff` (your work done, other's turn) · `approved` (reviewer signs off) · `needs_human` (escalate).

---

## Termination

- **Converged:** Codex appends `status:"approved"` with empty `points`. Claude surfaces the final artifact to the human and stops.
- **Round cap:** if `round` reaches **25** without approval, the next agent sets `status:"needs_human"`, `next_turn:"human"`, and both pause. (Generous on purpose — a runaway backstop, not a target.)
- **Escalate any time:** either agent may set `status:"needs_human"` on an irreconcilable disagreement or an out-of-scope call. Pause for the human.

---

## Guardrails

- Reviewer never edits artifacts. Writer must address **every** reviewer point explicitly (no silent drops) — this is what stops points from being re-raised round after round.
- Weight Codex's **specific, verifiable catches** highly; treat **sweeping verdicts** cautiously. Domain standards are owned by the repo's own sources (in KLPW2: `CLAUDE.md`, `analysis/PLAN.md`, the paper), not by either reviewer's taste.
- **Review cadence:** run the cheap deterministic check if the artifact has one (in KLPW2, e.g. a `--limit-*` smoke run or `python pipeline/code/main.py --validate`) **every round**; reserve any heavyweight multi-agent gate (e.g. `/code-review` at high/ultra effort) for when a full draft first exists and the **final gate**, not between every round. After the final heavyweight gate, **reopen one loop** so the reviewer can check the writer's post-gate edits.

---

## How each agent waits (automation)

After handing off, run a watcher that exits the moment the other writes, then react:

- **Claude waits for Codex:** `until tail -n1 {{LOOP_DIR}}/loop.jsonl | grep -q '"author":"codex"'; do sleep 5; done`
- **Codex waits for Claude:** same, with `"author":"claude"` — and Codex should loop this continuously (review → append → wait again) until it sets `status:"approved"`, so handoffs need no human relay.
