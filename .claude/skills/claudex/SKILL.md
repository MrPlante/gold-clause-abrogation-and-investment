---
name: claudex
description: Stand up and run an automated Claude×Codex iteration loop where Claude (writer/pen-holder) and Codex (cross-model reviewer) iterate on an artifact to convergence. Does the legwork: scaffolds the loop folder + PROTOCOL, seeds round 1, then AUTO-DRIVES Codex directly by calling the `mcp__codex__codex` MCP tool (read-only, synchronous, no copy-paste) when Codex is registered as an MCP server — or falls back to RELAY mode (git-ignored file-bus + watcher + a self-monitoring kickoff) only if that tool isn't available. Use for "loop with Codex", "claudex", "reconcile/iterate with Codex", "cross-model review loop".
---

# claudex

Initiate and drive a two-agent iteration loop between **Claude** (this session, the **writer/pen-holder**) and **Codex** (OpenAI CLI, the **cross-model reviewer**). The two trade turns over a shared, git-ignored **file-bus** (`loop.jsonl`) until they converge. Claude is the only agent that edits the artifact; Codex critiques via the bus. Packaged so you don't re-derive the setup each time.

**Why a file-bus:** the two agents are separate processes; the only thing they both touch is the filesystem. An append-only JSONL log is the message bus + control channel; the artifacts are edited separately so two writers never clobber one file.

## Usage

`/claudex <what to iterate on>` — e.g. `/claudex the SC hook in scripts/.../reconciliation/`, or `/claudex reconcile RB+OL in <dir>`.

Resolve up front (infer what you can; ask only if genuinely unclear):
- **Loop dir** — where the bus + PROTOCOL live (default: a `loop/` or `reconciliation/` subfolder beside the artifacts).
- **Artifact(s)** under iteration (the files Claude will edit).
- **Scope** — what's open vs locked (state it so neither agent reopens settled decisions).
- **Roles** — default Claude=writer, Codex=reviewer (swappable, but only one pen-holder).
- **Done** — convergence is Codex `status:"approved"`; round cap 25; or `needs_human`.

## Step 1 — Scaffold (the legwork)

Set `LOOP=<loop dir>` (repo-relative). Create the folder, drop in the protocol, git-ignore the bus + the watcher pidfile, and create the empty bus:

```bash
LOOP="<loop dir>"            # e.g. analysis/loops/measure-reconcile
mkdir -p "$LOOP"
# drop the protocol template in, filling the two placeholders
sed -e "s#{{LOOP_DIR}}#$LOOP#g" -e "s#{{ARTIFACTS}}#<artifact list>#g" \
  .claude/skills/claudex/protocol-template.md > "$LOOP/PROTOCOL.md"
# git-ignore the transient bus + any watcher pidfile (do not commit these)
for p in "$LOOP/loop.jsonl" ".codex-watcher.pid"; do
  grep -qxF "$p" .gitignore 2>/dev/null || printf '%s\n' "$p" >> .gitignore
done
touch "$LOOP/loop.jsonl"
```

## Step 2 — Seed round 1 (Claude's opening turn)

As the writer, post the opening entry: what's under iteration, what's open vs locked, and the first ask. Append a **compact single-line** JSON object (see the schema in `PROTOCOL.md`). Use a real UTC timestamp; keep document content in the artifacts, not the log; avoid apostrophes / embedded double-quotes in the JSON string values (they break the one-line append).

```bash
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
printf '%s\n' '{"ts":"'"$TS"'","round":1,"author":"claude","role":"writer","status":"handoff","next_turn":"codex","artifacts":["<paths>"],"summary":"<one line: what is under review and the scope>","points":[],"dispositions":[],"requests":["<what you want Codex to check>","Iterate until we converge; give specific line-level fixes, not just a verdict.","Monitor dynamically per PROTOCOL: watch loop.jsonl, take each turn as soon as the last author is claude, append one entry, resume watching, until you set status approved."]}' >> "$LOOP/loop.jsonl"
```

## Step 2.5 — Pick the transport: DIRECT (auto-drive) or RELAY

Drive Codex **directly** whenever you can — no watcher, no human paste. The proven, preferred transport is the **Codex MCP tool (`mcp__codex__codex`)**: it round-trips **synchronously, in-turn**, so the whole loop runs inside your turns with zero copy-paste. The file-bus + watcher + pasted kickoff (Steps 3–4) exist only as a fallback.

**Check it's available:** is the `mcp__codex__codex` tool loaded this session? (If its schema isn't loaded yet, fetch it: ToolSearch `select:mcp__codex__codex,mcp__codex__codex-reply`.) If the tool exists → DIRECT mode. If it doesn't → do the one-time setup, or fall back to RELAY.

*One-time setup* (persists across sessions once done):

```bash
claude mcp add codex -- codex mcp-server   # register Codex as an MCP server (run in a terminal)
claude mcp list                            # confirm: "codex: codex mcp-server - ✔ Connected"
```

Then **restart/reconnect Claude Code** so the `mcp__codex__codex` tool loads into the session (MCP tools attach at startup).

**DIRECT mode (preferred) — each round, call `mcp__codex__codex`:**
- `prompt`: the reviewer brief — state the scope, name the artifact to read (Codex reads it itself), and ask for **APPROVED, or a numbered list of specific, located, line-level fixes**.
- `sandbox: "read-only"` — the reviewer literally **cannot edit** the artifact; this enforces the single-pen rule at the tool level (stronger than the file-bus convention).
- `cwd`: the **loop/artifact dir** (point at the small loop subfolder, not a huge repo root, so Codex doesn't scan a big tree).
- `approval-policy: "never"` — non-interactive; never stalls waiting on a prompt.
- `config: { "model_reasoning_effort": "xhigh" }` — pin the reviewer to the **highest** reasoning effort explicitly, on every opening call. The review is the assurance step, so it always runs at max depth; pinning it here means quality never silently follows a changed global `~/.codex/config.toml` default or a model whose default differs. `config` overrides `CODEX_HOME/config.toml` per-call; `model_reasoning_effort` is the effort knob (`gpt-5.5` scale: `low → medium → high → xhigh`). Note `mcp__codex__codex-reply` takes **no** `config` — continuations inherit the thread's effort, so pinning the *opening* call carries `xhigh` through the whole loop.

  It returns `{threadId, content}`; `content` is the review. **Append that to `loop.jsonl` yourself** (Codex ran read-only, so it can't write the bus — you are its scribe), then adjudicate (Step 5), edit as the sole pen, and call again. Keep the `threadId` and use **`mcp__codex__codex-reply`** (`threadId` + `prompt`) to continue the *same* Codex thread across rounds — warmer context, faster turns. Because the call is synchronous, **skip Step 3 (watcher) and Step 4 (kickoff)** — go straight to Step 5 after each call.

  **Prefer the persistent `mcp-server` transport** — it round-trips cleanly. *Origin-project caveat (Windows):* shelling out to `codex exec` hung there on the per-call read-only sandbox setup. That is **untested on this Linux cluster** — don't treat it as fact here; verify `codex exec` returns before relying on it.

- **`mcp__codex__codex` unavailable and can't be set up → RELAY mode:** fall back to Steps 3–4 (arm the watcher, print the kickoff for the human to paste). Same protocol, same bus; only the transport differs.

Steps 3–4 are **relay-mode only**; in direct mode you skip them.

## Step 3 (relay mode) — Arm the watcher (so Codex's reply wakes you)

Run this **in the background**; the harness re-invokes you when it exits (Codex wrote, or it timed out ~30 min):

```bash
LOG="$LOOP/loop.jsonl"; BASE=$(wc -l < "$LOG"); i=0
while [ "$(wc -l < "$LOG")" -le "$BASE" ] || ! tail -n1 "$LOG" | grep -q '"author":"codex"'; do
  i=$((i+1)); [ $i -gt 360 ] && { echo "WATCHER_TIMEOUT: no new Codex entry ~30 min"; exit 2; }
  sleep 5
done
echo "CODEX_RESPONDED"; tail -n1 "$LOG"
```

The watcher lives in this session; if the session is torn down it dies silently — just re-run this step to re-arm (loop state lives in the file, nothing is lost).

## Step 4 (relay mode) — Print the Codex kickoff (hand to the human to paste into Codex)

Codex runs in its own CLI; surface this so its side speaks the protocol and self-monitors to convergence:

> You're the **Reviewer** in a Claudex loop. Read `<LOOP>/PROTOCOL.md` first — your role is review only; **never edit the artifacts** (Claude is sole pen-holder; you propose changes via the log). Then run hands-free until convergence:
> 1. Watch the bus: `until tail -n1 <LOOP>/loop.jsonl | grep -q '"author":"claude"'; do sleep 5; done`
> 2. When it's your turn, read the latest entry + the artifact(s). Review against the stated scope; give specific, located, line-level fixes — not just a verdict.
> 3. Append **exactly one** compact JSON line to `<LOOP>/loop.jsonl` (`author:"codex"`, `next_turn:"claude"`, your `points`; `status:"handoff"`, or `status:"approved"` with empty `points` when it's good).
> 4. Loop back to step 1. **Stop only when you set `status:"approved"`** (or `needs_human`).

## Step 5 — Drive the loop to convergence (Claude's per-turn job)

Each time the watcher wakes you:
1. **Read** the latest Codex entry (and any since your last turn).
2. **Adjudicate every point** — accept+apply / modify / reject+reason. Weight Codex's *specific, verifiable* catches high; treat sweeping verdicts cautiously; settle standards disputes against the repo's own sources (in KLPW2: `CLAUDE.md`, `analysis/PLAN.md`, and the paper's verification targets), escalating to the human if stuck.
3. **Apply** accepted edits to the artifact (you are the only pen).
4. **Run the cheap check every round** if the artifact has one — e.g. for a klpw2 build step, smoke-run on `--limit-cusips` / `--limit-rows` or run the validation harness (`python pipeline/code/main.py --validate --targets <table>`); fix errors before handing back. (This repo has no per-round source linter.)
5. **Append one entry** with your `dispositions` + the version produced, `next_turn:"codex"`, then hand back to Codex: **make the next `mcp__codex__codex-reply` call** (direct mode, Step 2.5) or **re-arm the watcher** (relay mode, Step 3).
6. Repeat until Codex `status:"approved"` (converged) or `needs_human`/round-cap (pause for the human). Then surface the final artifact.

**Heavyweight gates (cadence):** don't run a heavyweight gate (e.g. `/code-review` at high/ultra effort, or a full `duel`) between every round — it taxes the fast loop and prematurely line-level-validates drafts that still change. Run it once when a full draft first exists and as the **final gate**; after the final gate, **reopen one loop** so Codex can check your post-gate edits.

## Adversarial hardening (final assurance)

A warm, same-thread loop is the right tool for *convergence* — it builds context and stops re-raising settled points. But it is the wrong tool for *final assurance*: a thread that has been collaborating (and especially one that just APPROVED) goes agreeable and stops hunting. Separate the two jobs.

After the warm loop reports convergence, run a **cold adversarial gate**:

- **At least two FRESH, independent adversary passes** — new `mcp__codex__codex` sessions (not `codex-reply` on the warm thread), ideally in parallel. Independence is the point: in this repo a second fresh adversary caught a real `prod()`-without-import fault that the first thread had already approved.
- **Don't tell them it was approved.** Frame each as a hostile review — *try to break it.* Give them the artifact, the scope, and the compact dispositions (so settled points aren't re-litigated), and ask for **blockers only**: technical errors, missing imports/setup, viewer-confusion, factual or standard violations — not taste.
- **Adjudicate, edit, re-check.** If a fresh adversary finds something real, fix it and re-run a targeted check; the gate passes only when **two independent adversaries find nothing new worth fixing.** Run it as a bounded loop (e.g. at least 3 rounds, cap ~10) so it terminates.

This is a *mode* of claudex, not a separate skill — same bus, dispositions, and single-pen rule; only the reviewer stance (cold / independent) and the ask (blockers only) change.

## Notes

- **Single pen-holder, always** — the asymmetric roles are what keep two agents off one file. If you want Codex to write, swap roles by mutual note; never both at once.
- **The bus is the source of truth, not the watcher** — if a turn is missed or the session restarts, re-read `loop.jsonl` and continue; if a duplicate entry lands (parallel writers), dedupe the log.
- **Don't commit the bus** — `loop.jsonl` and `.codex-watcher.pid` are git-ignored by Step 1; the artifacts and `PROTOCOL.md` are the committable output.
- **Codex availability / transport** — prefer DIRECT mode via the **`mcp__codex__codex`** tool (Step 2.5): synchronous, in-turn, read-only, no human relay. *Origin-project provenance:* there it ran on Codex 0.142.0 as an MCP server with ChatGPT-plan auth, round-tripping cleanly; the `codex exec` hang was a Windows-sandbox issue there (see Step 2.5). *On this KLPW2 cluster:* Codex is installed at `~/.local/bin/codex` and registered with `claude mcp add codex -- ~/.local/bin/codex mcp-server` (absolute path, because `~/.local/bin` may not be on PATH when the server launches), then reconnect — **verify the round-trip yourself before relying on it.** Fall back to RELAY (watcher + pasted kickoff) only if the MCP tool isn't loaded and can't be registered.
- **Highest effort, always, everywhere** — *every* Codex call in the pipeline pins `config: { "model_reasoning_effort": "xhigh" }` on its opening `mcp__codex__codex` call: the warm convergence loop (Step 2.5), the cold adversarial gate (fresh sessions below), and the cross-model passes any other skill runs on this engine (here: `duel`; `forge`/`validate`/`gate` exist in the origin project but were not imported). The pin is a property of the review pipeline, not of a global config that happens to be set right. Skills that defer to claudex for the call mechanics inherit it through this rule.
- Point, don't duplicate: review *content* lives in the repo's own standards (KLPW2: `CLAUDE.md`, `PLAN.md`, the paper); this skill owns the loop *mechanics*.
- **General-purpose engine with repo bindings.** The loop is domain-agnostic — one writer + one reviewer iterating to convergence on any prompt. The domain-specific bits are inline and optional: the per-round cheap check and settling disputes against the repo's standards (KLPW2: the validation harness + `PLAN.md`/the paper). `duel` builds two cross pairs on this same engine. (`forge`, an origin-project caller, was not imported.) Kept repo-shared (not relocated to user-global) so collaborators get it through the repo.
