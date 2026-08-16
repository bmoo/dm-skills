# The Session Spotlight Plan

The spotlight procedure of the `build-session` skill. Step 3 of a session
build loads this file and follows it to allocate the session's spotlight
plan; the fight and keyed-site procedures ([`combat.md`](combat.md),
[`dungeon.md`](dungeon.md)) spend the beats it allocates.

A player's build is a **statement** — *this is what I want to do at the table*
— and most of a statement is reactive or situational: it fires only if the DM
stages for it. This file owns the procedure for honoring statements without
turning every scene into an engineered showcase.

Two reference files sit beside this one:

- [`spotlight-doctrine.md`](spotlight-doctrine.md) — the pacing rules: the
  session budget, the texture palette, the anti-tell rules, the flagging
  heuristic, evidence and precedence.
- [`class-patterns.md`](class-patterns.md) — per-class staging patterns,
  combat and out-of-combat, verified against the 2024 rules. Patterns, not
  inventory.

The fight and keyed-site procedures load both files directly for their
texturing steps, and `party-sync` loads
[`spotlight-doctrine.md`](spotlight-doctrine.md) across the skill boundary
for its sync-time flagging. Changing their shape is a breaking change
(library sync obligations: `docs/campaign-contract.md`).

## The data ladder

Reading a PC for spotlighting climbs down this ladder — take the highest rung
that is present and fresh. The ladder self-heals: the DM never has to
remember the dependency.

1. **The Spotlight profile** on the player page. Its *character half* is the
   flagged-ability list party-sync precomputes at sync time; its *player
   half* is observed play, maintained by catch-up from this campaign's
   transcripts. Player half outranks character half; both outrank
   class-generic patterns.
2. **Profile missing or stale (>7 days)?** Derive the flags live: read the
   party cache wherever this repo keeps synced sheets, look up the build's
   features at its level via the sourcing chain in
   [`rules-sourcing.md`](rules-sourcing.md), and apply
   the flagging heuristic in
   [`spotlight-doctrine.md`](spotlight-doctrine.md). Offer to persist the
   result to the profile. Never auto-trigger a re-scrape of a third-party
   service — a real re-sync is the DM's call.
3. **No party cache at all?** Say so and offer a party-sync run. Don't
   spotlight from memory.

**Evidence for the variety check** is the structured combat data in this
campaign's record repo (the repo's guide says where): the encounter ledger
and per-session JSONs. **Only this campaign's record feeds this** — never
another campaign's data, even for the same players. Before played sessions
exist, fall back to `Spotlight:` lines in prepped encounter-meta blocks
(format: the *Filing format* section of [`combat.md`](combat.md)).

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
its fight- and site-level procedures without a second ladder pass — and the
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
the same run — into its own page or sheet, and down to the fight- or
site-level procedure it loads, which spends the beat it is handed instead of
aiming independently. The session build owns whether every PC came out
covered, whether a beat it could not stage is reported, and what (if
anything) reaches a page: this procedure files nothing.
