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
MOST_ROUNDS = 50
MOST_COPIES = 30
MOST_CREATURES = 60
MOST_DICE = 100
MOST_SIDES = 1000
MOST_TEXT = 2000
MOST_NESTING = 8
BIG = 1_000_000

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
TARGET_POLICIES = ("nearest", "weakest", "strongest", "random")
POSITIONS = ("close", "hold", "keep range")
NESTED = {"attack": ("hit", "miss"), "save": ("fail", "success"), "area": ("effects",)}

# The shape, stated once. Every object lists its exact keys and every leaf its type, so a value
# the table does not name is rejected. `_walk` reads this table; nothing else decides what a
# scenario may contain.
TEXT, FLAG, DICE = ("text",), ("flag",), ("dice",)


def whole(low=None, high=BIG):
    return ("whole", low, high)


def number(low=None, high=BIG):
    return ("number", low, high)


def one_of(*values):
    return ("enum", *values)


def listing(item):
    return ("list", item)


def table(value):
    return ("map", value)


def obj(required, optional=None):
    return ("object", required, optional or {})


def either(hint, *options):
    return ("either", hint, options)


def by_kind(options):
    return ("by kind", options)


ABILITY = one_of(*ABILITIES)
SIDE = one_of(*SIDES)
EFFECT_LIST = listing(("effect",))
DURATION = either(
    'must be {"rounds": n}, {"until": "source turn"}, or {"until": "save", "ability": ..., "dc": ...}',
    obj({"rounds": whole(1, MOST_ROUNDS)}),
    obj({"until": one_of("source turn")}),
    obj({"until": one_of("save"), "ability": ABILITY, "dc": whole(0, 100)}),
)
EFFECTS = {
    "attack": obj({"to_hit": whole(-100, 100), "hit": EFFECT_LIST},
                  {"miss": EFFECT_LIST, "advantage": FLAG, "crit_from": whole(2, 20)}),
    "save": obj({"ability": ABILITY, "dc": whole(0, 100), "fail": EFFECT_LIST},
                {"success": EFFECT_LIST, "half_on_success": FLAG}),
    "damage": obj({"dice": DICE}, {"type": TEXT}),
    "condition": obj({"name": TEXT, "duration": DURATION}),
    "heal": obj({"dice": DICE}),
    "move": obj({"subject": one_of("target", "self"), "feet": number(0), "direction": one_of("away", "toward", "to")},
                {"zone": TEXT}),
    "area": obj({"who": one_of("enemies", "allies", "all"), "effects": EFFECT_LIST}, {"max": whole(1, 1000)}),
}
WHEN = obj({}, {
    "round": whole(1, MOST_ROUNDS), "round_min": whole(1, MOST_ROUNDS), "round_max": whole(1, MOST_ROUNDS),
    "hp_below": number(0, 10), "ally_hp_below": number(0, 10), "targets_min": whole(0, 1000),
    "target_has": TEXT, "target_lacks": TEXT,
})
TACTICS = obj({}, {
    "target": one_of(*TARGET_POLICIES),
    "focus": listing(TEXT),
    "position": either("must be 'close', 'hold', 'keep range', or {\"go\": zone}",
                       one_of(*POSITIONS), obj({"go": TEXT})),
    "plan": listing(obj({"use": TEXT}, {"when": WHEN})),
    "flee": obj({}, {"hp_below": number(0, 10), "side_below": number(0, 10)}),
})
ACTION = obj({"id": TEXT}, {
    "name": TEXT,
    "time": one_of("action", "bonus"),
    "reach": either("must be 'melee', 'self', or {\"range\": feet}",
                    one_of("melee", "self"), obj({"range": number(0)}, {"long": number(0)})),
    "target": one_of("enemy", "ally", "self"),
    "uses": obj({}, {"resource": TEXT, "cost": whole(1, 1000), "per_fight": whole(1, 1000), "recharge": whole(2, 6)}),
    "effects": EFFECT_LIST,
    "steps": listing(TEXT),
    "concentration": FLAG,
    "unmodelled": TEXT,
})
COMBATANT = obj(
    {"id": TEXT, "side": SIDE, "ac": whole(1, 100), "hp": whole(1), "actions": listing(ACTION)},
    {"name": TEXT, "count": whole(1, MOST_COPIES), "zone": either("must be a zone id or null", ("null",), TEXT),
     "pc": FLAG, "speed": number(0, 10_000), "initiative": whole(-1000, 1000),
     "saves": obj({}, {a: whole(-100, 100) for a in ABILITIES}), "surprised": FLAG,
     "resistances": listing(TEXT), "immunities": listing(TEXT), "vulnerabilities": listing(TEXT),
     "condition_immunities": listing(TEXT), "senses": listing(TEXT), "movement": listing(TEXT),
     "resources": table(whole(0)), "tactics": TACTICS, "unmodelled": listing(TEXT), "source": TEXT},
)
ZONE_FIELDS = {
    "name": TEXT, "roles": listing(TEXT), "cover": one_of("none", "half", "three-quarters"),
    "light": one_of("bright", "dark"), "elevation": number(-BIG), "hazard": EFFECT_LIST,
}
ZONE = obj({"id": TEXT}, {**ZONE_FIELDS, "capacity": whole(1, 1000)})
EVENT_COMMON = {"unless_down": TEXT}
EVENT = by_kind({
    "enter": obj({"round": whole(1, MOST_ROUNDS), "combatant": TEXT, "zone": TEXT}, EVENT_COMMON),
    "leave": obj({"round": whole(1, MOST_ROUNDS), "combatant": TEXT}, EVENT_COMMON),
    "zone": obj({"round": whole(1, MOST_ROUNDS), "zone": TEXT, "set": obj({}, ZONE_FIELDS)}, EVENT_COMMON),
})
WIN = by_kind({
    "defeat": obj({}, {"side": SIDE, "combatant": TEXT}),
    "rounds": obj({"round": whole(1, MOST_ROUNDS)}),
    "reach": obj({"zone": TEXT, "count": either("must be 'all' or a whole number of 1 or more",
                                                one_of("all"), whole(1, 1000))}),
})
OBJECTIVES = obj({side: obj({"wins": listing(WIN)}) for side in SIDES})
VARIANT = obj({"name": TEXT}, {
    "tactics": table(TACTICS), "counts": table(whole(1, MOST_COPIES)), "drop_events": listing(whole(0, 1000)),
    "objectives": OBJECTIVES, "first": SIDE,
})
SCENARIO = obj(
    {"format": one_of(FORMAT), "name": TEXT, "zones": listing(ZONE), "combatants": listing(COMBATANT),
     "objectives": OBJECTIVES},
    {"sources": TEXT, "assumptions": listing(TEXT), "round_limit": whole(1, MOST_ROUNDS), "first": SIDE,
     "links": listing(obj({"between": listing(TEXT), "feet": number(0)})), "events": listing(EVENT),
     "variants": listing(VARIANT)},
)
RECORD = obj({}, {
    "rounds": whole(1, 1000), "party_met_objective": FLAG, "damage_dealt": table(number(0)),
    "damage_taken": table(number(0)), "dropped": listing(TEXT),
})

_DICE = re.compile(r"^\s*(?:(\d+)d(\d+))?\s*(?:([+-])?\s*(\d+))?\s*$")
_NAMED_LISTS = {"combatants": "combatant", "zones": "zone", "actions": "action"}


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
        kind = e.get("kind")
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


def _here(path, key, value):
    listed = _NAMED_LISTS.get(key.split("[")[0])
    ident = value.get("id") if isinstance(value, dict) else None
    if listed and isinstance(ident, str) and len(ident) <= 60:
        label = f"{listed} '{ident}'"
        return label if path == "scenario" else f"{path} {label}"
    return key if path == "scenario" else f"{path}.{key}"


def _walk_object(value, spec, here, errors, depth, extra=()):
    _, required, optional = spec
    if not isinstance(value, dict):
        errors.append(f"{here}: expected an object")
        return
    for k in sorted(required.keys() - value.keys()):
        errors.append(f"{here}: missing '{k}'")
    for k in sorted(k for k in value if k not in required and k not in optional and k not in extra):
        errors.append(f"{here}: unknown key '{k}'"[:200])
    for k, sub in {**optional, **required}.items():
        if k in value:
            _walk(value[k], sub, here, k, errors, depth)


def _walk(value, spec, path, key, errors, depth=0):
    kind = spec[0]
    at = f"{path}: '{key}'"
    if kind == "text":
        if not isinstance(value, str):
            errors.append(f"{at} must be text")
        elif len(value) > MOST_TEXT:
            errors.append(f"{at} must be {MOST_TEXT} characters or fewer")
        else:
            try:
                value.encode("utf-8")
            except UnicodeEncodeError:
                errors.append(f"{at} must be plain text")
    elif kind == "null":
        if value is not None:
            errors.append(f"{at} must be null")
    elif kind == "flag":
        if not isinstance(value, bool):
            errors.append(f"{at} must be true or false")
    elif kind in ("whole", "number"):
        _, low, high = spec
        ok = not isinstance(value, bool) and isinstance(value, int if kind == "whole" else (int, float))
        ok = ok and -BIG * 1000 <= value <= BIG * 1000 if ok and isinstance(value, int) else ok and math.isfinite(value)
        name = "whole number" if kind == "whole" else "number"
        if not ok or (low is not None and value < low):
            errors.append(f"{at} must be a {name}" + (f" of {low} or more" if low is not None else ""))
        elif value > high:
            errors.append(f"{at} must be {high} or less")
    elif kind == "enum":
        if not isinstance(value, str) or value not in spec[1:]:
            errors.append(f"{at} must be " + ", ".join(f"'{v}'" for v in spec[1:]))
    elif kind == "dice":
        _dice_ok(value, at, errors)
    elif kind == "list":
        if not isinstance(value, list):
            errors.append(f"{at} must be a list")
            return
        for i, item in enumerate(value):
            _walk(item, spec[1], path, f"{key}[{i}]", errors, depth)
    elif kind == "map":
        if not isinstance(value, dict):
            errors.append(f"{at} must be an object")
            return
        here = _here(path, key, value)
        for k, item in value.items():
            _walk(k, TEXT, here, "a key", errors, depth)
            _walk(item, spec[1], here, k[:60], errors, depth)
    elif kind == "object":
        _walk_object(value, spec, _here(path, key, value), errors, depth)
    elif kind == "either":
        _, hint, options = spec
        objects = [o for o in options if o[0] == "object"]
        if isinstance(value, dict) and len(objects) == 1:
            _walk(value, objects[0], path, key, errors, depth)
            return
        for option in options:
            trial = []
            _walk(value, option, path, key, trial, depth)
            if not trial:
                return
        errors.append(f"{at} {hint}")
    elif kind == "by kind":
        here = _here(path, key, value)
        choice = value.get("kind") if isinstance(value, dict) else None
        if not isinstance(choice, str) or choice not in spec[1]:
            errors.append(f"{here}: 'kind' must be " + ", ".join(f"'{k}'" for k in spec[1]))
        else:
            _walk_object(value, spec[1][choice], here, errors, depth, extra=("kind",))
    elif kind == "effect":
        here = _here(path, key, value)
        if depth > MOST_NESTING:
            errors.append(f"{here}: effects nest more than {MOST_NESTING} deep")
        elif not isinstance(value, dict):
            errors.append(f"{here}: expected an effect object")
        elif not isinstance(value.get("kind"), str):
            errors.append(f"{here}: 'kind' must be text")
        elif value["kind"] in EFFECTS:
            _walk_object(value, EFFECTS[value["kind"]], here, errors, depth + 1, extra=("kind",))
        else:
            _walk(value["kind"], TEXT, here, "kind", errors, depth)


def _dice_ok(value, at, errors):
    if isinstance(value, bool) or not isinstance(value, (str, int)) or len(str(value)) > 40:
        errors.append(f"{at} must be dice such as '2d6+3' or a flat number")
        return
    try:
        dice = parse_dice(value)
    except ValueError as e:
        errors.append(f"{at}: {e}")
        return
    if "d" in str(value).lower() and (dice.number < 1 or dice.sides < 1):
        errors.append(f"{at}: a roll needs at least one die with at least one side: {value!r}")
    elif dice.number > MOST_DICE or dice.sides > MOST_SIDES or abs(dice.bonus) > BIG:
        errors.append(f"{at}: a roll takes at most {MOST_DICE} dice of at most {MOST_SIDES} sides: {value!r}")


def _hazard_gap(fields, where, errors):
    gap = effect_gap(fields.get("hazard"))
    if gap:
        errors.append(f"{where}.hazard: {gap}. A hazard must use the closed set")


def _move_targets(effects, where, zones, errors):
    for i, e in enumerate(effects or []):
        at = f"{where}[{i}]"
        if e.get("kind") == "move" and e.get("direction") == "to" and e.get("zone") not in zones:
            errors.append(f"{at}: direction 'to' needs a known zone")
        for key in NESTED.get(e.get("kind"), ()):
            _move_targets(e.get(key), f"{at}.{key}", zones, errors)


def _tactics_meaning(card, where, action_ids, ids, zones, errors):
    for f in card.get("focus", []):
        if f not in ids:
            errors.append(f"{where}: focus names unknown combatant '{f}'")
    position = card.get("position", "close")
    if isinstance(position, dict) and position["go"] not in zones:
        errors.append(f"{where}: position go names unknown zone '{position['go']}'")
    for i, entry in enumerate(card.get("plan", [])):
        if entry["use"] not in action_ids:
            errors.append(f"{where}.plan[{i}]: 'use' must name one of this combatant's actions")
    if "flee" in card and not card["flee"]:
        errors.append(f"{where}: flee must be {{'hp_below': x}} or {{'side_below': x}}")


def _objectives_meaning(objectives, at, ids, zones, errors):
    for side in SIDES:
        wins = objectives[side]["wins"]
        if not wins:
            errors.append(f"{at}: '{side}' needs a non-empty 'wins' list")
        for i, w in enumerate(wins):
            where = f"{at}.{side}.wins[{i}]"
            if w["kind"] == "defeat":
                if ("side" in w) == ("combatant" in w):
                    errors.append(f"{where}: defeat needs a 'side' or a 'combatant', not both")
                elif "combatant" in w and w["combatant"] not in ids:
                    errors.append(f"{where}: unknown combatant '{w['combatant']}'")
            elif w["kind"] == "reach" and w["zone"] not in zones:
                errors.append(f"{where}: unknown zone '{w['zone']}'")


def _meaning(sc, errors):
    """What the shape cannot say: references, uniqueness, and whether the fight can be fought."""
    zones = set()
    capacity = {}
    for z in sc["zones"]:
        if z["id"] in zones:
            errors.append(f"zone '{z['id']}': duplicate id")
        zones.add(z["id"])
        if "capacity" in z:
            capacity[z["id"]] = z["capacity"]
        _hazard_gap(z, f"zone '{z['id']}'", errors)
    if not zones:
        errors.append("scenario: needs at least one zone")
        return
    linked = {z: set() for z in zones}
    for i, link in enumerate(sc.get("links", [])):
        ends = link["between"]
        if len(ends) != 2 or not set(ends) <= zones or ends[0] == ends[1]:
            errors.append(f"links[{i}]: 'between' must name two different known zones")
        elif link["feet"] <= 0:
            errors.append(f"links[{i}]: 'feet' must be more than 0")
        else:
            linked[ends[0]].add(ends[1])
            linked[ends[1]].add(ends[0])
    reached, frontier = {sc["zones"][0]["id"]}, [sc["zones"][0]["id"]]
    while frontier:
        for z in linked[frontier.pop()] - reached:
            reached.add(z)
            frontier.append(z)
    for z in sorted(zones - reached):
        errors.append(f"zones: '{z}' is not linked to the rest of the ground")

    combatants = sc["combatants"]
    ids = {c["id"] for c in combatants}
    off_field = {c["id"] for c in combatants if c.get("zone") is None}
    seen = set()
    standing = {}
    if sum(c.get("count", 1) for c in combatants) > MOST_CREATURES:
        errors.append(f"scenario: a fight takes at most {MOST_CREATURES} creatures in all")
    for c in combatants:
        where = f"combatant '{c['id']}'"
        if c["id"] in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(c["id"])
        zone = c.get("zone")
        if zone is not None and zone not in zones:
            errors.append(f"{where}: unknown zone '{zone}'")
        elif zone is not None:
            standing[(zone, c["side"])] = standing.get((zone, c["side"]), 0) + c.get("count", 1)
        action_ids = set()
        for a in c["actions"]:
            if a["id"] in action_ids:
                errors.append(f"{where}: duplicate action id '{a['id']}'")
            action_ids.add(a["id"])
        with_steps = {a["id"] for a in c["actions"] if "steps" in a}
        for a in c["actions"]:
            at = f"{where} action '{a['id']}'"
            reach = a.get("reach", "melee")
            if isinstance(reach, dict) and reach.get("long", reach["range"]) < reach["range"]:
                errors.append(f"{at}: 'long' must not be shorter than 'range'")
            uses = a.get("uses")
            if uses is not None:
                if not ({"resource", "per_fight", "recharge"} & set(uses)):
                    errors.append(f"{at}: uses needs 'resource', 'per_fight', or 'recharge'")
                elif "resource" in uses and uses["resource"] not in c.get("resources", {}):
                    errors.append(f"{at}: uses unknown resource '{uses['resource']}'")
            if a.get("unmodelled"):
                continue
            if ("steps" in a) == ("effects" in a):
                errors.append(f"{at}: needs exactly one of 'effects', 'steps', or 'unmodelled'")
            for s in a.get("steps", []):
                if s not in action_ids or s == a["id"]:
                    errors.append(f"{at}: step '{s}' must name another of this combatant's actions")
                elif s in with_steps:
                    errors.append(f"{at}: step '{s}' has steps of its own. List every attack in one action")
            _move_targets(a.get("effects"), f"{at}.effects", zones, errors)
        _tactics_meaning(c.get("tactics", {}), f"{where}.tactics", action_ids, ids, zones, errors)

    for side in SIDES:
        if not any(side == s for _, s in standing):
            errors.append(f"scenario: the {side} side needs a combatant on the field when the fight starts")
    for (zone, side), count in sorted(standing.items()):
        if count > capacity.get(zone, count):
            errors.append(f"zones: '{zone}' has a capacity of {capacity[zone]} and the {side} side starts {count} there")

    for i, e in enumerate(sc.get("events", [])):
        where = f"events[{i}]"
        if e["kind"] in ("enter", "leave"):
            if e["combatant"] not in ids:
                errors.append(f"{where}: unknown combatant '{e['combatant']}'")
            elif e["kind"] == "enter" and e["combatant"] not in off_field:
                errors.append(f"{where}: '{e['combatant']}' starts on the field. "
                              "An enter event needs a combatant whose zone is null")
        if "zone" in e and e["zone"] not in zones:
            errors.append(f"{where}: unknown zone '{e['zone']}'")
        if e["kind"] == "zone":
            _hazard_gap(e["set"], f"{where}.set", errors)
        if "unless_down" in e and e["unless_down"] not in ids:
            errors.append(f"{where}: unless_down names unknown combatant '{e['unless_down']}'")

    _objectives_meaning(sc["objectives"], "objectives", ids, zones, errors)

    by_id = {c["id"]: c for c in combatants}
    for i, v in enumerate(sc.get("variants", [])):
        where = f"variants[{i}]"
        before = len(errors)
        for cid in list(v.get("tactics", {})) + list(v.get("counts", {})):
            if cid not in ids:
                errors.append(f"{where}: unknown combatant '{cid}'")
        for cid, card in v.get("tactics", {}).items():
            if cid in by_id:
                action_ids = {a["id"] for a in by_id[cid]["actions"]}
                _tactics_meaning(card, f"{where}.tactics.{cid}", action_ids, ids, zones, errors)
        if any(n >= len(sc.get("events", [])) for n in v.get("drop_events", [])):
            errors.append(f"{where}: drop_events must be positions in 'events', counted from 0")
        if "objectives" in v:
            _objectives_meaning(v["objectives"], f"{where}.objectives", ids, zones, errors)
        if len(errors) == before and not before:
            errors += [f"{where} '{v['name'][:60]}': {e}" for e in check(apply_variant(sc, v))]


def check(sc):
    errors = []
    _walk(sc, SCENARIO, "scenario", "scenario", errors)
    if not errors:
        _meaning(sc, errors)
    return errors


def check_record(sc, record):
    errors = []
    _walk(record, RECORD, "scenario", "record", errors)
    if not isinstance(record, dict):
        return errors
    ids = {c["id"] for c in sc["combatants"]}
    named = [(key, cid) for key in ("damage_dealt", "damage_taken")
             if isinstance(record.get(key), dict) for cid in record[key]]
    named += [("dropped", cid) for cid in record.get("dropped", [])
              if isinstance(record.get("dropped"), list) and isinstance(cid, str)]
    errors += [f"record: {key} names unknown combatant '{cid[:60]}'" for key, cid in named if cid not in ids]
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
        if n < MOST_COPIES:
            out.append({"name": f"{name}: one more", "counts": {c["id"]: n + 1}})
        if n > 1:
            out.append({"name": f"{name}: one fewer", "counts": {c["id"]: n - 1}})
    out.append({"name": "the party acts first", "first": "party"})
    out.append({"name": "the enemies act first", "first": "enemies"})
    return out
