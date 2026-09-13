# mechanical-checker

The **deterministic tier** of the runtime output-verification loop. A model-free library a
generator runs on its *own* output to catch mechanical promise-breaks —
arithmetic, counts, format — before it offers the output to file. A generator
cannot cheat a compiler, so no external grader is needed.

## What it checks

This checker verifies the mechanical parts of combat-generator's output — the
`> [!encounter-meta]` block: its structure, XP and budget arithmetic,
stat-block references, spotlight fields, encounter constraints, and the
floating form's role-terrain line.

Each rule has a stable `<skill>/<rule>` check id, such as
`combat-generator/enemies-line-arithmetic`. The decorated function in
[`checker.py`](checker.py) is the rule's executable specification; a failure is
reported with that id in `Finding.check_id`. The checker deliberately does not
make judgement calls: subjective completion criteria are evaluated by the
separate fresh check described in the shared verification protocol
(`lib/verification.md`).

## Public interface — the sole test seam

```python
from checker import run_checks, Finding

findings = run_checks(artifact, producing_skill, checks)
```

- `run_checks(artifact: str, producing_skill: str, checks: list[str], context: dict | None = None) -> list[Finding]`
  - `artifact` — the generated output **as a string**. The generator has its
    output text in context and hands it in. `run_checks` performs **no I/O**: it
    never reads a file, never calls a model. String in, findings out.
  - `producing_skill` — the skill that produced the artifact
    (`"combat-generator"`). Only checks owned by this skill may be requested,
    so a caller applies **only its own skill's check subset**.
  - `checks` — the list of check ids to apply.
  - `context` *(optional)* — external data a check needs and the artifact
    text cannot carry, handed only to checks registered with
    `takes_context=True`. No shipped check takes context today; the seam is
    pure (data in, never I/O) and defaults to `None`, so every 3-arg call is
    unchanged.
- `Finding` — a frozen dataclass with exactly four string fields:
  `check_id`, `expected`, `actual`, `output_location`. A **passing check
  contributes no finding** — the list is failures only.

`run_checks` **raises `ValueError`** when a requested id is unregistered, or is
registered but owned by a different skill. Silently skipping an unknown or
mis-scoped check is the same failure class as a broken symlink — this loop
refuses to skip silently. A context-taking check run without the context it
needs raises the same way: it refuses to fake a verdict it cannot reach.

## The findings log — where telemetry actually goes

`run_checks` is pure and stays pure. The write path lives in **one separate
module**, `findings_log.py`, called by the [self-heal loop](self-heal-loop.md)
after a verdict is settled — never from inside a check:

```python
from findings_log import log_finding, log_run

log_run("combat-generator", checks, "mechanical")    # once per pass — unconditionally
log_finding("combat-generator", "combat-generator/enemies-line-arithmetic",
            "mechanical", "healed", 1, "the Enemies line")
```

A check that heals on *every* run is a generator systematically emitting the
wrong thing while the checker silently corrects it and nobody is told; the
deterministic tier is the only place with a perfect record of that, and this
log is where it reports it.

- **Append-only JSONL**, one record per line, at
  `.claude/validator-findings/findings.jsonl` **relative to the working
  directory** — the campaign repo where the loop runs, never this installed skill
  folder. Tracked in git there, as a sibling of that repo's existing
  `.claude/agent-memory/`. The path is **injectable** (`path=`), so tests never
  touch the real log.
- **Two record kinds**, discriminated by the `record` field, so a reader never has
  to infer the kind from which fields are present:
  - `"finding"` — `timestamp · skill · inventory_row · tier · disposition ·
    heal_attempts · output_anchor`. The compatibility-named `inventory_row` field
    is **the grouping key**: it holds a stable check id, not a line citation; for
    a mechanical finding it is the `Finding`'s `check_id` verbatim.
  - `"run"` — `timestamp · skill · tier · checks_evaluated`, supplying **the
    denominator** and **the record that a tier ran at all**.
    `checks_evaluated` is the **list** of check ids, not a count:
    a run-level total would inflate the failure rate of conditional checks and
    deflate the unconditional ones. `tier` is there because **both** tiers write
    one through `log_run` — and a
    denominator attributed to the wrong tier is worse than none. A judgement
    run row also carries its `verdict` (`approve` / `disapprove`).
- **All three channels are logged** — healed mechanical, terminal mechanical
  escalation, and the fresh check's judgement
  findings, each of those carrying its required `quoted_span` and `reason`. **Nothing is filtered at write time**: weight is a property of the
  *group*, not the finding. One healed arithmetic slip carries none; forty are the
  top-ranked defect class.
- **Stdlib only** (`json`, `sys`, `datetime`, `pathlib`) — the shipped library takes no
  dependency, matching `checker.py`.
- **I/O failure is swallowed but announced**, deliberately against this repo's
  loud-failure norm. That norm protects verification correctness; this is
  out-of-band telemetry firing at the table mid-prep, and a lost line beats a dead
  prep session. So the write never aborts the loop — the return value reports
  whether it landed — but every failure also **says so on `stderr`, carrying the
  record it lost**, so the line can be re-appended by hand and a lost write stops
  being indistinguishable from a write nobody attempted. A bare `stderr` write
  rather than `warnings.warn`, which dedups per call site and would hide the second
  through Nth loss — the ones that say *systematic*. *Caller* mistakes — an unknown
  tier, a disposition that tier cannot produce — still raise `ValueError`.
- **The default path will not invent a campaign repo**. `.claude/` already
  existing is the premise of the placement above, so on the default path it must be
  there: absent, the loop is being driven from somewhere that is not the campaign
  repo, and the append declines and names the directory it was standing in instead
  of building the tree there and reporting success. Only the default is
  second-guessed — an explicit `path=` is taken at its word.
- **Reading is out of scope.** Recurrence ranking is a
  `GROUP BY inventory_row` over this file, and regression detection additionally
  joins it against *this* repo's git history for when a fix landed.

### Conformance — `run_checks` alone is not a verification run

**Calling `run_checks` is not driving the tier.** The complete run is
[`self-heal-loop.md`](self-heal-loop.md): a run record, then heal-and-recheck per
finding, then a finding record for each — healed and unhealable alike. A caller
that imports `run_checks`, reads the findings and stops has done the *checking* and
none of the *recording*, and nothing in the return value hints at it: `run_checks`
is pure by contract, so its findings are correct, the output is correct, and the
run leaves no trace.

This note is a mitigation, **not a detection**. A run that never enters this
module cannot be caught from inside it — nothing was called that could notice. What
the run record buys is the *next* best thing: an empty log now means no pass was
ever driven, rather than meaning nothing-or-everything. Distinguishing a bypassed
pass from a genuinely clean campaign is a read-time join against the pages the
campaign filed, which belongs to the campaign's reporting workflow.

## Adding a check (the extension point)

Add a rule by extending this library with **one registration and one fixture
pair**:

```python
@register_check("combat-generator/enemies-line-arithmetic", "combat-generator")
def check_enemies_line_arithmetic(artifact: str) -> list[Finding]:
    # pure str -> list[Finding]; return [] when the promise holds
    ...
```

Write a pure `str -> list[Finding]` function, decorate it with a stable check id
and producing skill, and `run_checks` selects it whenever a caller requests that
id. Add a labeled fixture pair under `fixtures/` (one that passes → zero
findings, one that breaks → the expected finding) and a `test_*.py` case,
mirroring the encounter-meta required-lines reference check. If the rule needs
external input, register it with `takes_context=True`, document the required
context here, and test the missing-context failure.

## How this ships

There is **one copy**, this directory:

```
lib/mechanical-checker/
```

It materialises into combat-generator by a relative symlink from that skill's
own `scripts/` (`skills/combat-generator/scripts/mechanical_checker`) — the same
arrangement as `lib/rules-sourcing.md` and `lib/srd/`. At install time the
symlink dereferences, so the installed skill carries its own materialised copy
and stays selective-install-safe.

## Running the tests

Flat module layout — no package, no `__init__.py`. pytest inserts the test
file's own directory on `sys.path`, so `from checker import ...` resolves when
tests run from within this dir; at the consumer the materialised copy sits
beside the skill's other scripts and imports the same flat way.

```
# The gate — checks over shipped content, this checker, then the script
# tests that ship with prep-session and review-rewards (pytest.ini keeps the
# skill-side symlink from being collected a second time).
python -m pytest checks/ lib/mechanical-checker skills/prep-session/scripts/ skills/review-rewards/scripts/

python -m pytest lib/mechanical-checker/  # this dir only
```
