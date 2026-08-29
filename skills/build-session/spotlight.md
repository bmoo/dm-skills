# The Session Spotlight Plan

The spotlight procedure of the `build-session` skill. Step 3 of a session
build loads this file and follows it to allocate the session's spotlight
plan; the fight builds (the `combat-generator` skill) and the keyed-site
procedure ([`dungeon.md`](dungeon.md)) spend the beats it allocates.

A player's build is a **statement** — *this is what I want to do at the table*
— and most of a statement is reactive or situational: it fires only if the DM
stages for it. This file owns the procedure for honoring statements without
turning every scene into an engineered showcase.

Two reference files sit beside this one — library-shared statements that
materialise here by symlink (`lib/`):

- [`spotlight-doctrine.md`](spotlight-doctrine.md) — the pacing rules: the
  session budget, the texture palette, the anti-tell rules, the flagging
  heuristic, evidence and precedence.
- [`class-patterns.md`](class-patterns.md) — per-class staging patterns,
  combat and out-of-combat, verified against the 2024 rules. Patterns, not
  inventory.

The keyed-site procedure and the `combat-generator` skill load both files
for their texturing steps, and `party-sync` loads
[`spotlight-doctrine.md`](spotlight-doctrine.md) for its sync-time flagging.
Changing their shape is a breaking change (library sync obligations:
`docs/campaign-contract.md`).

## The data ladder

Reading a PC for spotlighting climbs the **data ladder** in
[`spotlight-doctrine.md`](spotlight-doctrine.md#the-data-ladder) — the
profile-first, self-healing read every spotlight consumer shares. Climb it
once per PC here and hand the resolved roster back, so no later pass climbs
it again. Evidence for the variety check is likewise the doctrine's
*Evidence and precedence* section: this campaign's structured combat data,
falling back to prepped encounter-meta `Spotlight:` lines before played
sessions exist.

## Allocating the plan

**What the session build hands this procedure:** the party (so the data
ladder above has a roster to climb for each PC), the session's **planned
situations** — the likely set-pieces and scenes, with the pillar each lives in
(social, exploration, combat) — and any beat already fixed by an earlier run or
by the DM. Planned situations only: reserve pressure the session may never
inject is not yours to allocate against.

**What the procedure hands back — in-run, never filed:** the **roster you
read** — each PC with the flagged abilities and the **Table experience** rung
the ladder resolved, so the session build can spend it into its own checks and
its fight and site builds without a second ladder pass — and the
session's **allocated budget**: one line per PC, either a real beat with its
pillar or a named rest, plus a
texture per likely set-piece from the palette, and, for every **Aimed** or
**Puzzle** beat, its **legibility** — *how plainly the DM points at it*. Set
legibility per
[`spotlight-doctrine.md`](spotlight-doctrine.md#legibility): read the target
PC's **Table experience** rung off their profile's player half and calibrate
the tell as that section prescribes — its vocabulary, its never-default rule,
and its missing/off-list handling all live there, and this pass only reads
the rung, never writes it. Allocate from the record — profiles and the recent
ledger — not from memory; the ladder's own fallbacks apply when a rung is
missing or stale.

**What the session build is responsible for:** the plan is **transient
prep-run state** handed back in chat, so the session build spends it inside
the same run — into its own page or sheet, and down to the fight or site
build it hands off to, which spends the beat it is handed instead of aiming
independently. The session build owns whether every PC came out
covered, whether a beat it could not stage is reported, and what (if
anything) reaches a page: this procedure files nothing.
