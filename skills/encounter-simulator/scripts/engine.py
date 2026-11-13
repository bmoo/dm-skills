from __future__ import annotations

import heapq

from scenario import CONDITIONS, DEFAULT_ROUND_LIMIT, SIDES, action_gap, parse_dice

COVER_BONUS = {"half": 2, "three-quarters": 5}
ZoneId = str
StepCost = BudgetLeft = int
DEFEATED = ("down", "out", "fled")


class Creature:
    def __init__(self, spec, name):
        self.spec = spec
        self.id = spec["id"]
        self.name = name
        self.side = spec["side"]
        self.pc = bool(spec.get("pc"))
        self.zone = spec.get("zone")
        self.status = "up" if self.zone else "off"
        self.hp = self.max_hp = spec["hp"]
        self.actions = {a["id"]: a for a in spec["actions"]}
        self.tactics = spec.get("tactics", {})
        self.resources = dict(spec.get("resources", {}))
        self.uses_left = {a["id"]: a["uses"]["per_fight"] for a in spec["actions"]
                          if "per_fight" in (a.get("uses") or {})}
        self.recharging = set()
        self.conditions = []
        self.concentrating = None
        self.initiative = 0
        self.dealt = self.taken = self.healed = self.drops = 0

    def flags(self):
        out = set()
        for cond in self.conditions:
            out |= CONDITIONS[cond["name"]]
        return out

    def has(self, sense_or_mode):
        return sense_or_mode in self.spec.get("senses", []) or sense_or_mode in self.spec.get("movement", [])

    def speed(self):
        return 0 if "speed0" in self.flags() else self.spec.get("speed", 30)


class Fight:
    def __init__(self, sc, rng, log=False):
        self.sc = sc
        self.rng = rng
        self.log = [] if log else None
        self.round = 0
        # Damage that a save-based area deals is rolled once for every creature caught (SRD 5.2,
        # "Damage against Multiple Targets"). An attack roll inside an area still rolls its own.
        self.area_rolls: dict[int, int] | None = None
        self.zones = {z["id"]: dict(z) for z in sc["zones"]}
        self.adjacent = {z: {} for z in self.zones}
        for link in sc.get("links", []):
            a, b = link["between"]
            self.adjacent[a][b] = self.adjacent[b][a] = link["feet"]
        self.feet = {a: self._distances(a) for a in self.zones}
        self.creatures = []
        for spec in sc["combatants"]:
            count = spec.get("count", 1)
            label = spec.get("name") or spec["id"]
            for i in range(count):
                self.creatures.append(Creature(spec, label if count == 1 else f"{label} {i + 1}"))
        self.handlers = {
            "attack": self._attack, "save": self._save, "damage": self._damage,
            "condition": self._condition, "heal": self._heal, "move": self._move, "area": self._area,
        }

    def _distances(self, start, mover=None):
        best = {start: 0}
        heap = [(0, start)]
        while heap:
            d, z = heapq.heappop(heap)
            if d > best.get(z, float("inf")):
                continue
            for nxt, feet in self.adjacent[z].items():
                nd = d + (self._step_cost(mover, z, nxt) if mover else feet)
                if nd < best.get(nxt, float("inf")):
                    best[nxt] = nd
                    heapq.heappush(heap, (nd, nxt))
        return best

    def _step_cost(self, mover, a, b):
        feet = self.adjacent[a][b]
        uphill = self.zones[b].get("elevation", 0) > self.zones[a].get("elevation", 0)
        return feet * 2 if uphill and not (mover.has("fly") or mover.has("climb")) else feet

    def _path(self, mover, dest) -> list[tuple[ZoneId, StepCost]] | None:
        if dest == mover.zone:
            return []
        costs = self._distances(mover.zone, mover)
        if dest not in costs:
            return None
        route, here = [], dest
        while here != mover.zone:
            prev = min((z for z in self.adjacent[here] if z in costs
                        and costs[z] + self._step_cost(mover, z, here) == costs[here]),
                       key=lambda z: costs[z])
            route.append((here, self._step_cost(mover, prev, here)))
            here = prev
        return route[::-1]

    def _room(self, zone, side):
        cap = self.zones[zone].get("capacity")
        return cap is None or sum(1 for c in self.creatures
                                  if c.zone == zone and c.side == side and c.status == "up") < cap

    def _may_step(self, mover, here, zone):
        if not self._room(zone, mover.side):
            return False
        for cond in mover.conditions:
            src = cond.get("source")
            if "no_approach" in CONDITIONS[cond["name"]] and src and src.status == "up":
                if self.feet[zone].get(src.zone, 0) < self.feet[here].get(src.zone, 0):
                    return False
        return True

    def _route(self, mover, dest, budget) -> list[tuple[ZoneId, BudgetLeft]]:
        steps, here = [], mover.zone
        for zone, cost in self._path(mover, dest) or []:
            if cost > budget or not self._may_step(mover, here, zone):
                break
            budget -= cost
            here = zone
            steps.append((zone, budget))
        return steps

    def _walk(self, mover, dest, budget) -> BudgetLeft:
        left = budget
        for zone, left in self._route(mover, dest, budget):
            mover.zone = zone
            self._say(f"  {mover.name} moves to {self.zones[zone].get('name', zone)}")
        return left

    def _d20(self, adv=False, dis=False):
        a = self.rng.randint(1, 20)
        if adv == dis:
            return a
        b = self.rng.randint(1, 20)
        return max(a, b) if adv else min(a, b)

    def _roll(self, dice, crit=False):
        count, sides, bonus = parse_dice(dice)
        if crit:
            count *= 2
        return sum(self.rng.randint(1, sides) for _ in range(count)) + bonus

    def _say(self, text):
        if self.log is not None:
            self.log.append(text)

    def play(self):
        limit = self.sc.get("round_limit", DEFAULT_ROUND_LIMIT)
        rolled = {}
        for c in self.creatures:
            if c.status == "up":
                self._roll_initiative(c, rolled)
        met = []
        while not met and self.round < limit:
            self.round += 1
            self._say(f"Round {self.round}")
            self._fire_events(rolled)
            first = self.sc.get("first")
            order = sorted((c for c in self.creatures if c.status in ("up", "down")),
                           key=lambda c: (c.side == first, c.initiative), reverse=True)
            for c in order:
                if c.status == "up":
                    self._take_turn(c)
                    met = self._objectives_met(round_over=False)
                    if met:
                        break
            if not met:
                met = self._objectives_met(round_over=True)
        self._say("Result: " + (" and ".join(f"the {s} met the objective" for s in met)
                                or "the round limit passed with no objective met"))
        return {
            "rounds": self.round,
            "met": met,
            "creatures": [{
                "id": c.id, "name": c.name, "side": c.side, "pc": c.pc, "status": c.status,
                "dealt": c.dealt, "taken": c.taken, "healed": c.healed, "drops": c.drops,
                "spent": {k: v - c.resources[k] for k, v in c.spec.get("resources", {}).items()},
            } for c in self.creatures],
            "log": self.log,
        }

    def _roll_initiative(self, c, rolled):
        if c.id not in rolled:
            rolled[c.id] = (self._d20(dis=bool(c.spec.get("surprised"))) + c.spec.get("initiative", 0),
                            self.rng.random())
        c.initiative = rolled[c.id]

    def _fire_events(self, rolled):
        for e in self.sc.get("events", []):
            if e["round"] != self.round or self._guard_tripped(e):
                continue
            if e["kind"] == "zone":
                self.zones[e["zone"]].update(e["set"])
                self._say(f"  {self.zones[e['zone']].get('name', e['zone'])} changes")
                continue
            for c in self.creatures:
                if c.id != e["combatant"]:
                    continue
                if e["kind"] == "enter" and c.status == "off":
                    c.zone, c.status = e["zone"], "up"
                    self._roll_initiative(c, rolled)
                    self._say(f"  {c.name} enters at {self.zones[c.zone].get('name', c.zone)}")
                elif e["kind"] == "leave" and c.status != "off":
                    c.status = "gone"
                    self._end_concentration(c)
                    self._say(f"  {c.name} leaves")

    def _guard_tripped(self, event):
        guard = event.get("unless_down")
        return guard and all(c.status in DEFEATED for c in self.creatures if c.id == guard)

    def _objectives_met(self, round_over):
        return [side for side in SIDES
                if any(self._holds(side, w, round_over) for w in self.sc["objectives"][side]["wins"])]

    def _holds(self, side, win, round_over):
        if win["kind"] == "rounds":
            return round_over and self.round >= win["round"]
        if win["kind"] == "reach":
            here = sum(1 for c in self.creatures if c.side == side and c.status == "up" and c.zone == win["zone"])
            standing = sum(1 for c in self.creatures if c.side == side and c.status == "up")
            return here > 0 and here >= (standing if win["count"] == "all" else win["count"])
        if "combatant" in win:
            return all(c.status in ("down", "out") for c in self.creatures if c.id == win["combatant"])
        foes = [c for c in self.creatures if c.side == win["side"]]
        if any(c.status == "up" for c in foes):
            return False
        still_to_come = any(
            e["kind"] == "enter" and e["round"] > self.round and not self._guard_tripped(e)
            and any(c.id == e["combatant"] and c.status == "off" for c in foes)
            for e in self.sc.get("events", []))
        return not still_to_come and any(c.status in DEFEATED for c in foes)

    def _take_turn(self, c):
        for other in self.creatures:
            other.conditions = [k for k in other.conditions
                                if not (k.get("until") == "source turn" and k.get("source") is c)]
        for action_id in sorted(c.recharging):
            if self.rng.randint(1, 6) >= c.actions[action_id]["uses"]["recharge"]:
                c.recharging.discard(action_id)
        hazard = self.zones[c.zone].get("hazard")
        if hazard:
            self._apply(hazard, None, c, {})
        if c.status == "up" and "no_act" not in c.flags():
            self._say(f" {c.name} ({c.hp}/{c.max_hp} hp)")
            if self._flees(c):
                c.status = "fled"
                self._end_concentration(c)
                self._say(f"  {c.name} flees")
                return
            budget = c.speed()
            if budget and any(k["name"] == "prone" for k in c.conditions):
                c.conditions = [k for k in c.conditions if k["name"] != "prone"]
                budget -= budget // 2
            budget = self._reposition(c, budget)
            acted, budget = self._act(c, "action", budget)
            self._act(c, "bonus", budget)
            if not acted and c.status == "up" and c.tactics.get("position", "close") == "close":
                foes = [f for f in self.creatures if f.side != c.side and f.status == "up"]
                if foes:
                    nearest = min(foes, key=lambda f: self.feet[c.zone].get(f.zone, float("inf")))
                    self._walk(c, nearest.zone, budget + c.speed())
        if c.status == "up":
            self._end_turn(c)

    def _end_turn(self, c):
        kept = []
        for cond in c.conditions:
            if cond.get("until") == "save" and self._saves(c, cond["ability"], cond["dc"], None):
                self._say(f"  {c.name} shakes off {cond['name']}")
                continue
            if cond.get("until") == "source turn" and (cond["source"] is None or cond["source"].status != "up"):
                continue
            if "rounds" in cond:
                cond["rounds"] -= 1
                if cond["rounds"] <= 0:
                    continue
            kept.append(cond)
        c.conditions = kept

    def _flees(self, c):
        flee = c.tactics.get("flee") or {}
        if "hp_below" in flee and c.hp / c.max_hp < flee["hp_below"]:
            return True
        if "side_below" in flee:
            side = [o for o in self.creatures if o.side == c.side and o.status not in ("off", "gone")]
            return sum(o.status == "up" for o in side) / len(side) < flee["side_below"]
        return False

    def _reposition(self, c, budget):
        position = c.tactics.get("position", "close")
        if isinstance(position, dict):
            return self._walk(c, position["go"], budget)
        if position == "keep range" and self._foes_in(c, c.zone):
            clear = [(cost, z) for z, cost in ((z, self._step_cost(c, c.zone, z)) for z in self.adjacent[c.zone])
                     if cost <= budget and not self._foes_in(c, z) and self._may_step(c, c.zone, z)]
            if clear:
                return self._walk(c, min(clear)[1], budget)
        return budget

    def _foes_in(self, c, zone):
        return [f for f in self.creatures if f.side != c.side and f.status == "up" and f.zone == zone]

    def _act(self, c, time, budget):
        plan = c.tactics.get("plan") or [{"use": a_id} for a_id in c.actions]
        for entry in plan:
            action = c.actions[entry["use"]]
            when = entry.get("when", {})
            if (action.get("time", "action") != time or action_gap(action)
                    or not self._available(c, action) or not self._when_self(c, when)):
                continue
            steps = [c.actions[s] for s in action["steps"]] if "steps" in action else [action]
            steps = [s for s in steps if not action_gap(s)]
            done = False
            for step in steps:
                if c.status != "up":
                    break
                picked = self._pick_target(c, step, {} if done else when, budget)
                if picked is None:
                    continue
                target, dest = picked
                if not done:
                    self._spend(c, action)
                    done = True
                budget = self._walk(c, dest, budget)
                self._say(f"  {c.name} uses {step.get('name', step['id'])} on {target.name}")
                if step.get("concentration"):
                    self._end_concentration(c)
                    c.concentrating = step["id"]
                self._apply(step["effects"], c, target, step)
            if done:
                return True, budget
        return False, budget

    def _available(self, c, action):
        uses = action.get("uses") or {}
        if "resource" in uses and c.resources[uses["resource"]] < uses.get("cost", 1):
            return False
        if "per_fight" in uses and c.uses_left[action["id"]] <= 0:
            return False
        return action["id"] not in c.recharging

    def _spend(self, c, action):
        uses = action.get("uses") or {}
        if "resource" in uses:
            c.resources[uses["resource"]] -= uses.get("cost", 1)
        if "per_fight" in uses:
            c.uses_left[action["id"]] -= 1
        if "recharge" in uses:
            c.recharging.add(action["id"])

    def _when_self(self, c, when):
        return (when.get("round", self.round) == self.round
                and when.get("round_min", self.round) <= self.round <= when.get("round_max", self.round)
                and ("hp_below" not in when or c.hp / c.max_hp < when["hp_below"]))

    def _when_target(self, c, t, when):
        names = {k["name"] for k in t.conditions}
        return (("target_has" not in when or when["target_has"] in names)
                and ("target_lacks" not in when or when["target_lacks"] not in names)
                and ("ally_hp_below" not in when or t.hp / t.max_hp < when["ally_hp_below"])
                and ("targets_min" not in when or len(self._foes_in(c, t.zone)) >= when["targets_min"]))

    def _pick_target(self, c, action, when, budget) -> tuple[Creature, ZoneId] | None:
        kind = action.get("target", "enemy")
        if kind == "self" or action.get("reach") == "self":
            return (c, c.zone) if self._when_target(c, c, when) else None
        if kind == "ally":
            pool = [o for o in self.creatures if o.side == c.side
                    and (o.status == "up" or (o.pc and o.status == "down"))]
        else:
            spared = {id(k.get("source")) for k in c.conditions if "spares_source" in CONDITIONS[k["name"]]}
            pool = [o for o in self.creatures if o.side != c.side and o.status == "up" and id(o) not in spared]
        options = []
        for t in pool:
            dest = self._zone_to_act_from(c, action, t, budget)
            if dest is not None and self._when_target(c, t, when):
                options.append((t, dest))
        if not options:
            return None
        if kind == "ally":
            return min(options, key=lambda o: o[0].hp / o[0].max_hp)
        focus = c.tactics.get("focus", [])
        focused = [o for o in options if o[0].id in focus]
        options = focused or options
        policy = c.tactics.get("target", "nearest")
        if policy == "random":
            return self.rng.choice(options)
        key = {
            "nearest": lambda o: self.feet[c.zone].get(o[0].zone, float("inf")),
            "weakest": lambda o: o[0].hp,
            "strongest": lambda o: -o[0].max_hp,
        }[policy]
        best = min(key(o) for o in options)
        return self.rng.choice([o for o in options if key(o) == best])

    def _zone_to_act_from(self, c, action, target, budget) -> ZoneId | None:
        reach = action.get("reach", "melee")
        position = c.tactics.get("position", "close")
        if reach == "melee":
            if target.zone == c.zone:
                return c.zone
            route = self._route(c, target.zone, budget) if position == "close" else []
            return target.zone if route and route[-1][0] == target.zone else None
        normal, far = reach["range"], reach.get("long", reach["range"])
        gap = self.feet[c.zone].get(target.zone, float("inf"))
        if gap <= normal or position == "hold" or isinstance(position, dict):
            return c.zone if gap <= far else None
        here = c.zone
        for zone, _ in self._route(c, target.zone, budget):
            if position == "keep range" and self._foes_in(c, zone):
                break
            here = zone
            if self.feet[here][target.zone] <= normal:
                break
        return here if self.feet[here].get(target.zone, float("inf")) <= far else None

    def _apply(self, effects, source, target, action, crit=False, half=False):
        for e in effects:
            if target.status in ("out", "fled", "gone"):
                return
            self.handlers[e["kind"]](e, source, target, action, crit, half)

    def _attack_mods(self, source, target, action):
        tf = target.flags()
        if source is None:
            return "attacked_adv" in tf, False
        sf = source.flags()
        same = source.zone == target.zone
        adv = "attacked_adv" in tf or ("prone" in tf and same)
        dis = "attacks_dis" in sf or ("prone" in tf and not same)
        for cond in source.conditions:
            f, src = CONDITIONS[cond["name"]], cond.get("source")
            if "attacks_dis_near_source" in f and src and src.status == "up":
                dis = True
            if "attacks_dis_except_source" in f and src is not target:
                dis = True
        reach = action.get("reach", "melee")
        if isinstance(reach, dict):
            if any("no_act" not in f.flags() for f in self._foes_in(source, source.zone)):
                dis = True
            if self.feet[source.zone].get(target.zone, 0) > reach["range"]:
                dis = True
        if self.zones[target.zone].get("light") == "dark" and not source.has("darkvision"):
            dis = True
        if self.zones[source.zone].get("light") == "dark" and not target.has("darkvision"):
            adv = True
        return adv, dis

    def _cover(self, source, target):
        if source is None or source.zone == target.zone:
            return 0
        return COVER_BONUS.get(self.zones[target.zone].get("cover", "none"), 0)

    def _attack(self, e, source, target, action, crit, half):
        if target.status != "up":
            return
        adv, dis = self._attack_mods(source, target, action)
        adv = adv or bool(e.get("advantage"))
        roll = self._d20(adv, dis)
        hit = roll == 20 or (roll != 1 and roll + e["to_hit"] >= target.spec["ac"] + self._cover(source, target))
        crit = hit and (roll >= e.get("crit_from", 20) or ("melee_crit" in target.flags() and source is not None
                                                           and source.zone == target.zone))
        self._say(f"   d20 {roll}{' with advantage' if adv and not dis else ''}"
                  f"{' with disadvantage' if dis and not adv else ''}: "
                  f"{'critical hit' if crit else 'hit' if hit else 'miss'}")
        shared, self.area_rolls = self.area_rolls, None
        self._apply(e["hit"] if hit else e.get("miss", []), source, target, action, crit=crit)
        self.area_rolls = shared

    def _saves(self, target, ability, dc, source):
        tf = target.flags()
        if ability in ("str", "dex") and "autofail_str_dex" in tf:
            return False
        bonus = target.spec.get("saves", {}).get(ability, 0)
        if ability == "dex":
            bonus += self._cover(source, target)
        return self._d20(dis=ability == "dex" and "dex_save_dis" in tf) + bonus >= dc

    def _save(self, e, source, target, action, crit, half):
        if target.status != "up":
            return
        saved = self._saves(target, e["ability"], e["dc"], source)
        self._say(f"   {target.name} {'makes' if saved else 'fails'} the {e['ability']} save")
        if not saved:
            self._apply(e["fail"], source, target, action)
            return
        if e.get("half_on_success"):
            self._apply([x for x in e["fail"] if x["kind"] == "damage"], source, target, action, half=True)
        self._apply(e.get("success", []), source, target, action)

    def _damage(self, e, source, target, action, crit, half):
        if target.status != "up":
            return
        if self.area_rolls is None:
            amount = max(self._roll(e["dice"], crit), 0)
        else:
            if id(e) not in self.area_rolls:
                self.area_rolls[id(e)] = max(self._roll(e["dice"]), 0)
            amount = self.area_rolls[id(e)]
        if half:
            amount //= 2
        kind = e.get("type")
        if kind in target.spec.get("immunities", []):
            amount = 0
        if kind in target.spec.get("resistances", []):
            amount //= 2
        if kind in target.spec.get("vulnerabilities", []):
            amount *= 2
        lost = min(amount, target.hp)
        target.hp -= lost
        target.taken += lost
        if source is not None:
            source.dealt += lost
        self._say(f"   {target.name} takes {amount}{' ' + kind if kind else ''} damage ({target.hp}/{target.max_hp} hp)")
        if target.hp == 0:
            target.status = "down" if target.pc else "out"
            target.drops += 1
            self._end_concentration(target)
            self._say(f"   {target.name} drops")
        elif target.concentrating and lost and not self._saves(target, "con", min(max(10, amount // 2), 30), None):
            self._end_concentration(target)
            self._say(f"   {target.name} loses concentration")

    def _condition(self, e, source, target, action, crit, half):
        if target.status != "up":
            return
        if e["name"] in target.spec.get("condition_immunities", []):
            self._say(f"   {target.name} is immune to {e['name']}")
            return
        target.conditions = [k for k in target.conditions
                             if not (k["name"] == e["name"] and k.get("source") is source)]
        target.conditions.append({"name": e["name"], "source": source, **e["duration"],
                                  "concentration": bool(action.get("concentration"))})
        if "no_act" in CONDITIONS[e["name"]]:
            self._end_concentration(target)
        self._say(f"   {target.name} is {e['name']}")

    def _end_concentration(self, c):
        if c.concentrating is None:
            return
        c.concentrating = None
        for other in self.creatures:
            other.conditions = [k for k in other.conditions
                                if not (k.get("concentration") and k.get("source") is c)]

    def _heal(self, e, source, target, action, crit, half):
        gained = min(max(self._roll(e["dice"]), 0), target.max_hp - target.hp)
        target.hp += gained
        if source is not None:
            source.healed += gained
        if target.status == "down" and target.hp > 0:
            target.status = "up"
        self._say(f"   {target.name} regains {gained} hp ({target.hp}/{target.max_hp} hp)")

    def _move(self, e, source, target, action, crit, half):
        subject, other = (target, source) if e["subject"] == "target" else (source, target)
        if subject is None or subject.status != "up":
            return
        near = {z: feet for z, feet in self.adjacent[subject.zone].items()
                if feet <= e["feet"] and self._room(z, subject.side)}
        if e["direction"] == "to":
            dest = e["zone"] if e["zone"] in near else None
        else:
            if other is None:
                return
            sign = 1 if e["direction"] == "away" else -1
            here = self.feet[subject.zone].get(other.zone, 0)
            better = [z for z in near if sign * (self.feet[z].get(other.zone, 0) - here) > 0]
            dest = max(better, key=lambda z: sign * self.feet[z].get(other.zone, 0)) if better else None
        if dest:
            subject.zone = dest
            self._say(f"   {subject.name} is moved to {self.zones[dest].get('name', dest)}")

    def _area(self, e, source, target, action, crit, half):
        side = source.side if source is not None else None
        pool = [c for c in self.creatures if c.zone == target.zone and c.status == "up" and c is not target and (
            e["who"] == "all" and c is not source
            or e["who"] == "enemies" and c.side != side
            or e["who"] == "allies" and c.side == side)]
        self.rng.shuffle(pool)
        primary_fits = target.status == "up" and target is not source and (
            e["who"] == "all" or (e["who"] == "enemies") == (target.side != side))
        caught = ([target] if primary_fits else []) + pool
        outer, self.area_rolls = self.area_rolls, {}
        for c in caught[:e.get("max", len(caught))]:
            self._apply(e["effects"], source, c, action)
        self.area_rolls = outer


def play(sc, rng, log=False):
    return Fight(sc, rng, log).play()
