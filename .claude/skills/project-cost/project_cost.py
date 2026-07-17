#!/usr/bin/env python3
"""Estimate the total Claude API cost of every local Claude Code session
transcript for the current project.

Sums token usage (input, output, cache write, cache read) across every
.jsonl session transcript under ~/.claude/projects/ that belongs to this
project's working directory (including sessions run from a subdirectory of
it), then prices that usage at current list rates.

Usage: python admin/tools/project_cost.py [path]
  path defaults to the current working directory.
"""

import glob
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date

# Per-1M-token list pricing (input, output). Update from the `claude-api`
# skill or https://platform.claude.com/docs/en/pricing if this goes stale.
PRICING = {
    "claude-fable-5": {"input": 10.00, "output": 50.00},
    "claude-mythos-5": {"input": 10.00, "output": 50.00},
    "claude-opus-4-8": {"input": 5.00, "output": 25.00},
    "claude-opus-4-7": {"input": 5.00, "output": 25.00},
    "claude-opus-4-6": {"input": 5.00, "output": 25.00},
    "claude-opus-4-5": {"input": 5.00, "output": 25.00},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00},
}

# Claude Sonnet 5 has introductory pricing through 2026-08-31.
_SONNET_5_INTRO_CUTOFF = date(2026, 8, 31)
if date.today() <= _SONNET_5_INTRO_CUTOFF:
    PRICING["claude-sonnet-5"] = {"input": 2.00, "output": 10.00}
else:
    PRICING["claude-sonnet-5"] = {"input": 3.00, "output": 15.00}

# Cache pricing is derived from the input rate: 1.25x for a 5-minute
# write, 2x for a 1-hour write, 0.1x for a cache read.
CACHE_WRITE_5M_MULT = 1.25
CACHE_WRITE_1H_MULT = 2.0
CACHE_READ_MULT = 0.1


def project_slug(path: str) -> str:
    """Replicate Claude Code's project-directory slug for a cwd path
    (every non-alphanumeric character becomes a '-')."""
    return re.sub(r"[^a-zA-Z0-9]", "-", os.path.abspath(path))


def find_transcript_files(slug: str) -> list:
    projects_root = os.path.expanduser("~/.claude/projects")
    files = []
    if not os.path.isdir(projects_root):
        return files
    for name in os.listdir(projects_root):
        full = os.path.join(projects_root, name)
        if not os.path.isdir(full):
            continue
        # exact match, or a subdirectory-of-this-project session
        if name == slug or name.startswith(slug + "-"):
            files.extend(glob.glob(os.path.join(full, "*.jsonl")))
    return files


def collect_usage(files: list):
    usage_by_model = defaultdict(lambda: {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_5m_tokens": 0,
        "cache_1h_tokens": 0,
        "cache_read_input_tokens": 0,
    })
    seen = set()
    min_ts = None
    max_ts = None

    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                ts = obj.get("timestamp")
                if ts:
                    if min_ts is None or ts < min_ts:
                        min_ts = ts
                    if max_ts is None or ts > max_ts:
                        max_ts = ts

                if obj.get("type") != "assistant":
                    continue
                message = obj.get("message") or {}
                usage = message.get("usage")
                if not usage:
                    continue

                model = message.get("model", "unknown")
                cc_total = usage.get("cache_creation_input_tokens", 0) or 0
                cache_creation = usage.get("cache_creation") or {}
                c5m = cache_creation.get("ephemeral_5m_input_tokens", 0) or 0
                c1h = cache_creation.get("ephemeral_1h_input_tokens", 0) or 0
                if not cache_creation and cc_total:
                    c5m = cc_total  # assume 5m default if no breakdown given

                msg_id = message.get("id")
                key = (msg_id, usage.get("input_tokens"), usage.get("output_tokens"),
                       cc_total, usage.get("cache_read_input_tokens"))
                if msg_id:
                    if key in seen:
                        continue
                    seen.add(key)

                u = usage_by_model[model]
                u["input_tokens"] += usage.get("input_tokens", 0) or 0
                u["output_tokens"] += usage.get("output_tokens", 0) or 0
                u["cache_5m_tokens"] += c5m
                u["cache_1h_tokens"] += c1h
                u["cache_read_input_tokens"] += usage.get("cache_read_input_tokens", 0) or 0

    return usage_by_model, min_ts, max_ts


def price_usage(usage_by_model: dict):
    rows = []
    total_cost = 0.0
    unpriced = []
    for model, u in sorted(usage_by_model.items(), key=lambda kv: -kv[1]["output_tokens"]):
        if u["input_tokens"] == u["output_tokens"] == u["cache_5m_tokens"] == u["cache_1h_tokens"] == u["cache_read_input_tokens"] == 0:
            continue  # synthetic/empty entries
        price = PRICING.get(model)
        if not price:
            unpriced.append((model, u))
            continue
        in_price = price["input"] / 1_000_000
        out_price = price["output"] / 1_000_000
        cost = (
            u["input_tokens"] * in_price
            + u["output_tokens"] * out_price
            + u["cache_5m_tokens"] * in_price * CACHE_WRITE_5M_MULT
            + u["cache_1h_tokens"] * in_price * CACHE_WRITE_1H_MULT
            + u["cache_read_input_tokens"] * in_price * CACHE_READ_MULT
        )
        total_cost += cost
        rows.append((model, u, cost))
    return rows, total_cost, unpriced


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    slug = project_slug(target)
    files = find_transcript_files(slug)

    if not files:
        print(f"No session transcripts found for project slug: {slug}")
        sys.exit(1)

    usage_by_model, min_ts, max_ts = collect_usage(files)
    rows, total_cost, unpriced = price_usage(usage_by_model)

    print(f"Project: {target}")
    print(f"Sessions scanned: {len(files)}")
    print(f"Date range: {min_ts}  ->  {max_ts}")
    print()

    header = f"| {'Model':<18} | {'Input':>12} | {'Output':>12} | {'Cache read':>14} | {'Cost':>10} |"
    print(header)
    print("|" + "-" * (len(header) - 2) + "|")
    for model, u, cost in rows:
        print(f"| {model:<18} | {u['input_tokens']:>12,} | {u['output_tokens']:>12,} | {u['cache_read_input_tokens']:>14,} | ${cost:>9,.2f} |")
    print(f"| {'Total':<18} | {'':>12} | {'':>12} | {'':>14} | ${total_cost:>9,.2f} |")

    if unpriced:
        print()
        print("Models with usage but no pricing entry (add to PRICING in this script):")
        for model, u in unpriced:
            print(f"  - {model}: {u}")


if __name__ == "__main__":
    main()
