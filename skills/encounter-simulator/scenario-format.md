# The scenario file

A scenario is one JSON file that holds everything the engine needs to play a
fight: who is in it, what each combatant can do, the ground, the timed
changes, and what each side is trying to achieve. The engine reads this file
and nothing else. **This file is the one statement of the scenario's shape.**
`scripts/simulate.py check` enforces it, and the fixtures under
`scripts/fixtures/` are worked examples.

A scenario sits beside the fight it was compiled from and is named
`<fight-slug>.scenario.json`. The fight's `> [!encounter-meta]` block does
not change.

```json
{
  "format": "encounter-scenario/1",
  "name": "Toll road ambush",
  "sources": "bundled SRD 5.2; party sheets synced 2026-11-10",
  "assumptions": ["The barbarian rages on turn one, so rage damage and resistance are in the numbers."],
  "round_limit": 20,
  "zones": [],
  "links": [],
  "combatants": [],
  "events": [],
  "objectives": {},
  "variants": []
}
```

`format`, `name`, `zones`, `combatants`, and `objectives` are required.
`round_limit` defaults to 20. `"first": "party"` or `"first": "enemies"`
makes that whole side act before the other. Without it every combatant
rolls initiative, and a group of identical creatures shares one roll.

## Zones and links

Ground is a set of named zones, not a grid. A zone is an area where
everyone can reach everyone else in melee.

```json
"zones": [
  {"id": "road", "name": "the toll road", "roles": ["choke"], "capacity": 3},
  {"id": "rocks", "name": "the rockfall", "roles": ["cover field"], "cover": "half"},
  {"id": "ledge", "name": "the ledge", "roles": ["high position"], "elevation": 15, "light": "dark"}
],
"links": [
  {"between": ["road", "rocks"], "feet": 30},
  {"between": ["rocks", "ledge"], "feet": 20}
]
```

| Field | Meaning in the engine |
|---|---|
| `id`, `name` | `id` is what other fields point at. `name` appears in logs. |
| `roles` | The terrain roles from the fight (`high position`, `cover field`, `choke`, `hazard`). The engine does not read them. They let a floating fight keep its role names. |
| `cover` | `half` gives +2 and `three-quarters` gives +5 to the AC and the Dexterity saves of a creature in the zone, against an attack or effect from another zone. |
| `light` | `bright` (the default) or `dark`. An attacker without `darkvision` has disadvantage against a target in a dark zone. An attacker in a dark zone has advantage against a target without `darkvision`. |
| `elevation` | Height in feet. A move along a link into a higher zone costs double, unless the mover has `fly` or `climb`. |
| `capacity` | The choke. At most this many creatures per side can stand in the zone. |
| `hazard` | A list of effects (see *Effects*) that the engine applies to each creature that starts its turn in the zone. |

A link gives the distance in feet between two zones. The distance between
two unlinked zones is the shortest path. On its turn a combatant moves up
to its `speed` in feet along links, and a link it cannot afford stops it.
A combatant whose position is `close` and who has no usable action moves up
to twice its `speed` toward the nearest enemy. Creatures in the same zone are 5
feet apart. A melee attack needs the attacker and the target in one zone. A
ranged attack needs the distance to be within `range`, and has disadvantage
beyond `range` up to `long`.

## Combatants

```json
{
  "id": "bandit", "name": "Bandit", "side": "enemies", "count": 4, "zone": "rocks",
  "ac": 12, "hp": 11, "speed": 30, "initiative": 1,
  "saves": {"str": 0, "dex": 1, "con": 1, "int": 0, "wis": 0, "cha": 0},
  "resistances": [], "immunities": [], "vulnerabilities": [],
  "condition_immunities": [],
  "senses": [], "movement": [],
  "resources": {},
  "actions": [],
  "tactics": {},
  "unmodelled": ["Parry reaction"],
  "source": "SRD 5.2, Bandit"
}
```

| Field | Meaning |
|---|---|
| `id` | Unique. With `count` above 1 the engine names the copies `bandit 1`, `bandit 2`. |
| `side` | `party` or `enemies`. |
| `pc` | `true` for a player character. The report counts how often each PC dropped to 0 hit points. A PC at 0 is down and returns if healed. Any other creature at 0 is out. |
| `zone` | The starting zone. `null` means the combatant is off the field until an event brings it in. |
| `ac`, `hp`, `speed`, `initiative`, `saves` | Numbers from the stat block or sheet. `initiative` is the bonus. |
| `surprised` | `true` gives the combatant disadvantage on its initiative roll. |
| `resistances`, `immunities`, `vulnerabilities` | Damage types. |
| `condition_immunities` | Condition names. |
| `senses` | `darkvision` is the only sense the engine reads. |
| `movement` | `fly` and `climb` are the only modes the engine reads. |
| `resources` | Limited resources by name with the starting amount, for example `{"spell slot 1": 4, "second wind": 1}`. The report states how much of each was spent. |
| `unmodelled` | Traits, reactions, and features that the compile step could not express. The report lists each one. |
| `source` | Where the numbers came from. |

## Actions

An action is one thing the combatant can do on its turn.

```json
{"id": "scimitar", "name": "Scimitar", "time": "action", "reach": "melee",
 "effects": [{"kind": "attack", "to_hit": 3,
              "hit": [{"kind": "damage", "dice": "1d6+1", "type": "slashing"}]}]}
```

| Field | Meaning |
|---|---|
| `time` | `action` or `bonus`. A combatant takes at most one of each on a turn. |
| `reach` | `"melee"`, `{"range": 80, "long": 320}`, or `"self"`. `long` is optional. |
| `target` | `enemy` (the default), `ally`, or `self`. |
| `uses` | Absent means at will. `{"resource": "spell slot 1", "cost": 1}` spends a named resource. `{"per_fight": 1}` limits uses. `{"recharge": 5}` makes the action available again on a d6 roll of 5 or higher at the start of the combatant's turn. |
| `effects` | What happens, as a list of effects. |
| `steps` | Used instead of `effects` for a multiattack. A list of action ids that the combatant performs in order, each with its own target choice. |
| `concentration` | `true` for a concentration spell. Its conditions end when the caster drops, fails a Constitution save after damage, or uses another concentration action. |
| `unmodelled` | A sentence that says why the action cannot be expressed. The engine never chooses the action, and the report lists it. Such an action needs no `effects`. |

An action carries exactly one of `effects`, `steps`, or `unmodelled`.
`uses` works with any of them.

## Effects

Effects are a closed set of seven kinds. An action that needs anything else
is unmodelled.

| `kind` | Fields | What the engine does |
|---|---|---|
| `attack` | `to_hit`, `hit`, optional `miss`, `advantage`, `crit_from` | Rolls d20 plus `to_hit` against the target's AC. A natural 20 hits and doubles the dice of each `damage` in `hit`. A natural 1 misses. Applies `hit` or `miss`. `"advantage": true` is for an attacker who always has it. `"crit_from": 19` widens the critical range. |
| `save` | `ability`, `dc`, `fail`, optional `success`, optional `half_on_success` | The target rolls d20 plus its save bonus. Applies `fail` or `success`. With `half_on_success`, a success applies half of the `fail` damage and no other `fail` effect. |
| `damage` | `dice`, optional `type` | Rolls `dice` (`2d6+3`, `1d8`, or a flat `4`) and subtracts it from the target's hit points after resistance, immunity, and vulnerability. |
| `condition` | `name`, `duration` | Puts a condition on the target. `duration` is `{"rounds": 1}` (ends after that many of the target's own turns), `{"until": "source turn"}` (ends at the start of the source's next turn), or `{"until": "save", "ability": "wis", "dc": 12}` (the target repeats the save at the end of each of its turns). |
| `heal` | `dice` | Restores hit points up to the maximum. A PC at 0 returns to the fight. |
| `move` | `subject` (`target` or `self`), `feet`, `direction` (`away`, `toward`, or `to` with a `zone`) | Moves the subject along a link when `feet` covers the link's distance. |
| `area` | `who` (`enemies`, `allies`, or `all`), optional `max`, `effects` | Applies `effects` to each matching creature in the target's zone, up to `max` creatures. |

The engine knows these conditions: `blinded`, `charmed`, `frightened`,
`grappled`, `incapacitated`, `paralyzed`, `poisoned`, `prone`, `restrained`,
`stunned`, `unconscious`. A `condition` effect with any other name makes its
action unmodelled.

## Tactics cards

A tactics card says how a combatant plays. The engine walks `plan` from the
top on each turn and takes the first entry it can use for the action, and
the first it can use for the bonus action. A combatant with no `plan` tries
its actions in the order listed.

```json
"tactics": {
  "target": "weakest",
  "focus": ["bandit-captain"],
  "position": "close",
  "plan": [
    {"use": "second-wind", "when": {"hp_below": 0.5}},
    {"use": "action-surge-attack", "when": {"round": 1}},
    {"use": "longsword"}
  ],
  "flee": {"hp_below": 0.25}
}
```

| Field | Values |
|---|---|
| `target` | `nearest` (the default), `weakest` (lowest current hit points), `strongest` (highest maximum hit points), `random`. |
| `focus` | Combatant ids to attack first while any of them stands. |
| `position` | `close` (the default) walks into the target's zone for a melee action and into range for a ranged one. `hold` never moves. `keep range` steps out of a zone that holds an enemy, walks into range for a ranged action, and never walks into an enemy's zone. `{"go": "ledge"}` walks toward that zone at the start of each turn and acts only from where it stands. |
| `plan` | Entries of `{"use": <action id>, "when": {...}}`. An entry with no `when` always applies. |
| `flee` | The combatant leaves the fight at the start of its turn when the condition holds. `{"hp_below": 0.25}` reads its own hit points. `{"side_below": 0.5}` reads the fraction of its side still standing. Both are strict: exactly a quarter is not below a quarter. A combatant that has fled counts as defeated for its side, and does not satisfy a `defeat` that names it. |

`when` keys, all of which must hold: `round`, `round_min`, `round_max`,
`hp_below` (own fraction of hit points), `ally_hp_below` (the fraction of
the ally the action targets, and the combatant counts as its own ally),
`targets_min` (enemies in the target's zone), `target_has` and
`target_lacks` (a condition name).

## Events

An event changes the fight at the start of a round.

```json
"events": [
  {"round": 2, "kind": "enter", "combatant": "reinforcements", "zone": "road", "unless_down": "lookout"},
  {"round": 3, "kind": "zone", "zone": "rocks", "set": {"hazard": [{"kind": "damage", "dice": "1d6", "type": "fire"}]}},
  {"round": 4, "kind": "leave", "combatant": "captive"}
]
```

| `kind` | What happens |
|---|---|
| `enter` | The combatant, whose starting `zone` is `null`, enters at `zone` and rolls initiative. |
| `leave` | The combatant leaves the field. It does not count as defeated. |
| `zone` | The fields in `set` replace the zone's fields. |

`unless_down` names a combatant. The event does not fire when that combatant
is down or has fled.

## Objectives

Each side has a list of win conditions. A side meets its objective when any
one of them holds. The fight ends when a side meets its objective or the
round limit passes.

```json
"objectives": {
  "party":   {"wins": [{"kind": "defeat", "side": "enemies"}]},
  "enemies": {"wins": [{"kind": "defeat", "side": "party"}, {"kind": "rounds", "round": 5}]}
}
```

| `kind` | Holds when |
|---|---|
| `defeat` | Every combatant of `side` on the field is down or has fled, and no `enter` event can still bring more. With `combatant` instead of `side`, every copy of that combatant is down. |
| `rounds` | Round `round` has ended, whatever else has happened. Use it for a clock that favours one side. The other side stops the clock only by meeting its own objective first. |
| `reach` | `count` creatures of the side (or all of them, with `"count": "all"`) stand in `zone`. |

## Variants

A variant is the scenario with one change. The report runs each variant and
ranks the changes by how far they move the result.

```json
"variants": [
  {"name": "optimal play", "tactics": {"fighter": {"target": "weakest", "plan": [{"use": "longsword"}]}}},
  {"name": "six bandits", "counts": {"bandit": 6}},
  {"name": "no reinforcements", "drop_events": [0]},
  {"name": "no clock", "objectives": {
    "party": {"wins": [{"kind": "defeat", "side": "enemies"}]},
    "enemies": {"wins": [{"kind": "defeat", "side": "party"}]}}}
]
```

| Key | The change |
|---|---|
| `tactics` | Replaces the tactics card of each named combatant. |
| `counts` | Sets the `count` of each named combatant. |
| `drop_events` | Removes the events at these positions in `events`, counted from 0. |
| `objectives` | Replaces `objectives`. |
| `first` | Sets which side acts first. |

The engine adds its own variants to this list: one creature more and one
fewer for each enemy group, the party acting first, and the enemies acting
first.

## The engine's limits

The engine never plays the rules below, whatever the scenario says. The
report repeats this list under *Not modelled*.

- Reactions, which include opportunity attacks. A creature leaves a zone
  freely.
- Death saving throws. A player character at 0 hit points stays down until
  healed.
- Hiding, readied actions, and anything a player improvises.
- Positions inside a zone. Every creature in a zone can reach every other.

## The replay record

A replay compares one fight the table already played with the simulated
spread. The record is a second JSON file. Every key is optional.

```json
{
  "rounds": 4,
  "party_met_objective": true,
  "damage_dealt": {"fighter": 61, "wizard": 22},
  "damage_taken": {"fighter": 26},
  "dropped": ["rogue"]
}
```

The keys of `damage_dealt` and `damage_taken`, and the entries of `dropped`,
are combatant ids from the scenario. For a combatant with `count` above 1,
give the total across its copies. `damage_taken` is hit points lost, so it
never exceeds the combatant's `hp`.
