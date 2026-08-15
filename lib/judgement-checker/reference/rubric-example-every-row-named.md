# Reference rubric row — `build-session/npc-rows-named` (a format example)

> **This is an example of the [rubric format](../rubric-format.md), not a shippable
> rubric.** It works one inventory row — **npc-rows-named** — so the format is
> legible and the [verdict contract](../verdict-contract.md) is proven end to end
> on a fixture. The real `build-session` rubric (all its judgement rows) is
> authored beside `skills/build-session/SKILL.md` by
> , in this same format. Do not
> file per-skill rubrics in this shared directory.

`npc-rows-named` is a **structural** judgement row (is this cell a name?), so it
uses no roster and needs no golden corpus — hand-written anchors are sufficient and
complete. It is the simplest honest demonstration of the format. (A
reader-interpretation row like `lead-interpretability` would additionally reserve a
corpus pointer; see the rubric format.)

---

## Row `build-session/npc-rows-named` — every Key NPCs row is named

- **Inventory check id:** `build-session/npc-rows-named`
  *(from [`docs/eval-assertion-inventory.md`](../../../docs/eval-assertion-inventory.md),
  the `build-session + session-page-format` table — method: judgement.)*

- **Promise text:** Every row of the **Key NPCs** table is **named** — a
  descriptive placeholder ("the strongman", "the handler") is a **defect**. Where
  the fiction deliberately hides a name from the players, the row **still carries
  it for the DM** with the concealment noted (`"Kate — don't name her"`); an NPC
  nobody has named yet **gets named now**, in the campaign's own naming idiom.
  *(Source: `build-session/session-page-format.md` — "**Every row is named**" —
  the Key NPCs **Name** column, "**Every
  row is named**".)*

- **Roster use:** **None.** `npc-rows-named` is structural — it asks whether the
  Name cell holds a name, which is legible from the output alone. The checker does
  not consult the party roster for this row. *(The roster is still handed in per
  the launch protocol; this row simply does not read it. Roster-dependent rows — a
  flagged-ability spotlight, a level-appropriate budget — say which field they
  read.)*

- **Criteria:**
  - **Holds when** every row in the Key NPCs table has a **proper name** in its
    Name cell — a name a player or DM would use to refer to the NPC (`"Kate"`,
    `"Old Harl"`, `"The Verdant Choir"` for a group). A concealed-from-players
    name still **counts as named** when the row carries the real name plus the
    concealment note (`"Kate — don't name her"`).
  - **Breaks when** any row's Name cell is a **descriptive placeholder** standing
    in for a name — a role-noun or epithet with no proper name (`"the strongman"`,
    `"the handler"`, `"the bartender"`, `"Guard 2"`, `"TBD"`, an empty cell). The
    defect is one row; report it at that row.
  - **Cannot tell → disapprove.** If a cell is ambiguous between a name and an
    epithet used *as* a name (`"Red"` — nickname, or "the red one"?), the checker
    **disapproves** and names the row, so the generator can disambiguate (add the
    given name, or note it is a used nickname). Uncertainty is a disapprove, never
    a pass.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** `| Kate — don't name her | Aunt Bea (Andy Griffith) | Innkeeper who fronts for the ring | {monster:spy} | T1 |`
    → a concealed-from-players NPC, but the row carries her real name for the DM
    with the concealment noted. **Named.** Holds.
  - **Bad — breaks.** `| the bartender | Sam Malone (Cheers) | Pours drinks, overhears everything | {monster:commoner} | T2 |`
    → the Name cell is a role-noun, no proper name. A descriptive placeholder.
    **Breaks `npc-rows-named`** at this row. The NPC should be named now in the campaign's idiom.
  - **Edge — the boundary.** `| The Verdant Choir | Enya, as a cult (group voice) | Chanting eco-zealots blocking the grove | {monster:cultist} | T4 |`
    → a **group** row. A group gets **one analog for the group's voice**, and its
    Name cell carries the group's proper name, not a member list. `"The Verdant
    Choir"` is a proper name for the group. **Named.** Holds. *(Contrast the bad
    case: "the cultists" would be a placeholder and break.)*

- **Corpus pointer:** *none* — `npc-rows-named` is structural, so hand-written
  anchors are the floor and the ceiling. (Reserved slot exists in the format for
  reader-interpretation rows `lead-interpretability` / `clue-interpretability` /
  `plain-language` / `read-aloud-boundary` only.)

---

## What a verdict looks like against this row

Two fixture outputs sit beside this file. Each is a **Key NPCs table only** — the
slice of output the checker grades against `npc-rows-named` — plus the fixed inputs
the checker is handed (rubric subset `[build-session/npc-rows-named]`, roster).
**Neither fixture contains any generator reasoning**: the checker sees the output,
the `npc-rows-named` row above, and the roster, and nothing else — that is the
independence the launch protocol requires.

### `fixture-approve.md` → `approve`

Every row's Name cell holds a proper name (including one concealed-from-players NPC
carried correctly for the DM). The checker tries to disprove `npc-rows-named`,
finds every row named, and cannot break it.

```
verdict: approve
findings: []
```

An `approve` with an empty findings list produces a file-offer
**indistinguishable from today's** — no enrichment.

### `fixture-disapprove.md` → `disapprove`

The same table with **one row toggled** from a name to a descriptive placeholder
(`Sam Malone` → `the bartender`). One promise breaks; the checker returns
`disapprove` with exactly one finding, in the [verdict-contract](../verdict-contract.md)
shape:

```
verdict: disapprove
findings:
  - promise:          build-session/npc-rows-named  # required — the inventory row (the added promise-pointer field)
    output-location:  Key NPCs table, row 2       # required — where in the output (rides `file`/`line`)
    short_summary:    Key NPCs row 2 unnamed
    summary:          Row 2's Name cell is "the bartender", a descriptive
                      placeholder, not a proper name.
    failure_scenario: A player or DM reading the Key NPCs table meets a row
                      with no name and cannot refer to the NPC; the promise
                      that every row is named is broken at this row.
    # NO fix field: the finding does not say "name him Sam Malone" — the checker
    # names WHICH promise broke; the generator owns HOW to fix it (user story 19).
    # outcome: unset — the checker is stateless; the generator writes outcome
    # across rounds (fixed | skipped | no_change_needed).
```

The generator, on this `disapprove`, refines row 2 (names the bartender in the
campaign's idiom), marks the finding `fixed`, and re-drives a **fresh** checker per
the [back-pressure driver](../back-pressure-driver.md). If it instead judged the
finding a false alarm it would mark `no_change_needed`, and a fresh checker raising
`npc-rows-named` again on row 2 would be a genuine standoff that survives to the
enriched offer.
