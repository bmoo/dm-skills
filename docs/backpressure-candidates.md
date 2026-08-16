# Backpressure candidates

Where a skill's output was corrected downstream in the primary consumer campaign
repo, read its `log.md` (the campaign wiki log)
and its git history, then cross-checked against what actually landed in this
library's `skills/*` source and `docs/eval-assertion-inventory.md`.

"Backpressure" here = a real correction at the table or in review that should
push back on the *skill*, so the skill stops re-emitting the output that needed
fixing. Each candidate is a correction a well-designed skill could have
prevented.

## Method & filter

For every logged correction, one test: **could a better skill have prevented
this, or was it a creative call no skill owns?**

- Kept: defects — the skill emitted something wrong/unrunnable/uncheckable.
- Dropped: campaign creative decisions (villain identity, a player character's
  arc, a time-loop rework, item approvals). No skill prevents those; they are authoring,
  not backpressure. The bulk of `log.md` is this — correctly out of scope.

Ranked by **recurrence, not recency**. The strongest candidate is a defect class
that recurred, strongest of all one that recurred *after* an upstream fix.

## Scope boundary (named, not silently dropped)

- **In scope:** the eight portable skills in this repo (`build-session`,
  `combat-generator`, `dungeon-generator`, `spotlight`, `catch-up`, `seed-clues`,
  `party-sync`, `campaign-art`).
- **Out of scope:** a campaign-local site pipeline — `publish-site`,
  `links.lua`, `style.css`, `publish.sh`, topbar/mojibake/CSS lints. These are
  ~15 log entries but they correct a repo-local skill that does not live here.
  Redirect if "my skills" is meant to include repo-local ones.

## The meta-finding (root cause behind most recurrences)

The dominant failure mode is **a rule added to a skill's prose while its
definition-of-done never grew a box to check it** — so the skill keeps emitting
the old output until a human re-catches it. The 2026-07-16 log entry says it
outright: *"the `build-session` format doc mandates hotspot embeds but its
definition-of-done checklist doesn't check for them."* Same shape drove the
`8f44a47` "U2" fix — an unenforceable rule replaced with a countable one.

**Highest-leverage single action:** sweep every `build-session` /
`combat-generator` / `dungeon-generator` format mandate against its own DoD and
against `eval-assertion-inventory.md`; any mandate with no matching checkable
row is a latent recurrence. This is a superset of the individual candidates
below.

---

## Open — act on these

| Candidate | Skill | Defect (log) | Status | Action |
|---|---|---|---|---|
| **not-runnable-at-the-table** | build-session | **"Not runnable at the table."** Cryptic scenes / undefined abstractions the DM can't execute. Recurred: 07-11 "four cryptic scenes made table-concrete" (Carousel/Wheel/Sky Ride/locket), then 07-18 "plain-language pass" ("the needle," "thread the tide," "the leash-line"). | Rule + DoD box added **only at 07-18** (`ea85237`; `build-session/session-page-format.md` — "**Plain language in run-time text.**", and the DoD box "The plain-language sweep is done") — *after* two recurrences. **Corrected 08-05:** the fix is further along than this row first recorded. The `judgement`-class row is fully specified — `judgement-rubric.md` row `build-session/plain-language`, plus a 9-instance labeled corpus quoting the exact recurrence phrases. What is missing is not a fixture but an **executor**; see [the outside-comparison section](#what-an-outside-comparison-surfaced-2026-08-05). | Run the existing corpus. Not: write a new fixture, and not: sharpen the DoD box toward a regex — the row is correctly judgement-class. |
| **spotlight-plan-lifecycle** | spotlight (+ its 6 consumers) | **Spotlight-plan wiring / transience.** The session spotlight plan's lifecycle has been re-cut repeatedly: 07-06 "two spotlight-pipeline wiring fixes" (plan evaporating with the chat → combat-generator reads the page), then reversed — `d1a08f9` "don't print it as a table," then the spotlight-transience consolidation (`bc75cac`, `ab0d0cb`) "the plan is *transient*, not filed on the page," across all six consumers. | The most-churned interface in the library; direction actually flipped (durable → transient). The transience consolidation claims consistency across all six consumers. | Confirm that consolidation truly settled it (one contract, six consumers agree) and add an assertion so a seventh consumer can't drift. Treat as the fragile-interface case. |
| **mandate-without-a-check** | build-session | **DoD-completeness gap** (the meta-finding, as a concrete task). Format doc mandated hotspot embeds; DoD didn't check → miss re-caught at the table 07-16 (`de7ba92` added the box after the fact). | Individual box added; the *class* (mandate-without-check) is not swept. | Do the sweep in the meta-finding above. Every un-checked mandate is a future not-runnable-at-the-table or mandate-without-a-check. |

## Watch — upstreamed, but fragile / recurred in one area

| Candidate | Skill | Defect (log) | Status |
|---|---|---|---|
| **clue-interpretability-and-self-containment** | seed-clues / build-session | **Clue interpretability & self-containment.** Three hardenings in one week: 07-12 a clue scripted recognition of art the party never saw (`6952d43`); 07-12 a clue "only told the DM," no player-facing vehicle (`8719a87`); 07-14 payloads not self-contained → Show/They-learn/Points-at contract (`f469f37`). | All upstreamed. Three fixes to one surface in days = fragile. Verify the three rules compose and are DoD-enforced, not just documented in prose. A 9-instance `clue-interpretability` corpus exists and is likewise unexecuted. |
| **lethality-vs-target-hp** | combat-generator | **Lethality sanity vs target HP.** 07-05 the Session 1 goblin one-shot commoners (1d4+2 vs 4 HP) *and* could die before acting (3 HP vs six attackers) — a mechanically broken set-piece shipped, hand-tuned by the DM. | No assertion. A "damage/HP sanity for scripted/low-HP participants" check would catch it; borderline vs. legitimate DM fine-tuning. Medium. |
| **spotlight-reads-real-builds** | spotlight / party-sync | **Spotlight uses real builds, not an archetype kit.** 07-05 the A4 drill's job list still assigned the retired archetype kit instead of the synced sheets. | Tied to the spotlight↔party-sheet data flow (same surface as spotlight-plan-lifecycle). Verify the spotlight step always reads real synced abilities. |

## Closed — verified fed back into source; listed so they're not re-raised

| Skill | Correction | Where it landed |
|---|---|---|
| combat-generator, dungeon-generator | Fights shortlisted from model memory (2024 MM only), not the catalog → **mandate browsing all active sources.** | In source: `build-session/combat.md` — "**MUST** browse the chosen source's catalog" (the single copy since the generator merge; the keyed-site procedure points at it). Closed. |
| combat-generator | Bare creature names on the page → **names must carry stat-block refs.** | `330f614`; assertion C6. Closed unless it recurs. |
| dungeon-generator | Unenforceable "no consecutive fights" rule → **countable balance rule.** | `8f44a47` (U2). Closed — and the model for how a U-row becomes a real check. |

---

## Housekeeping note (not backpressure, but surfaced en route)

One campaign still vendors a standalone `.claude/skills/zoom-in/` directory, but
`zoom-in` was collapsed into `build-session` as `node-deepening.md` here
(`857fb56`). The vendored copy is stale against source — worth a re-sync.

## What an outside comparison surfaced (2026-08-05)

Compared against an agentic end-to-end verification setup described in
["OpenAI Made a New Kind of AI Coding Possible"](https://youtu.be/_eCtUVds3wA)
— PR diff → enumerate new user flows → one ephemeral sandbox per flow → an agent
drives Playwright as a user → a **judge agent grades the recording** and
re-triggers on weak evidence → failures open issues. Two deltas are genuinely new
here; the rest of this document's queue it merely corroborates.

### The graders are specified but never executed

Four labeled golden corpora exist — 37 instances total:

| Corpus | Instances |
|---|---|
| `build-session/corpus/plain-language` | 9 |
| `build-session/corpus/clue-interpretability` | 9 |
| `build-session/corpus/spotlight-coverage` | 10 |
| `dungeon-generator/corpus/lead-interpretability` | 9 |

Each has a `verdict-map.md` naming the expected verdict per instance. Every one
of them defers the run: *"A future harness (out of scope here — deferred to a
separate follow-up) runs the checker over each
instance and asserts the returned verdict equals the **Expected verdict**
column."* Nothing in `lib/` does. The only code that touches these files is
`lib/citation_anchors.py`, which asserts their **anchor phrases still exist** —
not that any grader returns the right verdict.

This re-scopes the **not-runnable-at-the-table** candidate above. Its status note
says the fix "relies on the author re-reading" and is "untested against a third
recurrence" — but the rubric row and corpus for it are complete, and quote the
exact recurrence phrases from the log ("thread the needle", "thread the tide",
"when the tide turns, spend the candle"). The gap is not a missing fixture. It
is a missing **executor**. Same for the
**clue-interpretability-and-self-containment** candidate.

### Every check reads a hand-authored fixture, never real skill output

`claude -p` and `stream-json` appear in this repo only as aspiration
(`docs/eval-assertion-inventory.md` — "a headless run also yields the tool-call
stream", "need real output from a real run — the expensive tier"). No harness
runs a skill and checks what it emitted. Both mechanical-tier recurrences are
artifacts of that: `9517e92` (the brief page graded against only the 9-row Spec
subset, missing a `Preparation` section and 4 art pieces) and `fbfe586` (five
keyed pages with no map) are both *"a fixture passed because nobody ran the right
subset against it."* That bug **cannot exist** against real runs, where each
fresh artifact must clear the full applicable subset by construction.
`lib/test_session_fixture_sweep.py` is the corpus-shaped patch for a
corpus-shaped problem.

### Verdicts carry no evidence

The judge in the video grades a Playwright recording and can re-trigger the
sandbox when the evidence is thin. `lib/judgement-checker/verdict-contract.md`
has no equivalent: a verdict arrives with nothing behind it, so a wrong verdict
is indistinguishable from a right one and the grader itself can never be
regression-tested. A required quoted-span + reason field is the cheap fix, and it
is what would justify trusting the judgement tier enough to widen it.

### What the comparison corroborates rather than originates

The mandate-vs-DoD sweep (the meta-finding above) is the same move as
the video's *diff → new user flows* enumerator, one domain over. The
[Unenforceable as written](eval-assertion-inventory.md) backlog is the same shape
as the video's capability gaps (a flow that cannot be verified because the
sandbox has no Slack account) — and its answer there is to treat that backlog as
the work, not as a standing footnote. Neither is a new idea here; both are
already queued.

## How this connects to the existing machinery

`docs/eval-assertion-inventory.md` already tracks the library's checkable
promises and flags the "Unenforceable as written" U-rows. Every open and watch
candidate is either a promise the skill made but doesn't enforce (→ new
assertion) or a promise it can't enforce as written (→ a U-row to rewrite, like
U2). Folding these candidates into that inventory is the durable form of the
backpressure.
