# Beside-file rubric format

The rubric is what the [fresh-context checker](checker-launch-protocol.md) grades
against. It ships as a file **beside each generator's `SKILL.md`** (not in this
shared directory — see the [README](README.md#where-the-real-rubrics-live)).
Each generator's rubric follows the format defined here.

## Derived from the inventory — never hand-copied

Every rubric row **is** a row of
[`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md) — one
of that skill's `judgement`-method rows. The rubric does not invent criteria; it
**derives** each row from its inventory entry (the promise text, and the
`SKILL.md`/reference source line the inventory already cites). Because the row's
identity, promise text, and source all trace back to the inventory, an
inventory→rubric drift is **structurally impossible**: change the promise and the
row it derives from changes with it. (The harder leg — skill-text→inventory drift
— is guarded separately at maintainer time by the agentic sweep, spec §"Rubric
source of truth"; out of scope here.)

## The row schema

Each rubric row has these parts:

| Part | What it holds |
|---|---|
| **Inventory check id** | The row's id in the inventory — `build-session/npc-rows-named`, `dungeon-generator/lead-interpretability`, `build-session/clue-interpretability`, … This is the **promise-pointer** every finding against this row must cite (see [`verdict-contract.md`](verdict-contract.md)). It is the row's identity; it is never invented, only carried from the inventory. |
| **Promise text** | The promise, quoted or derived from the inventory row **and the passage its anchor phrase names** (e.g. `build-session/session-page-format.md` — "**Every row is named**"). This is the thing the output must honour, in the skill's own words. |
| **Roster use** | Whether the check consumes the party roster, and how. Structural rows (is this cell a name?) say **none**; roster-dependent rows (a flagged-ability spotlight, a level-appropriate budget) say **which** roster field they read. Tells the checker whether to look at the roster it was handed. |
| **Criteria** | The test the checker applies, stated so a reader reaches the same verdict twice. What makes the promise *hold*; what makes it *break*; and — because the verdict is disapprove-on-uncertainty — what the checker does when it **cannot tell** (it disapproves). |
| **Anchors** | Hand-written worked examples inline: a **good** (passes), a **bad** (breaks), and an **edge** (the borderline the criteria must adjudicate). These pin the criteria by example so verdicts are repeatable rather than re-litigated every run (spec user story 14). See below. |
| **Corpus pointer** (optional) | For the reader-interpretation rows only — a link to a labeled golden corpus. See below. |

### Anchors — hand-written per case (the default)

Every in-scope judgement row carries **hand-written anchors**: a good, a bad, and
an edge example, written inline beside the criteria. They are self-contained,
folder-hash-pinned, and cheap to keep current, and they are what make the checker's
verdicts repeatable. This is the **default and the floor** — no judgement row ships
without them. Write the edge example at the exact boundary the criteria draw, so
the checker has a worked precedent for the case it is most likely to get wrong.

### Corpus pointer — added on top, for reader-interpretation rows only

Four rows are **reader-interpretation** judgements — *does a stranger understand
this? can the party act on it? could someone at the scene perceive this?* — where
the same criteria words drift across
outputs and only a labeled corpus pins the boundary:
**`dungeon-generator/lead-interpretability`**,
**`build-session/clue-interpretability`** (node-deepening),
**`build-session/plain-language`** (undefined-coinage), and
**`build-session/read-aloud-boundary`** (perception boundary). For these, the format has a **place to point
at a labeled golden corpus** on top of the hand-written anchors.

The **corpus authoring is not part of this rubric format** — the golden
corpora and their verdict-match harness are edit-time work for the evaluation
harness. The format only reserves
the slot; a reader-interpretation row ships its hand-written anchors now and gains
its corpus pointer when the corpus exists. Structural rows (is this cell a name?)
never get a corpus — hand-written anchors are sufficient and complete for them.

### Corpus pointer — also for legal-absence rows

A second class earns a corpus, on the same rationale rather than the same subject
matter: a **legal-absence** row, where the deterministic tier can compute the
*fact* but not the *verdict*, because the thing it found is legal in one reading
and a defect in the other. The library's one such row is
**`build-session/spotlight-coverage`**: a deterministic pre-pass computes `roster − PCs named in Spotlight
annotations`, but "absence is the record — a PC named nowhere on the page was
planned as resting" (`build-session/session-page-format.md` — "**Absence is the
record:**") makes an
uncovered PC either a deliberate rest or a dropped beat. The judgement is *is this
rest defensible?*, and those criteria words drift run to run exactly as the
reader-interpretation rows' do, which is what a corpus is for.

Note the shape difference: a reader-interpretation instance carries a line plus
the context it is read against; a legal-absence instance carries the **pre-pass
output** (which PCs are uncovered, and each PC's beat share) plus enough of the
page to judge whether the absence is defensible.

Split criterion, for a future row author: **default to hand-written anchors;
promote to hand-written + corpus only for reader-interpretation judgements or
legal-absence judgements**, never for plainly structural ones (is this cell a
name? is this section present?), where the deterministic tier's finding *is* the
verdict.

## What the checker does with a row

For each row it is handed, the checker applies the **criteria** (consulting the
**roster** iff the row's *roster use* says to, and the **corpus** if one is
pointed at), and on a break emits a finding that:

- cites this row's **inventory check id** as its promise-pointer (required),
- anchors the break to **where in the output** it occurs (required),
- states the **defect only, no fix** (forbidden to prescribe a remedy).

That finding shape is fixed in [`verdict-contract.md`](verdict-contract.md). If the
checker cannot tell whether the row holds, it **disapproves** — the criteria's
"cannot tell" branch is not optional.

## A worked example

[`reference/`](reference/) carries one row — **`build-session/npc-rows-named`**,
"every NPC row is named" —
written in this exact format, with a good/bad/edge anchor set and two fixture
outputs showing an `approve` and a `disapprove` verdict against it. It is an
*example of the format*, not a shippable rubric; the real rows are authored beside
each `SKILL.md`.
