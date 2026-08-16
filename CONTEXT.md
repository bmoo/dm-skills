# dm-skills

The ubiquitous language of this skills library: the terms its skills and
planning artifacts use with a fixed meaning.

This is a **glossary and nothing else** — no specs, no decisions, no
implementation notes. A term earns a place here only if it means something
particular *inside this library*; general software vocabulary does not belong
even where the repo leans on it heavily.

It is deliberately short. The bar is **load-bearing**: a term stays because
skill text or `lib/` actually uses it with this
meaning. Vocabulary minted for work that has not landed yet belongs in that
work's issue until the skills speak it — a glossary of terms nothing says is
noise, and it hides the dozen that matter.

Where two words are in live use for one concept, the `_Avoid_` line names the
loser. Several of those entries record a real collision found in shipped skill
text, not a stylistic preference.

## Verification

**Promise**:
A commitment a skill's text makes about its own output, stated so that something
other than its author can check it.
_Avoid_: assertion, guarantee, requirement

**Row**:
One registered check or completion criterion, carrying a stable id
(`build-session/npc-rows-named`) that outlives any rewording of its promise.
_Avoid_: entry, check id, rule

**Completion criterion**:
A subjective bar written in a skill's own text — where the promise is
authored — that the generator reads while building and the fresh check grades
after. Since the verification-chain cut this is where every judgement row's
criterion lives; there is no separate rubric.
_Avoid_: rubric row, quality bar, acceptance criterion

**Check method**:
How a row is settled: `regex`, `parse`, `graph`, or `judgement`.
The first three are code, run by the deterministic tier (a **mechanical check**);
a **judgement row** is one no code can settle, graded by the fresh check reading
the artifact against the skill text's completion criteria.
_Avoid_: check type, validator kind, subjective check

## The fresh check

**Fresh check**:
The one-round stage where a drafted artifact is handed to a fresh checker that
tries to disprove it against the skill text's completion criteria. It gates
completion, never filing; on `disapprove` the generator makes one fix pass and
does not re-grade.
_Avoid_: judgement pass, review pass, validation pass, QA

**Fresh checker**:
A genuinely new-context, read-only grader, handed the artifact, the criteria
it grades against, and nothing that would let it grade the generator's
reasoning instead of the output.
_Avoid_: validator, reviewer, judge

**Finding**:
One break a checker reports: where in the artifact the break sits, the stable
check id it cites — the **promise-pointer**, which *is* the instruction
to the generator, naming which promise broke and never how to repair it — and,
for a judgement finding, the **quoted span** it fired on plus a one-line
reason.
_Avoid_: issue, error, defect report, rule reference

**Verdict**:
A checker's plain `approve` or `disapprove`. Its default when it cannot tell is
`disapprove`.
_Avoid_: result, score, grade

**Self-heal**:
The deterministic tier's own repair attempts against mechanical failures, before
any checker runs.
_Avoid_: auto-fix, retry

**Standing feedback**:
The one campaign-owned, DM-authored file (`.claude/standing-feedback.md` at the
campaign repo root) of accumulated corrections a generator loads if present.
Where the DM's judgement accumulates now that corpora are retired.
_Avoid_: memory file, feedback log
