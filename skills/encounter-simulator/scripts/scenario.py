from __future__ import annotations

import copy
import json
import math
import re
from typing import NamedTuple

FORMAT = "encounter-scenario/1"
SIDES = ("party", "enemies")
ABILITIES = ("str", "dex", "con", "int", "wis", "cha")
DEFAULT_ROUND_LIMIT = 20
# Ceilings that keep a typo from hanging a run or filling memory.
MOST_ROUNDS = 100
MOST_COPIES = 100
MOST_DICE = 100
MOST_SIDES = 1000

# What each condition does in the engine, per the 2024 Rules Glossary.
CONDITIONS = {
    "blinded": {"attacks_dis", "attacked_adv"},
    "charmed": {"spares_source"},
    "frightened": {"attacks_dis_near_source", "no_approach"},
    "grappled": {"speed0", "attacks_dis_except_source"},
    "incapacitated": {"no_act"},
    "paralyzed": {"no_act", "speed0", "autofail_str_dex", "attacked_adv", "melee_crit"},
    "poisoned": {"attacks_dis"},
    "prone": {"attacks_dis", "prone"},
    "restrained": {"speed0", "attacks_dis", "attacked_adv", "dex_save_dis"},
    "stunned": {"no_act", "autofail_str_dex", "attacked_adv"},
    "unconscious": {"no_act", "speed0", "autofail_str_dex", "attacked_adv", "melee_crit", "prone"},
}

EFFECTS = {
    "attack": ({"to_hit", "hit"}, {"miss", "advantage", "crit_from"}),
    "save": ({"ability", "dc", "fail"}, {"success", "half_on_success"}),
    "damage": ({"dice"}, {"type"}),
    "condition": ({"name", "duration"}, set()),
    "heal": ({"dice"}, set()),
    "move": ({"subject", "feet", "direction"}, {"zone"}),
    "area": ({"who", "effects"}, {"max"}),
}
NESTED = {"attack": ("hit", "miss"), "save": ("fail", "success"), "area": ("effects",)}

WHEN_KEYS = {
    "round", "round_min", "round_max", "hp_below", "ally_hp_below",
    "targets_min", "target_has", "target_lacks",
}
TARGET_POLICIES = ("nearest", "weakest", "strongest", "random")
POSITIONS = ("close", "hold", "keep range")

TOP_KEYS = ({"format", "name", "zones", "combatants", "objectives"},
            {"sources", "assumptions", "round_limit", "first", "links", "events", "variants"})
ZONE_KEYS = ({"id"}, {"name", "roles", "cover", "light", "elevation", "capacity", "hazard"})
COMBATANT_KEYS = (
    {"id", "side", "ac", "hp", "actions"},
    {"name", "count", "zone", "pc", "speed", "initiative", "saves", "surprised",
     "resistances", "immunities", "vulnerabilities", "condition_immunities",
     "senses", "movement", "resources", "tactics", "unmodelled", "source"},
)
ACTION_KEYS = ({"id"}, {"name", "time", "reach", "target", "uses", "effects", "steps",
                        "concentration", "unmodelled"})
TACTICS_KEYS = (set(), {"target", "focus", "position", "plan", "flee"})
VARIANT_KEYS = ({"name"}, {"tactics", "counts", "drop_events", "objectives", "first"})

_DICE = re.compile(r"^\s*(?:(\d+)d(\d+))?\s*(?:([+-])?\s*(\d+))?\s*$")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class Dice(NamedTuple):
    number: int
    sides: int
    bonus: int


def parse_dice(text) -> Dice:
    m = _DICE.match(str(text))
    if not m or (m.group(1) is None and m.group(4) is None):
        raise ValueError(f"not a dice expression: {text!r}")
    bonus = int(m.group(4) or 0) * (-1 if m.group(3) == "-" else 1)
    return Dice(number=int(m.group(1) or 0), sides=int(m.group(2) or 0), bonus=bonus)


ReasonNotModelled = str


def effect_gap(effects) -> ReasonNotModelled | None:
    for e in effects or []:
        kind = e.get("kind") if isinstance(e, dict) else None
        if kind not in EFFECTS:
            return f"effect kind {kind!r} is outside the closed set"
        if kind == "condition" and e.get("name") not in CONDITIONS:
            return f"condition {e.get('name')!r} is not one the engine knows"
        for key in NESTED.get(kind, ()):
            gap = effect_gap(e.get(key))
            if gap:
                return gap
    return None


def action_gap(action) -> ReasonNotModelled | None:
    if action.get("unmodelled"):
        return str(action["unmodelled"])
    if "steps" in action:
        return None
    return effect_gap(action.get("effects"))


def steps_gap(action, actions) -> ReasonNotModelled | None:
    by_id = {a["id"]: a for a in actions}
    missing = [by_id[s].get("name") or s for s in action.get("steps", []) if action_gap(by_id[s])]
    if not missing:
        return None
    if len(missing) == len(action["steps"]):
        return "never plays, because none of its steps is modelled"
    return f"plays without {', '.join(missing)}, which is not modelled"


def unmodelled(sc):
    out = []
    for c in sc.get("combatants", []):
        who = c.get("name") or c.get("id")
        for note in c.get("unmodelled", []):
            out.append({"combatant": who, "item": note, "reason": "listed by the compile step"})
        for a in c.get("actions", []):
            gap = action_gap(a) or steps_gap(a, c["actions"])
            if gap:
                out.append({"combatant": who, "item": a.get("name") or a.get("id"), "reason": gap})
    return out


def _keys(obj, where, spec, errors):
    required, optional = spec
    if not isinstance(obj, dict):
        errors.append(f"{where}: expected an object")
        return False
    for k in sorted(required - obj.keys()):
        errors.append(f"{where}: missing '{k}'")
    for k in sorted(obj.keys() - required - optional):
        errors.append(f"{where}: unknown key '{k}'")
    return True


def _whole_from(value, low):
    return isinstance(value, int) and not isinstance(value, bool) and value >= low


def _number(obj, key, where, errors, whole=False, low=None, high=None):
    if key not in obj:
        return
    value = obj[key]
    ok = not isinstance(value, bool) and isinstance(value, int if whole else (int, float)) and math.isfinite(value)
    if not ok or (low is not None and value < low):
        kind = "whole number" if whole else "number"
        errors.append(f"{where}: '{key}' must be a {kind}" + (f" of {low} or more" if low is not None else ""))
    elif high is not None and value > high:
        errors.append(f"{where}: '{key}' must be {high} or less")


def _dice_ok(value, where, errors):
    try:
        dice = parse_dice(value)
    except ValueError as e:
        errors.append(f"{where}: {e}")
        return
    if "d" in str(value).lower() and (dice.number < 1 or dice.sides < 1):
        errors.append(f"{where}: a roll needs at least one die with at least one side: {value!r}")
    elif dice.number > MOST_DICE or dice.sides > MOST_SIDES:
        errors.append(f"{where}: a roll takes at most {MOST_DICE} dice of at most {MOST_SIDES} sides: {value!r}")


def _check_zone_fields(fields, where, zones, errors):
    """One validator for a zone's fields, wherever they appear: on a zone, or in a zone event's `set`."""
    if not isinstance(fields.get("name", ""), str):
        errors.append(f"{where}: 'name' must be text")
    roles = fields.get("roles", [])
    if not (isinstance(roles, list) and all(isinstance(r, str) for r in roles)):
        errors.append(f"{where}: 'roles' must be a list of words")
    if fields.get("cover", "none") not in ("none", "half", "three-quarters"):
        errors.append(f"{where}: cover must be 'none', 'half', or 'three-quarters'")
    if fields.get("light", "bright") not in ("bright", "dark"):
        errors.append(f"{where}: light must be 'bright' or 'dark'")
    _number(fields, "elevation", where, errors)
    _number(fields, "capacity", where, errors, whole=True, low=1)
    if "hazard" in fields:
        _check_effects(fields["hazard"], f"{where}.hazard", zones, errors)
        gap = effect_gap(fields["hazard"]) if isinstance(fields["hazard"], list) else None
        if gap:
            errors.append(f"{where}.hazard: {gap}. A hazard must use the closed set")


def _check_effects(effects, where, zones, errors):
    if not isinstance(effects, list):
        errors.append(f"{where}: expected a list of effects")
        return
    for i, e in enumerate(effects):
        at = f"{where}[{i}]"
        kind = e.get("kind") if isinstance(e, dict) else None
        if kind not in EFFECTS:
            continue
        required, optional = EFFECTS[kind]
        _keys(e, at, (required | {"kind"}, optional), errors)
        if kind in ("damage", "heal") and "dice" in e:
            _dice_ok(e["dice"], at, errors)
        if not isinstance(e.get("type", ""), str):
            errors.append(f"{at}: 'type' must be a damage type in words")
        for key, whole, low in (("to_hit", True, None), ("crit_from", True, 2), ("dc", True, None),
                                ("feet", False, 0), ("max", True, 1)):
            _number(e, key, at, errors, whole, low)
        if kind == "save" and e.get("ability") not in ABILITIES:
            errors.append(f"{at}: ability must be one of {', '.join(ABILITIES)}")
        if kind == "condition":
            d = e.get("duration")
            ok = isinstance(d, dict) and (
                _whole_from(d.get("rounds"), 1)
                or d.get("until") == "source turn"
                or (d.get("until") == "save" and d.get("ability") in ABILITIES and _whole_from(d.get("dc"), 0))
            )
            if not ok:
                errors.append(f"{at}: duration must be rounds, until 'source turn', or until 'save' with ability and dc")
        if kind == "move":
            if e.get("subject") not in ("target", "self"):
                errors.append(f"{at}: subject must be 'target' or 'self'")
            if e.get("direction") not in ("away", "toward", "to"):
                errors.append(f"{at}: direction must be 'away', 'toward', or 'to'")
            if e.get("direction") == "to" and e.get("zone") not in zones:
                errors.append(f"{at}: direction 'to' needs a known zone")
        if kind == "area" and e.get("who") not in ("enemies", "allies", "all"):
            errors.append(f"{at}: who must be 'enemies', 'allies', or 'all'")
        for key in NESTED.get(kind, ()):
            if key in e:
                _check_effects(e[key], f"{at}.{key}", zones, errors)


def _check_tactics(t, where, action_ids, combatant_ids, zones, errors):
    if not _keys(t, where, TACTICS_KEYS, errors):
        return
    if t.get("target", "nearest") not in TARGET_POLICIES:
        errors.append(f"{where}: target must be one of {', '.join(TARGET_POLICIES)}")
    for f in t.get("focus", []):
        if f not in combatant_ids:
            errors.append(f"{where}: focus names unknown combatant '{f}'")
    pos = t.get("position", "close")
    if isinstance(pos, dict):
        if pos.get("go") not in zones:
            errors.append(f"{where}: position go names unknown zone '{pos.get('go')}'")
    elif pos not in POSITIONS:
        errors.append(f"{where}: position must be one of {', '.join(POSITIONS)} or {{'go': zone}}")
    for i, entry in enumerate(t.get("plan", [])):
        at = f"{where}.plan[{i}]"
        if not isinstance(entry, dict) or entry.get("use") not in action_ids:
            errors.append(f"{at}: 'use' must name one of this combatant's actions")
            continue
        for k in sorted(set(entry) - {"use", "when"}):
            errors.append(f"{at}: unknown key '{k}'")
        when = entry.get("when", {})
        if not isinstance(when, dict):
            errors.append(f"{at}: 'when' must be an object")
            continue
        for k in sorted(set(when) - WHEN_KEYS):
            errors.append(f"{at}: unknown when key '{k}'")
        for k in ("round", "round_min", "round_max", "targets_min"):
            _number(when, k, at, errors, whole=True)
        for k in ("hp_below", "ally_hp_below"):
            _number(when, k, at, errors)
    flee = t.get("flee")
    if flee is not None:
        if not (isinstance(flee, dict) and set(flee) <= {"hp_below", "side_below"} and flee):
            errors.append(f"{where}: flee must be {{'hp_below': x}} or {{'side_below': x}}")
        else:
            for k in flee:
                _number(flee, k, f"{where} flee", errors)


def _check_objectives(objectives, at, ids, zones, errors):
    objectives = objectives if isinstance(objectives, dict) else {}
    for side in SIDES:
        wins = objectives.get(side, {}).get("wins") if isinstance(objectives.get(side), dict) else None
        if not isinstance(wins, list) or not wins:
            errors.append(f"{at}: '{side}' needs a non-empty 'wins' list")
            continue
        for i, w in enumerate(wins):
            where = f"{at}.{side}.wins[{i}]"
            kind = w.get("kind") if isinstance(w, dict) else None
            if kind == "defeat":
                if w.get("side") not in SIDES and w.get("combatant") not in ids:
                    errors.append(f"{where}: defeat needs a 'side' or a known 'combatant'")
            elif kind == "rounds":
                if "round" not in w:
                    errors.append(f"{where}: rounds needs a 'round'")
                _number(w, "round", where, errors, whole=True, low=1)
            elif kind == "reach":
                count = w.get("count")
                if w.get("zone") not in zones or not (count == "all" or _whole_from(count, 1)):
                    errors.append(f"{where}: reach needs a known 'zone' and a 'count' of 1 or more, or 'all'")
            else:
                errors.append(f"{where}: kind must be 'defeat', 'rounds', or 'reach'")


def check(sc):
    errors = []
    try:
        _check_shape(sc, errors)
    except (TypeError, AttributeError, KeyError, IndexError) as e:
        errors.append(f"scenario: a value has a type the format does not allow ({e}). "
                      "Compare the file with scenario-format.md")
    return errors


def _check_shape(sc, errors):
    if not _keys(sc, "scenario", TOP_KEYS, errors):
        return errors
    if sc.get("format") != FORMAT:
        errors.append(f"scenario: format must be '{FORMAT}'")
    if sc.get("first") not in (None, *SIDES):
        errors.append("scenario: first must be 'party' or 'enemies'")
    _number(sc, "round_limit", "scenario", errors, whole=True, low=1, high=MOST_ROUNDS)
    for key in ("name", "sources"):
        if not isinstance(sc.get(key, ""), str):
            errors.append(f"scenario: '{key}' must be text")
    notes = sc.get("assumptions", [])
    if not (isinstance(notes, list) and all(isinstance(n, str) for n in notes)):
        errors.append("scenario: 'assumptions' must be a list of sentences")
    for key in ("zones", "links", "combatants", "events", "variants"):
        if not isinstance(sc.get(key, []), list):
            errors.append(f"scenario: '{key}' must be a list")
            return errors

    zones = set()
    capacity = {}
    for i, z in enumerate(sc.get("zones") or []):
        if _keys(z, f"zones[{i}]", ZONE_KEYS, errors) and "id" in z:
            if z["id"] in zones:
                errors.append(f"zones[{i}]: duplicate id '{z['id']}'")
            zones.add(z["id"])
            _check_zone_fields(z, f"zones[{i}]", zones, errors)
            if isinstance(z.get("capacity"), int):
                capacity[z["id"]] = z["capacity"]
    if not zones:
        errors.append("scenario: needs at least one zone")
    linked = {z: set() for z in zones}
    for i, link in enumerate(sc.get("links", [])):
        ends = link.get("between") if isinstance(link, dict) else None
        if not (isinstance(ends, list) and len(ends) == 2 and all(isinstance(z, str) for z in ends)
                and set(ends) <= zones and ends[0] != ends[1]):
            errors.append(f"links[{i}]: 'between' must name two different known zones")
        elif (isinstance(link.get("feet"), bool) or not isinstance(link.get("feet"), (int, float))
              or not math.isfinite(link["feet"]) or link["feet"] <= 0):
            errors.append(f"links[{i}]: 'feet' must be a positive number")
        else:
            linked[ends[0]].add(ends[1])
            linked[ends[1]].add(ends[0])
    if zones:
        start = next(z["id"] for z in sc["zones"] if isinstance(z, dict) and "id" in z)
        reached, frontier = {start}, [start]
        while frontier:
            for z in linked[frontier.pop()] - reached:
                reached.add(z)
                frontier.append(z)
        for z in sorted(zones - reached):
            errors.append(f"zones: '{z}' is not linked to the rest of the ground")

    combatants = sc.get("combatants") or []
    ids = {c.get("id") for c in combatants if isinstance(c, dict) and isinstance(c.get("id"), str)}
    off_field = {c["id"] for c in combatants
                 if isinstance(c, dict) and isinstance(c.get("id"), str) and c.get("zone") is None}
    seen = set()
    standing = {}
    for i, c in enumerate(combatants):
        where = f"combatants[{i}]"
        if not _keys(c, where, COMBATANT_KEYS, errors):
            continue
        if not isinstance(c.get("id"), str):
            errors.append(f"{where}: 'id' must be text")
            continue
        where = f"combatant '{c.get('id')}'"
        if c.get("id") in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(c.get("id"))
        if c.get("side") not in SIDES:
            errors.append(f"{where}: side must be 'party' or 'enemies'")
        for key in ("name", "source"):
            if not isinstance(c.get(key, ""), str):
                errors.append(f"{where}: '{key}' must be text")
        if c.get("zone") is not None and c.get("zone") not in zones:
            errors.append(f"{where}: unknown zone '{c.get('zone')}'")
        for key, whole, low in (("ac", True, 1), ("hp", True, 1), ("speed", False, 0), ("initiative", True, None)):
            _number(c, key, where, errors, whole, low)
        _number(c, "count", where, errors, whole=True, low=1, high=MOST_COPIES)
        for key in ("saves", "resources"):
            table = c.get(key, {})
            if not isinstance(table, dict):
                errors.append(f"{where}: '{key}' must be an object")
                continue
            for k in table:
                _number(table, k, f"{where} {key}", errors, whole=True, low=0 if key == "resources" else None)
        for k in sorted(set(c.get("saves", {}) if isinstance(c.get("saves", {}), dict) else ()) - set(ABILITIES)):
            errors.append(f"{where}: unknown save '{k}'")
        for key in ("resistances", "immunities", "vulnerabilities", "condition_immunities",
                    "senses", "movement", "unmodelled"):
            if not (isinstance(c.get(key, []), list) and all(isinstance(x, str) for x in c.get(key, []))):
                errors.append(f"{where}: '{key}' must be a list of words")
        if not isinstance(c.get("actions"), list):
            errors.append(f"{where}: 'actions' must be a list")
        count = c.get("count", 1)
        if c.get("zone") in zones and c.get("side") in SIDES and isinstance(count, int):
            standing[(c["zone"], c["side"])] = standing.get((c["zone"], c["side"]), 0) + count
        actions = c.get("actions") if isinstance(c.get("actions"), list) else []
        action_ids = set()
        for a in actions:
            if isinstance(a, dict) and isinstance(a.get("id"), str):
                if a["id"] in action_ids:
                    errors.append(f"{where}: duplicate action id '{a['id']}'")
                action_ids.add(a["id"])
        with_steps = {a["id"] for a in actions if isinstance(a, dict) and a.get("id") in action_ids and "steps" in a}
        for j, a in enumerate(actions):
            at = f"{where} action '{a.get('id') if isinstance(a, dict) else j}'"
            if not _keys(a, at, ACTION_KEYS, errors):
                continue
            if not isinstance(a.get("name", ""), str):
                errors.append(f"{at}: 'name' must be text")
            if a.get("time", "action") not in ("action", "bonus"):
                errors.append(f"{at}: time must be 'action' or 'bonus'")
            if a.get("target", "enemy") not in ("enemy", "ally", "self"):
                errors.append(f"{at}: target must be 'enemy', 'ally', or 'self'")
            reach = a.get("reach", "melee")
            if isinstance(reach, dict):
                if "range" not in reach or set(reach) - {"range", "long"}:
                    errors.append(f"{at}: a ranged reach is {{'range': feet}} with an optional 'long'")
                before = len(errors)
                _number(reach, "range", f"{at} reach", errors, low=0)
                _number(reach, "long", f"{at} reach", errors, low=0)
                if len(errors) == before and reach.get("long", reach.get("range", 0)) < reach.get("range", 0):
                    errors.append(f"{at}: 'long' must not be shorter than 'range'")
            elif reach not in ("melee", "self"):
                errors.append(f"{at}: reach must be 'melee', 'self', or {{'range': feet}}")
            uses = a.get("uses")
            if uses is not None:
                if not isinstance(uses, dict):
                    errors.append(f"{at}: uses must be an object")
                elif "resource" in uses and uses["resource"] not in c.get("resources", {}):
                    errors.append(f"{at}: uses unknown resource '{uses['resource']}'")
                elif not ({"resource", "per_fight", "recharge"} & set(uses)):
                    errors.append(f"{at}: uses needs 'resource', 'per_fight', or 'recharge'")
                else:
                    for key, low in (("cost", 1), ("per_fight", 1), ("recharge", 2)):
                        _number(uses, key, f"{at} uses", errors, whole=True, low=low)
            if a.get("unmodelled"):
                continue
            if ("steps" in a) == ("effects" in a):
                errors.append(f"{at}: needs exactly one of 'effects', 'steps', or 'unmodelled'")
            steps = a.get("steps", [])
            if not isinstance(steps, list):
                errors.append(f"{at}: 'steps' must be a list of action ids")
                steps = []
            for s in steps:
                if s not in action_ids or s == a.get("id"):
                    errors.append(f"{at}: step '{s}' must name another of this combatant's actions")
                elif s in with_steps:
                    errors.append(f"{at}: step '{s}' has steps of its own. List every attack in one action")
            if "effects" in a:
                _check_effects(a["effects"], f"{at}.effects", zones, errors)
        if "tactics" in c:
            _check_tactics(c["tactics"], f"{where} tactics", action_ids, ids, zones, errors)

    for side in SIDES:
        if not any(side == s for _, s in standing):
            errors.append(f"scenario: the {side} side needs a combatant on the field when the fight starts")
    for (zone, side), count in sorted(standing.items()):
        if count > capacity.get(zone, count):
            errors.append(f"zones: '{zone}' has a capacity of {capacity[zone]} and the {side} side starts {count} there")

    for i, e in enumerate(sc.get("events", [])):
        where = f"events[{i}]"
        if not isinstance(e, dict) or "round" not in e:
            errors.append(f"{where}: needs a whole-number 'round'")
            continue
        _number(e, "round", where, errors, whole=True, low=1)
        kind = e.get("kind")
        if kind in ("enter", "leave"):
            if e.get("combatant") not in ids:
                errors.append(f"{where}: unknown combatant '{e.get('combatant')}'")
            elif kind == "enter" and e["combatant"] not in off_field:
                errors.append(f"{where}: '{e['combatant']}' starts on the field. "
                              "An enter event needs a combatant whose zone is null")
            if kind == "enter" and e.get("zone") not in zones:
                errors.append(f"{where}: unknown zone '{e.get('zone')}'")
        elif kind == "zone":
            if e.get("zone") not in zones or not isinstance(e.get("set"), dict):
                errors.append(f"{where}: needs a known 'zone' and a 'set' object")
            elif set(e["set"]) - (ZONE_KEYS[1] - {"capacity"}):
                errors.append(f"{where}: 'set' takes name, roles, cover, light, elevation, or hazard")
            else:
                _check_zone_fields(e["set"], f"{where}.set", zones, errors)
        else:
            errors.append(f"{where}: kind must be 'enter', 'leave', or 'zone'")
        if "unless_down" in e and e["unless_down"] not in ids:
            errors.append(f"{where}: unless_down names unknown combatant '{e['unless_down']}'")

    _check_objectives(sc.get("objectives"), "objectives", ids, zones, errors)

    for i, v in enumerate(sc.get("variants", [])):
        where = f"variants[{i}]"
        if not _keys(v, where, VARIANT_KEYS, errors):
            continue
        before = len(errors)
        if not isinstance(v.get("name"), str):
            errors.append(f"{where}: 'name' must be text")
        if not (isinstance(v.get("tactics", {}), dict) and isinstance(v.get("counts", {}), dict)):
            errors.append(f"{where}: 'tactics' and 'counts' must be objects keyed by combatant id")
            continue
        for cid in list(v.get("tactics", {})) + list(v.get("counts", {})):
            if cid not in ids:
                errors.append(f"{where}: unknown combatant '{cid}'")
        events = len(sc.get("events", []))
        dropped = v.get("drop_events", [])
        if not (isinstance(dropped, list)
                and all(isinstance(n, int) and not isinstance(n, bool) and 0 <= n < events for n in dropped)):
            errors.append(f"{where}: drop_events must be a list of positions in 'events', counted from 0")
        if v.get("first") not in (None, *SIDES):
            errors.append(f"{where}: first must be 'party' or 'enemies'")
        if len(errors) == before and not before:
            errors += [f"{where} '{v['name']}': {e}" for e in check(apply_variant(sc, v))]
    return errors


RECORD_KEYS = (set(), {"rounds", "party_met_objective", "damage_dealt", "damage_taken", "dropped"})


def check_record(sc, record):
    errors = []
    if not _keys(record, "record", RECORD_KEYS, errors):
        return errors
    ids = {c["id"] for c in sc["combatants"]}
    _number(record, "rounds", "record", errors, whole=True, low=1)
    if not isinstance(record.get("party_met_objective", True), bool):
        errors.append("record: 'party_met_objective' must be true or false")
    for key in ("damage_dealt", "damage_taken"):
        table = record.get(key, {})
        if not isinstance(table, dict):
            errors.append(f"record: '{key}' must be an object keyed by combatant id")
            continue
        for cid in table:
            if cid not in ids:
                errors.append(f"record: {key} names unknown combatant '{cid}'")
            _number(table, cid, f"record {key}", errors, low=0)
    dropped = record.get("dropped", [])
    if not isinstance(dropped, list):
        errors.append("record: 'dropped' must be a list of combatant ids")
    else:
        errors += [f"record: dropped names unknown combatant '{cid}'" for cid in dropped
                   if not (isinstance(cid, str) and cid in ids)]
    return errors


def apply_variant(sc, variant):
    out = copy.deepcopy(sc)
    by_id = {c["id"]: c for c in out["combatants"]}
    for cid, card in variant.get("tactics", {}).items():
        by_id[cid]["tactics"] = copy.deepcopy(card)
    for cid, count in variant.get("counts", {}).items():
        by_id[cid]["count"] = count
    drop = set(variant.get("drop_events", []))
    out["events"] = [e for i, e in enumerate(out.get("events", [])) if i not in drop]
    if "objectives" in variant:
        out["objectives"] = copy.deepcopy(variant["objectives"])
    if variant.get("first"):
        out["first"] = variant["first"]
    out.pop("variants", None)
    return out


def auto_variants(sc):
    out = []
    for c in sc["combatants"]:
        if c["side"] != "enemies":
            continue
        n = c.get("count", 1)
        name = c.get("name") or c["id"]
        out.append({"name": f"{name}: one more", "counts": {c["id"]: n + 1}})
        if n > 1:
            out.append({"name": f"{name}: one fewer", "counts": {c["id"]: n - 1}})
    out.append({"name": "the party acts first", "first": "party"})
    out.append({"name": "the enemies act first", "first": "enemies"})
    return out
