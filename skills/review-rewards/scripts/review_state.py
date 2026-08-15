"""Shared validation for the review-rewards app's two JSON files.

Both halves of the bundled app import this module and nothing else validates:
``review_server.py`` runs ``validate_state`` on every browser save, and
``ingest.py`` runs both validators before it will rewrite the Approved Reward
Pool. Keeping the rules in one module is what makes the promise in the skill
text — a malformed or stale browser payload can never corrupt the pool — a
single place to check.

The two files (shapes documented for authors in ``../state-format.md``):

- **review data** — the catalog the agent writes once per review: campaign
  framing (party level, proposal standard, Protected Challenges, requested
  depth) plus one entry per item with its full official rules text.
- **decision state** — the file the localhost server persists as the DM
  reviews: one decision record per item id, echoing the catalog's
  ``catalogVersion`` so a stale browser tab is detected instead of ingested.

Validators return a list of error strings (empty = valid) rather than raising,
so callers can report every defect at once.
"""

from __future__ import annotations

from typing import Any

DECISIONS = {"unreviewed", "approve", "defer", "remove"}

# Where an entry came from. "awarded" is read-only history: it renders for
# loot-parity context and any decision record against it is a validation error.
# "graveyard" is an item removed in a previous review, shown collapsed until
# the DM writes an explicit decision record to restore it.
ORIGINS = {"existing", "candidate", "awarded", "graveyard"}
REVIEWABLE_ORIGINS = ORIGINS - {"awarded"}

_ENTRY_REQUIRED = ("id", "name", "source", "rarity", "attunement", "origin", "rulesText")
_REVIEWABLE_REQUIRED = ("target", "fitNote")


def validate_review_data(data: Any) -> list[str]:
    """Every defect in an agent-authored review-data payload."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["review data must be a JSON object"]

    for field, kind in (
        ("catalogVersion", str),
        ("partyLevel", int),
        ("proposalStandard", str),
        ("protectedChallenges", list),
        ("requestedDepth", dict),
        ("entries", list),
    ):
        value = data.get(field)
        if not isinstance(value, kind) or (kind is str and not value.strip()):
            errors.append(f"review data field {field!r} is missing or not a {kind.__name__}")
    if errors:
        return errors

    depth = data["requestedDepth"]
    for field in ("perPC", "party"):
        if not isinstance(depth.get(field), int) or depth[field] < 0:
            errors.append(f"requestedDepth.{field} must be a non-negative integer")
    for i, challenge in enumerate(data["protectedChallenges"]):
        if not isinstance(challenge, str) or not challenge.strip():
            errors.append(f"protectedChallenges[{i}] must be a non-empty string")

    seen_ids: set[str] = set()
    seen_identity: set[tuple[str, str]] = set()
    for i, entry in enumerate(data["entries"]):
        label = f"entries[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        for field in _ENTRY_REQUIRED:
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                errors.append(f"{label} field {field!r} is missing or empty")
        entry_id = entry.get("id")
        if isinstance(entry_id, str):
            if entry_id in seen_ids:
                errors.append(f"ambiguous item identity: duplicate id {entry_id!r}")
            seen_ids.add(entry_id)
        origin = entry.get("origin")
        if isinstance(origin, str) and origin not in ORIGINS:
            errors.append(f"{label} has unknown origin {origin!r}")
        if origin in REVIEWABLE_ORIGINS:
            for field in _REVIEWABLE_REQUIRED:
                if not isinstance(entry.get(field), str) or not entry[field].strip():
                    errors.append(f"{label} field {field!r} is required for origin {origin!r}")
        name, source = entry.get("name"), entry.get("source")
        if isinstance(name, str) and isinstance(source, str):
            identity = (name.strip().lower(), source.strip().lower())
            if identity in seen_identity:
                errors.append(f"ambiguous item identity: {name!r} from {source!r} appears twice")
            seen_identity.add(identity)
    return errors


def validate_state(state: Any, data: dict[str, Any]) -> list[str]:
    """Every defect in a decision-state payload, judged against its catalog.

    ``data`` must already have passed ``validate_review_data``.
    """
    errors: list[str] = []
    if not isinstance(state, dict):
        return ["decision state must be a JSON object"]

    version = state.get("catalogVersion")
    if not isinstance(version, str) or not version.strip():
        errors.append("decision state field 'catalogVersion' is missing or empty")
    elif version != data["catalogVersion"]:
        errors.append(
            "stale decision state: catalogVersion "
            f"{version!r} does not match the review data's {data['catalogVersion']!r}"
        )

    decisions = state.get("decisions")
    if not isinstance(decisions, dict):
        return errors + ["decision state field 'decisions' is missing or not an object"]

    entries_by_id = {e["id"]: e for e in data["entries"]}
    for item_id, record in decisions.items():
        entry = entries_by_id.get(item_id)
        if entry is None:
            errors.append(f"decision for unknown item id {item_id!r}")
            continue
        if entry["origin"] == "awarded":
            errors.append(f"decision recorded against read-only awarded item {item_id!r}")
            continue
        if not isinstance(record, dict):
            errors.append(f"decision record for {item_id!r} must be an object")
            continue
        decision = record.get("decision")
        if decision not in DECISIONS:
            errors.append(f"unknown decision {decision!r} for item {item_id!r}")
        note = record.get("note")
        if note is not None and not isinstance(note, str):
            errors.append(f"note for item {item_id!r} must be a string")
        condition = record.get("deferCondition")
        if condition is not None and not isinstance(condition, str):
            errors.append(f"deferCondition for item {item_id!r} must be a string")
        if isinstance(condition, str) and condition.strip() and decision != "defer":
            errors.append(f"deferCondition on item {item_id!r} whose decision is not 'defer'")
        unknown = set(record) - {"decision", "note", "deferCondition"}
        if unknown:
            errors.append(f"unknown field(s) {sorted(unknown)} in decision record for {item_id!r}")
    return errors


def empty_state(data: dict[str, Any]) -> dict[str, Any]:
    """The decision state a fresh review starts from."""
    return {"catalogVersion": data["catalogVersion"], "decisions": {}}


def decision_for(entry: dict[str, Any], state: dict[str, Any]) -> str:
    """The effective decision for an entry under a validated state.

    A graveyard-origin entry with no explicit record stays removed; an explicit
    record (even "unreviewed") is the DM restoring it into active review.
    """
    record = state["decisions"].get(entry["id"])
    if record is None:
        return "remove" if entry["origin"] == "graveyard" else "unreviewed"
    return record["decision"]
