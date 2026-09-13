---
name: prep-session
description: >-
  Prep the next session as a short Lazy DM sheet — Mike Shea's eight steps
  traversed against the campaign record, filed as `sessions/<slug>.md` and
  read cold at the table. Use when the DM wants the next session prepped
  ("what do I need before Thursday"), asks for a strong start, secrets, or
  a prep sheet, or when planning talk turns into "let's build the session".
  Fights the DM wants costed go to `combat-generator`; everything else is
  cues.
---

# Prep Session

Traverse the eight steps of lazy prep — from Michael E. Shea's
[*Lazy GM's Resource Document*](https://slyflourish.com/lazy_gm_resource_document.html)
(CC BY 4.0) — against the campaign record, and write the result as one short
**prep sheet**: the whole session on a sheet the DM reads in a few minutes
before play and can abandon at the table without loss. About half an hour
of prep for a four-hour session is the scale to aim at.

The sheet is **throw-away prep**, not canon. The campaign record is the
memory; the sheet is what tonight needs from it. Prep situations the players
can walk into, never a story they must follow.

## Output contract — table cues only

Write the sheet as terse prompts for an experienced DM. Each entry carries
the concrete fact, image, action, or mechanic needed to run play, and
nothing about how it was chosen: selection rationale, rules summaries, prep
methodology, and instructions for using the sheet stay in chat. Link a rule
or item by name and leave its explanation at the source.

Write `Guard demands the missing seal`, not `Use this guard to give the
face a chance to shine`. A fact that changes play — `At the bell, guards
seal the exits` — sits in the scene or fight it changes.

Describe openings the players can take; the players choose who acts and how.
`A high ledge reachable by climbing or teleportation` leaves the approach and
the actor to the table. A PC's name on a cue marks an intended beneficiary,
never a prediction of who acts or whether they succeed.

Report caveats (attendance, a skipped step, a supersession) briefly in chat
and record durable changes in the campaign log. A routine delivery is the
sheet's link and one line of status.

## Read the campaign first

This skill hardcodes no repo layout. Read the campaign guide (`CLAUDE.md` or
equivalent) and the method handbook and schema it points to — in a
scaffolded wiki, `wiki-schema.md`. The handbook owns the campaign's house
rules for prep (a combat minimum, an NPC cap, a page limit); apply them
where they speak and the steps below where they are silent. Where the guide
leaves a slot this skill needs unanswered — no live layer, no session home,
no player pages — ask the DM inline and offer to record the answer in the
campaign's docs.

Then bring the record current:

- **Progress marker.** If the live layer shows a played session not yet
  absorbed, finish absorbing it first — `catch-up` if installed; otherwise
  ask the DM to bring the record current before building.
- **Session horizon.** When the schema defines `next_session` and
  `stale_after`, check `now >= stale_after`. Stale: ask whether the session
  on `next_session` was played. Yes: catch-up first. No: roll
  `next_session` forward and rewrite the live layer's horizon per the
  schema's *Session horizon* rule, and use that value on this sheet. When
  the schema defines the fields but the live layer carries neither, ask
  the DM for the next date and offer to set both; if none is known, build
  without a horizon.
- **Loose ends and contradictions.** Read the live layer's generated
  loose-ends section and any contradiction callouts on the concepts this
  prep touches (shapes in the schema). Loose ends are candidates, never
  obligations. Carry an unresolved contradiction as a prep gap in chat; ask
  for a ruling if it blocks the build, and leave its callouts intact.
- **The previous played sheet.** Reread it. Carry forward what is still
  relevant and not yet revealed — secrets, unfired scenes, unused
  locations, NPCs, unawarded rewards — and discard the rest. Nothing
  carried is owed.

**Done when:** the marker and the session history agree on where play
stands, the horizon is current, and you can name the expected party, its
level, and the session's likely ground.

## The eight steps

Run them in order. Every step is skippable when it would not help tonight —
say which you skipped in chat. Under time pressure, the document's own
reduced checklist is three steps: strong start, secrets and clues, fantastic
locations.

1. **Review the characters** — off-sheet. Read the player pages and the
   party cache; confirm who is expected. Ask of each: what do they want,
   what plays into their background, what does this player enjoy, what
   hook draws this character into the next session? Nothing is written
   down; the review shapes the steps that follow. Relationships surface
   naturally in scenes and NPCs; explicit spotlight staging belongs to
   fights, where `combat-generator` reads each PC's Spotlight profile.
2. **Create a strong start** — the most important piece of prep. One
   sentence or a short paragraph that opens in the middle of the action,
   close to the situation, with something the players can act on. When in
   doubt, start with a fight — and a fight the DM wants costed is built
   **pinned** (below) and filed under the opening.
3. **Outline potential scenes** — a few words per scene, one or two per
   hour of play, so you feel you have a handle on the night. Expect to
   abandon half. A scene that *is* a fight the DM wants costed holds its
   encounter block. Detailed procedures (clocks, tracks, option pools) live
   on the node and are linked by a named cue.
4. **Define secrets and clues** — second only to the strong start. About
   ten single sentences the characters can discover, each abstract from
   its place of discovery — a secret that names who reveals it or where it
   is found is rewritten until it doesn't. Carry forward last sheet's
   unrevealed, still-relevant secrets; check the live layer's revelation
   tracking so the must-land revelations are represented.
5. **Develop fantastic locations** — a handful, each an evocative name and
   up to three fantastic aspects; minor locations get a name alone. Sets
   worth describing out loud, not keyed maps.
6. **Outline important NPCs** — only those who drive the session, each a
   name (linked to its page where one exists), their connection to tonight,
   and an archetype from popular fiction. Everyone else is improvised at
   the table.
7. **Choose relevant monsters** — list the monsters the characters are
   likely to face, chosen for the situation and the place, each linked to
   its stat block through the lookup chain in
   [`rules-sourcing.md`](rules-sourcing.md). Read the stat blocks for a
   rough sense of danger. That completes the step. Cost a fight only when
   the DM asks for one — a boss, a set piece, a threat worth the work —
   and then through `combat-generator` (below), **floating** for a threat
   not tied to a scene.
8. **Select rewards** — items the players will find interesting, from the
   campaign's approved pool and player wish lists where it keeps them,
   mixing character fit with story fit; an item is a fine vehicle for a
   secret. **Anchor every item at a PC** — a name, several names, or
   `the party` for shared consumables — and anchor overdue PCs first, read
   from the record's actual reward receipts, not from the plan. A slate is
   a candidate pool, not an award schedule; "no items — the payout is
   information or favors" is a valid, stated answer.

**Done when:** every step was run or named as skipped, and each entry on
the sheet survives being read cold at speed.

## Fights — the combat-generator handoff

This skill never sizes a fight itself. Every costed fight on the sheet comes
from `combat-generator` (`/combat-generator`, once per fight) — if installed;
without it, name the fight as a gap. Ask for a compact delivery: the
`> [!encounter-meta]` block plus one tactics line covering the enemies'
opening and response, and embed it **as-is** — no re-derived budget, no
re-picked complication. Pass the output contract's opening rule with every
request: the block's `Spotlight:` field names an opportunity and the
conditions that make it available, never who takes it.

Name each fight's form:

- **Pinned** — the scene *is* the fight (a fight-scene from step 3, a
  combat strong start). Hand over the situation, the party, and the
  difficulty band; the block files at that scene.
- **Floating** — step 7's portable threat: cast named on the `Enemies:`
  line, everything else in roles, dropped into whichever scene fires. Files
  under *Relevant Monsters*, never onto a node.

## Sheet format and filing

- **File** as `sessions/<slug>.md` wherever the campaign keeps session
  records, `type: session`, `status: draft`, a one-sentence plain
  description, `tags` including `prep-sheet`, and `generated: { by:
  dm-skills/prep-session, at: <ISO 8601 with UTC offset> }` per the
  schema's last-writer rule. Copy `stale_after`
  from the live layer when `next_session` is known; omit it otherwise. A
  sheet delivered only in chat creates no file. Catch-up owns the flip to
  played history.
- **Open** with the title, one contents line — `*Contents: [Strong
  Start](#strong-start) · …*`, the sheet's only whole-line italic — then
  `## Strong Start`. Sections are unnumbered H2s in checklist order, named
  for steps 2–8: *Strong Start*, *Potential Scenes*, *Secrets and Clues*,
  *Fantastic Locations*, *Important NPCs*, *Relevant Monsters*, *Rewards*.
  Step 1 has no section.
- **Scenes** are a line each, or a `> [!scene]` card when a scene carries a
  nested encounter block. **NPCs** and **rewards** read well as tables (name
  · tonight · archetype; item · anchored at · their last reward), but the
  shape is yours.
- **Embed nothing but encounter blocks.** Read-alouds, stat blocks, and
  maps are linked, never copied.
- **Lint** before delivering:
  `python3 <this skill>/scripts/validate_sheet.py sessions/<slug>.md`.
  It checks the opening, unnumbered H2s, and stray whole-line italics — the
  clutter that creeps onto a sheet — and nothing about content. Fix a
  finding by deleting or folding, never by restyling the note.
- **Finish** like any record edit: the campaign's catalog and conformance
  scripts if it has them, a log entry, and the sheet's link in chat.

**Done when:** the lint passes and the DM has the link.
