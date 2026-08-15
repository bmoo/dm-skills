# build-session — judgement rubric

The rows the [fresh-context checker](scripts/judgement_checker/checker-launch-protocol.md)
grades a drafted session page (and, when Step 3 deepened one, a node page)
against. This file ships **beside `SKILL.md`** (per
[`scripts/judgement_checker/rubric-format.md`](scripts/judgement_checker/rubric-format.md),
"Where the real rubrics live") and is written in the format that directory
defines. It is build-session's rubric and build-session's only — a fight is
graded against combat-generator's rows, a keyed site against dungeon-generator's,
never these (spec user story 17).

Every row below **is** a `judgement`-method row of
[`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md)'s
build-session tables — **derived from the inventory, never hand-copied**. Two inventory
tables feed this rubric, which is why it is split into two artifacts below. The
`build-session + session-page-format` table carries the page-owned judgement rows
`build-session/npc-rows-named`, `build-session/no-page-history-preamble`,
`build-session/lead-actionability`, `build-session/spotlight-coverage`,
`build-session/stat-block-sweep-page-wide`, `build-session/plain-language` and
`build-session/read-aloud-boundary`; the
`build-session — node-deepening.md` table carries the node-owned judgement rows
`build-session/clue-interpretability` and `build-session/no-plot-decisions`. (The
trace/diff/vision and mechanical rows of both tables are out of scope here — they are
the deterministic self-check's or evaluation harness's responsibility; this rubric holds only the in-scope
`judgement`-method rows the artifacts themselves own.)

## Two artifacts, two subsets (parallel to the deterministic split)

build-session produces **two** artifacts, and each is graded by its own subset —
exactly as the deterministic self-check runs the session page's mechanical
checks over the session page and
`[build-session/clue-web-section-present, build-session/clue-web-indexes-only]`
over a deepened node page:

- The **session-page subset**
  `[build-session/npc-rows-named, build-session/no-page-history-preamble,
  build-session/lead-actionability, build-session/spotlight-coverage,
  build-session/stat-block-sweep-page-wide, build-session/plain-language,
  build-session/read-aloud-boundary]`
  grades the **session page**.
- The **node-page subset**
  `[build-session/clue-interpretability, build-session/no-plot-decisions]`
  grades a **deepened node page** — and
  runs **only when Step 3 deepened a thin node** via
  [`node-deepening.md`](node-deepening.md), which produces that separate artifact.
  A run that deepened no node grades only the session-page subset.

The checker is handed the subset for the artifact it is grading and nothing else.

## Inheritance — build-session inherits from BOTH delegates

The session page pulls in **fights built by invoking combat-generator** and
**keyed sites built by invoking dungeon-generator**. Both arrive **already
judgement-checked**: combat's **stat-block-refs-in-prose** /
**swarm-carries-fragile-creatures** rows ran when combat built each fight, and
dungeon's **objective-routes-cost-differently** / **lead-interpretability** rows
ran when dungeon built each site
(which itself inherited combat's fights). **This pass re-grades none of them.**
The checker is handed only build-session's subset — which holds no combat row and
no dungeon row — so it is **structurally unable** to re-grade a delegated piece,
exactly as the deterministic self-check re-runs no combat-generator row and no
dungeon-generator row (spec user
stories 9/10/20).

## Which rows carry corpora

Five of these nine rows are **structural** judgements (is this cell a name? is this
preamble present? does this creature-mention carry its token?), so each carries
**hand-written anchors only** — no golden corpus: **`npc-rows-named`,
`no-page-history-preamble`, `lead-actionability`, `stat-block-sweep-page-wide`,
`no-plot-decisions`**. Three are **reader-interpretation** judgements (can a stranger
execute this line? can the party read and reach this clue? could someone at the scene
perceive this?), so each carries
hand-written anchors **and** a labeled golden corpus: **`build-session/plain-language`**
(undefined coinage), **`build-session/read-aloud-boundary`** (perception boundary) and
**`build-session/clue-interpretability`** (node-deepening).
These are three of the library's four reader-interpretation rows (`lead-interpretability`
/ `clue-interpretability` / `plain-language` / `read-aloud-boundary`) for which the
format reserves a corpus pointer.

**`build-session/spotlight-coverage`** is the ninth, and neither class. It is the
library's only **legal-absence** row — the one where the deterministic tier can compute
the fact (which PCs the page never names) but *cannot* compute the verdict, because
"absence is the record" makes an uncovered PC either a deliberate rest or a dropped
beat. Its judgement is *is this rest defensible?*, whose criteria words drift exactly
the way the reader-interpretation rows' do, so it carries a corpus too — under the
legal-absence class the [rubric format](scripts/judgement_checker/rubric-format.md)
names alongside reader-interpretation.

A finding against any row here **cites that row's inventory id as its
promise-pointer**, **anchors to where in the output the break is**, and **carries
no concrete fix** — the checker names *which* promise broke; the generator owns
*how* (spec user story 19; shape fixed in
[`scripts/judgement_checker/verdict-contract.md`](scripts/judgement_checker/verdict-contract.md)).

---

# Session-page subset — `[build-session/npc-rows-named, build-session/no-page-history-preamble, build-session/lead-actionability, build-session/stat-block-sweep-page-wide, build-session/plain-language, build-session/read-aloud-boundary]`

The rows below grade the **session page**. (This is build-session's own `npc-rows-named`
row, in the [rubric format](scripts/judgement_checker/rubric-format.md) — aligned with
the format example at
[`scripts/judgement_checker/reference/rubric-example-every-row-named.md`](scripts/judgement_checker/reference/rubric-example-every-row-named.md)
but distinct from it: the reference works the row in isolation to prove the format; this
is the shipped row, sitting beside its four page siblings and the two-artifact split
above.)

## Row `build-session/npc-rows-named` — every Key NPCs row is named

- **Inventory check id:** `build-session/npc-rows-named`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the `build-session + session-page-format` table — method: judgement,
  enforceable-as-written: No. Structural — the deterministic self-check settles the
  table's **shape** (`key-npcs-header` header, `role-word-count` word-count,
  `stat-block-resolvable` resolvable Stat Block, `location-uses-page-keys` Location
  key); `npc-rows-named` grades what no regex can: whether the Name cell holds a *name*
  rather than a role-noun standing in for one.)*

- **Promise text:** Every row of the **Key NPCs** table is **named** — a descriptive
  placeholder ("the strongman", "the handler", "the bartender") is a **defect**. Where
  the fiction deliberately hides a name from the players, the row **still carries it for
  the DM** with the concealment noted (`"Kate — don't name her"`); an NPC nobody has
  named yet **gets named now**, in the campaign's own naming idiom. A **group** row
  carries the group's proper name, not a member list. *(Source:
  `session-page-format.md` — "**Every row is named** — a descriptive placeholder" —
  the Key NPCs **Name** column. The inventory row `npc-rows-named` cites
  the same passage.)*

- **Roster use:** **None.** `npc-rows-named` is structural — it asks whether the Name
  cell holds a name, which is legible from the output alone. The disambiguating context
  is the cell's own text, not the roster. *(The roster is handed in per the launch
  protocol regardless; this row does not consult it.)*

- **Criteria:**
  - **Holds when** every row in the Key NPCs table has a **proper name** in its Name
    cell — a name a player or DM would use to refer to the NPC (`"Kate"`, `"Old
    Harl"`, `"The Verdant Choir"` for a group). A concealed-from-players name still
    **counts as named** when the row carries the real name plus the concealment note
    (`"Kate — don't name her"`).
  - **Breaks when** any row's Name cell is a **descriptive placeholder** standing in
    for a name — a role-noun or epithet with no proper name (`"the strongman"`, `"the
    handler"`, `"the bartender"`, `"Guard 2"`, `"TBD"`, an empty cell). The defect is
    one row; report it at that row.
  - **Cannot tell → disapprove.** If a cell is ambiguous between a name and an epithet
    used *as* a name (`"Red"` — a given nickname the table treats as the name, or "the
    red one" as a placeholder?), the checker **disapproves** and names the row, so the
    generator can disambiguate (add the given name, or note it is a used nickname).
    Uncertainty is a disapprove, never a pass.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** `| Kate — don't name her | Aunt Bea (Andy Griffith) | Innkeeper
    who fronts for the ring | {monster:spy} | T1 |` — a concealed-from-players NPC, but
    the row carries her real name for the DM with the concealment noted. **Named.**
    Holds.
  - **Bad — breaks.** `| the bartender | Sam Malone (Cheers) | Pours drinks, overhears
    everything | {monster:commoner} | T2 |` — the Name cell is a role-noun, no proper
    name. A descriptive placeholder. **Breaks `npc-rows-named`** at this row; the NPC should be named
    now in the campaign's idiom.
  - **Edge — the boundary.** `| Red | Rooster Cogburn (True Grit) | Ferryman who owes
    the party | {monster:commoner} | T3 |` — is `"Red"` a given nickname the table uses
    *as* his name, or a colour-epithet placeholder ("the red-headed one")? If the page
    establishes elsewhere that the party knows him as Red — it reads as his name and
    **holds**; if `"Red"` is bare with nothing making it a used handle, the checker
    **cannot tell** and **disapproves**, naming the row so the generator settles it.
    This is the borderline the criteria exist to draw.

- **Corpus pointer:** *none* — `npc-rows-named` is structural (does this cell hold a
  name?), so hand-written anchors are the floor and the ceiling. (The reserved corpus
  slot is for the reader-interpretation rows `lead-interpretability` /
  `clue-interpretability` / `plain-language` / `read-aloud-boundary` only.)

---

## Row `build-session/no-page-history-preamble` — no page-history preamble opens the page

- **Inventory check id:** `build-session/no-page-history-preamble`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the `build-session + session-page-format` table — method: judgement,
  enforceable-as-written: No. The sibling row **no-empty-scaffolding** covers the
  mechanical case — a regex for the *absence* of empty `Recap`/`Notes` scaffolding
  **headings**, already run in the deterministic self-check. `no-page-history-preamble`
  grades what no regex can: whether the opening *prose* narrates how the page came to
  be. A page-history preamble need carry no telltale heading, so only a judgement of the
  opening text catches it.)*

- **Promise text:** The header carries no **page history**: provenance, rework notes,
  redesign dates, variant-selection mechanics, and "how this page came to be" paragraphs
  **never open a session sheet** — they live in the repo's log and commit history. The
  most the header may carry beyond the badge line is a single italic navigation line and
  the one-line contents index. *(Source: `session-page-format.md` — "**No page
  history.**" — "**No page
  history.** Provenance, rework notes, redesign dates, variant-selection mechanics, and
  'how this page came to be' paragraphs never open a session sheet". The inventory row
  `no-page-history-preamble` cites the same lines.)*

- **Roster use:** **None.** `no-page-history-preamble` is structural — it asks whether
  the page's opening narrates its own authorship history, which is legible from the
  header prose alone. *(The roster is handed in per protocol; this row does not read
  it.)*

- **Criteria:**
  - **Holds when** the header runs title → badge line → scope note → (optional) one
    italic navigation line → contents index → the session's own content, with **no prose
    about the page's own making** — no "originally drafted as", no "reworked after
    session 4", no "this variant was chosen because", no redesign date.
  - **Breaks when** the opening carries a **page-history preamble** — a sentence or
    paragraph narrating provenance, rework, variant-selection reasoning, or "how this
    came to be" before the session's content begins. Report it at the offending opening
    block. (Contrast `no-empty-scaffolding`'s mechanical case: an empty `## Recap`
    heading is `no-empty-scaffolding`'s, not `no-page-history-preamble`'s —
    `no-page-history-preamble` is the *prose* preamble that carries no such heading.)
  - **Cannot tell → disapprove.** If an opening line is ambiguous between in-fiction
    scope-setting the format allows (the scope note, a navigation line) and disallowed
    page-history narration, the checker **disapproves** and names the block, so the
    generator can cut the history or plainly mark the line as navigation. Uncertainty is
    a disapprove, never a pass.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** Header: the title, `*Built for level 3 characters ·
    sized to one or two nights*`, `*See also: [Variant B](…)*`, then
    `*Contents: [Plot](#plot) · [Map](#map) · [Clues](#clues) · [Close](#close)*`, then
    Key Plot Points. No authorship narration anywhere. **Holds.**
  - **Bad — breaks.** Header opens: *"This page began as the western fork of Session 4,
    was split out after the party skipped the docks, and was reworked on 2026-06-11 to
    fold in the smuggler thread."* That is provenance + rework-date + how-it-came-to-be
    — exactly what belongs in the log, not the sheet. **Breaks
    `no-page-history-preamble`** at the opening paragraph.
  - **Edge — the boundary.** Header carries a single italic line: *"Sibling to [Session
    4B](…) — the party's choice at the docks selects which page runs."* Is this allowed
    navigation, or disallowed "variant-selection mechanics" narration? If it reads as a
    **pointer** a DM uses to jump between sibling pages, it is the permitted navigation
    line and **holds**; if it slides into *explaining the selection machinery* ("we
    built two variants because the vote was 3–2 and…"), it is page-history and
    **breaks**. Where the line's intent is unsettled the checker **cannot tell** and
    **disapproves**, naming it so the generator sharpens it to a bare pointer or cuts
    it.

- **Corpus pointer:** *none* — `no-page-history-preamble` is structural (does authorship
  history open the page?), so hand-written anchors are the floor and the ceiling.

---

## Row `build-session/lead-actionability` — "Lead →" only where the actionability test passes

- **Inventory check id:** `build-session/lead-actionability`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the `build-session + session-page-format` table — method: judgement,
  enforceable-as-written: No. The sibling mechanical rows settle the *counting*:
  **conclusion-leads** the Conclusion carries ≥ 2 live leads, **foreshadow-not-a-lead**
  foreshadow-tagged content never counts toward the exits. `lead-actionability` grades
  what no parser can: whether a clue tagged `"Lead →"` actually **passes the
  actionability test** — a mislabelled foreshadow wearing a Lead tag would pass
  `conclusion-leads`/`foreshadow-not-a-lead`'s arithmetic while breaking the promise the
  tag makes.)*

- **Promise text:** Tag **"Lead →" only when the *They learn* line passes the
  actionability test** — holding it plus what the party has already encountered, the
  players **could decide where to go or what to do next**. Content that reads only in
  retrospect is labeled **foreshadow**, never "Lead", and never counts toward the
  Conclusion's exits.
  *(Source: `session-page-format.md` — "the actionability test" — the
  Lead-vs-foreshadow convention: "**tag 'Lead →' only when the *They learn* line
  passes the actionability test**". The inventory row `lead-actionability` cites
  the same passage.)*

- **Roster use:** **None** — but for the same reason `lead-interpretability` gives, not
  `npc-rows-named`'s. `lead-actionability` turns on **what the party has already
  encountered** — their accumulated campaign knowledge — which is **not in the roster**
  (the roster carries flagged-ability / Spotlight profiles, nothing about what the party
  has learned). So the checker judges actionability against the "what the party has
  already encountered" context the clue sits in, not the roster. *(Handed in per
  protocol; this row does not consult it.)*

- **Criteria:**
  - **Scope — clues tagged `"Lead →"`.** `lead-actionability` grades only the payloads a
    `"Lead →"` tag claims are actionable. An untagged clue, or one already labeled
    **foreshadow**, is out of scope (`foreshadow-not-a-lead`'s parser already keeps
    foreshadow out of the exit count).
  - **Holds when** a `"Lead →"`-tagged clue's *They learn* line, held with what the
    party has already encountered, resolves to a **decision the players can make now** —
    a direction, a place to go, an action to take. The tag's promise is kept.
  - **Breaks when** a `"Lead →"`-tagged clue reads **only in retrospect** — it means
    something later but gives the players nothing to decide or act on *now*. That is a
    **foreshadow mislabelled as a Lead**: it would count toward the Conclusion's exits
    while offering no real exit. Report it at that clue payload / its slate line.
  - **Cannot tell → disapprove.** If it is ambiguous whether a tagged clue is actionable
    now or only readable later — the package does not establish whether the party holds
    the context that makes it actionable — the checker **disapproves** and names the
    clue, so the generator can either ground the actionability or retag it foreshadow.
    Uncertainty is a disapprove, never a pass.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** Clue tagged `"Lead →"`. *They learn:* "The winter cargo is being
    moved to the Salt Docks tonight." The party knows the Salt Docks (they have been
    there); holding this they can **decide to go to the docks tonight** — a live
    decision now. Actionable. **Holds.**
  - **Bad — breaks.** Clue tagged `"Lead →"`. *They learn:* "The sigil on the ledger
    matches one they will later find carved above the Sunless Vault." Nothing about the
    Sunless Vault is in reach yet; the line means something only once a future node is
    seen. It reads **only in retrospect** — a foreshadow wearing a Lead tag. **Breaks
    `lead-actionability`** at this clue; it should be labeled foreshadow (and dropped
    from the exit count).
  - **Edge — the boundary.** Clue tagged `"Lead →"`. *They learn:* "The kidnappers
    answer to someone they call the Harbormaster." Whether this is a Lead or a
    foreshadow turns on **whether the party can act on 'the Harbormaster' now** — if
    they have met or can place the Harbormaster (a known figure, a reachable office at
    the docks), it is a direction they can take and it **holds**; if "the Harbormaster"
    is a first-mention title with no one and nowhere the party can go to now, it is a
    hook that only pays off later and **breaks**. Where the package does not establish
    whether the Harbormaster is reachable, the checker **cannot tell** and
    **disapproves**, naming the clue so the generator grounds the actionability or
    retags it. This is the borderline the criteria exist to settle.

- **Corpus pointer:** *none* — `lead-actionability` is structural (does this tagged clue
  pass the actionability test?), so hand-written anchors are the floor and the ceiling.

---

## Row `build-session/spotlight-coverage` — spotlight coverage: every PC got a beat, or the rest is defensible

- **Inventory check id:** `build-session/spotlight-coverage`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the `build-session + session-page-format` table — method: **judgement over a
  deterministic pre-pass**. The pre-pass — `spotlight_coverage(page, roster)` in the
  shared [mechanical checker](scripts/mechanical_checker/checker.py) — computes `roster
  − PCs named in Spotlight annotations` and **is not a check**: it returns no `Finding`
  and can fail nothing, because an uncovered PC is **legal**. It hands this row the
  facts; this row rules on them. That split is the whole reason `spotlight-coverage` is
  judgement rather than mechanical. The mechanical siblings settle everything about the
  annotations except who is missing from them: **spotlight-plan-not-filed** the plan is
  never filed on the page, **spotlight-annotations-name-pc** each annotation present
  names a roster PC — except a fight field declaring the `plain` texture, which
  stages no beat and has nobody to name — **spotlight-shapes-separate** the fight and
  scene shapes stay separate. A page could stage one PC six times and leave five unmentioned and pass all
  three clean — that gap is exactly `spotlight-coverage`.)*

- **Promise text:** The plan is done when **every PC is either given a beat or named as
  resting** — and **every PC gets a beat somewhere across a scenario group, in any
  pillar** (the Rogue's beat may be the impossible lock, not a fight; a social scene
  where the Bard's charm *works* spends the budget as legitimately). On the finished
  page, **absence is the record**: a PC named nowhere was planned as resting. A beat the
  plan allocated but the page could not stage is **neither** — it is a drop wearing a
  rest's clothes. *(Source: `SKILL.md` — "every PC is either given a beat or named
  as resting", "the spotlight plan covers every PC (a beat or named resting)";
  `spotlight/doctrine.md` — "Every PC gets a beat somewhere across a scenario
  group — in any pillar" for the session budget; `session-page-format.md` — "a PC
  named nowhere on the page was planned as resting" for "absence is the record".
  The inventory row `spotlight-coverage` cites the same passages.)*

- **Roster use:** **Yes — this row reads the roster, and it is the only
  session-page row that does.** The roster supplies the PC list the coverage is
  computed against; without it there is no denominator. The checker is handed the
  pre-pass output alongside it: the **uncovered set** (roster PCs named in no
  Spotlight annotation) and **each PC's beat share** (how many annotations name
  them). It grades the uncovered set; it does not recompute it.

- **Criteria:**
  - **Scope — the uncovered set only.** A PC the page names in any Spotlight annotation
    is **covered and out of scope**; `spotlight-coverage` never second-guesses the
    quality of a beat that exists (that is `plain-language`'s and the spotlight skill's
    business). This row rules only on the PCs the pre-pass reports uncovered.
  - **The secondary-mention rule.** A PC named **anywhere** in an annotation's value
    counts as **covered**, including as a secondary named inside another PC's beat
    ("…with Bram bracing the line"). Doctrine budgets "a beat somewhere — in any
    pillar", and a scene that reinforces one PC with another has staged both. Naming is
    the test; primacy is not. This rule is stated so the row does not disagree with
    itself run to run.
  - **Holds when** the uncovered set is **empty**, *or* every PC in it reads as a
    **defensible rest**: the page stages no obvious scene that plainly should have
    carried them, and the beats it does stage are spread rather than hoarded. A
    deliberate rest is correct doctrine — "no single situation must aim at anyone" — and
    a page where one or two PCs sit out a tight session is a normal page.
  - **Breaks when** an uncovered PC reads as a **dropped beat** rather than a rest. The
    two signals that make the difference:
    - **An obvious carrier went unused** — the page stages a scene that plainly should
      have carried them (the locked vault and the party's only lockpick; the parley and
      the party's only face) and it is annotated for someone else or for no one. A rest
      that the page's own content contradicts is not a rest.
    - **Hoarding** — one PC absorbed a disproportionate share of the beats while another
      got none. Report it at the uncovered PC, naming the page content that should have
      carried them or the share that crowded them out.
  - **Out of scope — consecutive rests.** A PC resting two sessions running is a real
    finding, but it is **catch-up's** (`catch-up/SKILL.md` — "note a PC who has now
    rested across consecutive sessions"), because only catch-up sees across sessions.
    This checker grades **this page in fresh context** and is handed no prior-session
    state, so it never rules on rest streaks — a first rest and a fifth look identical
    to it, and it must not pretend otherwise.
  - **Cannot tell → disapprove.** If the checker cannot tell whether an uncovered PC was
    rested or dropped — the page stages a scene that *might* have been theirs, or the
    coverage is so lopsided the intent is unclear — it **disapproves** and names the PC
    and the scene in question, so the generator can stage the beat or say plainly in the
    run that the PC is resting. Uncertainty is a disapprove, never a pass. (This is the
    branch that does the work: because absence is legal, a checker reaching for a pass
    will always find one.)

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** Roster: Vex, Bram, Sera, Nyla. Pre-pass: uncovered `["Nyla"]`,
    beat share `{Vex: 1, Bram: 1, Sera: 1, Nyla: 0}`. The page is a tight two-scene
    infiltration — a fight annotated for Vex, a parley for Sera, a climb for Bram.
    Nothing on it is a cleric's scene; no undead, no crisis of faith, no wounded NPC
    left standing. Nyla's absence is a **deliberate rest** the page's own content
    supports, and the three beats are evenly spread. **Holds.**
  - **Bad — breaks.** Same roster. Pre-pass: uncovered `["Nyla"]`, beat share
    `{Vex: 3, Bram: 1, Sera: 1, Nyla: 0}`. The page stages a **consecration scene at
    the desecrated shrine** — the one place a cleric's flagged Channel Divinity is the
    obvious key — and annotates it `Spotlight (scene): Vex — exploration`. Nyla is
    named nowhere, while Vex carries three of five beats. An obvious carrier went to
    someone else and one PC hoarded the budget: this is a **dropped beat wearing a
    rest's clothes**, exactly what "absence is the record" cannot distinguish and this
    row exists to catch. **Breaks `spotlight-coverage`** at the shrine scene and at Nyla.
  - **Edge — the boundary.** Same roster. Pre-pass: uncovered `["Nyla"]`, beat share
    `{Vex: 2, Bram: 1, Sera: 1, Nyla: 0}`. The page stages a **funeral for the drowned
    ferryman**, annotated for no one. Is that Nyla's obvious scene — a cleric, a rite,
    the one beat she should plainly have carried — or is it ambient set-dressing that
    aims at nobody, which doctrine expressly permits ("no single situation must aim at
    anyone")? If the page gives the funeral a staged action a cleric's flagged ability
    answers (the body will not stay consecrated; the widow begs a rite), it is an
    obvious carrier left unused and it **breaks**; if the funeral is a scene the party
    passes through with nothing staged in it, it aims at no one legitimately and Nyla's
    rest **holds**. Where the page leaves the funeral's staging unsettled the checker
    **cannot tell** and **disapproves**, naming Nyla and the funeral so the generator
    either stages her beat there or states the rest in the run. This is the borderline
    the corpus pins by example.

- **Corpus pointer:** **`corpus/spotlight-coverage/`** — the labeled golden corpus
  for this row (pass / fail / edge instances + a
  [verdict map](corpus/spotlight-coverage/verdict-map.md)). Each instance carries
  the **pre-pass output** (the uncovered set and each PC's beat share) plus the minimal
  page content the absence is judged against, labeled with its expected verdict — the
  **legal-absence** instance shape the [rubric
  format](scripts/judgement_checker/rubric-format.md) defines, distinct from the
  reader-interpretation rows' line-plus-context shape. *(The verdict-match harness is
  **out of scope here** — edit-time work for the evaluation harness.
  This rubric authors the corpus data
  + verdict map only.)*

---

## Row `build-session/stat-block-sweep-page-wide` — the page-wide stat-block sweep: every creature name carries a resolvable reference

- **Inventory check id:** `build-session/stat-block-sweep-page-wide`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the `build-session + session-page-format` table — method: judgement, "No — see
  `unenforceable/stat-block-sweep-page-wide`". The mechanical siblings settle the
  *structured* creature slots: **stat-block-resolvable** every Key NPCs Stat Block cell
  is resolvable, **fights-are-encounter-meta** every fight is a filed encounter-meta
  block. `stat-block-sweep-page-wide` is the **page-wide prose sweep** — creature names
  in read-aloud text, the Preparation bookmark list, contingencies, keyed-area run notes
  — where no regex can tell which strings are creature names
  (`unenforceable/stat-block-sweep-page-wide`). It is the session-page sibling of
  combat's **stat-block-refs-in-prose**, which sweeps a single encounter's prose;
  `stat-block-sweep-page-wide` sweeps the whole page.)*

- **Promise text:** **Every creature named anywhere on the page** — the Preparation
  bookmark list, the Key NPCs table, read-aloud text, encounter blocks, contingencies —
  **carries a resolvable stat-block reference**: `{monster:Name}` (the renderer's token)
  for published creatures, a campaign-record link to its stat-block page for homebrew or
  reskins. **A bare creature name is a defect** — a missing link is not a broken link,
  so only a deliberate sweep catches it. *(Source: `session-page-format.md` —
  "**Stat-block references.** Every creature named anywhere on the page", "The
  stat-block sweep is done" — the convention and its DoD checklist line. The
  inventory row `stat-block-sweep-page-wide` cites both.)*

- **Roster use:** **None.** `stat-block-sweep-page-wide` is structural — it asks whether
  a creature named in the page's prose carries its reference token, which is legible
  from the page alone. The disambiguating context ("which strings are creature names")
  is the page's own statted slots — the `Enemies:` lines of its fights, the Key NPCs
  Stat Block column, the Preparation bookmark list — not the roster. *(Handed in per
  protocol; this row does not read it.)*

- **Criteria:**
  - **Scope — the page's own prose; delegate block internals are inherited, not
    re-swept.** The creatures in play are the ones the page gives a stat block: on a
    fight's `Enemies:` line, in the Key NPCs Stat Block column, on the Preparation
    bookmark list. `stat-block-sweep-page-wide` sweeps **build-session's own page
    prose** — read-aloud text, contingencies, keyed-area run notes, transitions,
    spotlight lines, the Key NPCs and Preparation text — for mentions **of those
    creatures**. It does **not** re-sweep the **internal terrain/tactics prose of an
    embedded delegate block** — a combat `> [!encounter-meta]` block or an embedded
    dungeon keyed-site package: that prose was already graded by the delegate's own
    creature-name row (combat's **stat-block-refs-in-prose**, which scoped itself to
    "this encounter"; dungeon inside its package) when the delegate built it, and it
    arrives **already judgement-checked** (spec user stories 9/10).
    `stat-block-sweep-page-wide` grades what the *page* owns — the prose build-session
    itself wrote around and between the embedded blocks — never the delegated block's
    insides, exactly as the deterministic **fights-are-encounter-meta** grades a fight's
    *filing shape* on the page without re-running its XP arithmetic. Ambient fiction
    naming nothing statted on the page ("crows scatter from the gallows", "this is
    bandit country") is not a creature reference and is out of scope.
  - **Holds when** every prose mention of a page-statted creature carries the reference
    convention — the `{monster:Name}` token where render tokens are in use, or a
    stat-block link to the campaign record otherwise — exactly as it appears in the
    structured slot.
  - **Breaks when** a page-statted creature is named **bare** anywhere in the prose —
    the token/link present on the `Enemies:` line or in the Key NPCs table is dropped
    when the same creature appears in read-aloud text or a contingency ("the ogre steps
    from the treeline", with no token, though `{monster:ogre}` is on a fight below). The
    defect is one prose mention; report it at that line/paragraph.
  - **Cannot tell → disapprove.** If it is ambiguous whether a prose noun refers to a
    page-statted creature or to never-statted ambient fiction ("the wolves" — the
    `{monster:wolf} ×3` of the ambush below, or the region's wildlife at large?), the
    checker **disapproves** and names the location, so the generator can disambiguate
    (tokenise it, or reword the ambient mention so it plainly is not one). Uncertainty
    is a disapprove, never a pass (this is the
    `unenforceable/stat-block-sweep-page-wide` difficulty made explicit).

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** A fight below carries `Enemies: {monster:ghoul} ×3`; the
    Preparation bookmark list carries `{monster:ghoul}`; the read-aloud text reads
    *"three `{monster:ghoul}` shapes uncurl from the pew shadows and hiss."* Every prose
    mention of the statted creature carries its token. **Holds.**
  - **Bad — breaks.** Same statted ghouls. The Key Plot Points read-aloud says *"the
    ghouls have already been here — the pews are gnawed."* `{monster:ghoul}` is statted
    on the page, but this prose mention is **bare** — the sweep the promise names exists
    exactly to catch this. **Breaks `stat-block-sweep-page-wide`** at that read-aloud
    line.
  - **Edge — the boundary.** Read-aloud text: *"Somewhere past the treeline a wolf
    howls, and is answered."* Is `wolf` a page-statted creature named bare, or ambient
    fiction? If the page stats `{monster:wolf}` anywhere (a fight, the bookmark list),
    the howl is a bare mention of an in-play creature and **breaks**; if no wolf is
    statted anywhere on the page, the howl is ambient set-dressing, **out of scope**,
    and **holds**. Where the checker cannot decide whether the page stats the referent —
    the creature list is ambiguous — it **disapproves** and names the line, so the
    generator either tokenises it or makes plain it is ambient. This is the borderline
    the criteria exist to settle.

- **Corpus pointer:** *none* — `stat-block-sweep-page-wide` is structural (does this
  prose creature-mention carry its reference token?), so hand-written anchors are the
  floor and the ceiling. (The reserved corpus slot is for the reader-interpretation rows
  `lead-interpretability` / `clue-interpretability` / `plain-language` /
  `read-aloud-boundary` only —
  `stat-block-sweep-page-wide` is a *name-carries-a-token* sweep, not a
  *does-a-stranger-understand-it* interpretation, so it stays anchors-only.)

---

## Row `build-session/plain-language` — the plain-language sweep: no run-time line rests on an undefined coinage

- **Inventory check id:** `build-session/plain-language`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the `build-session + session-page-format` table — method: judgement,
  enforceable-as-written: No. This is one of the library's three
  **reader-interpretation** rows — *can a stranger execute this?* — so it carries a
  golden corpus on top of its anchors, alongside `lead-interpretability` and
  `clue-interpretability`. No sibling mechanical row exists: whether a coined term is
  defined-nearby-or-not, and whether a line is run-time text at all, are both judgements
  no regex settles.)*

- **Promise text:** Everything the DM **executes mid-session** — encounter blocks,
  spotlight lines, keyed-area run notes, contingencies — states **mechanics and named
  page fiction only**. A coined term is legal **only if the page defines it before or
  where it's used** ("the Forgotten", "the candle-ledger"); an **undefined metaphor**
  ("the needle", "polish the brass") is a defect, however evocative. **The test: a
  competent DM who has never seen this campaign could execute the line with only this
  page open.** Aphoristic compression belongs in design discussion and commit messages,
  never in text that runs at 9pm mid-fight. *(Source: `session-page-format.md` —
  "**Plain language in run-time text.**", "no run-time line depends on an undefined
  coinage or metaphor" — the convention and its DoD checklist line. The inventory
  row `plain-language` cites both.)*

- **Roster use:** **None.** `plain-language` is structural in the sense that its test —
  *could a competent stranger DM execute this line with only this page?* — reads the
  page's own text and its own definitions, not the roster. *(Handed in per protocol;
  this row does not read it.)*

- **Criteria:**
  - **Scope — run-time text only.** `plain-language` grades only **text the DM executes
    at the table**: encounter blocks, spotlight lines, keyed-area run notes,
    contingencies, read-aloud. Design-discussion prose, rationale, and
    commit-message-style asides are **out of scope** — a coinage there is not a run-time
    defect. *Which* text is run-time is itself part of `plain-language`'s judgement (a
    line's placement and function decide it).
  - **Holds when** every run-time line executes on **mechanics and named page fiction
    only** — game terms (a save, a DC, a condition) and coined terms the page **defines
    before or where they are used** (a "candle-ledger" the page has already introduced
    as the smugglers' book). A competent stranger DM could run the line with only this
    page open.
  - **Breaks when** a run-time line **rests on an undefined coinage or metaphor** — a
    term the page never defines, so its meaning lives only in the author's head ("thread
    the needle", "once the brass is polished, knock twice") . The stranger DM hits the
    line at 9pm mid-fight and cannot execute it. Report it at that run-time line.
  - **Cannot tell → disapprove.** If it is ambiguous whether a coinage is defined
    somewhere on the page, or whether a line is run-time text at all, the checker
    **disapproves** and names the line, so the generator can define the term where it is
    used, plain-language the metaphor, or move a design aside out of run-time text.
    Uncertainty is a disapprove, never a pass.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** Contingency line: *"If the party opens the candle-ledger, they
    read the next three drop sites."* The page's clue slate already defined the
    **candle-ledger** as the smugglers' shipment book. A stranger DM runs the line with
    only this page open — the coinage is defined here. **Holds.**
  - **Bad — breaks.** Spotlight line: *"Once the brass is polished, let Brenna thread
    the needle."* Neither "the brass is polished" nor "thread the needle" is a game
    mechanic or a page-defined term — they are metaphors whose meaning is nowhere on the
    page. The stranger DM cannot execute this mid-fight. **Breaks `plain-language`** at
    the spotlight line — aphoristic compression in run-time text. (The anchor's phrasing
    is deliberately inert — a bad example vivid enough to admire is vivid enough to leak
    into generated pages.)
  - **Edge — the boundary.** Keyed-area run note: *"The Forgotten stir when a light is
    struck."* Is **"the Forgotten"** a defined coinage or an undefined one? If the page
    introduced the Forgotten earlier (a Key Plot Point naming them as the drowned dead
    of the vault), the run note executes on named page fiction and **holds**; if "the
    Forgotten" appears **only here**, first-used in run-time text with no definition,
    the stranger DM cannot tell who stirs and it **breaks**. Where the page's definition
    of the term is unclear — mentioned once elsewhere but never actually pinned — the
    checker **cannot tell** and **disapproves**, naming the line so the generator
    defines it where used. This is the borderline the corpus pins by example.

- **Corpus pointer:** **`corpus/plain-language/`** — the labeled golden corpus for this
  row (pass / fail / edge instances + a [verdict
  map](corpus/plain-language/verdict-map.md)). Each instance is a self-contained
  run-time page line **plus** the minimal "what the page defines nearby" context the row
  is judged against, labeled with its expected verdict, so `plain-language`'s boundary
  is pinned **by example**, not by adjectives alone. The corpus is added **on top of**
  the hand-written anchors above, per the rubric format's reader-interpretation slot.
  *(The harness that runs the checker over the corpus and asserts each verdict matches
  its label is **out of scope here** — it is edit-time work for the evaluation harness.
  This rubric authors the corpus data
  + verdict map only.)*

---

## Row `build-session/read-aloud-boundary` — the read-aloud sweep: the box holds only what the characters perceive

- **Inventory check id:** `build-session/read-aloud-boundary`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the `build-session + session-page-format` table — method: judgement,
  enforceable-as-written: No. This is one of the library's four
  **reader-interpretation** rows — *could someone at the scene perceive this?* — so it
  carries a golden corpus on top of its anchors, alongside `lead-interpretability`,
  `clue-interpretability` and `plain-language`. No sibling mechanical row exists:
  a four-digit year or a past-tense verb inside the box is legal when it sits in
  dialogue or on a readable inscription, so no regex separates leaked history from
  quoted text.)*

- **Promise text:** A `> [!read-aloud]` block — wherever it appears: the opener, a
  keyed area, a clue payload's Show — carries only what the characters **see, hear,
  smell, feel, or taste right now**, plus dialogue spoken in their presence and text
  they can read. **The test: could someone standing there perceive this, from where
  they stand, right now?** Hidden history, causes, another's intent, meanings, imposed
  emotions and decisions, and detail beyond the party's vantage belong beside the box —
  as interaction-keyed DM text or a clue payload — never in it. *(Source:
  `session-page-format.md` — "**Read-aloud is what they perceive.**", "could someone
  standing there perceive this, from where they stand, right now?" — the convention
  and its DoD checklist line "The read-aloud sweep is done". The inventory row
  `read-aloud-boundary` cites all three.)*

- **Roster use:** **None.** The test reads the read-aloud text against the scene the
  page itself establishes — where the party stands, what light there is, what is
  hidden — never the roster. *(Handed in per protocol; this row does not read it.)*

- **Criteria:**
  - **Scope — read-aloud blocks only.** `read-aloud-boundary` grades every
    `> [!read-aloud]` block on the page, including one serving as a clue payload's
    Show. DM-facing prose, sidebars, and encounter blocks are out of scope — history
    and interpretation are *supposed* to live there. The rule follows the callout,
    not the section.
  - **Holds when** every sentence in the box is something a person at the party's
    position could perceive right now: sensory description, immediate universal
    inference ("a long-abandoned mill"), atmosphere as sensation, involuntary
    physical reactions, dialogue spoken in their presence, and the verbatim text of
    anything they can read — an inscription's date is legal because the date is *on
    the stone*, not in the narrator's head.
  - **Breaks when** a sentence asserts what no one present could perceive: hidden
    history or causes ("pavers discarded these stones decades ago"), another's
    intent or meaning, an unperceivable claim dressed as mood presented as fact, an
    imposed emotion or decision ("you feel terrified"), or detail beyond the party's
    vantage — the contents of darkness, a closed container, or a shape too far to
    resolve. Report it at the offending sentence; the physical description around it
    may be blameless.
  - **Cannot tell → disapprove.** If the checker cannot tell whether the party could
    perceive a described detail from where the page puts them — the page never
    establishes the light, the distance, or whether a door is open — it
    **disapproves** and names the sentence, so the generator either establishes the
    vantage or moves the detail out of the box. Uncertainty is a disapprove, never a
    pass.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** Opener: *"Rows of headstones lean at odd angles, and the
    church door hangs open. Carved over the lintel: 'Rest, and be counted.'"* Every
    clause is perceivable from the gate — stones, door, and an inscription the
    characters can read. **Holds.**
  - **Bad — breaks.** Same scene, next sentence: *"The pavers who widened the road
    discarded these stones decades ago; the dead recovered and arranged every one."*
    No one at the gate perceives who moved the stones or when — that is DM knowledge
    narrated into the box. **Breaks `read-aloud-boundary`** at that sentence; the
    headstone description before it is blameless.
  - **Edge — the boundary.** Keyed-area box: *"Against the far wall, a dark shape
    slumps beneath a torn banner."* The far wall is beyond the party's torchlight. As
    written it **holds** — a dark shape is exactly what that vantage registers. Had it
    read *"a dwarf's corpse clutching a ledger"*, the box would claim detail the
    light cannot deliver and **break**. Where the page never establishes how far the
    light reaches, the checker **cannot tell** and **disapproves**, naming the
    sentence. This is the borderline the corpus pins by example.

- **Corpus pointer:** **`corpus/read-aloud-boundary/`** — the labeled golden corpus
  for this row (pass / fail / edge instances + a [verdict
  map](corpus/read-aloud-boundary/verdict-map.md)). Each instance is a self-contained
  read-aloud block **plus** the minimal scene state it is judged against — where the
  party stands, what light there is, what is actually true of the scene — labeled with
  its expected verdict, so the perception boundary is pinned **by example**, not by
  adjectives alone. The corpus is added **on top of** the hand-written anchors above,
  per the rubric format's reader-interpretation slot. *(The harness that runs the
  checker over the corpus and asserts each verdict matches its label is **out of scope
  here** — it is edit-time work for the evaluation harness.
  This rubric authors the corpus
  data + verdict map only.)*

---

# Node-page subset — `[build-session/clue-interpretability, build-session/no-plot-decisions]`

The rows below grade a **deepened node page** — the separate artifact
[`node-deepening.md`](node-deepening.md) produces at Step 3 — and run **only when a
node was deepened this run**. They are never applied to the session page (and the
session-page rows above are never applied to a node page). This is the same
two-artifact split the deterministic self-check draws between the session
page's mechanical rows and the node page's
`[build-session/clue-web-section-present, build-session/clue-web-indexes-only]`.

## Row `build-session/clue-interpretability` — every clue carries a player-reachable vehicle AND is interpretable when found

- **Inventory check id:** `build-session/clue-interpretability`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the `build-session — node-deepening.md` table — method: judgement,
  enforceable-as-written: No. This is one of the library's three
  **reader-interpretation** rows, so it carries a golden corpus on top of its anchors,
  alongside `lead-interpretability` and `plain-language`. The mechanical sibling
  **clue-web-indexes-only** settles the *filing shape* — that clue content lives in the
  body under its own headings while the clue-web section only indexes;
  `clue-interpretability` grades the two things no parser can: does a clue have a way
  for the players to **get** it, and once they have it, can they **read** it?)*

- **Promise text:** Every clue or lead written into a deepened node **must carry a
  player-reachable vehicle** — a **concrete scene, action, check, or bargain that
  yields it** — *and* **must be interpretable using only what the players already know
  when they could plausibly find it** (a clue may gain meaning later, but must never
  require unseen content to mean anything at all). **A fact stated in DM-facing text
  with no way for the players to obtain it is not a placed clue.**
  *(Source: `node-deepening.md` — "the clue-web section only indexes it" — the
  Step 3 Draft rule: "Any clue or lead written
  here must be interpretable using only what the players already know … and must carry
  a player-reachable vehicle: a concrete scene, action, check, or bargain yields it. A
  fact stated in DM-facing text with no way for the players to obtain it is not a placed
  clue." The inventory row `clue-interpretability` cites the same line.)*

- **Roster use:** **None.** `clue-interpretability` has **two prongs**, and neither
  reads the roster. The **vehicle** prong asks whether a concrete
  scene/action/check/bargain yields the clue — legible from the node page's own scenes.
  The **interpretability** prong turns on *what the players already know when they could
  find it* — their accumulated campaign knowledge, which is **not in the roster** (as
  `lead-interpretability`'s *Roster use* explains). So the checker judges both prongs
  from the node page and the "what the players already know" context, not the roster.
  *(Handed in per protocol; this row does not consult it.)*

- **Criteria:** `clue-interpretability` grades **two prongs**; a clue must pass
  **both**. A failure of *either* prong breaks the row.
  - **Prong 1 — the vehicle (player-reachable).** For each clue, find the **concrete
    scene, action, check, or bargain** by which the players obtain it — something they
    can *do* at the node that yields the clue. **Holds** when such a vehicle exists on
    the page (search the strongbox, pass the check, question the prisoner, strike the
    bargain). **Breaks** when the clue's content sits **only in DM-facing text** with no
    scene, action, check, or bargain that delivers it to the players — "a fact stated in
    DM-facing text with no way for the players to obtain it is not a placed clue." This
    is the prong with **no `lead-interpretability` analog** — `lead-interpretability`
    assumes the lead is found and asks only whether it reads; `clue-interpretability`
    first asks whether it can be **got** at all.
  - **Prong 2 — interpretable when found.** Judge each clue as the party reads it **at
    the moment they obtain it**, with only what they already know then. **Holds** when
    it resolves to a direction, a place, or a next question using that prior knowledge
    (it may deepen later, but it means something now). **Breaks** when it can only be
    read once the party sees content they **have not yet reached** — a name, symbol, or
    cipher first defined in unreached content is noise at the moment of finding. (This
    prong mirrors `lead-interpretability`; the difference from `lead-interpretability`
    is that `lead-interpretability` grades leads *planted in a dungeon* that point at
    another node, while `clue-interpretability` grades a clue *inside a deepened node* —
    and `clue-interpretability` carries Prong 1, which `lead-interpretability` does
    not.)
  - **Cannot tell → disapprove.** If it is ambiguous whether a clue has a reachable
    vehicle (a scene is described but it is unclear the players can act on it to get the
    clue), **or** whether the party would already hold the knowledge it needs, the
    checker **disapproves** and names the clue and *which prong* is in doubt, so the
    generator can add the vehicle, ground the reference, or make either explicit.
    Uncertainty is a disapprove, never a pass.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes both prongs.** The node's ledger-room. **Vehicle:** *a player who
    searches the desk (Investigation) or asks the clerk finds the shipping ledger.*
    **Interpretability:** the ledger is stamped with **Old Harl's** seal — the party met
    Harl two nodes ago — so on finding it they read "Harl routed cargo here." A
    reachable vehicle **and** interpretable with what they know. **Holds.**
  - **Bad — breaks Prong 1 (vehicle).** The DM notes under the shrine read: *"The shrine
    was built by the drowned cult; the altar hides the vault key."* This fact is stated
    **only in DM-facing text** — no scene, no search, no check, no bargain lets the
    players obtain it. It is not a placed clue; the players can never come to know it.
    **Breaks `clue-interpretability`** at the shrine — the vehicle prong fails even
    though, were it found, it would read fine.
  - **Edge — the boundary (borderline vehicle).** The node's mural room. DM text: *"The
    mural depicts the founding — a keen eye notes the seventh figure was painted over."*
    A perceivable detail is present (the painted-over figure), but is there a
    **vehicle** the players can act on to get it — is it a passive backdrop, or does the
    page give them a scene/check that yields the observation? If the page stages it as
    something the players can **do** — a Perception/Investigation check, an NPC who
    points at it, a reason to look closely — the vehicle exists and (if interpretable)
    it **holds**; if the painted-over figure sits in DM narration with **no player
    action that surfaces it**, it is DM-facing colour, not a placed clue, and the
    checker **cannot tell** the vehicle is reachable → **disapproves**, naming the clue
    and the vehicle prong. This is the borderline the corpus pins by example.

- **Corpus pointer:** **`corpus/clue-interpretability/`** — the labeled golden corpus
  for this row (pass / fail / edge instances + a [verdict
  map](corpus/clue-interpretability/verdict-map.md)). Each instance is a self-contained
  node-clue example (the clue **plus** the minimal "what the players already know when
  they could find it" context) labeled with its expected verdict, and the fail class
  spans **both prongs** — a vehicle-fail (DM-facing fact with no obtaining scene) and an
  interpretability-fail (needs unseen content) — so `clue-interpretability`'s boundary
  is pinned **by example** across both. The corpus is added **on top of** the
  hand-written anchors, per the rubric format's reader-interpretation slot. *(The
  verdict-match harness is **out of scope here** — edit-time work for the
  evaluation harness. This rubric authors
  the corpus data + verdict map only.)*

---

## Row `build-session/no-plot-decisions` — decide nothing plot-relevant; bring plot decisions to the DM

- **Inventory check id:** `build-session/no-plot-decisions`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the `build-session — node-deepening.md` table — method: judgement,
  enforceable-as-written: No. Structural — it asks whether the drafted page **decided a
  plot-tier question on its own** rather than bringing it to the DM. No regex can tell a
  plot decision from set dressing; the authorship test the source states is exactly a
  judgement.)*

- **Promise text:** In deepening a node, **elaborate set dressing freely — but decide
  nothing plot-relevant; bring every plot decision to the DM as a question.** The
  authorship test: **if the players could later discover a detail was retconned, it is
  plot** — bring it to the DM as a question (in prose, with a recommendation), or park
  it *(undecided)*; if it is set dressing they would never notice changing, draft it.
  *(Source: `node-deepening.md` — "Elaborate set dressing freely — decide nothing plot-relevant" —
  "Elaborate set dressing freely — decide nothing
  plot-relevant; bring every plot decision to the DM as a question. … if the players
  could later discover a detail was retconned, it is plot". The inventory row
  `no-plot-decisions` cites the same lines.)*

- **Roster use:** **None.** `no-plot-decisions` is structural — it asks whether the page
  silently settled a plot-tier question, which is legible from the page's own content
  against the authorship test (would a change be player-noticeable?). *(Handed in per
  protocol; this row does not read it.)*

- **Criteria:**
  - **The authorship test is the line.** A detail is **plot** if the players could later
    **discover it was retconned** — it commits the campaign to something they would
    notice changing (who the villain answers to, what the artifact does, whose body is in
    the crypt). A detail is **set dressing** if they would never notice it changing (the
    colour of the shutters, the name of a dead cooper).
  - **Holds when** every **plot-tier** detail the deepening needed was either brought to
    the DM as a question (in prose, with a recommendation) or **parked** *(undecided)* on
    the page — the page decided **only set dressing** on its own.
  - **Breaks when** the page **silently decided a plot-relevant question** — invented a
    retconnable, player-noticeable fact and filed it as settled canon without asking (the
    node page asserts the cult answers to the Harbormaster, a commitment no prior canon
    made and the players would notice being reversed). Report it at the detail the page
    decided.
  - **Cannot tell → disapprove.** If it is ambiguous whether a drafted detail is plot or
    set dressing — the retcon test is genuinely borderline — the checker **disapproves**
    and names the detail, so the generator can lift it to a DM question, park it, or make
    plain it is inconsequential set dressing. Uncertainty is a disapprove, never a pass.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** The deepened node names a defaced statue in the square, invents
    the long-dead mason who carved it, and colours the market stalls — all set dressing
    no player would notice changing. The one plot-tier question the node raised — *whose
    sigil is under the defacement?* — is brought to the DM **as a prose question with a
    recommendation**, not decided. **Holds.**
  - **Bad — breaks.** The deepened node **asserts as settled canon** that the shrine's
    cult answers to the Harbormaster and that the vault holds the crown's true heir —
    plot-tier commitments no prior canon made, filed without asking. The players could
    later discover either was retconned. **Breaks `no-plot-decisions`** at those
    assertions — plot decided silently, not brought to the DM.
  - **Edge — the boundary.** The node invents a **focal monument** — a burned-out
    lighthouse — and ties it to "a shipwreck the town still mourns." The monument and
    its faction tie are set dressing the source *invites* (`node-deepening.md` —
    "Ground invented things in the concrete real-world place"). But
    does the tie **decide a plot question**? If the shipwreck is **texture** — history
    that colours the place and could anchor a clue later without committing the plot —
    it is draftable set dressing and **holds**; if the tie **commits the campaign** to a
    plot fact (the wreck was the heir's ship, sabotaged by the villain) the players
    would notice being reversed, it crosses into plot and must go to the DM —
    **breaks**. Where the tie's reach is unsettled the checker **cannot tell** and
    **disapproves**, naming it so the generator either keeps it inert texture or lifts
    the commitment to a DM question. This is the borderline the criteria exist to draw.
    *(Source note: the deepening procedure itself says "the tie is set dressing;
    deciding what it *reveals* stays plot-tier" — `no-plot-decisions` grades exactly
    that seam.)*

- **Corpus pointer:** *none* — `no-plot-decisions` is structural (did the page decide a
  plot question on its own?), so hand-written anchors are the floor and the ceiling.
  (The reserved corpus slot is for the reader-interpretation rows
  `lead-interpretability` / `clue-interpretability` / `plain-language` /
  `read-aloud-boundary` only.)
