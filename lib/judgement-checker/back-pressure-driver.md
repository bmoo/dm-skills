# Back-pressure driver — the refinement loop

This is how the generator acts on the [judgement verdict](verdict-contract.md). It
runs at the point the generator would offer to file, and it **gates completion**:
the file-offer does not form until this loop reaches `approve` or exhausts.

## The loop

```
round = 1
launch a FRESH checker (output, own-skill rubric subset, roster)   # checker-launch-protocol.md
verdict = its approve | disapprove

while verdict == disapprove and round <= 3:
    if any of this round's findings cites a `build-session/brief-*` row:
        launch a FRESH BUILDER to regenerate the page    # carry-forward only, never the page
    else:
        # the ranked findings + their promise-pointers ARE the refinement instruction
        for each finding, in rank order (most-severe first):
            attempt to refine the output so that finding's promise holds
    record each finding's outcome in the cross-round ledger
    round += 1
    if round <= 3:
        launch a NEW fresh checker on the revised output       # fresh each round
        verdict = its approve | disapprove

# exit: either verdict == approve, or round exhausted at 3
```

Five properties are load-bearing and are **decisions, not tuning surfaces**:

### The same invocation refines — a contract finding regenerates instead

On `disapprove` the **same generator invocation** refines and re-drives, and there
is **no orchestrator** — the generator that produced the output is the one that
revises it. The ranked findings and their promise-pointers **are** the refinement
instruction: each finding names a broken inventory row and where it broke, and the
generator, which owns *how* to fix it, does so. This is why the checker carries **no
concrete fix** — the fix is the generator's job, and it has all the context to do it.

**One class of finding is exempt, and it does not refine at all.** A finding whose
promise-pointer is a **`build-session/brief-*` row** cites tonight's brief — the DM's
contract of decisions that are hard to reverse by definition, so being wrong about
one means *throwing the page away instead of editing it*. Refinement cannot repair
that, and rounds spent politely rewording around a constraint the page cannot satisfy
are rounds wasted. That round **regenerates**: the page is rebuilt by a **fresh
builder** (below) rather than edited.

The trigger is a **prefix test over the round's findings, and nothing cleverer** —
does any promise-pointer start `build-session/brief-`. Two consequences follow from
its dumbness, both wanted:

- **A mixed round regenerates.** A rebuild subsumes a repair, so a round carrying
  both a Standards finding and a contract finding takes this branch, and the
  Standards findings ride into the new build with it.
- **A Standards-only round refines, exactly as before.** `combat-generator` and
  `dungeon-generator` drive this same loop and are handed no brief, so no finding of
  theirs can carry that prefix and the branch is unreachable for them.

*The round's findings* means the union across every checker launched that round —
the Standards axis and the
[Spec axis](checker-launch-protocol.md#the-spec-axis--a-second-checker-in-parallel-verdicts-unmerged),
whose verdicts stay unmerged — since a contract finding can only arrive from the
second.

### A fresh builder regenerates, carrying a capped carry-forward

Regeneration gets a **new agent**. The same invocation rebuilding would hold the
discarded page in its context, and an agent holding the page it just wrote will
reconstruct it — that page is the most available thing it has — so the result would
be a re-skin, not a regeneration. This is the property the checker has always had,
applied to the builder.

**No new layer.** The driver already spawns a fresh checker every round; spawning a
fresh **builder** is the same driver doing one more thing it already does. The
original invocation stays what it was — the thin thing holding state across rounds —
and there is still no orchestrator above it.

**What is discarded is the page, not the run.** The fresh builder rebuilds the
artifact the contract finding is against. Everything the run settled before drafting
stands: the brief, the roster, the campaign record extract, the round budget, and the
carry-forward. The rebuilt page re-enters where any draft does — the deterministic
self-check, then a new fresh checker. **A regeneration spends a round** like any
other: three rounds is the loop's budget, not three per branch, and a fresh builder
is not a fresh budget.

**The carry-forward** is the handoff to each fresh builder — the cross-round ledger's
contents and nothing else — **capped at one line per finding per round**, so a third
builder inherits a handful of lines rather than an essay. Each line carries these
three and no fourth:

- the **row that broke** — its inventory id, plus the constraint text from the
  brief, so the line names the promise as the DM wrote it and not only by id;
- **what the attempt did**, one factual line, no rationale (*"routed all three exits
  into the catacombs"*);
- **what not to retry**, so the budget is not spent twice on the same approach.

**It never includes the previous page**, not even in summary. The failed approach is
worth naming; the artifact it produced is the single largest pollution risk.

**It goes to the builder, never to the checker.** The fresh checker's inputs are
exactly the list in [`checker-launch-protocol.md`](checker-launch-protocol.md) and
this is not among them. A checker handed the record of what the generator tried is a
checker reading the generator's reasoning, which is the one thing the independence
rule exists to withhold.

### A fresh checker each round — independence preserved

Every round launches a **new** fresh-context checker on the revised output, never
the same checker re-consulted. A checker that remembered the previous round would
accumulate sympathy for the generator's revisions and stop being adversarial. Fresh
each round means each verdict is formed from the artifact alone, exactly as the
first was (see [`checker-launch-protocol.md`](checker-launch-protocol.md)).

### The generator owns cross-round memory (the `outcome` ledger)

The checker is stateless across rounds — it emits findings with `outcome` unset,
because it does not know what happened before. The **generator** owns the
cross-round memory: after each round it marks every finding's
[`outcome`](verdict-contract.md#outcome--owned-by-the-generator-never-the-checker)
—

- **`fixed`** — the generator changed the output so the promise now holds;
- **`skipped`** — the generator chose not to act on it this round;
- **`no_change_needed`** — the generator judges the finding a false alarm and left
  the output as-is.

This ledger is the generator's alone. It travels with the **original invocation**
across rounds, never into a checker's context — that separation is what lets a fresh
checker each round coexist with memory of what has been tried. A **fresh builder**
does not inherit it either; it receives only the capped carry-forward drawn from it,
and on a regeneration round the ledger records what the rebuild attempted, which is
where that entry's one factual line comes from. A finding a fresh checker raises
again after the generator marked it `no_change_needed` is a genuine standoff, and
it will survive to the offer.

### Up to 3 rounds, then exhaust

The loop runs at most **3 rounds**. If round 3's checker still returns
`disapprove`, the loop **exhausts** — it does not spin, does not escalate to a
fourth round, and does not silently file. The generator is the fallback's fallback;
the DM is the fallback (spec user story 6).

## On exhaustion — the enriched file-offer

Enrichment fires on **exhaustion** — a final `disapprove` after round 3, i.e. a
fresh adversarial checker that *still* sees at least one broken promise. Those
**surviving findings become the enriched file-offer**: the generator folds them
into the same file-offer it already makes — *"N issues I couldn't resolve — file
anyway, or take over."* (spec user story 7). The surviving findings are available to
the offer carrying their promise-pointers, output anchors, and the generator's
outcome ledger, so the DM sees which promises are unresolved, where, and what was
tried.

**A contract finding is no different at the offer.** Three rebuilds is the machine
**insisting**; it never becomes a veto. A surviving `build-session/brief-*` finding
folds into that same single offer — the DM is the counterparty to their own contract
and is entitled to rule on it, and a hard gate would let one false negative on round
three cost a session that was needed that evening.

A terminal **`approve` never enriches.** A fresh checker that approves returned an
**empty findings list** — it could not disprove the output — so there is nothing to
surface (`approve` with a non-empty list is a contradiction, treated as
`disapprove`; see [`verdict-contract.md`](verdict-contract.md#top-level-a-plain-approve--disapprove-an-addition)).
Any run that ends on `approve` therefore produces the offer **indistinguishable
from today's**. A finding the generator marked `skipped` or `no_change_needed`
enriches the offer only by *surviving to a final `disapprove`* — a fresh checker
raising it again is the standoff that carries it through; a fresh checker no longer
raising it means the output now holds and it is gone.

Two rules hold here without exception:

- **Enrich, don't gate.** Judgement gates *completion* — the offer does not *form*
  until the loop exhausts — but once it forms it is the **same offer** the skill
  always makes, only enriched. It is **not** a second gate the DM must clear.
- **The DM's yes stays the sole file trigger; the verifier is read-only over the
  artifact.** Neither the checker nor the driver writes anything a reader sees —
  no page, no edit, no change to the output. The one exception is the checker's
  out-of-band [telemetry append](checker-launch-protocol.md#logging-the-pass-and-its-findings--the-checkers-one-write)
  after its verdict is formed: it alters no output, files nothing, and is
  never read back into a verdict. An output with
  **no findings** (an `approve` on round 1 with an empty list) produces an offer
  **indistinguishable from today's** — no enrichment, no trace of the loop.

The surviving-findings hand-off shares its vocabulary with the sibling tier's
[terminal mechanical-escalation](verdict-contract.md#channel-2--terminal-mechanical-escalation-generator--dm):
at the exhausted offer the DM reads one enriched list — unhealed mechanical breaks
and unresolved judgement findings together — in one dialect, not two.
