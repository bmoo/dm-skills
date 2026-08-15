# Fixture — `build-session/npc-rows-named` approve

A worked fixture for the [`build-session/npc-rows-named` reference rubric row](rubric-example-every-row-named.md).
It is the exact, complete set of inputs a [fresh-context
checker](../checker-launch-protocol.md) is handed — **output, rubric subset, roster, and
nothing else**. There is **no generator reasoning here**, by design: that withholding is
the independence that keeps the grade adversarial (acceptance criterion 1).

Graded against `npc-rows-named`, every Key NPCs row is named → the checker returns **`approve`**
with an empty findings list.

---

## Input 1 — the output (the slice `npc-rows-named` grades: the Key NPCs table)

> ## Key NPCs
>
> | Name | Personality | Role | Stat Block | Location |
> |---|---|---|---|---|
> | Old Harl | Wilford Brimley (Cocoon) | Retired caravan master, knows the old roads | {monster:veteran} | T1 |
> | Kate — don't name her | Aunt Bea (Andy Griffith) | Innkeeper fronting for the ring | {monster:spy} | T1 |
> | The Verdant Choir | Enya, as a cult (group voice) | Eco-zealots blocking the grove | {monster:cultist} | T4 |
> | Bram Ashford | Ron Swanson (Parks & Rec) | Blacksmith who forged the murder weapon | {monster:commoner} | T2 |

## Input 2 — the rubric subset

`[build-session/npc-rows-named]` — from `build-session`'s beside-`SKILL.md` rubric. (The generator names the
producing skill so only `build-session`'s rows apply — spec user story 17.)

## Input 3 — the party roster

| PC | Class | Flagged ability / Spotlight profile |
|---|---|---|
| Vera | Wizard | Divination — wants clues to read |
| Tomas | Fighter | Grappler — wants terrain to pin enemies |
| Odile | Rogue | Face — wants social pressure points |

*(`npc-rows-named` does not consult the roster — it is a structural row. The roster is handed in
per protocol regardless; other rows use it.)*

---

## Expected verdict

```
verdict: approve
findings: []
```

Every row's Name cell holds a proper name: `Old Harl`, `The Verdant Choir`,
`Bram Ashford`, and `Kate` — the last concealed from players but carried for the DM
with the concealment noted (`"Kate — don't name her"`), which **counts as named**
per the criteria. The checker tries to disprove `npc-rows-named` and cannot. An `approve` with no
findings yields a file-offer indistinguishable from today's — no enrichment.
