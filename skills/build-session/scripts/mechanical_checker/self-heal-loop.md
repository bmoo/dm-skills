# Self-heal loop — the deterministic refinement loop

This is how a generator acts on the [mechanical findings](README.md) `run_checks`
returns. It is the **deterministic sibling** of the judgement tier's one-round
fresh check: same place in
the run (it fires where the generator would offer to file),
same read-only law. It differs in two ways that matter — the grader is **code, not
a subagent**, so a passing check is *certain*; and it retries, up to
**3 fix attempts per check**, where the fresh check grades once.

This doc ships to every consumer inside `build-session`'s own `scripts/`, so
that skill's fight, keyed-site, and page flows drive
the identical loop over their own check subsets.

## The loop

```
checks   = [this generator's check subset]
findings = run_checks(output, "<this skill>", checks)      # before the file-offer
log_run("<this skill>", checks, "mechanical")              # the entry condition (below)

for each finding:                              # per-check, independently
    attempts = 0
    while finding is present and attempts < 3:
        attempt a fix for THIS finding          # re-derive the sum, re-add the line,
                                                #   re-source the bare name, …
        attempts += 1
        re-run run_checks for that one check id  # did this fix hold?
    # a check clean within 3 attempts healed SILENTLY — it never reaches the DM

    log_finding("<this skill>", finding.check_id, "mechanical",
                "healed" if it is now clean else "unhealable",
                attempts, finding.output_location)          # telemetry — always, both ways

# the unhealable remainder — checks still failing after 3 attempts each —
# becomes the Channel-2 terminal mechanical-escalation list (below)
```

Both log calls come from [`findings_log.py`](README.md#the-findings-log--where-telemetry-actually-goes),
which ships beside `checker.py`:

```python
from findings_log import log_finding, log_run
```

**`log_run` is not optional and is not only the denominator** — it is the record
that this tier ran at all.
It fires **once, unconditionally, before the per-finding loop**, including on the
run where every check passes and there is nothing else to write. A pass that ran
clean then leaves a run row; a pass that was never driven leaves an empty file,
and the two stop being the same thing. Skipping it — or driving `run_checks`
straight from an import and never opening this file — discards the run silently:
`run_checks` is pure by contract, so the findings look right, the output looks
right, and nothing anywhere says the record was lost. That is the failure.
records, and it cost a full prep session's telemetry.

Four properties are load-bearing and are **decisions, not tuning surfaces**:

### The generator heals; a compiler grades — so heals are certain and silent

`run_checks` is pure and model-free: string in, findings out. The generator that
produced the output is the one that fixes it — it re-derives the arithmetic,
re-adds the missing line, re-sources a bare creature name — and then **re-runs the
check** to confirm the fix held. A check that returns no finding is *certain* to
hold (a compiler does not hedge), so a healed finding is **pure telemetry**:
appended to the findings log for the maintainer's later analysis, **never surfaced
to the DM**. The DM is not asked to adjudicate arithmetic (spec user story 2).

Silent to the DM is **not** the same as discarded. A check that heals on *every*
run is a generator systematically emitting the wrong thing — the defect class no
human ever sees, and the one worth catching. The heal record is what makes
it visible, so `log_finding` fires on the healed branch exactly as it does on the
unhealable one.

### Three attempts **per check**, not per round

The ceiling is counted **per check id**, independently. Each finding gets up to
**3 fix attempts**, each followed by a re-run of *that one check*. This is the
structural difference from the judgement tier's fresh check, which grades the
*whole* output once and never re-grades. Here there is no fresh grader at all
and no cross-finding interaction to re-weigh — a finding is a single mechanical
break with a single deterministic fix, so it is healed on its own budget. One
check exhausting its three attempts does not consume another check's.

### The unhealable remainder escalates terminally — Channel 2

A check still failing after its third attempt is **unhealable by the generator**.
Those survivors become the
**terminal mechanical-escalation list**
— a **list**, one entry per surviving check, each carrying the `Finding`'s four
fields (`check_id`, `expected`, `actual`, `output_location`) **plus
`heal-attempts-tried`** (what the generator already tried, so the DM acts without
re-deriving it; spec user story 3). **No confidence field** — the deterministic
tier is certain by construction. This list is surfaced to the DM as part of the
enriched file-offer, in the same dialect as the judgement tier's surviving findings
so the DM reads one list, not two.

### Read-only — the DM's yes stays the sole file trigger

Neither `run_checks` nor this loop writes **anything the DM would read**: no page,
no edit, no file-offer of its own. `run_checks` itself remains pure — string in,
findings out, zero I/O. The one thing that touches disk is `log_finding` /
`log_run`, appending out-of-band telemetry to
[the findings log](README.md#the-findings-log--where-telemetry-actually-goes)
**after** a verdict is already settled — it alters no output, feeds nothing back
into a check, and files nothing ( narrows the guarantee to exactly this).
The whole loop runs over the
generator's **drafted output held in context**, before the file-offer forms. A run
whose checks all pass (or all heal silently) offers to file **exactly as the skill
does today** — no escalation, no trace of the loop. The DM's yes remains the only
thing that writes to a page (spec user story 8).

## Where it sits in the generator

The loop runs **before the file-offer** — after the output is drafted, before the
skill says "offer, but don't assume". It is the deterministic slice of the skill's
Definition of done. The judgement tier (a fresh-context checker subagent) is a
separate, later slice per skill; where both are wired, the deterministic self-heal
runs first (silent, in-context) and the one-round fresh check gates completion
after.
