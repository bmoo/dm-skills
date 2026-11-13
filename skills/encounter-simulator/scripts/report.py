import math
import random
import statistics
from collections import Counter

from engine import play
from scenario import SIDES, apply_variant, auto_variants, unmodelled

CLEAR_AT_STANDARD_ERRORS = 3.0

NEVER_MODELLED = [
    "Reactions, which include opportunity attacks. A creature leaves a zone freely.",
    "Death saving throws. A player character at 0 hit points stays down until healed.",
    "Hiding, readied actions, and anything a player improvises.",
    "Positions inside a zone. Every creature in a zone can reach every other.",
]


def run_seed(seed, label, i):
    return random.Random(f"{seed}/{label}/{i}")


def run_many(sc, runs, seed, label="baseline"):
    return [play(sc, run_seed(seed, label, i)) for i in range(runs)]


def percentile(values, p):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, math.ceil(p / 100 * len(ordered)) - 1))]


def spread(values):
    return {"mean": statistics.fmean(values), "p10": percentile(values, 10),
            "p50": percentile(values, 50), "p90": percentile(values, 90)}


def _party_taken(result):
    return sum(c["taken"] for c in result["creatures"] if c["pc"])


def _party_drops(result):
    return sum(c["drops"] for c in result["creatures"] if c["pc"])


def _by_id(result, field):
    totals = Counter()
    for c in result["creatures"]:
        totals[c["id"]] += c[field]
    return totals


def summarize(results):
    n = len(results)
    first = results[0]["creatures"]
    pcs = []
    for i, c in enumerate(first):
        if c["pc"]:
            pcs.append({
                "name": c["name"],
                "drop_rate": sum(r["creatures"][i]["drops"] > 0 for r in results) / n,
                "taken": spread([r["creatures"][i]["taken"] for r in results]),
                "dealt": spread([r["creatures"][i]["dealt"] for r in results]),
            })
    resources = []
    seen = set()
    for i, c in enumerate(first):
        for name in c["spent"]:
            if (c["id"], name) in seen:
                continue
            seen.add((c["id"], name))
            same = [j for j, o in enumerate(first) if o["id"] == c["id"]]
            spent = [statistics.fmean(r["creatures"][j]["spent"][name] for j in same) for r in results]
            resources.append({"combatant": c["id"], "resource": name, "spent": statistics.fmean(spent)})
    return {
        "runs": n,
        "objective": {
            **{side: sum(side in r["met"] for r in results) / n for side in SIDES},
            "neither": sum(not r["met"] for r in results) / n,
        },
        "rounds": {**spread([r["rounds"] for r in results]),
                   "histogram": dict(sorted(Counter(r["rounds"] for r in results).items()))},
        "pcs": pcs,
        "party": {"drops_per_fight": statistics.fmean(_party_drops(r) for r in results),
                  "hp_lost": spread([_party_taken(r) for r in results])},
        "resources": resources,
    }


def _z_rate(p1, p2, n1, n2):
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    return 0.0 if p1 == p2 else (p2 - p1) / se if se else math.inf


def _z_mean(a, b):
    se = math.sqrt(statistics.pvariance(a) / len(a) + statistics.pvariance(b) / len(b))
    diff = statistics.fmean(b) - statistics.fmean(a)
    return 0.0 if diff == 0 else diff / se if se else math.inf


def sensitivity(sc, baseline, runs, seed):
    base_rate = sum("party" in r["met"] for r in baseline) / len(baseline)
    base_drops = [_party_drops(r) for r in baseline]
    base_rounds = [r["rounds"] for r in baseline]
    rows = []
    for variant in sc.get("variants", []) + auto_variants(sc):
        results = run_many(apply_variant(sc, variant), runs, seed, variant["name"])
        rate = sum("party" in r["met"] for r in results) / runs
        drops = [_party_drops(r) for r in results]
        rounds = [r["rounds"] for r in results]
        z = max(abs(_z_rate(base_rate, rate, len(baseline), runs)),
                abs(_z_mean(base_drops, drops)), abs(_z_mean(base_rounds, rounds)))
        rows.append({
            "name": variant["name"],
            "party_objective": rate - base_rate,
            "drops_per_fight": statistics.fmean(drops) - statistics.fmean(base_drops),
            "rounds": statistics.fmean(rounds) - statistics.fmean(base_rounds),
            "clear": z >= CLEAR_AT_STANDARD_ERRORS,
        })
    rows.sort(key=lambda r: (not r["clear"], -abs(r["party_objective"]),
                             -abs(r["drops_per_fight"]), -abs(r["rounds"])))
    return rows


def sample_logs(sc, results, seed, label="baseline"):
    rounds_mid = percentile([r["rounds"] for r in results], 50)
    taken_mid = percentile([_party_taken(r) for r in results], 50)
    taken_scale = max(1, max(_party_taken(r) for r in results))
    typical = min(range(len(results)), key=lambda i: (
        abs(results[i]["rounds"] - rounds_mid) + abs(_party_taken(results[i]) - taken_mid) / taken_scale))
    worst_first = sorted(range(len(results)), key=lambda i: (
        "party" in results[i]["met"], -_party_drops(results[i]), -_party_taken(results[i])))
    bad = worst_first[len(results) // 10]
    return {name: play(sc, run_seed(seed, label, i), log=True)["log"]
            for name, i in (("typical", typical), ("bad", bad))}


def _pct(x):
    return f"{x:.0%}"


def _signed(x, digits=2):
    return f"{x:+.{digits}f}"


def render(sc, summary, rows, logs, seed):
    s = summary
    obj = s["objective"]
    out = [f"# {sc['name']}: how the fight tends to go", "",
           f"{s['runs']} runs, seed {seed}. Numbers from: {sc.get('sources', 'not stated').rstrip('.')}.", ""]
    for note in sc.get("assumptions", []):
        out.append(f"- Assumption: {note}")
    out += ["", "## Outcome", "",
            f"- The party met its objective in {_pct(obj['party'])} of runs. "
            f"The enemies met theirs in {_pct(obj['enemies'])}. Neither did in {_pct(obj['neither'])}.",
            f"- The fight ran {s['rounds']['p50']} rounds in the median run. "
            f"The middle 80% of runs took {s['rounds']['p10']} to {s['rounds']['p90']} rounds.",
            f"- The party lost {s['party']['hp_lost']['p50']} hit points in the median run "
            f"and {s['party']['hp_lost']['p90']} in a bad one (90th percentile).",
            f"- Player characters dropped to 0 hit points {s['party']['drops_per_fight']:.2f} times per fight on average.",
            "", "## Player characters", "",
            "| Character | Dropped to 0 | HP lost, median | HP lost, bad run | Damage dealt, median |",
            "|---|---|---|---|---|"]
    for pc in s["pcs"]:
        out.append(f"| {pc['name']} | {_pct(pc['drop_rate'])} of runs | {pc['taken']['p50']} "
                   f"| {pc['taken']['p90']} | {pc['dealt']['p50']} |")
    if s["resources"]:
        out += ["", "## Limited resources spent", "",
                "| Combatant | Resource | Spent per fight |", "|---|---|---|"]
        for r in s["resources"]:
            out.append(f"| {r['combatant']} | {r['resource']} | {r['spent']:.1f} |")
    if rows:
        out += ["", "## What moves the result", "",
                "Each row is the fight with one change. A row marked *within noise* did not move any "
                "headline number by more than the run-to-run noise.", "",
                "| One change | Party meets objective | PC drops per fight | Rounds | |",
                "|---|---|---|---|---|"]
        for r in rows:
            out.append(f"| {r['name']} | {r['party_objective'] * 100:+.0f} points | {_signed(r['drops_per_fight'])} "
                       f"| {_signed(r['rounds'], 1)} | {'' if r['clear'] else 'within noise'} |")
        top = rows[0]
        out += ["", f"The change that moves the result most is **{top['name']}**." if top["clear"]
                else "No single change moved the result beyond the noise."]
    for title, key in (("A typical run", "typical"), ("A bad run", "bad")):
        if logs and logs.get(key):
            out += ["", f"## {title}", "", "```", *logs[key], "```"]
    out += ["", "## Not modelled", ""]
    gaps = unmodelled(sc)
    for g in gaps:
        out.append(f"- {g['combatant']}: {g['item']} ({g['reason']})")
    out += [f"- {line}" for line in NEVER_MODELLED]
    return "\n".join(out) + "\n"


def _position(sims, recorded):
    below = sum(v < recorded for v in sims)
    equal = sum(v == recorded for v in sims)
    return (below + equal / 2) / len(sims)


def replay(results, record):
    measures = []
    if "rounds" in record:
        measures.append(("rounds", record["rounds"], [r["rounds"] for r in results]))
    for field, label in (("damage_dealt", "damage dealt by"), ("damage_taken", "damage taken by")):
        key = "dealt" if field == "damage_dealt" else "taken"
        for cid, value in record.get(field, {}).items():
            measures.append((f"{label} {cid}", value, [_by_id(r, key)[cid] for r in results]))
    rows = []
    for name, recorded, sims in measures:
        pos = _position(sims, recorded)
        rows.append({"measure": name, "recorded": recorded, "p10": percentile(sims, 10),
                     "p50": percentile(sims, 50), "p90": percentile(sims, 90),
                     "position": pos, "outside": pos < 0.10 or pos > 0.90})
    facts = []
    if "party_met_objective" in record:
        rate = sum("party" in r["met"] for r in results) / len(results)
        facts.append(f"The table's party {'met' if record['party_met_objective'] else 'did not meet'} its objective. "
                     f"The simulated party met it in {_pct(rate)} of runs.")
    for cid in record.get("dropped", []):
        rate = sum(_by_id(r, "drops")[cid] > 0 for r in results) / len(results)
        facts.append(f"{cid} dropped to 0 at the table. The simulation drops {cid} in {_pct(rate)} of runs.")
    return {"rows": rows, "facts": facts}


def render_replay(sc, outcome, runs, seed):
    out = [f"# {sc['name']}: replay check", "", f"{runs} runs, seed {seed}.", "",
           "| Measure | Recorded | Simulated median | Simulated middle 80% | Position in the spread |",
           "|---|---|---|---|---|"]
    for r in outcome["rows"]:
        out.append(f"| {r['measure']} | {r['recorded']} | {r['p50']} | {r['p10']} to {r['p90']} "
                   f"| {_pct(r['position'])}{' (outside the middle 80%)' if r['outside'] else ''} |")
    outside = sum(r["outside"] for r in outcome["rows"])
    out += ["", f"{outside} of {len(outcome['rows'])} recorded measures fall outside the middle 80% of the simulated spread.",
            "One played fight is one sample. A wide simulated spread contains almost any record, so read the "
            "position and the width together.", ""]
    out += outcome["facts"]
    return "\n".join(out) + "\n"
