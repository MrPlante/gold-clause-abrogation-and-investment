---
name: project-cost
description: Estimate the total Claude API cost of this project's entire Claude Code session history, broken down by model. Use when asked for the cost/spend of "this project," "our chat," or session usage so far.
---

# project-cost

Reports the total estimated API cost of every local Claude Code session transcript for this project, broken down by model.

## Steps

1. Run `.claude/skills/project-cost/project_cost.py` from the repo root:

   ```
   python .claude/skills/project-cost/project_cost.py
   ```

   It auto-detects this project's session transcripts under `~/.claude/projects/` (including any sessions run from a subdirectory of the repo) and sums token usage per model from each `.jsonl` transcript.

2. Present the script's table to the user as-is (model, input tokens, output tokens, cache-read tokens, cost per model, and total).

3. Note the caveats inline if relevant:
   - Cost is estimated at **current list pricing** applied retroactively — not a record of what was actually billed at the time, since prices can change.
   - If the model reports usage for a model not in its `PRICING` table, it lists those separately — check `.claude/skills/project-cost/project_cost.py` and add current pricing there (via the `claude-api` skill or `platform.claude.com/docs/en/pricing`).
   - This reflects local session transcripts only. If `cleanupPeriodDays` in `~/.claude/settings.json` is short, older sessions may already be gone from disk.

## Notes

- Pricing constants live at the top of `.claude/skills/project-cost/project_cost.py` — update them there when Anthropic's pricing changes, rather than hardcoding numbers elsewhere.
- The tool takes an optional path argument to price a different project's sessions: `python .claude/skills/project-cost/project_cost.py <path>`.
