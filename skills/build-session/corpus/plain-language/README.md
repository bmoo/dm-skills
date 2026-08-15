# Golden corpus — `build-session/plain-language` (undefined coinage)

A labeled corpus for **`build-session/plain-language`** — *"everything the DM executes
mid-session — encounter blocks, spotlight lines, keyed-area run notes, contingencies —
states mechanics and named page fiction only. A coined term is legal only if the page
defines it before or where it's used; an undefined metaphor is a defect, however
evocative. The test: a competent DM who has never seen this campaign could execute the
line with only this page open."* (See the row in
[`../../judgement-rubric.md`](../../judgement-rubric.md), source:
`session-page-format.md` — "**Plain language in run-time text.**" and the DoD
checklist line "no run-time line depends on an undefined coinage or metaphor".)

## Purpose — pin the boundary by example

`plain-language` is a **reader-interpretation** judgement: *could a competent stranger
DM execute this run-time line with only this page open?* The same criteria words
("undefined", "coinage", "defined nearby", "run-time") drift from page to page, so
hand-written anchors alone leave the boundary soft. This corpus pins it **by example**
— run-time line instances labeled with the verdict a correct checker must return,
spanning clear passes, clear fails, and the genuine edges the criteria exist to
adjudicate.

## What each instance is

Every instance is **self-contained** — it carries exactly what the
[fresh-context checker](../../scripts/judgement_checker/checker-launch-protocol.md)
would see for this one line, and nothing else:

1. **The line** — a single page line, labeled with the run-time slot it sits in
   (encounter block, spotlight line, contingency, keyed-area run note) — or, for the
   scope edge, a passage that is *not* run-time text.
2. **What the page defines nearby** — the minimal context needed to judge the line:
   whether the page defines any coined term the line uses (before use, at the point of
   use, or not at all), and whether the line is run-time text at all. This is the "with
   only this page open" context the row is graded against. (It is *not* the party
   roster — `plain-language` does not read the roster; see the rubric row's *Roster use*.)

Nothing else travels with an instance — no generator reasoning, no fix, no hint at the
expected verdict inside the instance file. The label lives only in the
[verdict map](verdict-map.md).

## Labels

Each instance is labeled with the verdict a correct checker returns:

- **pass** → `approve` — a stranger DM could execute the line with only this page open
  (mechanics, named page fiction, or a coinage the page defines).
- **fail** → `disapprove` — a run-time line rests on an **undefined coinage or
  metaphor** (the `plain-language` defect).
- **edge** → the borderline the criteria must adjudicate; its expected verdict is stated
  explicitly in the verdict map (an edge is not a third label — it resolves to `approve`
  or `disapprove`, and the map says which, so the boundary is pinned rather than left to
  a shrug).

## The two boundaries the edges exercise

By design the edges bracket `plain-language`'s two hard calls: **is the coinage
actually defined?** (`edge-loosely-mentioned-not-pinned` → disapprove vs.
`edge-self-defining-in-line` → approve) and **is this even run-time text?**
(`edge-coinage-in-design-aside` → approve, because `plain-language` is scoped to text
the DM executes mid-session and the metaphor sits in a design aside). The second is
`plain-language`'s scope prong — deciding *which* text is run-time is itself part of
the judgement.

## The verdict map

[`verdict-map.md`](verdict-map.md) is the manifest: each instance file → its label →
its expected verdict → a one-line rationale. A future harness runs the checker over
each instance and asserts its verdict matches the map.

## Out of scope — the validation harness

**This corpus is data only.** The harness that runs the checker over these instances
and asserts each verdict matches the map is **out of scope here** — it is edit-time work
for the evaluation harness, not
built or run at the table. This corpus contains the labeled instances and
the verdict map; it adds no pytest and no validation harness for them.

## Layout

```
plain-language/
├── README.md                     ← this file
├── verdict-map.md                ← instance → label → expected verdict → rationale
└── instances/
    ├── pass-mechanics-only.md
    ├── pass-defined-coinage-candle-ledger.md
    ├── pass-named-page-fiction.md
    ├── fail-undefined-metaphor-thread-needle.md
    ├── fail-aphorism-contingency.md
    ├── fail-first-use-coinage-run-note.md
    ├── edge-loosely-mentioned-not-pinned.md     ← named but not pinned → disapprove
    ├── edge-self-defining-in-line.md            ← defined at point of use → approve
    └── edge-coinage-in-design-aside.md          ← not run-time text → approve
```
