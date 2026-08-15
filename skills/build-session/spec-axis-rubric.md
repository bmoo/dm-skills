# build-session — Spec-axis rubric (tonight's contract)

The rows the **Spec checker** grades a drafted session page against. It is a
*second* checker, launched in parallel with the Standards checkers of
[`judgement-rubric.md`](judgement-rubric.md) and **its verdict is never merged
into theirs** (`lib/judgement-checker/checker-launch-protocol.md` — "The
Standards checkers are untouched and see no brief"). This file is that checker's
whole rubric: the subset
**`[build-session/brief-premise-enacted, build-session/brief-fit-to-geography,
build-session/brief-locked-subject-canon]`**, and it carries no Standards row.

It is the **sibling** of `judgement-rubric.md`, not an extension of it. The two
grade against different sources of truth — a library rubric identical on every run,
and a contract different every night — and one agent holding both can trade them off
(*"the brief asked for this, so the plain-language row can slide"*). Neither may buy
the other off, which is why they are two checkers and two files.

Every row below **is** a row of
[`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md)'s
`build-session — the Spec axis (the session brief)` table — derived from the
inventory, never hand-copied — and is written in the format defined by
[`scripts/judgement_checker/rubric-format.md`](scripts/judgement_checker/rubric-format.md).
The other nine rows of that table are the **mechanically-checkable** half: they ran
red-green during the build (`SKILL.md` — "Draft to green against tonight's contract")
and are not re-graded here.

## What this checker is handed, and what it is not

Beyond the drafted page and this subset, the Spec checker gets the two inputs the
launch protocol names for it: **the brief**, as a tracker issue URL, **body only,
comments excluded**, and **the campaign canon record extract**
(`lib/judgement-checker/checker-launch-protocol.md` — "body only, comments
excluded"). It is handed **no reasoning from the generator** — that withholding is
unchanged and is the whole point.

**A row whose field the brief left blank does not run.** The axis grades one row per
filled field; silence is never a constraint, so an unwritten `Fit to established
geography` yields no row, no finding and no disapprove (`SKILL.md` — "silence is
never a constraint"). The one row that is not a field row is
`build-session/brief-locked-subject-canon`, which grades the Locked lines as a set and
runs whenever a brief is in force.

**There are no waivers.** Nothing in the brief exempts a row on either axis, so there
is nothing to reconcile and neither verdict softens the other.

---

## Row `build-session/brief-premise-enacted` — the page enacts tonight's premise

- **Inventory check id:** `build-session/brief-premise-enacted`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the Spec-axis table — method: judgement, enforceable-as-written: No.)*

- **Promise text:** The page **enacts** the night the brief's `Premise` describes —
  the party arrive at it the way the premise says they do, and the scenes and keyed
  areas the page stages are that night being run. *(Source:
  `to-session-brief/SKILL.md` — "One sentence: what is happening tonight and why the
  party is in it", "rubric-graded: does the page enact it".)*

- **Roster use:** **None.** This row reads the page against the brief's `Premise`
  field. It never consults the roster, and it does not need the record extract.

- **Criteria:**
  - **Holds when** the page's **staged content** runs the premise's night: the
    situation the premise names is the situation the keyed areas, scenes and
    Conclusion are built to play out, and the party's way into it is the way the
    premise says. A page may compress, reorder or complicate the premise freely —
    what it may not do is stage a different night.
  - **Breaks when** the page **restates** the premise without running it, or runs a
    night the premise does not describe. Restatement never satisfies this row —
    **not the header, not a Key Plot Points beat, and not a clue payload block**.
    The clearest break is a page that names the premise's people and places in prose
    and then keys somewhere else, which is exactly the page
    `build-session/brief-destination-nodes` was weakened to let through.
  - **Not this row:** whether the revelation moved. The named state transition is
    `build-session/brief-revelation-paid-down`'s, and it reads clue payload blocks.
    A page that enacts the premise and leaves the revelation exactly where it was
    **holds here and breaks there**; a page that pays the revelation down while
    building a different night breaks here and holds there. Neither row may be
    satisfied by the sentence that satisfies the other.
  - **Cannot tell → disapprove.** If the staged night is *adjacent* to the premise —
    the right people, the right place, a different thing happening — the checker
    disapproves and names what it could not match. A written constraint that went
    unverified is a disapprove, never a pass.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** Premise: *the object hatches tonight and the client asks the
    party to steal it before it does.* The page keys the museum after hours, the
    client's ask opens the session, the keyed areas are the theft, and the
    Conclusion resolves contained-or-not. **The staged night is the premise's
    night.** Holds.
  - **Bad — breaks.** The same premise. The page's header and its Key Plot Points
    both say the egg hatches tonight — and the body keys a daytime gala with the
    egg in a locked annexe nobody enters, closing on a lead to come back later.
    Every premise noun is present; **the night is a different night**. Breaks.
  - **Edge — the boundary.** The same premise, and the page stages the theft as a
    *social* infiltration of the gala with the client waiting outside — no
    after-hours break-in at all. The premise names no method, so a changed method is
    not a changed night: **holds**. If the page had also moved the ask to a later
    session — the party acting on their own account — the night stops being the one
    the premise describes and the checker **disapproves**. Method is free; the night
    is not.

- **Corpus pointer:** *none* — hand-written anchors are the floor and the ceiling
  here. This is not a reader-interpretation row (it does not ask what a stranger
  understands) and not a legal-absence row (nothing mechanical computes a fact for it
  to rule on).

---

## Row `build-session/brief-fit-to-geography` — the page fits established geography

- **Inventory check id:** `build-session/brief-fit-to-geography`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the Spec-axis table — method: judgement, enforceable-as-written: No.)*

- **Promise text:** The page's geography **fits what the record already
  establishes** — what the brief's `Fit to established geography` line commits to
  holds against the campaign canon record extract: what stands next to what, how far
  apart, and in which direction, as the page's map, travel times and sight-lines
  carry it. *(Source: `to-session-brief/SKILL.md` — "Layout — what the geography
  commits to", "Fit to established geography.".)*

- **Roster use:** **None.** This row reads the **campaign canon record extract**
  (launch-protocol input 6) against the page, for the same reason
  `build-session/brief-introduced-canon` does: the checker has no filesystem reach
  into the campaign record, so a durable extract handed in is the only way to grade a
  claim about the record at all.

- **Criteria:**
  - **Holds when** every spatial relation the brief's line commits to survives on the
    page — adjacency, distance, direction, and what is visible from where — and
    nothing the page adds contradicts a relation the extract already holds.
  - **Breaks when** the page moves something the record has already placed: the shop
    next door becomes a street away, the mile becomes an afternoon's ride, the site
    the record puts north of the town sits south of it. A **contradiction** is the
    break; new geography the record is silent about is not this row's business.
  - **Not this row:** the **shape** of tonight's site — entrance counts, floors, a
    basement. That is `build-session/brief-map-topology`, graded mechanically against
    the page's own edge table. This row is about the site's place in the *world*.
  - **Cannot tell → disapprove.** If the extract is silent on a relation the brief's
    line asserts, the checker cannot confirm the fit and **disapproves**, naming what
    it could not check. Silence in the *extract* is not a pass; silence in the
    **brief** is a row that does not run at all.

- **Honesty note — this row ships precautionary.** It is retained on the
  precautionary reading rather than earned by evidence, and a checker should know
  that. The field passed in **every ablation arm scored for it**, including the arm
  handed **no brief at all**, and the test that would settle it has never been run:
  every frozen situation's record already carried enough geography for the generator
  to fit, so the field has **never been tested against genuinely blank geography**.
  It grades a real defect — a page that moves the tavern next door is a page the DM
  keeps and curses — but nothing has yet shown that withholding the field produces
  one.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** Brief: *the museum stands on Museum Square, the Gilded Folio
    next door, the university less than a mile off.* Extract agrees. The page's map
    puts the square at the front steps, an alley between museum and Quill, and a
    lead that walks to the university inside an hour. Holds.
  - **Bad — breaks.** The same line. The page opens with the party riding out to the
    museum *"a day's travel from town"* and puts the Gilded Folio across the river.
    Two record-held relations moved. Breaks.
  - **Edge — the boundary.** The same line, and the page adds a **storm drain**
    running from the museum basement to an alley the record has never mentioned.
    Nothing established is moved and the extract is silent, so this is new
    geography, not a misfit: **holds**. If that drain surfaced *inside* the
    university the record puts a mile off, it would contradict the distance and
    **break**. Silence is free; established relations are not.

- **Corpus pointer:** *none* — hand-written anchors only, for the same reason as the
  premise row. If this row ever earns a corpus it will be because the checker keeps
  drifting on *how far is "next door"*, and that is a boundary to pin with instances
  when it shows up, not before.

---

## Row `build-session/brief-locked-subject-canon` — no unlicensed canon on a locked subject

- **Inventory check id:** `build-session/brief-locked-subject-canon`
  *(from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md),
  the Spec-axis table — method: parse + judgement, enforceable-as-written: Partial.
  The parse half runs in the deterministic tier during the build; this row grades
  what a number does not mark.)*

- **Promise text:** For **each subject a Locked line names**, the page asserts no
  fact about that subject which neither the brief nor the campaign canon record
  extract supplies. *(Source: `SKILL.md` — "A subject a Locked line names is not
  silence".)*

- **Roster use:** **None.** This row reads the **brief's Locked lines** (for the
  subject set) and the **campaign canon record extract** (for what is already
  supplied). It consumes no input the axis did not already require — it is a row, not
  a channel.

- **Criteria:**
  - **The subject set first, and it is the whole scope.** A subject is a person,
    place, object or organisation a **Locked** line names. Subjects named only under
    `Not tonight` are **excluded**, not locked, and are not in the set.
  - **Holds when** every claim the page makes *about a subject in that set* is either
    supplied by the brief, supplied by the extract, or derivable from them —
    including the page saying it in fresh words, at greater length, or in
    read-aloud voice. Rendering a locked subject vividly is the page doing its job.
  - **Breaks when** the page **adds a fact** about a subject in the set that neither
    source supplies and neither implies: an origin, an age, a count, a history, a
    capability, a relationship. The test is *would a reader who took this page as
    true now know something about this locked subject that the DM never agreed to?*
    The frozen case this row exists for: a page that invented an item's whole
    provenance — who made it, when, and why badly — for an item its brief locked.
  - **This is not a general no-new-canon rule, and a row that fires on an unlocked
    subject is wrong.** Where the brief is silent the generator is *supposed* to
    invent, and silence is never a constraint. A new trap, a new courier, a new room
    the brief never names is not this row's business no matter how much canon it
    mints (`SKILL.md` — "invent where both are silent").
  - **Cannot tell → disapprove.** If the checker cannot tell whether a claim is a
    fresh rendering of a supplied fact or a new fact, it **disapproves** and names the
    sentence and the subject.

- **Anchors** (hand-written; good / bad / edge):
  - **Good — passes.** Brief locks *Fenwick has built a crystal box; it is not yet
    sealed.* The page: *"the casing is done, the seal is not, so the box cannot go on
    the job with them."* Fresh words, one supplied fact, one inference the brief's own
    words carry. Holds.
  - **Bad — breaks.** The same locked object. The page: *"Fenwick ground the panes
    herself over nine months in a rented room above the Gilded Folio, and it is her
    second attempt."* Three new facts about a locked object — a method, a duration, a
    predecessor — none supplied by either source. Breaks, at that sentence.
  - **Edge — the boundary.** The page invents *a weighted net that drops on the first
    person through the front doors, DC 12 Dexterity save*. It is a whole new
    mechanical fact with a number on it — and the brief locks **no** net. Not in the
    subject set: **holds**, and a finding here would be the row doing precisely what
    it was scoped not to do. If the same sentence had given the *egg* a new save
    nobody agreed to, it would break.

- **Corpus pointer:** *none* yet. This row is the likeliest of the three to earn one
  — *is this a new fact or the same fact said differently?* is exactly the kind of
  boundary that drifts run to run — but the corpus is authored from labeled instances
  the runs produce, not invented ahead of them.
