# `build-session/read-aloud-boundary` corpus — verdict map

The manifest for the [`build-session/read-aloud-boundary` corpus](README.md). Each row
maps one instance file → its **label** → the **expected verdict** a correct
[fresh-context checker](../../scripts/judgement_checker/checker-launch-protocol.md)
must return when handed that instance against the **read-aloud-boundary** rubric row →
a one-line rationale. A future evaluation harness (out of scope here) runs the checker over each instance
and asserts the returned verdict equals the **Expected verdict** column.

Labels: **pass** = every sentence in the block is perceivable from the party's
position (`approve`); **fail** = a sentence asserts what no one present could perceive
(`disapprove`); **edge** = the borderline the criteria adjudicate — it still resolves
to `approve` or `disapprove`, stated explicitly below so the boundary is pinned, not
shrugged.

| Instance | Label | Expected verdict | Why |
|---|---|---|---|
| [`instances/pass-physical-inventory-graveyard.md`](instances/pass-physical-inventory-graveyard.md) | pass | **approve** | Every clause is a **physical inventory** perceivable from the gate — stones, angles, moss, the open church door. Nothing about who, when, or why. |
| [`instances/pass-dialogue-and-inscription.md`](instances/pass-dialogue-and-inscription.md) | pass | **approve** | A spoken line and a **readable inscription carrying a date** — the date is on the stone, not in the narrator's head. Dialogue and text they can read are always legal. |
| [`instances/pass-atmosphere-as-sensation.md`](instances/pass-atmosphere-as-sensation.md) | pass | **approve** | Mood held entirely as **sensation** — still air, distant dripping, a chill on the arms (an involuntary physical reaction). No unperceivable fact asserted. |
| [`instances/fail-hidden-history-graveyard.md`](instances/fail-hidden-history-graveyard.md) | fail | **disapprove** | The same graveyard inventory plus **hidden history and causes** — who discarded the stones, decades ago, and that the dead arranged them. No one at the gate perceives any of that; the blameless description does not rescue it. |
| [`instances/fail-imposed-emotion-decision.md`](instances/fail-imposed-emotion-decision.md) | fail | **disapprove** | The box **imposes an emotion and a decision** — "you feel terrified", "you know you shouldn't be here". Inner states are the players' to declare, not the box's to assert. |
| [`instances/fail-vantage-contents-of-darkness.md`](instances/fail-vantage-contents-of-darkness.md) | fail | **disapprove** | The box narrates **detail the vantage cannot deliver** — the contents of an unlit alcove and a shut strongbox, described from the doorway. Beyond the party's vantage. |
| [`instances/edge-immediate-inference-abandoned.md`](instances/edge-immediate-inference-abandoned.md) | edge | **approve** | "Long-abandoned" is a conclusion, but one **anyone at the scene reaches at a glance** from the perceivable evidence the box itself lists. Immediate universal inference is perception. |
| [`instances/edge-mood-asserts-fact.md`](instances/edge-mood-asserts-fact.md) | edge | **disapprove** | "The dead here do not rest" reads as mood but **asserts an unperceivable fact as fact** — the sentence claims knowledge of the dead's state, which no one at the fence perceives. Atmosphere ends where fact assertion begins. |
| [`instances/edge-distant-shape-silhouette.md`](instances/edge-distant-shape-silhouette.md) | edge | **approve** | The far end is beyond the torchlight, and the box says only what that vantage registers — **a dark shape, a glint** — never the detail behind them. Honest limited vantage passes. |

## The boundaries the edges pin

The three edges bracket `read-aloud-boundary`'s three hard cases:

- **`edge-immediate-inference-abandoned` → approve** pins the **inference** boundary.
  The test is not "is this a conclusion?" but "could someone standing there conclude
  this at a glance, from what they perceive, without being told?" A sagging roof and a
  seized wheel make "long-abandoned" perception; a specific culprit or a date would
  make it hidden history. Glance-level inference passes; told-knowledge breaks.
- **`edge-mood-asserts-fact` → disapprove** pins the **atmosphere** boundary, against
  `pass-atmosphere-as-sensation`. The same register — quiet dread — passes while it
  stays in the characters' senses and breaks the moment a sentence asserts an
  unperceivable fact as fact. The checker asks "does this sentence claim something no
  one present could perceive?", never "is this spooky?" — tone alone never breaks the
  row.
- **`edge-distant-shape-silhouette` → approve** pins the **vantage** boundary, against
  `fail-vantage-contents-of-darkness`. A limited vantage is not a ban on mentioning
  what sits at its edge — it is a cap on resolution. Describing the shape the light
  actually delivers passes; describing what the DM knows the shape to be breaks. Where
  the page never establishes the vantage at all, the checker cannot tell and
  disapproves.

Together they say: `read-aloud-boundary` fires only on **narrated knowledge** — what
the box asserts that no one at the party's position could perceive — never on
conclusions the scene hands any observer, mood that stays in the senses, or an honest
report of a limited vantage.
