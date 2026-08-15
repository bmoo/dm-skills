# Checker launch protocol — the fresh-context judgement checker

When a generator believes its output is done — the deterministic tier has already
run and self-healed inline (see [`../mechanical-checker`](../mechanical-checker/README.md)) —
it does **not** grade its own subjective promises. It marks its own homework, and
it marks it kindly. Instead it launches a **fresh-context checker subagent** and
lets that checker try to disprove the output. The verdict gates *completion*: the
generator cannot present its file-offer until the checker approves or the
[back-pressure loop](back-pressure-driver.md) exhausts.

## The independence rule (load-bearing)

The checker is handed **only these things**, and never the generator's reasoning:

1. **The output** — the finished artifact text the generator would file (the
   session page, the encounter block, the keyed site), exactly as it stands.
2. **The rubric subset** — the [beside-file rubric](rubric-format.md) rows for the
   **skill that produced the output**, and only that skill. The generator names
   which skill it is (spec user story 17), so a session page is graded against
   `build-session`'s promises and never against combat's.
3. **The party roster** — each PC and their flagged-ability / Spotlight profile,
   so roster-dependent promises (a flagged-ability spotlight, a level-appropriate
   budget) are actually checkable (spec user story 16). Not every row consumes it
   — a structural row like `build-session/npc-rows-named` ("is this cell a name?")
   never looks at the roster —
   but roster-dependent rows cannot be graded without it, so it is always handed
   in and the rubric row says whether it is used.
4. **A deterministic pre-pass output, where a row has one** — and only where the
   rubric row names it. This exists for the **legal-absence** rows (see
   [rubric-format.md](rubric-format.md)), where the mechanical tier can compute the
   *fact* but not the *verdict*: build-session's **`spotlight-coverage`** is handed
   `spotlight_coverage`'s uncovered set and per-PC beat share, because coverage is
   arithmetic and *"was this absence a rest or a drop?"* is not.

   **This is not a fourth channel for the generator to argue through.** A pre-pass
   output qualifies only if it is (a) produced by **model-free code** in the
   mechanical tier, (b) **derivable from the artifact alone** — the same arithmetic
   any reader could redo over the finished page — and (c) **verdict-free**: it
   carries no finding, no judgement, and no claim that the output is good. Anything
   failing all three is the generator's reasoning wearing a data structure, and is
   forbidden by the rule below. The independence property is unchanged: the checker
   still sees only what a reader could see, having merely been spared the counting.

Those four are the list for a **Standards** checker — the axis that grades an output
against library promises — and they are unchanged. The **Spec axis** below is a
*different checker* with two further inputs of its own; nothing about it widens this
list.

**Never handed in: the generator's own reasoning** — its chain of thought, its
scratch work, its intermediate drafts, its justification for the choices it made,
the mechanical tier's heal telemetry, or any note that argues the output is good.
That withholding is the whole point. A checker that can see *why* the generator
did what it did will rationalise alongside it; a checker that sees only the
artifact a reader would see grades what a reader would get. Independence is what
makes the grade adversarial — it is a decision, not a tuning surface.

## The Spec axis — a second checker, in parallel, verdicts unmerged

Everything above is the **Standards** axis: does the output follow the promises the
library documents? A generator handed a **session brief** — the DM's contract of
hard-to-reverse decisions for tonight, agreed before the build — is answerable to a
second question: does the output do what *that* asked for? That is the **Spec** axis,
and it runs as its **own checker, launched in parallel with the Standards checkers,
with the two verdicts left unmerged**.

**Parallel and unmerged is about contamination, not cost.** The two axes grade against
different sources of truth — a rubric identical on every run, and a contract different
every night — and a single agent holding both can trade them off (*"the brief asked
for this, so the plain-language row can slide"*). Neither axis may buy the other off.
Keeping the verdicts apart also preserves at the report **which axis failed**: a broken
library promise and a broken contract are different problems.

**The Standards checkers are untouched and see no brief.** Nothing here changes the
shipped path.

### The Spec checker's two further inputs

Both are the same *kind* of input as the party roster — durable, authored by somebody
other than the generator, and carrying none of the generator's defence of its output:

5. **The brief**, handed as a **tracker issue URL, not text** — so the checker reads
   the artifact the DM actually agreed to, and the generator cannot paraphrase the
   contract in its own favour en route — and **body only, comments excluded**. Pulling
   the comment thread (the obvious `gh issue view --comments`) would drag the whole
   negotiation transcript in, and with it reasoning, by the back door. Amendments go
   back into the body; the read stays dumb. There is **no state field and no gate**: a
   brief that exists is a brief in force, and the axis runs against any brief it is
   handed.
6. **The campaign canon record extract** — a durable extract of what the record already
   holds, handed in as its own named input. The rows that grade a claim *about the
   campaign* rather than a property of the text need it, and the checker has **no
   filesystem reach into the campaign record**; input 3 is the only precedent for
   getting past that wall, and this rides on it.

**Why admitting the brief does not soften the grade.** The operative withholding rule
is the one written in bold above — ***never hand it your own reasoning*** — and *"a
checker that sees only what a reader sees"* is that rule's **rationale**, not a second
independent constraint. The admissibility test the library already applies when it
hands over the pre-pass is *does this input carry the generator's defence of its own
output?* A brief passes that test more cleanly than the pre-pass does: it is authored
by the **counterparty**, agreed **before** generation began, and cannot have been
shaped by the output it grades. It is not the generator's case for its page; it is
what the page is answerable to. It is also the **only channel for authorised
deviation** — anything needing special treatment belongs in the contract, where the DM
signs it, never supplied by the generator at grading time.

### One row per filled field, and none where the brief is silent

The axis grades **one row per brief field**, and a row whose field the brief left blank
**does not exist** — the same shape as a rubric subset that runs only over the artifact
it owns. Per-*constraint* rows were never available: every finding cites a
library-owned inventory id as its promise-pointer, and a night's brief text can never
carry one.

**Default-to-disapprove is unchanged, but it is scoped to a row.** *Cannot tell whether
the page enacts the stated premise* → disapprove, correctly: a written constraint went
unverified. *The brief says nothing about the tavern's name* → **no row, no finding, no
disapprove**. **Silence is never a constraint**, so the default never punishes the
generator for inventing exactly what it was told to invent.

### Two tiers

The brief's **mechanically-checkable** fields do not wait for this checker. They become
executable checks **derived from the named fields before drafting** and run red-green
during the build, in the [mechanical tier](../mechanical-checker/README.md) — which is
what closes the missing per-artifact test half, since the brief *is* the per-session
acceptance criteria. Only the brief's **rubric-graded** fields reach the Spec checker
here. The derivation is fill-in from an enumerated field set, never the generator's
judgement about what is worth checking: it may not drop a check for a field the brief
filled, nor add one the brief did not license.

### No waivers, and therefore no validation orchestrator

Nothing in either axis exempts a row. Waivers are what would create a reconciliation
problem — if the *builder* decided which findings its brief excused, the generator
would be grading its own homework — so removing them leaves that layer no job, and no
orchestrator is specified. If waivers ever arrive they must exempt by **naming the
inventory row id**, keeping reconciliation a set operation rather than an agent judging
which findings to suppress.

## A genuinely fresh context

The checker is a **separate agent run** — a fresh Claude, described
tool-agnostically because the launch mechanism differs by host (a subagent, a
nested `claude -p`, a Task tool — whatever the runtime provides). Two properties
are required of whatever mechanism is used:

- **Fresh context.** The checker starts from nothing but the inputs above.
  It does not share the generator's conversation, memory, or context window. If
  the host cannot give a genuinely clean context, the independence is not real and
  the grade is worthless.
- **Read-only over the artifact.** The checker **never writes what anyone reads** —
  no page, no edit, no change to the output it is grading. It reads the output and
  returns a verdict. The DM's yes remains the sole trigger that files anything
  (spec §"Integration into the file-gate"). Its **one** permitted write is the
  out-of-band telemetry append below, to a single fixed path that is not the
  output and is never read back into a verdict.

Each round of the loop launches a **new** fresh checker (see
[`back-pressure-driver.md`](back-pressure-driver.md)) — never the same instance
re-consulted — so independence is preserved round to round and no checker
accumulates sympathy for the generator's revisions.

## The checker's stance: adversarial, disapprove-on-uncertainty

The checker's job is to **try to disprove the output** against its rubric, not to
confirm it. Its default when it cannot tell is **disapprove** — a borderline
output gets a second look rather than a rubber stamp (spec user story 5). This is
encoded in the verdict itself: there is no "uncertain" verdict to hide in (see
[`verdict-contract.md`](verdict-contract.md)). If the checker is unsure whether the
Bartender's row counts as *named*, it disapproves and says why, and the generator
gets a chance to remove the doubt.

## What the checker returns

A single [judgement verdict](verdict-contract.md): a top-level plain
`approve | disapprove`, with advisory findings beneath it — each finding pointing
at the **inventory row** it broke and **where in the output** it broke, and
**carrying no fix**. The checker names *which* promise broke; the generator owns
*how* to fix it (spec user story 19). The exact shape is fixed in
[`verdict-contract.md`](verdict-contract.md).

## Logging the pass and its findings — the checker's one write

After returning its verdict, the checker **records the pass it just ran** in the
durable findings log: one
`"run"` record for the pass, then one `"finding"` record per finding it raised.
This is instructed here and **nowhere else** — no generator `SKILL.md` carries it
— because a rule added to a skill's prose while nothing checks it is the exact
failure class this telemetry exists to expose, and because the tier being
critiqued should not control its own record.

**The run record is not optional, and a pass with nothing to raise still writes
one**. Write it **first**,
on **every** pass, before any finding. It is what makes an approving pass
distinguishable from a pass nobody ran: without it, a checker that graded twelve
rows and found them all sound leaves behind exactly what a bypassed tier leaves,
which is nothing. A whole session's judgement telemetry was lost that way and read
afterwards as a clean run.

**Where to write.** Append one line of JSON per record to
`.claude/validator-findings/findings.jsonl`, **relative to the working
directory** — the campaign repo, which is what a launched checker can rely on
knowing. Create the `validator-findings/` directory if it is absent. **Do not
create `.claude/` itself**: if it is not already there you are not in the campaign
repo, and building the tree where you stand writes the session's telemetry to a
path nobody reads. Say so in your verdict instead — a stated gap is information, a
silently misplaced log is the same lost-telemetry failure with a different cause. (This
mirrors what `findings_log.py` does on its default path, which declines the same
way and names the directory it was standing in.) Deliberately *not* an import of
the deterministic tier's `findings_log.py`: that module materialises inside the
*generator's* installed skill folder, a location a fresh subagent has no way to
resolve and is handed nothing to find. (A checker that has been given a reachable
path to it should prefer calling `log_run` and `log_finding` — same schema, one
fewer place to drift.)

**What to write** — the same two record kinds
[`findings_log.py`](../mechanical-checker/README.md#the-findings-log--where-telemetry-actually-goes)
writes, which is their canonical definition. One `"run"` object for the pass:

```json
{"record": "run", "timestamp": "<UTC ISO-8601>",
 "skill": "<the skill that produced the output>", "tier": "judgement",
 "checks_evaluated": ["<each rubric row id you graded>"]}
```

then one `"finding"` object per finding:

```json
{"record": "finding", "timestamp": "<UTC ISO-8601>",
 "skill": "<the skill that produced the output>",
 "inventory_row": "<the row this finding cites>", "tier": "judgement",
 "disposition": "raised", "heal_attempts": null,
 "output_anchor": "<where in the output it broke>"}
```

`tier` is `"judgement"` on both, which is what keeps this pass's denominator from
being mistaken for the deterministic tier's over the same skill. `checks_evaluated`
is **the list of rubric row ids, not a count**, for the reason the mechanical tier
records it that way: a row's failure rate needs the number of passes where *that
row* was in force, and a pass total would inflate the rate of rows that are rarely
in scope and deflate the rest.

Every field is derivable from what the checker already holds: `skill` is input 2's
named skill (user story 17), `checks_evaluated` is the rubric subset it was handed,
and `inventory_row` and `output_anchor` are the finding's own promise-pointer and
anchor. Logging adds **no new input** to the independence rule's list.

If the append fails — no write permission, a full disk — **return the verdict
anyway**. Telemetry is out-of-band; a lost line beats a dead prep session.

Three things about this write:

- **Every finding, every round — and one run record per round.** A fresh checker
  runs per round, so each round appends its own records, its own run record
  included: the round is the pass. Whether a finding was **resolved** (raised in round 1,
  absent in round 2) or **survived to the DM** (present in the final round) is
  *inferred at read time* from that sequence — observed behaviour, rather than the
  generator's own account of whether it fixed something.
- **No round number, and no `heal_attempts`.** The checker is stateless across
  rounds by design; being told which round it is would tell it that prior fix
  attempts happened, which is precisely what the independence rule withholds.
  Timestamps recover the **order** of records — but not, on their own, the run
  boundaries: with no `run_id` (the schema deliberately defers it), two `raised` records for the same
  row are indistinguishable between rounds 1 and 2 of one run and two separate runs
  of the same skill. Clustering by timestamp is the accepted proxy; recorded here
  so a later reporting pass does not rediscover it.
- **Nothing is filtered.** Log every finding, including ones that look minor.
  Weight is a property of the *group* — one instance of a row carries none, forty
  are a defect class — and filtering at emit time is the mechanism by which the
  silent recurring class stays invisible.

Appending is not a breach of independence: it happens **after** the verdict is
formed, feeds nothing back into it, and the log is never an input to a checker.

## How a generator wires this in

This directory supplies the machinery but does not wire the loop into a
generator. When a later extension wires it, the SKILL.md step reads like the
skill's other beside-file loads (cf. combat-generator's "load the spotlight
skill's `doctrine.md`"): at the point the generator would offer to file, it
instead

1. loads its **own** beside-`SKILL.md` rubric (the rows it authored in the
   [rubric format](rubric-format.md)),
2. launches a fresh checker per this protocol, handing it (output, that rubric
   subset, roster, and any pre-pass output its rows name),
3. runs the [back-pressure driver](back-pressure-driver.md) on the verdict.
