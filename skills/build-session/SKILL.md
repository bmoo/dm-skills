---
name: build-session
description: >-
  Prep the next session: traverse Mike Shea's (Sly Flourish) Eight Steps of
  Lazy DM Prep against the campaign record, then compile the result into a
  durable session page in the library's WotC-convention format — or stop at
  a lean in-chat prep sheet when that's all the DM wants. Orchestrates the
  repo's prep skills (fights, keyed sites, spotlight plan, clue slate,
  maps) and verifies the page against the format's definition of done;
  renders a styled PDF on request. Use when the DM wants a session built or
  made table-ready, asks "what do I need before Thursday," or wants a
  printable PDF of a session page. Not for absorbing a played session
  (catch-up), a single fight (combat-generator), or standalone node
  deepening.
---

# Build Session

One skill owns session pages. It preps by traversing the **Eight Steps of
Lazy DM Prep** (Mike Shea's *Lazy GM's Resource Document*, CC-BY-4.0,
SlyFlourish.com) —
prep situations, not plots, pulling from what the campaign record already
establishes — and delivers at one of two depths:

- **Lean sheet** ("what do I need before Thursday"): traverse the prep
  steps, deliver the sheet in chat, stop.
- **Full page** (built / table-ready): the same traversal, then compile a
  durable session page and verify it.

Reference beside this file — load each when its step says to:

- [`session-page-format.md`](session-page-format.md) — the page skeleton,
  its conventions, and the **definition of done**; the library's one
  statement of page structure. Load at Step 4.
- [`node-deepening.md`](node-deepening.md) — promoting a seed into its own
  node page, or building a thin node out in place. Load at Step 3, when a
  location tonight's play needs is too thin to run cold.
- [`render.md`](render.md) — the PDF renderer (`scripts/` beside it). Load
  when the DM asks for a printable/styled PDF.

This skill is a **general contractor**: it decides the order of work and
hands each trade to the skill that owns it.

## Step 1 — Absorb, take the brief, discover the ground rules

Check the campaign record's live progress marker. If it shows a played
session not yet absorbed, hand off to the repo's absorption skill
(`catch-up`, if installed) and finish that before building anything — prep
built on a stale record bakes in contradictions.

**Then the brief, and in that order** — an unabsorbed session means the
brief itself was written against a stale record. Take the one the
invocation names by ticket number; failing that, the open
`ready-for-agent` ticket on the campaign's tracker; if that still doesn't
settle which, ask.

**No brief stops the run here, before anything is read for the build.**
Say why and stop: the DM writes one (`to-session-brief`, if installed) and
re-invokes, or re-invokes with an explicit *get creative*. That opt-out
belongs to the invocation — never a silent default, never a mid-run offer.

**Precedence from here down: brief · method doc · library checklist**,
with the campaign record as the substrate all three read.

Then the ground rules. This skill hardcodes no repo layout. Read, in
order:

1. The repo's own guide (`CLAUDE.md` / `CONTEXT.md` / `README`) — page
   categories, where session pages live, link and formatting conventions.
2. The repo's prep methodology (the planning-method handbook its guide
   points to) — **its session-prep rules are this skill's acceptance
   criteria**, checked at Step 6. The page *skeleton* is library-owned
   (the format file), but the method doc's rules win on conflict wherever
   the brief is silent.
3. The live campaign state (scenario timelines, active threads,
   revelations tracker) and the most recent session's ending.

**Done when:** the record's marker and the session history agree on where
play stands, and you can name the session's number, its likely destination
node(s), the party's level, and every method-doc rule a session page must
satisfy.

## Step 2 — Scope, from the brief

The brief's `Destination node(s)` is the scope, and its Locked lines bind
every step below. **Read it; don't check it** — a brief that contradicts
the record is *introducing canon*, which is the brief working correctly.

**Derive tonight's Spec-axis check set from it, before drafting.** Hand
the brief body verbatim to `brief_checks(<the brief body>)` from the
shared checker library beside this skill
([`scripts/mechanical_checker`](scripts/mechanical_checker)). It returns
one check id per filled mechanically-checkable field and nothing for a
blank one. The derivation is fill-in from the named fields, never your
judgement about what is worth checking: **you may not drop a check for a
field the brief filled, and you may not add one the brief did not
license** — a generator that writes its own acceptance criteria can write
weak ones, and nothing downstream would notice.

**Where the brief is silent — here and at every step below — take it in
this order: derive it from the record · draw on the wider corpus · invent
where both are silent.** Silence never stops the run; deriving is the
read this step has always made — what did the last session's ending make
likely?

**A subject a Locked line names is not silence.** On that subject the page
asserts nothing the brief or the campaign record does not already supply —
derive it or leave it unsaid. Everything the brief did not lock is still
silence, and inventing there is the job.

- Ended on a clean choice point → build the chosen destination; if the
  choice is still open and coverage was asked for, one variant page per
  destination (sibling pages that name each other).
- Ended mid-situation → one page prepping the small cluster of nodes in
  reach.

**Done when:** the page list is fixed, each with a destination node and a
level range. (Lean sheet: scope is just "the next session" — skip the
page list.)

## Step 3 — Traverse the prep steps

Shea's own guidance is that a **continuous campaign** shouldn't run all
eight steps every time — most of the load-bearing prep already exists in
the record. Default to the **lean set** and extend only what's thin:

| # | Step | Default? |
|---|------|----------|
| 1 | Review the characters | **Lean** |
| 2 | Create a strong start | **Lean** |
| 3 | Outline potential scenes | Conditional |
| 4 | Define secrets and clues | **Lean** |
| 5 | Develop fantastic locations | Conditional |
| 6 | Outline important NPCs | Conditional |
| 7 | Choose relevant monsters | Hand off |
| 8 | Select rewards | Skip by default |

A step with nothing to pull falls back in Step 2's order (derive · corpus
· invent) rather than stopping. The run never halts on a gap; Step 8
names what it filled.

### The lean set

- **Review the Characters** — one line per PC: current status, anything
  they're owed (a personal thread, an item, a promise) that could surface
  this session, read through the lens tonight's play needs rather than
  every lens every time. Where a lens wants a fact the record doesn't
  hold (how does this PC know that place?), surface it as a question for
  that player at the table — their PC's history is theirs to answer.
- **The spotlight plan** — a trade like any other: if this repo has a
  spotlight skill, hand it the session **through that skill's delegate
  interface** (its *Invoked as a delegate* section) — the party, this
  session's planned situations with the pillar each lives in (social,
  exploration, combat), and any beat already fixed. It owns the data
  ladder, the palette, and the legibility calibration behind that
  boundary. Hand it **planned situations alone**: the method doc's
  **pocket beat** is *not* a budgeted beat — it is unplanned reserve that
  may never fire and never discharges a PC's guaranteed beat. It hands
  back the allocated budget — a beat or a named rest per PC plus a
  texture per likely set-piece — and the **roster it read**, each PC with
  the flagged abilities and the rung the ladder resolved. That roster is
  what the Step 5 trades, the Step 6 checks, and the judgement pass are
  all handed; never climb the ladder a second time for it. The plan is
  done when every PC is either given a beat or named as resting — pull it
  from the record, not memory; a plan that leaves a PC unaccounted for
  goes back before you spend it. The plan itself is **transient prep-run
  state**: spend it in this run — hand it to the Step 5 trades, land its
  effects as one annotation per staged beat (Step 4) — and file it
  nowhere.
- **Strong Start** — a concrete opening beat that lands the party back in
  the fiction inside the first two minutes, built from the last session's
  ending point or the most pressing live thread. A punchy trigger the DM
  can read cold, not a paragraph of scene fiction. This becomes the
  page's *Beginning the Adventure* read-aloud.
- **Secrets & Clues** — a short list of clues ready to drop this session:
  pull from wherever mysteries/clues are tracked, prioritizing anything
  flagged as under-seeded or thin on evidence. Note *where* each clue
  naturally surfaces *and how the players actually obtain it* — a fact
  with no scene, action, check, or bargain that yields it is not a clue
  yet. **The division of labor is fixed: the DM presents a clue; the
  players interpret it.** Draft every clue in the format file's payload
  shape — **Show / They learn / Points at** (load that section now),
  never a bare conclusion with a destination tag. Check each *They learn*
  line against the live campaign state: it must be interpretable using
  only what the party has already encountered as of this session. Tag a
  clue a **lead** only if it passes the format file's actionability test;
  content that reads only in retrospect is **foreshadow** — keep it,
  label it, never count it as a lead. **Then dose delivery** — a *timing*
  rule atop the layer cake's *count* rule: it sets when in the session,
  and how loudly, each clue surfaces — never *which* node comes next:
    - a **forward/exit lead** — one pointing out of the current node —
      **surfaces late in node**: let the party work the node before the
      next one pulls at it.
    - a **deferred-thread tease** — foreshadow for a deliberately gated
      thread — lands **latest & flattest — offhand, once, no chaseable
      trail**, so a compelling premature clue can't metastasize into an
      all-night rabbit-hole.
  A lead the repo's clue-seeding skill (`seed-clues`, if installed)
  already tagged with its delivery timing inherits that tag here. These
  become the page's *Key Plot Points* and keyed-area clue payloads.
- **Key NPCs** — the roster table in the format's shape (the format
  file's conventions own the columns). Pull it from the session's own
  prep — strong start, likely scenes, encounters — plus any NPC the live
  campaign state says is due to reappear. The roster is durable: on a
  lean-sheet run, file it onto the session's page if one exists.

### Extending — only what's thin

- If the likely scenes aren't obvious from the live campaign state alone,
  add **Potential Scenes** — 2–4 scenes, each tied to a thread or place,
  not a scripted sequence. A scene the spotlight plan aims at carries its
  `Spotlight (scene):` line like any other (format file, *Spotlight
  lines*) — that annotation is the only page trace the plan leaves.
- If a location central to tonight's likely play doesn't have enough on
  record to run it cold, add **Fantastic Locations** — pull the
  sensory/tactical detail already established; if the location needs real
  depth, fork on what tonight's play actually needs. **Fiction depth** —
  the place has to read as a real, textured situation — load
  [`node-deepening.md`](node-deepening.md) and follow it. **An interior
  to explore room-by-room** — that's a keyed site, a trade to the
  dungeon skill, not a deepening pass. Either way, never invent the depth
  inline.
- If an NPC is due to reappear or react to recent party action, add
  **Important NPCs** — the depth pass (wants, knows, attitude) on top of
  the roster, pulled from that NPC's record and the live state.
- **Never do monster prep inline.** Fights are a trade to the
  combat skill.
- **Skip rewards** unless one is clearly owed (a promised item, a favor
  called in, a thread that resolves) — then note it as a single line for
  the Conclusion. Favors, information, and access count as rewards too.
  **Loot parity** governs any reward that is an item: read recent item
  receipts from the record (the last few session recaps and the player
  pages) and aim the item at a PC light on recent loot, never at a PC
  who banked items in the last played session. A promised item overrides
  parity — it belongs to the PC it was promised to. The Conclusion line
  for an aimed item names its target PC, for the same reason a spotlight
  line does: the name is what makes the handout reconcilable after play.

**Lean-sheet exit:** if the DM wanted the sheet, present it in chat as a
single markdown block headed by session number/date, every line traceable
to the record, closing with a one-line note on what's thin or missing.
Offer to go on to the full page; stop unless they say yes. The sheet is a
prep aid, not canon — only its one durable product (the Key NPCs roster)
is filed, as above. The spotlight plan is not filed on a lean-sheet run
either: a sheet with no page behind it simply spends it in chat.

**Done when:** the lean set exists, the spotlight plan covers every PC (a
beat or named resting), and each extension was either added or ruled
unnecessary.

## Step 4 — Draft the page

Read [`session-page-format.md`](session-page-format.md) now — skeleton,
boundaries, conventions — and compile Step 3's material into it, in the
campaign repo's established link and formatting conventions. The sibling
session pages are the exemplars for grain and voice.

Decisions the build forces (a concrete pick, a name, an objective) are
made explicitly and filed where the repo keeps decisions and open
questions.

**Spend the spotlight plan into the page.** Every beat the plan allocated
lands as its own annotation at the scene that stages it — the format
file's *Spotlight lines* convention gives the two shapes. This step
writes the scene lines for beats staged in non-combat scenes; the beats
riding on fights and keyed sites come back annotated from the Step 5
trades, and the plan is reconciled against the whole page there.

**Draft to green against tonight's contract.** The Spec-axis checks Step
2 derived read the page you are writing, so run them as you draft and
clear what they report before moving on. That is the red-green half, and
why the derivation happens before drafting: a constraint you can only
fail once the whole page exists is one you learn about too late to build
differently.

**Done when:** every skeleton section is either filled or its gap named
on the page, and every beat this step stages carries its scene line.

## Step 5 — The trades

Hand off, don't inline:

- **Fights** — the method doc's combat pacing sets how many; each one is
  a hand-off to the repo's combat skill (`combat-generator`, if
  installed) **through its delegate interface** (its *Invoked as a
  delegate* section): hand it the fight situation, the party and rosters,
  the difficulty band, and the beat the plan allocated to that fight; it
  hands back the sized encounter block and its `> [!encounter-meta]`
  filing block, which you embed as-is. It owns sizing, complications,
  spotlight texture, and the meta format behind that boundary. A fight it
  can't be told about aims for itself and spends nothing.
- **Maps** — the format wants a map per location set, and the method doc
  may require a node map of the session's explorable places. Generate
  them in **the session's own declared art style** (the format's
  session-art convention — never a house map default), via the repo's art
  skill (`campaign-art`, if installed); fall back to a hand-drawn
  ASCII diagram if the repo has no art pipeline.
- **Keyed sites** — when Step 3 found a location the party will explore
  room-by-room, the whole site is a hand-off to the repo's dungeon skill
  (`dungeon-generator`, if installed) **through its delegate interface**
  (its *Invoked as a delegate* section): hand it the anchor node and
  objective, the party and rosters, the scale, and the session's
  spotlight plan; it hands back the runnable dungeon package with its own
  fights already sized as `> [!encounter-meta]` blocks, which you embed
  as-is. It owns the room list, the non-linear edges, the per-route
  resource arc, and its own fights behind that boundary — it spends this
  session's spotlight budget rather than allocating a second one. Don't
  also send those fights to the combat skill; the dungeon skill sizes
  them.
- **Thin clue coverage** — if the slate leaves a revelation or route
  under-clued, hand the gap to the repo's clue-seeding skill
  (`seed-clues`, if installed) rather than padding the slate by hand.

**Then reconcile the spotlight plan** — here, once the trades have
brought their annotations back. Walk the plan against the finished page.
A beat the page never staged is not a rest, but absence on the page reads
as one, so say so in the run — name the PC and the beat that went
unplaced, and either find it a scene or tell the DM it dropped. The plan
itself still files nowhere.

**Done when:** every hand-off's product is on the page, in that skill's
own format, and every allocated beat is either annotated on the page or
reported unplaced.

## Step 6 — Definition of done — the mechanical self-check

The checklist in [`session-page-format.md`](session-page-format.md) is
the authority; this step runs its **mechanical rows as executable
self-checks** over the drafted page you hold in context, before Step 8
reports and offers. Checking is not filing: the DM's yes in Step 8 stays
the sole trigger that writes to a page. Where a checklist item and the
method doc disagree, the method doc wins; the brief wins over both, per
Step 0.

**Inherit, don't re-check.** The fights and keyed sites on the page
arrived already self-checked by the delegates that built them
(combat-generator's rows, dungeon-generator's rows). Run only the rows
the *page and session* own. Where a page-owned check reads a delegated
block — **fights-are-encounter-meta** reads that a fight is *filed* as an
encounter-meta callout — it grades the block's presence and shape on the
page; the block's internals (the XP arithmetic) arrived checked.

**Two artifacts, two subsets.** The session-page rows grade the session
page. When Step 3 deepened a thin node via
[`node-deepening.md`](node-deepening.md), the two node-page rows grade
that separate node page.

**Compile to shape first.** The checks read the format file's fixed
shapes — the ordered skeleton headings, the roster table's header, the
Show / They learn / Points at clue blocks, `> [!encounter-meta]`
callouts, the two spotlight-annotation shapes. A facet not in shape is
invisible to its check.

- **Run the page-owned checks.** Hand the drafted page to
  `run_checks(output, "build-session",
  ["build-session/skeleton-sections-in-order", "build-session/key-npcs-header",
  "build-session/role-word-count", "build-session/stat-block-resolvable",
  "build-session/location-uses-page-keys", "build-session/contents-index",
  "build-session/no-empty-scaffolding", "build-session/clue-payload-shape",
  "build-session/slate-indexes-only", "build-session/conclusion-leads",
  "build-session/foreshadow-not-a-lead", "build-session/fights-are-encounter-meta",
  "build-session/art-style-declared", "build-session/art-pieces",
  "build-session/float-before-prose",
  "build-session/art-style-differs-from-neighbors", "build-session/links-resolve",
  "build-session/hotspot-map", "build-session/keyed-site-carries-map",
  "build-session/edges-not-dm-visible", "build-session/spotlight-plan-not-filed",
  "build-session/spotlight-annotations-name-pc",
  "build-session/spotlight-shapes-separate"], context={"roster": <the Step 3
  spotlight roster>, "neighbor_art_styles": [<the neighboring sessions'
  art_style keys>]})` — the runnable checks live beside this skill at
  [`scripts/mechanical_checker`](scripts/mechanical_checker), and each
  id's promise is documented there. **Always hand the roster in** —
  **spotlight-annotations-name-pc** refuses to run without it rather than
  fake a verdict. Hand the neighbors' `art_style:` keys when they exist;
  **art-style-differs-from-neighbors** stays silent without them (the
  first session in a campaign has no neighbors). When Step 3 deepened a
  node, also run `run_checks(node_page, "build-session",
  ["build-session/clue-web-section-present",
  "build-session/clue-web-indexes-only"])` over that node page.
- **Run tonight's contract checks over the same page.** A second call
  into the same library: `run_checks(output, "build-session", <the ids
  brief_checks returned>, context={"brief": <the brief body, verbatim>,
  "canon_record": <the campaign canon record extract>})`. **Hand the
  brief verbatim** — the library reads the fields out of it, and a
  retyped contract is the one place a builder could paraphrase its own
  constraints in its own favour. **brief-introduced-canon** and
  **brief-locked-subject-canon** are defined as diffs against the
  campaign canon record, so both need that extract and refuse to run
  without it. **brief-locked-subject-canon** grades the Locked lines as a
  whole rather than any one field, so it is not in `brief_checks`'
  fill-in set — include its id in this call whenever a brief is in force
  (a library-owned row with a fixed id, not a check of your own
  invention). A field the brief left blank yielded no id at Step 2 and is
  graded nowhere — silence is never a constraint. The brief's
  rubric-graded fields belong to the Spec checker in the judgement pass
  below.
- **Compute the spotlight-coverage pre-pass.** Call
  `spotlight_coverage(output, <the Step 3 spotlight roster>)` from the
  same library. It is **not a check** — an uncovered PC is legal
  ("absence is the record": a PC named nowhere was planned as resting).
  It returns the uncovered set and each PC's beat share; carry that
  forward to the judgement pass, where **spotlight-coverage** rules on
  whether each rest is defensible — the only place the coverage promise
  is graded.
- **Self-heal, then escalate.** Drive the findings through the shared
  [`self-heal-loop.md`](scripts/mechanical_checker/self-heal-loop.md):
  re-derive each finding, up to three attempts per check, re-running that
  check after each. A finding that heals is telemetry and never reaches
  the DM. A check still failing after three attempts is **unhealable** —
  surface it in Step 8's report/offer as a terminal mechanical
  escalation: which check, expected vs. actual, where on the page, and
  what you tried. No confidence hedge — a compiler is certain. The
  loop's only writes are the out-of-band run record and findings-log
  appends it instructs; the page itself stays untouched until the DM's
  yes.

**Done when:** every check passes or heals, and any unhealable survivor
is stated for the DM — a named gap is prep information; a silent one is a
defect. The subjective rows the page owns are the judgement pass below,
which runs next and gates completion before Step 8's offer.

## Step 7 — Definition of done — the judgement pass

The self-check above settled the promises a compiler can settle. The
subjective ones — named NPC rows, interpretable clues, defensible rests,
plain run-time language — you must not grade yourself: you mark your own
homework, and you mark it kindly. Once the page (and any deepened node)
is drafted and self-healed, launch a **fresh checker** per
[`scripts/judgement_checker/checker-launch-protocol.md`](scripts/judgement_checker/checker-launch-protocol.md)
and let it try to disprove the artifact. This gates *completion*: Step
8's report/offer does not form until the checker approves or the loop
exhausts.

**Inherit, don't re-grade.** The checker is handed only build-session's
rubric subset — no combat row, no dungeon row — so it is structurally
unable to re-grade a delegated fight or keyed site, exactly as the
mechanical self-check re-runs no delegate row.

**Two artifacts, two subsets** of
[`judgement-rubric.md`](judgement-rubric.md):

- the **session-page subset** `[build-session/npc-rows-named,
  build-session/no-page-history-preamble, build-session/lead-actionability,
  build-session/spotlight-coverage, build-session/stat-block-sweep-page-wide,
  build-session/plain-language]` grades the **session page**;
- the **node-page subset** `[build-session/clue-interpretability,
  build-session/no-plot-decisions]` grades the **deepened node page** —
  run it only when a node was deepened this run.

**Two axes, two checkers.** Both subsets above are the Standards axis and
see no brief — they grade against library promises, a rubric identical on
every run. Tonight's contract has a different source of truth, and one
agent holding both can trade them off ("the brief asked for this, so the
plain-language row can slide"), so the **Spec axis is a separate checker,
launched in parallel with these and its verdict never merged into
theirs**. Hand it the brief as a **tracker issue URL, body only** — never
retyped text, never the comment thread — plus the campaign canon record
extract. Its whole rubric is
[`spec-axis-rubric.md`](spec-axis-rubric.md) — the subset
`[build-session/brief-premise-enacted, build-session/brief-fit-to-geography,
build-session/brief-locked-subject-canon]` — and it carries no Standards
row. There are no waivers on either axis.

- **Launch per the protocol.** Each checker is fresh-context and
  read-only, handed only: the artifact as it stands, its rubric subset
  (named as build-session's), the party roster, and — session-page
  subset only — the spotlight-coverage pre-pass output (computed fact
  any reader could re-derive, never your reasoning). It returns a plain
  `approve | disapprove` with advisory findings citing inventory rows
  and locations, carrying no fix; its default when it cannot tell is
  disapprove. **plain-language**, **clue-interpretability**, and
  **spotlight-coverage** carry labeled golden corpora
  ([`corpus/plain-language/`](corpus/plain-language/),
  [`corpus/clue-interpretability/`](corpus/clue-interpretability/),
  [`corpus/spotlight-coverage/`](corpus/spotlight-coverage/)) the
  checker reads to pin their boundaries.
- **Back-pressure — up to three rounds.** On `disapprove`, drive
  [`scripts/judgement_checker/back-pressure-driver.md`](scripts/judgement_checker/back-pressure-driver.md):
  you — this same invocation — refine the artifact against the ranked
  findings, then launch a **new** fresh checker; you own the cross-round
  ledger (`fixed` / `skipped` / `no_change_needed`). A round with any
  **`build-session/brief-*`** finding regenerates instead of refining:
  a fresh builder rebuilds the page from the capped carry-forward,
  never from the discarded draft. Three rounds, then the loop exhausts.
- **On exhaustion, enrich Step 8's one offer.** Surviving findings fold
  into the existing report/offer — promise-pointers, artifact anchors,
  and your outcome ledger: *"N issues I couldn't resolve — file anyway,
  or take over."* An `approve` leaves the offer indistinguishable from
  today's. Judgement gates *completion*, not filing: the checker is
  read-only over your page, and the DM's yes stays the sole trigger that
  writes to one.

## Step 8 — Report

Close in chat with: what was built, the decisions the build forced (and
where each was filed), what the record and the corpus left empty and you
invented instead, and what remains thin. Offer the repo's stress-test
skill (a grilling skill, if one is installed) for any decision heavy
enough to deserve pressure before it reaches the table — and offer a PDF
render ([`render.md`](render.md)) if the DM wants a printable copy.
