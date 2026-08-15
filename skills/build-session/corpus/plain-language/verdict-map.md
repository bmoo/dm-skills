# `build-session/plain-language` corpus — verdict map

The manifest for the [`build-session/plain-language` corpus](README.md). Each row maps
one instance file → its **label** → the **expected verdict** a correct [fresh-context
checker](../../scripts/judgement_checker/checker-launch-protocol.md) must return when
handed that instance against the **plain-language** rubric row → a one-line rationale. A
future evaluation harness (out of scope here) runs the checker over each instance
and asserts the returned verdict equals the **Expected verdict** column.

Labels: **pass** = a stranger DM could execute the run-time line with only this page
open (`approve`); **fail** = a run-time line rests on an undefined coinage or metaphor
(`disapprove`); **edge** = the borderline the criteria adjudicate — it still resolves
to `approve` or `disapprove`, stated explicitly below so the boundary is pinned, not
shrugged.

| Instance | Label | Expected verdict | Why |
|---|---|---|---|
| [`instances/pass-mechanics-only.md`](instances/pass-mechanics-only.md) | pass | **approve** | Runs on **game mechanics** (initiative, range, a DC check) and plain fiction (a bell, guards). No coinage to define. |
| [`instances/pass-defined-coinage-candle-ledger.md`](instances/pass-defined-coinage-candle-ledger.md) | pass | **approve** | "candle-ledger" is coined, but the **clue slate defined it earlier** on the page — legal coinage, defined before use. |
| [`instances/pass-named-page-fiction.md`](instances/pass-named-page-fiction.md) | pass | **approve** | Runs on **named page fiction** — Voss (a Key NPCs row) and the debt (his depth note), both established on this page. |
| [`instances/fail-undefined-metaphor-thread-needle.md`](instances/fail-undefined-metaphor-thread-needle.md) | fail | **disapprove** | "thread the needle" is an **undefined metaphor** in a spotlight line — no mechanic, no page definition; a stranger DM can't tell what Brenna does. |
| [`instances/fail-aphorism-contingency.md`](instances/fail-aphorism-contingency.md) | fail | **disapprove** | "when the tide turns, spend the candle … the wick" — stacked **aphoristic compression** in a contingency, none defined; unexecutable at the table. |
| [`instances/fail-first-use-coinage-run-note.md`](instances/fail-first-use-coinage-run-note.md) | fail | **disapprove** | "the Forgotten" is **first-used in run-time text** with no prior definition and no stat-block reference — a stranger DM can't tell what stirs. |
| [`instances/edge-loosely-mentioned-not-pinned.md`](instances/edge-loosely-mentioned-not-pinned.md) | edge | **disapprove** | "the Deep Bargain" is **named earlier but never pinned** — no invocation, cost, or content stated. Named ≠ defined; the checker can't confirm a stranger DM could run it → cannot-tell → disapprove. |
| [`instances/edge-self-defining-in-line.md`](instances/edge-self-defining-in-line.md) | edge | **approve** | "breath-book" is coined but **defined inline, in the same clause** ("a slim journal of confessions … in a whisper-code of dots"). "Defines it before **or where** it's used" is satisfied at the point of use. |
| [`instances/edge-coinage-in-design-aside.md`](instances/edge-coinage-in-design-aside.md) | edge | **approve** | "thread the tide" is an undefined metaphor, but it sits in a **design-intent aside**, not run-time text — `plain-language` is scoped to text the DM executes mid-session, and aphorism is explicitly allowed in design discussion. Out of scope → no defect. |

## The boundaries the edges pin

The three edges bracket `plain-language`'s two hard cases:

- **`edge-loosely-mentioned-not-pinned` → disapprove** vs.
  **`edge-self-defining-in-line` → approve** pin the **"is the coinage defined?"**
  boundary. A term merely **named** earlier (a rumor "of a deep bargain") is not defined
  — a stranger DM has a label but no executable content, so the checker's cannot-tell
  branch disapproves. A term **self-defined where it is used** (the breath-book,
  explained in the same clause) *is* defined — "before **or where** it's used" — so it
  passes. Naming a coinage is not defining it; explaining it at the point of use is.
- **`edge-coinage-in-design-aside` → approve** pins the **scope** boundary. The same
  undefined metaphor that breaks `plain-language` in a spotlight line is **out of
  scope** in a design-intent aside, because `plain-language` grades **run-time text
  only** — text the DM executes mid-session. Deciding *which* text is run-time is itself
  part of `plain-language`'s judgement, and this instance is the worked case: aphorism
  in design voice is allowed; aphorism in a line the DM runs at 9pm is not.

Together they say: `plain-language` fires only on **run-time text**, and a coinage there
is legal only when the page **actually defines it** — before use or at the point of use
— never when it is merely gestured at.
