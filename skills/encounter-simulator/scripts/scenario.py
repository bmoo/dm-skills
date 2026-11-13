from __future__ import annotations

import copy
import json
import re
from typing import NamedTuple

FORMAT = "encounter-scenario/1"
SIDES = ("party", "enemies")
ABILITIES = ("str", "dex", "con", "int", "wis", "cha")
DEFAULT_ROUND_LIMIT = 20

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


def unmodelled(sc):
    out = []
    for c in sc.get("combatants", []):
        who = c.get("name") or c.get("id")
        for note in c.get("unmodelled", []):
            out.append({"combatant": who, "item": note, "reason": "listed by the compile step"})
        for a in c.get("actions", []):
            gap = action_gap(a)
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


def _dice_ok(value, where, errors):
    try:
        parse_dice(value)
    except ValueError as e:
        errors.append(f"{where}: {e}")


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
        if kind == "save" and e.get("ability") not in ABILITIES:
            errors.append(f"{at}: ability must be one of {', '.join(ABILITIES)}")
        if kind == "condition":
            d = e.get("duration")
            ok = isinstance(d, dict) and (
                isinstance(d.get("rounds"), int)
                or d.get("until") == "source turn"
                or (d.get("until") == "save" and d.get("ability") in ABILITIES and isinstance(d.get("dc"), int))
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
        for k in sorted(set(entry.get("when", {})) - WHEN_KEYS):
            errors.append(f"{at}: unknown when key '{k}'")
    flee = t.get("flee")
    if flee is not None and not (isinstance(flee, dict) and set(flee) <= {"hp_below", "side_below"} and flee):
        errors.append(f"{where}: flee must be {{'hp_below': x}} or {{'side_below': x}}")


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
                if not isinstance(w.get("round"), int):
                    errors.append(f"{where}: rounds needs a whole-number 'round'")
            elif kind == "reach":
                if w.get("zone") not in zones or not (w.get("count") == "all" or isinstance(w.get("count"), int)):
                    errors.append(f"{where}: reach needs a known 'zone' and a 'count'")
            else:
                errors.append(f"{where}: kind must be 'defeat', 'rounds', or 'reach'")


def check(sc):
    errors = []
    if not _keys(sc, "scenario", TOP_KEYS, errors):
        return errors
    if sc.get("format") != FORMAT:
        errors.append(f"scenario: format must be '{FORMAT}'")
    if sc.get("first") not in (None, *SIDES):
        errors.append("scenario: first must be 'party' or 'enemies'")

    zones = set()
    for i, z in enumerate(sc.get("zones") or []):
        if _keys(z, f"zones[{i}]", ZONE_KEYS, errors) and "id" in z:
            if z["id"] in zones:
                errors.append(f"zones[{i}]: duplicate id '{z['id']}'")
            zones.add(z["id"])
            if z.get("cover", "none") not in ("none", "half", "three-quarters"):
                errors.append(f"zones[{i}]: cover must be 'none', 'half', or 'three-quarters'")
            if z.get("light", "bright") not in ("bright", "dark"):
                errors.append(f"zones[{i}]: light must be 'bright' or 'dark'")
            if "hazard" in z:
                _check_effects(z["hazard"], f"zones[{i}].hazard", zones, errors)
    if not zones:
        errors.append("scenario: needs at least one zone")
    for i, link in enumerate(sc.get("links", [])):
        ends = link.get("between") if isinstance(link, dict) else None
        if not (isinstance(ends, list) and len(ends) == 2 and set(ends) <= zones and ends[0] != ends[1]):
            errors.append(f"links[{i}]: 'between' must name two different known zones")
        elif not isinstance(link.get("feet"), (int, float)) or link["feet"] <= 0:
            errors.append(f"links[{i}]: 'feet' must be a positive number")

    combatants = sc.get("combatants") or []
    ids = {c.get("id") for c in combatants if isinstance(c, dict)}
    seen = set()
    for i, c in enumerate(combatants):
        where = f"combatants[{i}]"
        if not _keys(c, where, COMBATANT_KEYS, errors):
            continue
        where = f"combatant '{c.get('id')}'"
        if c.get("id") in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(c.get("id"))
        if c.get("side") not in SIDES:
            errors.append(f"{where}: side must be 'party' or 'enemies'")
        if c.get("zone") is not None and c.get("zone") not in zones:
            errors.append(f"{where}: unknown zone '{c.get('zone')}'")
        for k in ("ac", "hp"):
            if k in c and not (isinstance(c[k], int) and c[k] > 0):
                errors.append(f"{where}: '{k}' must be a positive whole number")
        for k in sorted(set(c.get("saves", {})) - set(ABILITIES)):
            errors.append(f"{where}: unknown save '{k}'")
        actions = c.get("actions") if isinstance(c.get("actions"), list) else []
        action_ids = {a.get("id") for a in actions if isinstance(a, dict)}
        for j, a in enumerate(actions):
            at = f"{where} action '{a.get('id') if isinstance(a, dict) else j}'"
            if not _keys(a, at, ACTION_KEYS, errors):
                continue
            if a.get("time", "action") not in ("action", "bonus"):
                errors.append(f"{at}: time must be 'action' or 'bonus'")
            if a.get("target", "enemy") not in ("enemy", "ally", "self"):
                errors.append(f"{at}: target must be 'enemy', 'ally', or 'self'")
            reach = a.get("reach", "melee")
            if not (reach in ("melee", "self") or (isinstance(reach, dict) and isinstance(reach.get("range"), (int, float)))):
                errors.append(f"{at}: reach must be 'melee', 'self', or {{'range': feet}}")
            uses = a.get("uses")
            if uses is not None:
                if not isinstance(uses, dict):
                    errors.append(f"{at}: uses must be an object")
                elif "resource" in uses and uses["resource"] not in c.get("resources", {}):
                    errors.append(f"{at}: uses unknown resource '{uses['resource']}'")
                elif not ({"resource", "per_fight", "recharge"} & set(uses)):
                    errors.append(f"{at}: uses needs 'resource', 'per_fight', or 'recharge'")
            if a.get("unmodelled"):
                continue
            if ("steps" in a) == ("effects" in a):
                errors.append(f"{at}: needs exactly one of 'effects', 'steps', or 'unmodelled'")
            for s in a.get("steps", []):
                if s not in action_ids or s == a.get("id"):
                    errors.append(f"{at}: step '{s}' must name another of this combatant's actions")
            if "effects" in a:
                _check_effects(a["effects"], f"{at}.effects", zones, errors)
        if "tactics" in c:
            _check_tactics(c["tactics"], f"{where} tactics", action_ids, ids, zones, errors)

    for i, e in enumerate(sc.get("events", [])):
        where = f"events[{i}]"
        if not isinstance(e, dict) or not isinstance(e.get("round"), int):
            errors.append(f"{where}: needs a whole-number 'round'")
            continue
        kind = e.get("kind")
        if kind in ("enter", "leave"):
            if e.get("combatant") not in ids:
                errors.append(f"{where}: unknown combatant '{e.get('combatant')}'")
            if kind == "enter" and e.get("zone") not in zones:
                errors.append(f"{where}: unknown zone '{e.get('zone')}'")
        elif kind == "zone":
            if e.get("zone") not in zones or not isinstance(e.get("set"), dict):
                errors.append(f"{where}: needs a known 'zone' and a 'set' object")
            elif "hazard" in e["set"]:
                _check_effects(e["set"]["hazard"], f"{where}.set.hazard", zones, errors)
        else:
            errors.append(f"{where}: kind must be 'enter', 'leave', or 'zone'")
        if "unless_down" in e and e["unless_down"] not in ids:
            errors.append(f"{where}: unless_down names unknown combatant '{e['unless_down']}'")

    _check_objectives(sc.get("objectives"), "objectives", ids, zones, errors)

    for i, v in enumerate(sc.get("variants", [])):
        where = f"variants[{i}]"
        if not _keys(v, where, VARIANT_KEYS, errors):
            continue
        if "objectives" in v:
            _check_objectives(v["objectives"], f"{where}.objectives", ids, zones, errors)
        for cid in list(v.get("tactics", {})) + list(v.get("counts", {})):
            if cid not in ids:
                errors.append(f"{where}: unknown combatant '{cid}'")
        if v.get("first") not in (None, *SIDES):
            errors.append(f"{where}: first must be 'party' or 'enemies'")
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
