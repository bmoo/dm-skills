"""Validates map-catalog.json entries."""

import json
from pathlib import Path
from graph import reachable_from


def validate_map_entry(entry: dict) -> list[str]:
    """Validate a single map catalog entry. Returns list of error strings."""
    errors = []
    w, h = entry.get("image_size", [0, 0])
    rooms = entry.get("rooms", [])
    connections = entry.get("connections", [])
    room_ids = [r["id"] for r in rooms]

    # Duplicate room IDs
    seen_ids = set()
    for rid in room_ids:
        if rid in seen_ids:
            errors.append(f"Duplicate room ID: {rid}")
        seen_ids.add(rid)

    # Room bounds
    for r in rooms:
        if r["x"] < 0 or r["x"] > w or r["y"] < 0 or r["y"] > h:
            errors.append(f"Room {r['id']} at ({r['x']},{r['y']}) out of bounds ({w}x{h})")

    # Entrance tag
    entrances = [r for r in rooms if "entrance" in r.get("tags", [])]
    if not entrances:
        errors.append("No room with 'entrance' tag")

    # Connection references
    rid_set = set(room_ids)
    for c in connections:
        for key in ("from", "to"):
            if c[key] not in rid_set:
                errors.append(f"Connection references unknown room: {c[key]}")

    # Reachability (from first entrance)
    if entrances and rooms:
        start = entrances[0]["id"]
        reached = reachable_from(start, connections)
        unreachable = rid_set - reached
        if unreachable:
            errors.append(f"Rooms unreachable from {start}: {unreachable}")

    return errors


def validate_catalog(path: str) -> dict[str, list[str]]:
    """Validate entire catalog file. Returns {map_id: [errors]}."""
    data = json.loads(Path(path).read_text())
    results = {}
    maps = data if isinstance(data, list) else data.get("maps", [])
    for entry in maps:
        errs = validate_map_entry(entry)
        if errs:
            results[entry.get("id", "unknown")] = errs
    return results
