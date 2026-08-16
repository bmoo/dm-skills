# The session page — format and definition of done

The library's **one** statement of what a table-ready session page is. No
other skill restates it: `build-session` compiles pages in this shape and
walks the checklist below as its definition of done; the PDF renderer
([render.md](render.md)) and any campaign-side site renderer consume pages
in this shape. Where an item here and the campaign repo's own method doc
disagree, **the method doc wins**.

The skeleton is the convention WotC adopted for its 2024-era adventures:
a chapter a DM can run one or two sessions from, front-loaded with
everything needed to prep, then keyed locations to run from at the table.

## The skeleton

Sections, in order. Every section is either filled or its gap named on the
page — a named gap is prep information; a silent one is a defect.

1. **Title + header** — session number/title, the level badge ("Built for
   level N characters"), a one-line scope note ("sized to one or two
   nights of play"), and a tagline if the campaign uses
   them. **No page history.** Provenance, rework notes, and "how this page
   came to be" paragraphs
   never open a session sheet — they live in the repo's log and commit
   history. Beyond the badge line the header carries at most a single
   italic navigation line and a
   one-line **contents** index: `*Contents: [a](#a) · [b](#b) · …*` —
   5–8 links to the page's key stops (the prep list, the map, the clue
   slate, contingencies, the close; a played page adds the recap). One
   line, no nesting — a jump bar, not an outline. Likewise
   the page carries **no post-play scaffolding**: no empty Recap/Notes
   sections waiting to be filled — the repo's played-session flow adds
   the record after the table, not before.
2. **Key Plot Points** — 2–4 bold-labeled beats ("Sirens at the
   Reservoir.", "The Night Watch Vanishes.") that carry the session's
   story: what's true, what
   the players can discover, where it heads. This is where the session's
   secrets & clues surface as plottable beats — each traces to the repo's
   revelations tracker.
3. **Preparation** — numbered steps the DM walks before play: read the
   background, review the Key NPCs table, copy map handouts, and
   **bookmark stat blocks** (a list of every creature that can appear,
   each as a resolvable reference). One house addition lives here: the
   embedded **node map** where the repo's method requires one. **The
   session spotlight plan is not filed here** — or anywhere on the page as
   a table. It is transient prep-run state; what lands on the page is its
   *effects*, one **Spotlight (scene)** line or encounter-meta `Spotlight:`
   field per staged beat, at the scene that stages it (see the conventions
   below).
4. **Key NPCs** — one table, one row per NPC or creature likely to
   appear: **Name | Personality | Role | Stat Block | Location**.
   - **Name** links to the NPC's page where one exists. **Every row is
     named** — a descriptive placeholder ("the strongman", "the handler")
     is a defect. A name the fiction hides from the players still sits in
     the row for the DM, concealment noted ("Kate — don't name her"); an
     NPC nobody has named yet gets named now, in the campaign's own
     naming idiom.
   - **Personality** is a single character from popular fiction the NPC
     plays like at the table. Pick from a canon the DM actually knows;
     the library default is American movies and TV of the late 1970s
     through the 1990s. Groups get one analog for the group's voice.
   - **Role** is a short phrase (3–8 words).
   - **Stat Block** is a resolvable reference per the conventions below,
     **on every row — combat or not**: social and background NPCs carry
     the block their checks run off. `N/A (non-combat)` is a defect; a
     bare creature name
     is too. A parenthetical note may qualify the block ("never fights —
     stats for checks only").
   - **Location** uses the page's own keys (`T1`, "Beginning the
     Adventure"), not prose directions.

   Pull the roster from the session's own prep plus any NPC
   the live campaign state says is due — don't pad it with everyone who
   *could* exist at the location.
5. **Adventure Background** — what is actually going on, written for the
   DM: the situation's truth, the antagonist's plan in motion, what the
   players' arrival disturbs.
6. **Beginning the Adventure** — the strong start: a read-aloud opener
   (`> [!read-aloud]`) that lands the party in the fiction inside the
   first two minutes, plus what happens in the opening scene. **When
   the opening scene happens at a keyed area, this section carries only
   the approach** (travel, arrival color, any en-route table) **and ends
   by handing off to that key** ("run the opening as `T1`") — the scene
   itself lives once, in the keyed section, never in both places.
7. **The body: named situation and location sections** — one section per
   scene cluster or explorable place ("Exploring Redwood Watch",
   "Death-at-Sunset's Lair"). A location set carries, in this order: the
   **map** (with a player-version handout where one exists), the **keyed
   index** directly under the map — one line per key, linked to its
   section, so map and key list read together — a **Features** preamble
   for what holds everywhere (ceilings, light, walls, tracking, local
   rules), then **keyed areas** (`T1`, `R3`…) each with its run content — read-aloud
   text, NPC voices and tells, clue payloads (each one self-contained
   block in the conventions' shape below), and fights as
   `> [!encounter-meta]` blocks in the fight procedure's format.
8. **Conclusion** — how the session's likely endings resolve, rewards owed
   (an item, a favor, information, access — an item aimed at a particular
   PC names its intended PC, so the handout reconciles after play; aiming
   evenly across the party is prep's job, `build-session`'s loot
   parity), and the **exits**: at least
   two live leads into the clue web toward other nodes, with no steer. A
   session that ends nowhere is a defect.
9. **Lore appendix** *(optional)* — a "Rise and Ruin of the Salt
   Barons"-style closer, only where the campaign record already holds the
   material.

## Boundaries — what shapes the page

- **The session page is an output, compiled from the campaign record.**
  Planning lives in the node and story pages; the session page is
  *generated from* them, and the DM must run the whole night from it
  alone — run content inlined as a prep-time snapshot, links reserved for
  trivial detail, never required mid-session. New material a node should
  own files on the node first, then compiles in. This is the repo's one
  sanctioned duplication: node pages stay canonical; on conflict the node
  wins and the snapshot is refreshed.
- **Situations, not sequences.** Scenes and keyed areas are material the
  table will reorder, never a script.
- **The page navigates itself.** Preparation steps link the sections they
  cite; Key Plot Points link forward to the sections that carry them; the
  Key NPCs Location column links to keyed areas; each keyed section ends
  with a small link back — to the map when the page carries a clickable
  hotspot map, otherwise to the keyed index.
- **The map navigates too.** Where the repo's site renderer offers a
  clickable keyed-map treatment (check the repo's publish/site skill), a
  keyed map embeds with a labeled hotspot link per key — each jumping to
  that key's section — never as a plain unlabeled image. Keys the art
  gives no landmark still get a badge at a plausible spot. Without such a
  renderer, the keyed link list beside the map carries the correlation.
  When the keyed site has a rendered tactical map (the keyed-site
  procedure's render step), **that render is the hotspot map** — one map, the sheet
  the DM actually runs from; an earlier stylized site illustration is
  replaced in place when it files, never shipped alongside. Badge
  positions start from the layout's room centers but are verified
  against the drawn render — rooms drift in generation.
- **A keyed site carries its map.** A session page with keyed areas
  **embeds its rendered map** — required, not polish. The per-key exits
  enumeration is abolished (*Connections, not an edge table*, below) and
  the edge table itself is machine state no DM ever sees, so **the room
  prose and the map are the only human-readable topology the site has**.
  A keyed page with no map is therefore **silent data loss — a keyed
  dungeon the DM cannot navigate**, which is why it is checked rather
  than merely asked for. The render files with the session it was built
  for, and it is the page's one keyed map.

## Conventions

- **Stat-block references.** Every creature named anywhere on the page —
  the Preparation bookmark list, the Key NPCs table, read-aloud text,
  encounter blocks, contingencies — carries a resolvable stat-block
  reference: `{monster:Name}` (the renderer's token; see
  [render.md](render.md) for the full token set) for published creatures,
  a campaign-record link to its stat-block page for homebrew or reskins.
  A bare creature name is a defect: a missing link is not a broken link,
  so only a deliberate sweep catches it.
- **Plain language in run-time text.** Everything the DM executes from
  mid-session — encounter blocks, spotlight lines, keyed-area run notes,
  contingencies — states **mechanics and named page fiction only**. A
  coined term is legal only if the page defines it before or where it's
  used ("the Forgotten", "the candle-ledger"); an undefined metaphor
  ("the needle", "polish the brass") is a defect, however evocative. (These
  bad examples are deliberately inert — an exemplar phrase vivid enough to
  admire is vivid enough to leak into generated pages. Keep them boring.)
  Two boundaries bind: **naming is not defining** — a term merely
  mentioned earlier on the page (a rumor "of a deep bargain") is still
  undefined at use, while a term explained in the clause that uses it
  ("a breath-book — a slim journal of confessions in a whisper-code") is
  defined where it's used; and the rule is **scoped to run-time text
  only** — the same aphorism that breaks a spotlight line is legal in a
  design-intent aside, because the DM never executes an aside mid-scene.
  The test: a competent DM who has never seen this campaign could execute
  the line with only this page open.
- **Read-aloud is what they perceive.** A `> [!read-aloud]` block —
  wherever it appears: the opener, a keyed area, a clue payload's Show —
  carries only what the characters **see, hear, smell, feel, or taste
  right now**, plus dialogue spoken in their presence and text they can
  read. The test: **could someone standing there perceive this, from
  where they stand, right now?** Both halves of the test bind:
  - **Knowledge.** Immediate, universal inference is perception ("a
    long-abandoned mill") — anyone at the scene concludes it at a glance.
    Knowledge nobody present holds is not: hidden history, causes,
    another's intent, and meanings stay out of the box, however
    atmospheric the phrasing. Mood language is welcome exactly as far as
    it stays a sensation ("the air hangs heavy and still") and breaks the
    moment it asserts an unperceivable fact as fact. Involuntary physical
    reactions are perceptions ("a chill crawls up your arms"); imposed
    emotions and decisions are not ("you feel terrified", "you know you
    shouldn't be here").
  - **Vantage.** The box describes only what is perceivable from where
    the party stands at that moment. Detail in darkness, behind a door,
    inside a container, or too far to make out appears only as what it
    would actually register as — a dark shape slumped against the far
    wall, never that shape's inventory.
  What the box excises is not deleted: it lands beside the box as DM
  text keyed to the interaction that reveals it ("if they examine the
  stones…"), or as a clue payload where it is discoverable knowledge.
- **Spotlight lines.** The session's spotlight plan never appears on the
  page as a table; each beat it stages appears at the scene that stages
  it, so the page records what was aimed where without holding the plan.
  A **fight** carries it as the `Spotlight:` field of its
  `> [!encounter-meta]` block (the fight procedure's *Filing format*; the block's
  shape is specified below, in
  [The encounter-meta block](#the-encounter-meta-block)). Any other
  scene — a body situation section, a keyed area, a Potential Scene —
  carries a one-line, behind-the-screen note in a `> [!dm-sidebar]`:

  > **Spotlight (scene):** <PC name> — <pillar: social / exploration>;
  > <the staging that fires their flagged ability, and the tell that
  > points at it>

  **The two labels are deliberately distinct.** The fight-variety check
  greps encounter-meta `Spotlight:` fields only — a scene line must never
  read as a fight in that ledger. `Spotlight (scene):` is read by
  catch-up, which reconciles both shapes after play.
  **Every staged beat names its target PC** — an unnamed line is a
  defect, because the named PC is what makes the beat reconcilable.
  **Absence is the record:** a PC named nowhere on the page was planned
  as resting. A beat the plan allocated but the page could not stage is
  neither — build-session flags it in the run rather than leaving it to
  look like a rest.
- **Connections, not an edge table.** A keyed site's render-ready edge table
  is machine state, not DM-facing content. It is filed on the session page
  **wrapped in an HTML comment**, so it renders to nothing and no reader ever
  sees it, while the map render and the page's own topology check keep reading
  it out of the raw markdown. It **stays on the page — never deleted**: it is
  the only record the site's topology has, and the map is re-rendered from it.
  **Edge IDs appear nowhere a DM reads**: not in a keyed area's exits, not in
  body prose, not in a `> [!dm-sidebar]`, not in an `> [!encounter-meta]`
  terrain line. A page that says `E7` points the DM at an identifier the page
  will not resolve. **Keyed-area IDs are unaffected** — `T1`, `N3` and their
  kin stay in prose, because they resolve visually against the hotspot map.
  **The per-key exits enumeration is abolished, not de-coded.**
  Connections appear in the room's own prose, and only where the connection is
  narratively relevant — never as an inventory of every way out. The
  connection's type (open, door, locked,
  secret, grate, vertical, hazard) and any DCs live in that prose too, where
  the DM reads them with the party standing in the room: the map can draw a
  glyph, but it cannot draw a DC.
- **Links and callouts.** Every link resolves; formatting, callout, and
  link style match the campaign repo's guide. Renderer directives
  (`> [!read-aloud]`, `> [!dm-sidebar]`, `> [!encounter-meta]`,
  `> [!map]`, …) are the library's house callouts even when no PDF is
  requested — the site renderer reads them too.
- **Clue payloads.** The DM *presents* a clue; the *players* interpret
  it. A clue lives on the page as **one self-contained block at its
  keyed area**, with three labeled parts:
  - **Show** — the concrete in-fiction content the DM presents, in
    perceivable form: the words spoken, the image seen, the object
    handled. The delivery text itself states the information the
    players receive — staging whose meaning lives only in DM-facing
    notes is not a Show.
  - **They learn** — the takeaway as the players' own notes would
    record it: the facts the table holds once the Show lands.
  - **Points at** *(behind the screen)* — the node or revelation the
    clue targets, the action the players can take on it, and what the
    clue deliberately does *not* convey.

  Build the block from the ordinary constructs — bold-labeled bullets,
  `> [!read-aloud]` for a verbatim Show, `> [!dm-sidebar]` for the
  Points-at — no dedicated directive. **One clue, one home:** every
  element the payload mentions has its meaning *for this clue* stated
  inside the payload; a link to a sibling payload is elaboration,
  never required reading. **The slate is an index:** the
  secrets-and-clues list carries one line per clue linking to its
  payload; no clue content lives only in the slate. **Lead vs.
  foreshadow:** tag "Lead →" only when the *They learn* line passes
  the actionability test — holding it plus what the party has already
  encountered, the players could decide where to go or what to do
  next. Content that reads only in retrospect is labeled
  **foreshadow**, never "Lead", and never counts toward the
  Conclusion's exits.
- **Session art.** Every session page owns **its own art style, themed to
  that session's fiction** — and styles must **vary widely between
  sessions**: change the *medium and register*, not just the palette
  (oil painting, screen-print poster, comic-book linework, ink-and-wash,
  photoreal, sci-fi concept art…). Before declaring a new session's
  style, read the neighboring sessions' `art_style:` keys and pick
  something clearly distinct from all of them. **No house default
  (sepia, parchment) applies.** Record the style in the page's
  frontmatter (`art_style:`, a short phrase — "neon carnival
  screen-print") and hold it across *every* image on the page, the node
  diagram included; the style is never stamped visibly on the art (no
  style/artist credit line).
  Every session carries **four narrative pieces**, regardless of length:
  1. **The chapter splash** — an establishing piece placed **immediately
     after the title/badge block**, before any body section, full width
     and **portrait by default**. The page opens on art.
  2. **The capstone piece** — the session's climax or exit beat.
  3. –4. **Two more at the DM's judgement**, chosen fresh each session —
     not the same slots every time. Favor floats
     (`> [!art-left]` / `> [!art-right]`) so prose wraps beside them —
     and place a float directly before the paragraphs or bullets that
     wrap it, never adjacent to another callout: callouts clear floats,
     so a float against a sidebar strands the image beside empty space.
  **The node diagram does not count** toward the four: it lives with the
  scene list (never at the top of the page), rendered in the session's
  declared style like everything else.
  Character-focused moments render portrait and float beside the text;
  establishing or crowd scenes render landscape or portrait, full width
  (`> [!art]`). The callout body is the image embed plus **one caption
  line — a short in-fiction description of the moment**, **or a verbatim
  read-aloud quote when one sings**. Beat pieces sit immediately after
  the read-aloud (or anchor paragraph) of the moment they depict.
  Ground the prompt in the page's own words, and pass existing portraits
  of recurring NPCs as generation references so they stay on-model.

## The encounter-meta block

Every fight on the page files as an `> [!encounter-meta]` callout — the
machine-findable summary of the fight's vitals, with the prose it sits in
(terrain, tactics, the complication's staging) as normal page text around it.
the fight procedure (`combat.md`) composes the block (its *Filing format*
section) and the keyed-site procedure (`dungeon.md`) files its fights in the
same shape; **this section is the
library's one statement of that shape** — nothing else restates it.

```markdown
> [!encounter-meta]
> **Party:** <size and level sized for, e.g. 6 PCs, Level 1>
> **Enemies:** <each creature × count with looked-up XP> → **<total XP>**
> **Budget:** <difficulty>, level <L>, <N> PCs = <per-char> × <N> = **<budget>** (<spent>, <remainder>)
> **Terrain:** <one line — levels, cover, hazards>
> **Spotlight:** <texture; if aimed/puzzle, who and the staging that fires their ability>
> **Objective:** <the win condition — the complication usually lives here>
> **Note:** <optional — table rules, dials, absence adjustments>
```

Party, Enemies, Budget, Terrain, Spotlight, and Objective are required;
Note is optional. Every creature named on the `Enemies:` line carries the
stat-block reference the conventions above require — a bare creature name is a
defect here as everywhere on the page. The `Spotlight:` field is the **fight**
half of the page's spotlight annotations (see *Spotlight lines* above): a
`Spotlight (scene):` line never sits inside this block, which is what keeps the
fight-variety ledger fights-only.

This is a **library-owned format — never improvise its shape.** The block above
is what the code reads: the parser (`scripts/session_parser.py`) reads the
callout, the deterministic self-check asserts its six labels, and campaign
repos may build tooling that parses it. Changing the shape is a breaking
change, and every reader is held to this section rather than to a copy of it
(library sync obligations: `docs/campaign-contract.md`).

## Definition of done

Walk every box; each points at the authority it checks against:

- [ ] Every skeleton section is filled or its gap is named on the page.
- [ ] Every session-prep rule in the repo's method doc is satisfied
      (pacing defaults, required elements).
- [ ] Every beat the session's spotlight plan staged carries its page
      annotation — an encounter-meta `Spotlight:` field for a fight, a
      `Spotlight (scene):` sidebar line otherwise — and each names its
      target PC. The plan itself appears nowhere on the page: no table,
      no Preparation entry.
- [ ] The Key NPCs table is complete: everyone likely to appear, no
      padding; every row named (no descriptive placeholders), every row
      carrying a personality analog, every row's stat block resolvable —
      non-combat rows included.
- [ ] No page-history preamble and no empty Recap/Notes scaffolding —
      the header carries at most one navigation line plus the one-line
      contents index (prep list, map, and clue slate among its stops).
- [ ] Every clue traces to the repo's revelations tracker, is plantable
      at a named spot, and has a player-reachable vehicle: a concrete
      scene, action, check, or bargain on the page yields it. A fact
      stated only in DM-facing text is not a placed clue.
- [ ] Every clue payload is one self-contained block in the
      conventions' shape — Show, They learn, Points at — at its keyed
      area; the slate only indexes it; no payload requires another
      payload, a sidebar, or a node page to state its meaning.
- [ ] Every clue's *They learn* line is interpretable by the players
      using only what they have already encountered as of this session
      (check the live state — a clue must not require unseen content
      to mean anything), and every "Lead →" tag passes the
      actionability test: holding the takeaway, the players could
      decide where to go or what to do next. Retrospective content is
      tagged foreshadow, and only true leads count toward the
      Conclusion's exits.
- [ ] Every fight is an `> [!encounter-meta]` block, complete per the
      fight procedure's own rules.
- [ ] Maps are embedded per location set and depict only what the page
      establishes.
- [ ] Where the repo's site renderer offers a clickable keyed-map
      treatment, every keyed map embeds with a hotspot link per key
      (see *The map navigates too*) — no keyed map ships as a plain
      unlabeled image, and no redundant text diagram of the same
      structure sits beside a hotspot map (a superseded ASCII duplicate
      is a defect; an authoritative diagram on a node page is not).
      Where a tactical render of the site exists, it is the page's one
      keyed map — a superseded site illustration alongside it is the
      same defect.
- [ ] The page has keyed areas only if it also embeds their rendered map
      (see *A keyed site carries its map*) — with the exits enumeration
      gone, a keyed site with no map leaves the DM no topology to read.
- [ ] The keyed site's edge table is on the page and concealed inside an
      HTML comment, and no edge ID survives anywhere a DM reads — exits,
      body prose, sidebars, encounter-meta blocks. No per-key exits list
      remains: each keyed area's connections are in its own prose, with the
      connection's type and any DCs, where they matter to this session.
- [ ] The session-art convention is satisfied: `art_style:` declared in
      frontmatter and held across every image (node diagram included);
      four narrative pieces — splash after the title/badge block,
      capstone, two judged beats varied from prior sessions; the node
      diagram with the scene list, not at the top; captions in the
      in-fiction form (or the gap is named on the page).
- [ ] The Conclusion leaves at least two live leads to other nodes, with
      no steer.
- [ ] Every item reward aimed at a particular PC names them, and the aim
      followed prep's loot parity (`build-session`'s rewards step).
- [ ] **The page runs standalone:** walk every keyed area, fight, and
      contingency asking "could I run this beat with only this page
      open?" — any beat whose run content lives behind a link is a
      defect. For each clue, ask the same question one block tighter:
      "could I present this clue reading only its payload block?" —
      meaning assembled from elsewhere on the page is the same defect
      within the page.
- [ ] The stat-block sweep is done: every creature name on the page
      passes the convention above.
- [ ] The plain-language sweep is done: no run-time line depends on an
      undefined coinage or metaphor — every term either is a game
      mechanic or resolves to a definition on this page.
- [ ] The read-aloud sweep is done: every read-aloud block — the opener,
      keyed areas, clue-payload Shows — passes the perception test: no
      hidden history, causes, intent, or meanings; no imposed emotions or
      decisions; nothing described beyond the party's vantage.
- [ ] Every link resolves; conventions match the repo guide.
- [ ] Stub references swept: any page that called this session a stub or
      placeholder now reflects the build.
- [ ] The repo's catalog and log are updated per its defaults.

Maintenance: this format is **library-owned** — downstream tooling
(a campaign repo's site renderer, the PDF renderer in `scripts/`) parses
pages in this shape. Treat skeleton or directive changes as breaking: call them
out in the commit message, and keep [render.md](render.md) and the parser
(`scripts/session_parser.py`) in step in the same commit.
