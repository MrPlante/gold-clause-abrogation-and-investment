#!/usr/bin/env python3
"""Byte-identity guard: every stage must regenerate its shipped output exactly.

This is the replication statement (analysis/README.md) made executable. For
each requested stage it snapshots every file under manuscript/tables/ and
manuscript/figures/, runs the stage, reports any file whose bytes changed
(or that appeared/disappeared), then restores the snapshot — the working
tree is left exactly as found, pass or fail.

Any changed byte is a failure. If a stage fails here, either the builder
broke (fix it, or add the stage to run.py's FROZEN set and log it in
DISCREPANCIES.md) or the change is deliberate (rerun the stage via run.py
and commit the new output together with the source change).

Figure PDFs are covered: run.py pins SOURCE_DATE_EPOCH so matplotlib output
is byte-deterministic.

Run from the repo root:

    .venv/bin/python analysis/tests/check_byte_identity.py              # all stages
    .venv/bin/python analysis/tests/check_byte_identity.py table4 ia15  # a subset

A full pass is slow: it rebuilds every table (including reghdfe vcov calls
through the Stata bridge) and the event study. IA.19 renders from the
versioned CSV, so no Stata installation is required for it.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ANALYSIS_ROOT.parent
for _p in (str(ANALYSIS_ROOT), str(REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from run import FROZEN, STAGES  # noqa: E402  (also pins SOURCE_DATE_EPOCH)

WATCHED = (
    REPO_ROOT / "manuscript" / "tables",
    REPO_ROOT / "manuscript" / "figures",
)


def snapshot() -> dict[Path, bytes]:
    return {
        p: p.read_bytes()
        for root in WATCHED
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def restore(before: dict[Path, bytes]) -> None:
    after = snapshot()
    for path, content in before.items():
        if after.get(path) != content:
            path.write_bytes(content)
    for path in after.keys() - before.keys():
        path.unlink()


def check_stage(stage: str) -> list[str]:
    """Run one stage; return descriptions of drifted files (empty = pass)."""
    before = snapshot()
    try:
        importlib.import_module(STAGES[stage]).main()
    except Exception as exc:  # builder crash is drift too
        restore(before)
        return [f"builder raised {type(exc).__name__}: {exc}"]
    after = snapshot()
    drift = [
        f"changed: {p.relative_to(REPO_ROOT)}"
        for p in sorted(before.keys() & after.keys())
        if before[p] != after[p]
    ]
    drift += [f"created: {p.relative_to(REPO_ROOT)}" for p in sorted(after.keys() - before.keys())]
    drift += [f"deleted: {p.relative_to(REPO_ROOT)}" for p in sorted(before.keys() - after.keys())]
    restore(before)
    return drift


def main(argv: list[str] | None = None) -> int:
    requested = (argv if argv is not None else sys.argv[1:]) or list(STAGES)
    unknown = [s for s in requested if s not in STAGES]
    if unknown:
        print(f"unknown stage(s): {', '.join(unknown)} — choices: {', '.join(STAGES)}")
        return 2

    failures: dict[str, list[str]] = {}
    for stage in requested:
        if stage in FROZEN:
            print(f"[skip] {stage}: in FROZEN (see DISCREPANCIES.md)")
            continue
        drift = check_stage(stage)
        if drift:
            failures[stage] = drift
            print(f"[FAIL] {stage}")
            for line in drift:
                print(f"       {line}")
        else:
            print(f"[ ok ] {stage}")

    print(
        f"\n{len(requested) - len(failures)}/{len(requested)} stages byte-identical"
        + ("" if not failures else f"; FAILED: {', '.join(failures)}")
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
