# dnd-skills

The ubiquitous language of this skills library: the terms its skills, its
verification chain, and its planning artifacts use with a fixed meaning.

This is a **glossary and nothing else** — no specs, no decisions, no
implementation notes. A term earns a place here only if it means something
particular *inside this library*; general software vocabulary does not belong
even where the repo leans on it heavily.

It is deliberately short. The bar is **load-bearing**: a term stays because
skill text, the verification chain, or `lib/` actually uses it with this
meaning. Vocabulary minted for work that has not landed yet belongs in that
work's issue until the skills speak it — a glossary of terms nothing says is
noise, and it hides the dozen that matter.

Where two words are in live use for one concept, the `_Avoid_` line names the
loser. Several of those entries record a real collision found in shipped skill
text, not a stylistic preference.

## The verification chain

**Promise**:
A commitment a skill's text makes about its own output, stated so that something
other than its author can check it.
_Avoid_: assertion, guarantee, requirement

**Inventory**:
`docs/eval-assertion-inventory.md` — the master list of every checkable promise
the library makes. Every other verification artifact is derived from it.
_Avoid_: assertion list, the spec, the manifest

**Row**:
One promise in the inventory, carrying a stable id (`build-session/npc-rows-named`)
that outlives any rewording of the promise text.
_Avoid_: entry, check id, rule

**Anchor phrase**:
The verbatim quotation a citation uses to point at where a promise lives, in place
of a line number. A citation names a file plus a phrase that still appears in it.
_Avoid_: line reference, pointer, quote

**Derived artifact**:
Anything generated from the inventory rather than authored directly — a
`judgement-rubric.md`, a corpus verdict-map, `checker.py` and its fixtures. Never
hand-edited out of sync with its inventory row.
_Avoid_: generated file, downstream artifact

**Check method**:
How a row is settled: `regex`, `parse`, `graph`, or `judgement`. (Two further
classes, `trace` and `diff`, were retired without ever executing — see the
inventory's "Deliberately removed" note.)
The first three are code, run by the deterministic tier (a **mechanical check**);
a **judgement row** is one no code can settle, graded by a checker reading the
artifact.
_Avoid_: check type, validator kind, subjective check

## The judgement loop

**Judgement pass**:
The stage where a drafted artifact is handed to a checker that tries to disprove
it. It gates completion, never filing.
_Avoid_: review pass, validation pass, QA

**Fresh checker**:
A genuinely new-context, read-only grader launched per round, handed the artifact,
its rubric subset, and nothing that would let it grade the generator's reasoning
instead of the output. Its counterpart is the fresh builder — a new-context
generator that rebuilds an artifact without inheriting the draft it replaces.
_Avoid_: validator, reviewer, judge

**Finding**:
One break a checker reports: where in the artifact the break sits, and the
inventory row id it cites — the **promise-pointer**, which *is* the instruction
to the generator, naming which promise broke and never how to repair it.
_Avoid_: issue, error, defect report, rule reference

**Verdict**:
A checker's plain `approve` or `disapprove`. Its default when it cannot tell is
`disapprove`.
_Avoid_: result, score, grade

**Self-heal**:
The deterministic tier's own repair attempts against mechanical failures, before
any checker runs.
_Avoid_: auto-fix, retry

**Back-pressure**:
The loop from `disapprove` to a revised artifact to a re-grade by a *new* checker,
capped at three rounds. A broken library promise is answered by revising the
artifact in place; a broken contract, which revision cannot repair, is answered by
discarding it and rebuilding from scratch. Round three still returning `disapprove`
stops the loop and surfaces the surviving findings to the DM rather than spinning
or silently filing.
_Avoid_: feedback loop, retry loop, iteration
