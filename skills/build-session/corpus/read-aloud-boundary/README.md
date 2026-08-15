# Golden corpus — `build-session/read-aloud-boundary` (perception boundary)

A labeled corpus for **`build-session/read-aloud-boundary`** — *"a read-aloud block
carries only what the characters see, hear, smell, feel, or taste right now, plus
dialogue spoken in their presence and text they can read. The test: could someone
standing there perceive this, from where they stand, right now?"* (See the row in
[`../../judgement-rubric.md`](../../judgement-rubric.md), source:
`session-page-format.md` — "**Read-aloud is what they perceive.**" and the DoD
checklist line "The read-aloud sweep is done".)

## Purpose — pin the boundary by example

`read-aloud-boundary` is a **reader-interpretation** judgement: *could someone at the
party's position perceive this, right now?* The same criteria words ("perceivable",
"vantage", "inference", "sensation") drift from page to page, so hand-written anchors
alone leave the boundary soft. This corpus pins it **by example** — read-aloud
instances labeled with the verdict a correct checker must return, spanning clear
passes, clear fails, and the genuine edges the criteria exist to adjudicate.

## What each instance is

Every instance is **self-contained** — it carries exactly what the
[fresh-context checker](../../scripts/judgement_checker/checker-launch-protocol.md)
would see for this one block, and nothing else:

1. **The read-aloud** — a single `> [!read-aloud]` block, labeled with the slot it
   sits in (the opener, a keyed area, a clue payload's Show).
2. **The scene state** — the minimal context the block is judged against: where the
   party stands, what light there is, and what is actually true of the scene (so the
   checker can tell perceivable description from narrated DM knowledge). (It is *not*
   the party roster — `read-aloud-boundary` does not read the roster; see the rubric
   row's *Roster use*.)

Nothing else travels with an instance — no generator reasoning, no fix, no hint at the
expected verdict inside the instance file. The label lives only in the
[verdict map](verdict-map.md).

## Labels

Each instance is labeled with the verdict a correct checker returns:

- **pass** → `approve` — every sentence in the block is perceivable from the party's
  position: sensory description, immediate universal inference, atmosphere as
  sensation, involuntary physical reactions, dialogue, readable text.
- **fail** → `disapprove` — a sentence asserts what no one present could perceive:
  hidden history, causes, intent, meanings, an imposed emotion or decision, or detail
  beyond the party's vantage (the `read-aloud-boundary` defect).
- **edge** → the borderline the criteria must adjudicate; its expected verdict is
  stated explicitly in the verdict map (an edge is not a third label — it resolves to
  `approve` or `disapprove`, and the map says which, so the boundary is pinned rather
  than left to a shrug).

## The three boundaries the edges exercise

By design the edges bracket `read-aloud-boundary`'s three hard calls: **how much
inference is perception?** (`edge-immediate-inference-abandoned` → approve — a
conclusion anyone at the scene reaches at a glance is perception), **when does mood
become a fact claim?** (`edge-mood-asserts-fact` → disapprove — atmosphere is legal as
sensation and illegal the moment it asserts an unperceivable fact as fact), and **what
does a limited vantage deliver?** (`edge-distant-shape-silhouette` → approve — a shape
beyond the light appears as exactly what that vantage registers, and no more).

## The regression pair

`pass-physical-inventory-graveyard` and `fail-hidden-history-graveyard` are the same
scene split at the boundary: the
physical inventory of the graveyard passes, and the same inventory with its historical
explanation attached fails. The blameless description does not rescue the leaked
history, and the leaked history does not condemn the description.

## The verdict map

[`verdict-map.md`](verdict-map.md) is the manifest: each instance file → its label →
its expected verdict → a one-line rationale. A future harness runs the checker over
each instance and asserts its verdict matches the map.

## Out of scope — the validation harness

**This corpus is data only.** The harness that runs the checker over these instances
and asserts each verdict matches the map is **out of scope here** — it is edit-time
work for the evaluation harness, not built or run at the table.
This corpus contains the
labeled instances and the verdict map; it adds no pytest and no validation harness for
them.

## Layout

```
read-aloud-boundary/
├── README.md                     ← this file
├── verdict-map.md                ← instance → label → expected verdict → rationale
└── instances/
    ├── pass-physical-inventory-graveyard.md
    ├── pass-dialogue-and-inscription.md
    ├── pass-atmosphere-as-sensation.md
    ├── fail-hidden-history-graveyard.md         ← the regression pair's fail half
    ├── fail-imposed-emotion-decision.md
    ├── fail-vantage-contents-of-darkness.md
    ├── edge-immediate-inference-abandoned.md    ← glance-level inference → approve
    ├── edge-mood-asserts-fact.md                ← mood as fact claim → disapprove
    └── edge-distant-shape-silhouette.md         ← limited vantage, honest → approve
```
