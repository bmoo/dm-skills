# Golden corpus — `build-session/spotlight-coverage`

A labeled corpus for **`build-session/spotlight-coverage`** — *"the plan is done when
every PC is either given a beat or named as resting"* (`SKILL.md` — "every PC is
either given a beat or named as resting"), against the session budget *"every PC
gets a beat somewhere across a scenario group — in any pillar"*
(`spotlight/doctrine.md` — "Every PC gets a beat somewhere across a scenario
group — in any pillar"), read on a page where
*"absence is the record: a PC named nowhere on the page was planned as resting"*
(`session-page-format.md` — "**Absence is the record:**"). (See the row in
[`../../judgement-rubric.md`](../../judgement-rubric.md).)

## Purpose — pin the boundary by example

`spotlight-coverage` is the library's **legal-absence** judgement, and the only row of
that class. Its deterministic pre-pass — `spotlight_coverage(page, roster)` in the
shared [mechanical checker](../../scripts/mechanical_checker/checker.py) — computes
`roster − PCs named in Spotlight annotations` and **emits no finding and fails
nothing**, because an uncovered PC is legal: they were either rested on purpose
(correct) or dropped (a defect), and the page alone cannot tell which.

So the pre-pass computes the *fact* and this row rules on the *verdict*, and the
verdict turns on the words "defensible rest" — which drift page to page exactly the
way the reader-interpretation rows' criteria do. Hand-written anchors alone leave that
boundary soft. This corpus pins it **by example**: instances labeled with the verdict a
correct checker must return, spanning clear passes, clear fails, and the genuine edges
the criteria exist to adjudicate.

## What each instance is

Every instance is **self-contained** — exactly what the
[fresh-context checker](../../scripts/judgement_checker/checker-launch-protocol.md)
would see, and nothing else:

1. **The roster** — the PC list and each PC's flagged ability. Unlike every other
   session-page row, **`spotlight-coverage` reads the roster**: it is the denominator
   the coverage is computed against, and the flagged abilities are what make a scene
   an "obvious carrier" for a particular PC.
2. **The pre-pass output** — the **uncovered set** and each PC's **beat share**. This
   is handed to the checker, not recomputed by it.
3. **What the page stages** — the minimal page content the absence is judged against:
   the annotated beats, and any scene that bears on whether an uncovered PC's rest is
   defensible.

This is the **legal-absence instance shape** the [rubric
format](../../scripts/judgement_checker/rubric-format.md) defines — distinct from the
reader-interpretation corpora (`plain-language`, `clue-interpretability`), whose
instances carry a *line* plus the context it is read against.

Nothing else travels with an instance — no generator reasoning, no fix, no hint at the
expected verdict inside the instance file. The label lives only in the
[verdict map](verdict-map.md).

## Labels

- **pass** → `approve` — the uncovered set is empty, or every absence in it is a
  defensible rest the page's content supports.
- **fail** → `disapprove` — an absence reads as a **dropped beat**: an obvious carrier
  scene went unused, or one PC hoarded the budget while another got nothing.
- **edge** → the borderline the criteria must adjudicate; its expected verdict is
  stated explicitly in the verdict map (an edge is not a third label — it resolves to
  `approve` or `disapprove`, and the map says which, so the boundary is pinned rather
  than left to a shrug).

## The three boundaries the edges exercise

By design the edges bracket `spotlight-coverage`'s hard calls — the
**obvious-carrier** boundary (the staged/unstaged funeral pair, which differ in
nothing else), the **secondary-mention** rule (a PC named inside another's beat is
covered), and the row's **scope** (a second straight rest is catch-up's finding, not
this checker's). The verdict map's *"boundaries the edges pin"* section states each in
full.

## The verdict map

[`verdict-map.md`](verdict-map.md) is the manifest: each instance file → its label →
its expected verdict → a one-line rationale. A future harness runs the checker over
each instance and asserts its verdict matches the map.

## Out of scope — the validation harness

**This corpus is data only.** The harness that runs the checker over these instances
and asserts each verdict matches the map is **out of scope here** — it is edit-time
work for the evaluation harness,
not built or run at the table. This corpus contains the labeled instances and
the verdict map; it adds no pytest and no validation harness for them.

## Layout

```
spotlight-coverage/
├── README.md                              ← this file
├── verdict-map.md                         ← instance → label → expected verdict → rationale
└── instances/
    ├── pass-full-coverage.md                     ← uncovered set empty
    ├── pass-defensible-rest-no-carrier.md        ← one rest, no scene was hers
    ├── pass-two-rests-short-session.md           ← two rests on a one-scene page
    ├── fail-obvious-carrier-aimed-elsewhere.md   ← her shrine annotated for someone else
    ├── fail-hoarded-beats.md                     ← 4 of 5 beats on one PC
    ├── fail-uncovered-pc-is-the-only-key.md      ← spread beats, her scene still dropped
    ├── edge-unstaged-funeral.md                  ← depicted, not staged → approve
    ├── edge-staged-funeral-rite.md               ← same scene, staged → disapprove
    ├── edge-secondary-mention-only.md            ← secondary counts as covered → approve
    └── edge-second-straight-rest.md              ← streaks are catch-up's → approve
```
