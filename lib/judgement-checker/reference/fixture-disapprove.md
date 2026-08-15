# Fixture — `build-session/npc-rows-named` disapprove

The [approve fixture](fixture-approve.md) with **one row toggled** — row 4's Name
cell changed from the proper name `Bram Ashford` to the descriptive placeholder
`the bartender`. Everything else is identical, including the inputs the
[fresh-context checker](../checker-launch-protocol.md) is handed: **output, rubric
subset, roster, and nothing else** — no generator reasoning (acceptance criterion
1). One promise breaks → the checker returns **`disapprove`** with exactly one
finding.

---

## Input 1 — the output (the slice `npc-rows-named` grades: the Key NPCs table)

> ## Key NPCs
>
> | Name | Personality | Role | Stat Block | Location |
> |---|---|---|---|---|
> | Old Harl | Wilford Brimley (Cocoon) | Retired caravan master, knows the old roads | {monster:veteran} | T1 |
> | Kate — don't name her | Aunt Bea (Andy Griffith) | Innkeeper fronting for the ring | {monster:spy} | T1 |
> | The Verdant Choir | Enya, as a cult (group voice) | Eco-zealots blocking the grove | {monster:cultist} | T4 |
> | **the bartender** | Ron Swanson (Parks & Rec) | Pours drinks, overhears everything | {monster:commoner} | T2 |

## Input 2 — the rubric subset

`[build-session/npc-rows-named]` — same as the approve fixture.

## Input 3 — the party roster

Same roster as the approve fixture. (`npc-rows-named` does not consult it.)

---

## Expected verdict

```
verdict: disapprove
findings:
  - promise:          build-session/npc-rows-named
    output-location:  Key NPCs table, row 4
    short_summary:    Key NPCs row 4 unnamed
    summary:          Row 4's Name cell is "the bartender", a descriptive
                      placeholder, not a proper name.
    failure_scenario: A player or DM reading the Key NPCs table meets a row with
                      no name and cannot refer to the NPC; `npc-rows-named`'s promise that every
                      row is named is broken at this row.
```

The verdict is `disapprove` — a single broken row is enough; the checker does not
average it away against the three named rows. The finding carries the three
required/forbidden properties of the [verdict contract](../verdict-contract.md):

- **`promise: build-session/npc-rows-named`** — required; every finding cites the inventory row it breaks in
  the added `promise` field (the judgement analogue of the mechanical
  `Finding.check_id`; `ReportFindings` has no native field for a row id).
- **output-location `row 4`** — required; where in the output the break is (rides
  `file` / `line`).
- **no fix** — `summary` and `failure_scenario` state the defect only. The finding
  does **not** say "name him Sam Malone" or otherwise prescribe the remedy: the
  checker names *which* promise broke; the generator owns *how* (user story 19).
- **no `outcome`** — the checker is stateless per round; the generator writes
  `outcome` (`fixed` / `skipped` / `no_change_needed`) across rounds as it owns the
  cross-round memory.

On this verdict the generator refines row 4 — naming the bartender in the
campaign's naming idiom — marks the finding `fixed`, and re-drives a **fresh**
checker (round 2) per the [back-pressure driver](../back-pressure-driver.md). If a
fresh checker approves, the loop completes; if three rounds exhaust with the finding
unresolved, it becomes part of the enriched file-offer ("1 issue I couldn't resolve
— file anyway, or take over").
