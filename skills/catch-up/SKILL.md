---
name: catch-up
description: Absorb played sessions into the campaign record — from a session transcript when one exists, by interviewing the DM otherwise. Use when the DM provides a transcript or recording of a played session, or when planning or prep starts while the live layer's progress marker shows a played session not yet absorbed — raise it unprompted rather than waiting for a recounting. Only played sessions are absorbed, never hypotheticals or planning talk.
---

# Catch-Up

Play happened; the world absorbed it. Every planning artifact must reach
"current" before prep starts, because prep against a stale record is prep
against a false world.

The campaign repo's own docs (`CLAUDE.md` or equivalent, and any
planning-method handbook they point to) own the conventions for the live layer
— timelines, threads, revelation tracking, the progress marker, strikethrough
discipline. Read them before anything: this skill enumerates *what* must reach
current; the docs say *how*. Where they leave a convention this skill needs
unresolved — no live layer, no progress marker, no stated home for session
records — ask the DM inline and offer to record the answer in the campaign's
own docs so the next run discovers it.

**Authorship:** consequences are recorded freely, reactions are proposed. A
*consequence* is mechanical — the thing broke, the NPC died, the clue was
found, the favor is owed. A *reaction* is the world deciding something — a
faction's response, a re-dated beat that implies new intent. Propose reactions
inline for the DM's nod as the account comes together.

**Hard rules:**

- **Never pick for the DM how a discrepancy resolves** — retcon vs. correct
  (Step 3) is a world-decision, like a reaction.
- **Catch-up never builds** — a consequence demanding new content becomes a
  named handoff in the closing summary, never inline work.
- A transcript is evidence, not canon: nothing from it lands on a page until
  its divergences have passed through reconciliation (Step 3). A deferred
  reaction is left honestly undecided (the trigger event recorded, the
  response blank) — never a speculative beat.

## Steps

### 1. Detect the lag
Compare the live layer's canonical progress marker against the session
records and name the unabsorbed played session(s). If none, say so and stand
down — there is nothing to catch up.
**Done when:** the sessions to absorb are named, oldest first.

### 2. Gather the account
Ask whether a transcript exists — a recording of play, not a recounting —
before interviewing.

**With a transcript:** read it against the played session's prep sheet and
the live layer as it stood going in. Extract what an interview would have
asked for — nodes reached, clues found, beats fired, the ending state, what
was left owed, broken, taken, or promised — and log every point where the
table diverged from the prep or the record: that log is the reconciliation
**docket** for Step 3. Then interview only the gaps: a transcript captures
what was said, not why — DM intent, off-screen rulings, anything the mic
lost.

**Without one:** the prep sheet is the questionnaire. From it, and from the
live layer as it stood going in, derive targeted questions: which prepped
nodes were reached, which in-reach checklist clues were found, which due
beats fired, what the session ended on, what was left owed, broken, taken,
or promised. Ask conversationally, a few at a time — the DM answers in
fragments while already thinking about the next session. Chase each fragment
that implies a world-change until it is concrete enough to file, adding every
divergence it reveals to the docket.

**Done when:** every prepped element is accounted for — reached, missed, or
changed — the ending state (choice point or mid-situation) is captured, and
the docket lists every divergence.

### 3. Reconcile
Work through the docket; no divergence is silently absorbed. Three kinds:

- **Misstatement** — the table contradicted established canon (wrong name,
  wrong date, a power the page says doesn't exist). Present both versions and
  let the DM pick per item: **retcon** (the table's version becomes canon —
  the record changes everywhere the old detail lives) or **correct** (canon
  stands — the flub goes onto the coming session's prep flags as a correction
  to deliver in play).
- **Veer** — the players left the prepped course. Record what actually
  happened as consequences like any other play; the prepped-but-unreached
  material survives being missed. Flag it in the live layer for reuse,
  re-dating, or restrike, and where the veer burned a clue's delivery
  vehicle, note the re-clueing handoff.
- **Improvisation** — the DM established something mid-scene the record never
  held (an NPC name, a shop, a ruling). New canon born at the table, not a
  contradiction. Confirm it with the DM and file it where it lives, at seed
  granularity unless it already earns a page.

**Done when:** the docket is empty — every divergence retconned, flagged for
correction, filed, or handed off.

### 4. File the recap
Assemble the reconciled account into the session record's recap section,
densely linked per the repo's conventions. The recap is the durable record of
play — the story, written after the fact — and every propagation edit that
follows should be traceable to it.
**Done when:** the recap reads as a complete account and neither the
transcript nor the interview holds anything it omits.

### 5. Propagate
Three rings, then stop:

1. **Directly impacted pages** — every node the players touched, changed, or
   learned from. Update always. Two spotlight ledgers ride in this ring:
   - *The Spotlight profile* on each player page: where the session revealed
     a player's style — an improvisation they loved, a signature move reached
     for again, an ability they built around finally firing (or conspicuously
     still waiting to) — fold the observation into their profile, creating
     the section on first observation.
   - *The staged beats* on the session page: the session's spotlight plan is
     transient — it died with the prep run — so the ledger is the session
     page itself: every encounter-meta `Spotlight:` field and every
     `Spotlight (scene):` sidebar line, each naming its target PC (the format
     lives in `build-session/session-page-format.md`). Record which of those
     staged beats **fired** and which were **denied or skipped** — a beat
     staged but never fired should get louder in future prep; one that fired
     big can rest. A PC the page never names was planned as resting, so there
     is nothing to reconcile — but note a PC who has now rested across
     consecutive sessions.
   - *The loot ledger* rides here too: the recap names which PC received
     each item the session handed out — those receipts are what the next
     prep's loot-parity read depends on. And where the played page
     leaves prepped-but-unreached material still holding aimed item
     rewards, re-aim any item whose named PC banked items this session
     toward a PC lighter on recent loot — changing the name on an
     existing reward line is presentation, not new content, so it is
     propagation, not building. A promised item keeps its PC.
2. **One link-hop out** — follow each impacted page's links and clue-web
   entries outward once, checking neighbors for *contradiction only*: update
   what now misstates the world, don't enrich what doesn't.
3. **Logically forced jumps, any distance** — route by the method's test:
   *does this change what is happening in the world, or only how the players
   encounter it?* World-changes chase their owning pages (the faction whose
   courier died hears about it regardless of link distance);
   encounter-changes stay local.

Per the hard rules, new content a consequence demands — a seed now worth
promoting, a revelation left short because the party burned a clue's source —
goes on the handoff list as a named handoff to the repo's node-building or
clue-seeding skill.
**Done when:** all three rings swept and the handoff list written.

### 6. Advance the clock
Update the live layer: the progress marker (session count and, if the
campaign keeps one, the in-fiction date); found clues ticked and landed
revelations marked per the repo's convention; thread lines revised;
intervened timelines restruck (superseded beats struck through, never
deleted); any standing ledgers the live layer keeps (debts, favors, markers)
updated with what the session left owed, called, settled, or broken; and
beats now due or overdue surfaced as flags for the coming prep — not written
into nodes.
**Done when:** the live layer describes the world as of the end of the
absorbed session.

### 7. Verify prep-ready
The completion test is operational: the repo's session-prep skill could run
immediately and find no artifact contradicting what happened at the table.
Re-walk Steps 5–6 against the actual files, not memory. Close with the
handoff flags and the log entry, and — if multiple sessions were absorbed or
the ripple ran wide — offer an integrity-audit pass.
**Done when:** the re-walk finds nothing stale; handoffs and log entry
written.
