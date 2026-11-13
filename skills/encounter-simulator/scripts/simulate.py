"""Check, review, run, or replay a scenario file.

    simulate.py check  <scenario.json>
    simulate.py review <scenario.json>
    simulate.py run    <scenario.json> [--runs 1000] [--seed 1] [--json out.json]
    simulate.py replay <scenario.json> --record <record.json> [--runs 1000] [--seed 1]

The scenario's shape is stated in scenario-format.md beside the skill.
"""

import argparse
import json
import sys

import report
from scenario import action_gap, check, load, unmodelled


def _effects_text(effects):
    parts = []
    for e in effects:
        kind = e.get("kind")
        if kind == "attack":
            text = f"attack {e['to_hit']:+d}"
            text += " with advantage" if e.get("advantage") else ""
            text += f", critical on {e['crit_from']}+" if "crit_from" in e else ""
            text += f", hit: {_effects_text(e['hit'])}"
            parts.append(text + (f", miss: {_effects_text(e['miss'])}" if e.get("miss") else ""))
        elif kind == "save":
            text = f"{e['ability']} save DC {e['dc']}, fail: {_effects_text(e['fail'])}"
            if e.get("half_on_success"):
                text += ", half damage on a success"
            parts.append(text + (f", success: {_effects_text(e['success'])}" if e.get("success") else ""))
        elif kind == "damage":
            parts.append(f"{e['dice']} {e.get('type', '')}".strip() + " damage")
        elif kind == "condition":
            d = e["duration"]
            how = (f"for {d['rounds']} of its turns" if "rounds" in d
                   else "until the source's next turn" if d["until"] == "source turn"
                   else f"until a {d['ability']} save DC {d['dc']}")
            parts.append(f"{e['name']} {how}")
        elif kind == "heal":
            parts.append(f"heal {e['dice']}")
        elif kind == "move":
            where = e.get("zone") if e["direction"] == "to" else e["direction"]
            parts.append(f"move the {e['subject']} {e['feet']} ft {where}")
        elif kind == "area":
            cap = f"up to {e['max']} " if "max" in e else "all "
            parts.append(f"area on {cap}{e['who']} in the zone: {_effects_text(e['effects'])}")
        else:
            parts.append(f"[{kind}]")
    return "; ".join(parts)


def _action_text(a):
    reach = a.get("reach", "melee")
    where = reach if isinstance(reach, str) else f"range {reach['range']}" + (f"/{reach['long']}" if "long" in reach else "")
    uses = a.get("uses")
    limit = ""
    if uses:
        limit = (f", costs {uses.get('cost', 1)} {uses['resource']}" if "resource" in uses
                 else f", {uses['per_fight']} per fight" if "per_fight" in uses
                 else f", recharge {uses['recharge']}+")
    on = {"ally": ", on an ally", "self": ", on itself"}.get(a.get("target", "enemy"), "")
    head = f"{a.get('name', a['id'])} [{a.get('time', 'action')}, {where}{on}{limit}"
    head += ", concentration]" if a.get("concentration") else "]"
    gap = action_gap(a)
    if gap:
        return f"{head} NOT MODELLED: {gap}"
    if "steps" in a:
        return f"{head} then in order: {', '.join(a['steps'])}"
    return f"{head} {_effects_text(a['effects'])}"


def review_text(sc):
    out = [f"{sc['name']} ({sc.get('sources', 'sources not stated')})"]
    out += [f"  assumption: {a}" for a in sc.get("assumptions", [])]
    out.append("Ground:")
    for z in sc["zones"]:
        extra = [f"{k} {z[k]}" for k in ("cover", "light", "elevation", "capacity") if k in z]
        extra += ["hazard: " + _effects_text(z["hazard"])] if z.get("hazard") else []
        roles = f" ({', '.join(z['roles'])})" if z.get("roles") else ""
        out.append(f"  {z.get('name', z['id'])}{roles}" + (": " + ", ".join(extra) if extra else ""))
    for link in sc.get("links", []):
        out.append(f"  {link['between'][0]} to {link['between'][1]}: {link['feet']} ft")
    for c in sc["combatants"]:
        count = f" x{c['count']}" if c.get("count", 1) > 1 else ""
        where = c.get("zone") or "off the field"
        out.append(f"{c.get('name', c['id'])}{count} [{c['side']}{', PC' if c.get('pc') else ''}, {where}] "
                   f"AC {c['ac']}, HP {c['hp']}, speed {c.get('speed', 30)}, initiative {c.get('initiative', 0):+d}")
        if c.get("saves"):
            out.append("  saves: " + ", ".join(f"{k} {v:+d}" for k, v in c["saves"].items()))
        for k in ("resistances", "immunities", "vulnerabilities", "condition_immunities", "senses", "movement"):
            if c.get(k):
                out.append(f"  {k.replace('_', ' ')}: {', '.join(c[k])}")
        if c.get("resources"):
            out.append("  resources: " + ", ".join(f"{k} {v}" for k, v in c["resources"].items()))
        out += [f"  - {_action_text(a)}" for a in c["actions"]]
        t = c.get("tactics", {})
        plan = ", then ".join(
            p["use"] + (f" when {json.dumps(p['when'])}" if p.get("when") else "") for p in t.get("plan", [])
        ) or "its actions in the order listed"
        out.append(f"  tactics: target {t.get('target', 'nearest')}"
                   + (f", first {', '.join(t['focus'])}" if t.get("focus") else "")
                   + f"; position {json.dumps(t.get('position', 'close'))}; plan: {plan}"
                   + (f"; flees when {json.dumps(t['flee'])}" if t.get("flee") else ""))
        out += [f"  NOT MODELLED: {note}" for note in c.get("unmodelled", [])]
    for e in sc.get("events", []):
        detail = {k: v for k, v in e.items() if k not in ("round", "kind")}
        out.append(f"Event, round {e['round']}: {e['kind']} {json.dumps(detail)}")
    for side, goal in sc["objectives"].items():
        out.append(f"{side} wins when any of: " + "; ".join(json.dumps(w) for w in goal["wins"]))
    for v in sc.get("variants", []):
        change = {k: val for k, val in v.items() if k != "name"}
        out.append(f"Variant: {v['name']} {json.dumps(change)}")
    gaps = unmodelled(sc)
    out.append(f"{len(gaps)} item(s) not modelled." if gaps else "Everything compiled is modelled.")
    return "\n".join(out) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("check", "review", "run", "replay"))
    parser.add_argument("scenario")
    parser.add_argument("--runs", type=int, default=1000)
    parser.add_argument("--seed", default="1")
    parser.add_argument("--json", help="also write the numbers to this file")
    parser.add_argument("--out", help="write the report to this file and print only where it went")
    parser.add_argument("--record", help="replay: the played fight's recorded numbers")
    args = parser.parse_args(argv)

    sc = load(args.scenario)
    errors = check(sc)
    if errors:
        print(f"{len(errors)} problem(s) in {args.scenario}:")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    if args.command == "check":
        print(f"OK: {len(sc['combatants'])} combatant entries, {len(unmodelled(sc))} item(s) not modelled.")
        return 0
    if args.command == "review":
        print(review_text(sc), end="")
        return 0

    results = report.run_many(sc, args.runs, args.seed)
    if args.command == "replay":
        if not args.record:
            parser.error("replay needs --record")
        outcome = report.replay(results, load(args.record))
        text = report.render_replay(sc, outcome, args.runs, args.seed)
        payload = outcome
    else:
        summary = report.summarize(results)
        rows = report.sensitivity(sc, results, args.runs, args.seed)
        logs = report.sample_logs(sc, results, args.seed)
        text = report.render(sc, summary, rows, logs, args.seed)
        payload = {"summary": summary, "variants": rows, "unmodelled": unmodelled(sc)}
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Report written to {args.out}")
    else:
        print(text, end="")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
