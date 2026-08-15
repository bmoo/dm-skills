"""Ingest saved review decisions into the Approved Reward Pool.

Run by the agent after the DM says the review is done::

    python ingest.py --data review-data.json --state decisions.json --pool-out <pool.md>

Validates both files with ``review_state`` first; any defect prints to stderr
and exits 1 **without writing anything**, so a malformed or stale browser
payload can never corrupt the pool. On success it rewrites ``--pool-out`` with
the narrow consumer contract (proposal standard, reviewed party level,
Protected Challenges considered, Eligible Now entries — never rules text,
deferrals, removals, notes, or awarded history) and prints the change report
(additions / retained / deferred / removed / unreviewed) to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import review_state


def load_validated(data_path: Path, state_path: Path) -> tuple[dict, dict, list[str]]:
    errors: list[str] = []
    data: Any = None
    state: Any = None
    for label, path in (("review data", data_path), ("decision state", state_path)):
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            errors.append(f"{label} file not found: {path}")
            continue
        except json.JSONDecodeError as exc:
            errors.append(f"{label} is malformed JSON: {exc}")
            continue
        if label == "review data":
            data = parsed
        else:
            state = parsed
    if data is not None:
        errors.extend(review_state.validate_review_data(data))
    if not errors and state is not None:
        errors.extend(review_state.validate_state(state, data))
    return data, state, errors


def _entry_line(entry: dict[str, Any], suffix: str = "") -> str:
    target = "the whole party" if entry["target"] == "party" else entry["target"]
    return (
        f"- **{entry['name']}** ({entry['rarity']}, {entry['attunement']}) — "
        f"{target} — {entry['fitNote']}{suffix}"
    )


def pool_markdown(data: dict[str, Any], eligible: list[dict[str, Any]]) -> str:
    challenges = "; ".join(data["protectedChallenges"]) or "none"
    lines = [
        "# Approved Reward Pool",
        "",
        f"**Proposal standard:** {data['proposalStandard']}",
        "",
        f"Reviewed at party level {data['partyLevel']}. "
        f"Protected Challenges considered: {challenges}.",
        "",
        "Session-building skills may place an item silently only if it is listed",
        "under Eligible Now. Everything else needs the DM's yes.",
        "",
        "## Eligible Now",
        "",
    ]
    if eligible:
        lines.extend(_entry_line(e) for e in eligible)
    else:
        lines.append("*(none — no items are currently approved for silent placement)*")
    lines.append("")
    return "\n".join(lines)


def change_report(data: dict[str, Any], state: dict[str, Any]) -> tuple[list[dict], str]:
    """The eligible list plus the human-facing report of what changed."""
    buckets: dict[str, list[str]] = {
        "Additions": [], "Retained": [], "Deferred": [], "Removed": [], "Left unreviewed": [],
    }
    eligible: list[dict[str, Any]] = []
    for entry in data["entries"]:
        if entry["origin"] == "awarded":
            continue
        untouched_graveyard = (
            entry["origin"] == "graveyard" and entry["id"] not in state["decisions"]
        )
        if untouched_graveyard:
            continue  # removed in a prior review and not restored — no change to report
        decision = review_state.decision_for(entry, state)
        record = state["decisions"].get(entry["id"], {})
        note = f" — note: {record['note']}" if record.get("note") else ""
        if decision == "approve":
            eligible.append(entry)
            bucket = "Retained" if entry["origin"] == "existing" else "Additions"
            buckets[bucket].append(f"**{entry['name']}**{note}")
        elif decision == "defer":
            condition = record.get("deferCondition", "").strip() or "no condition recorded"
            buckets["Deferred"].append(f"**{entry['name']}** — until: {condition}{note}")
        elif decision == "remove":
            buckets["Removed"].append(f"**{entry['name']}**{note}")
        else:
            buckets["Left unreviewed"].append(f"**{entry['name']}**{note}")

    lines = ["## Reward review — what changed", ""]
    for label, items in buckets.items():
        lines.append(f"**{label} ({len(items)}):**")
        if items:
            lines.extend(f"- {item}" for item in items)
        else:
            lines.append("- none")
        lines.append("")
    return eligible, "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--pool-out", required=True, type=Path)
    args = parser.parse_args(argv)

    data, state, errors = load_validated(args.data, args.state)
    if errors:
        print("ingest refused — nothing was written:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    eligible, report = change_report(data, state)
    args.pool_out.write_text(pool_markdown(data, eligible), encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
