# mechanical-checker

The **deterministic tier** of the runtime output-verification loop. A model-free library a
generator runs on its *own* output to catch mechanical promise-breaks —
arithmetic, counts, format, graph properties — before it offers the output to
file. A generator cannot cheat a compiler, so no external grader is needed.

## Public interface — the sole test seam

```python
from checker import run_checks, Finding

findings = run_checks(artifact, producing_skill, checks)
```

- `run_checks(artifact: str, producing_skill: str, checks: list[str], context: dict | None = None) -> list[Finding]`
  - `artifact` — the generated output **as a string**. The generator has its
    output text in context and hands it in. `run_checks` performs **no I/O**: it
    never reads a file, never calls a model. String in, findings out.
  - `producing_skill` — `"build-session"`, the one skill whose flows run
    these checks since the generator merge. Only checks owned by this skill
    may be requested, so a caller applies **only its own skill's rubric
    subset** (spec user story 17).
  - `checks` — the rubric subset: the list of check ids to apply.
  - `context` *(optional)* — external data a roster-dependent check needs and the
    artifact text cannot carry. See **Context** below. Defaults to `None`, so
    every pre-existing 3-arg call is unchanged.
- `Finding` — a frozen dataclass with exactly four string fields:
  `check_id`, `expected`, `actual`, `output_location`. A **passing check
  contributes no finding** — the list is failures only.

## The one non-check export: `spotlight_coverage` (the spotlight-coverage pre-pass)

```python
from checker import spotlight_coverage

cov = spotlight_coverage(session_page, roster)
cov.uncovered      # roster PCs named in NO Spotlight annotation
cov.covered        # the rest
cov.beats_per_pc   # how many annotations name each PC
```

This is **not a registered check** and is deliberately unreachable through
`run_checks`. It computes build-session's **spotlight-coverage** fact — `roster −
PCs named in Spotlight annotations`, over both annotation shapes — and returns
**data, never a `Finding`**, because an uncovered PC is *legal*: "absence is the
record: a PC named nowhere on the page was planned as resting"
(`build-session/session-page-format.md` — "**Absence is the record:**"). Whether
a given absence is a deliberate rest
or a dropped beat is the judgement tier's call, and the
`build-session/spotlight-coverage` rubric row makes it; the pre-pass only
supplies the arithmetic. A PC named **anywhere** in an annotation's
value counts as covered, including as a secondary inside another PC's beat.

Contrast dungeon's **every-flagged-pc-staged**, which is the same set-cover over
`_spotlight_lines` and *is* a registered check returning a `Finding` — because an
unstaged flagged
ability inside a single site is a defect outright. Same arithmetic, opposite
default, which is exactly why one is mechanical and the other is judgement.

`run_checks` **raises `ValueError`** when a requested id is unregistered, or is
registered but owned by a different skill. Silently skipping an unknown or
mis-scoped check is the same failure class as a broken symlink — this loop
refuses to skip silently.

## The Spec axis — checks parameterised by tonight's session brief

Every other check here grades an artifact against a **library** promise. The
`build-session/brief-*` checks grade it against **tonight's contract** — the
session brief the DM agreed before the build — handed in verbatim on the context
dict beside the artifact:

```python
from checker import brief_checks, run_checks

ids = brief_checks(brief)                     # derived BEFORE drafting
run_checks(page, "build-session", ids,
           context={"brief": brief, "canon_record": record_extract})
```

`brief_checks` is the axis's **second non-check export**, and it is the reason
the derivation is safe. Ruling the brief in as a checker input left one soft
edge: a generator deriving its own acceptance criteria can derive weak ones and
nothing downstream would notice. So the derivation is not the generator's — it is
**fill-in from an enumerated field set**, done here: brief in, one check id per
**filled** field out, in template order. The generator may not drop a check for a
field the brief filled, nor add one the brief did not license
(`skills/build-session/SKILL.md` — "add one the brief did not license"). `brief_fields`
is the same parse exposed as a dict, for a caller that wants the values.

Two rules that look like implementation detail and are neither:

- **A blank field produces no row.** Every `brief-*` check returns `[]` when its
  field is absent from the brief, so default-to-disapprove is scoped to a row and
  **silence is never a constraint** — the axis grades only what the brief locks.
- **A missing brief raises.** A blank *field* is the DM saying nothing; a missing
  *brief* is a caller error, and a check asked to grade a contract it never
  received cannot reach a verdict. Same refusal
  **spotlight-annotations-name-pc** makes without a roster.
  **brief-introduced-canon** raises again without `canon_record`, because a diff
  against the campaign canon record is that row's whole definition and the
  checker has no filesystem reach into the record.

`canon_record` is a **durable record extract handed in as its own named input**,
on the party roster's precedent — not a pre-pass. It is not derivable from the
artifact, so it could never qualify under the pre-pass test, and the judgement
tier's fresh check is handed it beside the roster on the same terms
(`skills/build-session/SKILL.md` — "campaign canon record extract").

## Context — the backward-compatible extension for roster-dependent checks

Most checks are pure `str -> list[Finding]`: the artifact carries everything they
need. A few cannot see their promise in the output alone — dungeon's
**every-flagged-pc-staged** and **aimed-slots-balanced** need the **party's
flagged-ability roster**, and **default-scale** needs to know whether the DM
**overrode** the default. That external data rides in an optional `context` dict:

```python
run_checks(output, "build-session", ["build-session/default-scale",
            "build-session/every-flagged-pc-staged",
            "build-session/aimed-slots-balanced"], context={
    "roster": [
        {"pc": "Vex",  "flagged": ["Sentinel reach"]},
        {"pc": "Bram", "flagged": ["Grapple"]},
        {"pc": "Sera", "flagged": ["Counterspell"]},
    ],
    "scale_overridden": False,
})
```

The extension is **pure** — `context` is data handed in, never I/O — and
**backward-compatible**: `context` defaults to `None`, so combat's 3-arg calls
(`run_checks(output, "build-session", [...])`) are untouched.

How it flows: a check declares its shape at registration. `register_check(id,
skill)` registers a context-free `str -> list[Finding]` check (the default —
every combat check, most dungeon checks); `register_check(id, skill,
takes_context=True)` registers a `(str, dict | None) -> list[Finding]` check.
`run_checks` reads that flag and hands the context **only** to the checks that
asked for it. A context-taking check handed no roster **raises `ValueError`**
(same loud-failure philosophy as an unknown id) — it refuses to fake a verdict it
cannot reach; the generator's Definition of done always supplies the roster.
`build-session` reuses this same seam for its own cross-piece checks.

## The findings log — where telemetry actually goes

`run_checks` is pure and stays pure. The write path lives in **one separate
module**, `findings_log.py`, called by the [self-heal loop](self-heal-loop.md)
after a verdict is settled — never from inside a check:

```python
from findings_log import log_finding, log_run

log_run("build-session", checks, "mechanical")    # once per pass — unconditionally
log_finding("build-session", "build-session/skeleton-sections-in-order",
            "mechanical", "healed", 1, "the roster table")
```

It exists because "it is telemetry" used to mean "it is discarded." A check that heals on
*every* run is a generator systematically emitting the wrong thing while the
checker silently corrects it and nobody is told; the deterministic tier is the
only place with a perfect record of that and, until now, no way to report it.

- **Append-only JSONL**, one record per line, at
  `.claude/validator-findings/findings.jsonl` **relative to the working
  directory** — the campaign repo where the loop runs, never this installed skill
  folder. Tracked in git there, as a sibling of that repo's existing
  `.claude/agent-memory/`. The path is **injectable** (`path=`), so tests never
  touch the real log.
- **Two record kinds**, discriminated by the `record` field, so a reader never has
  to infer the kind from which fields are present:
  - `"finding"` — `timestamp · skill · inventory_row · tier · disposition ·
    heal_attempts · output_anchor`. `inventory_row` is **the grouping key** (a row
    id, not a line citation — a line citation rots); for a mechanical finding it is
    the `Finding`'s `check_id` verbatim.
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
  being indistinguishable from a write nobody attempted
. A bare `stderr` write
  rather than `warnings.warn`, which dedups per call site and would hide the second
  through Nth loss — the ones that say *systematic*. *Caller* mistakes — an unknown
  tier, a disposition that tier cannot produce — still raise `ValueError`.
- **The default path will not invent a campaign repo**. `.claude/` already
  existing is the premise of the placement above, so on the default path it must be
  there: absent, the loop is being driven from somewhere that is not the campaign
  repo, and the append declines and names the directory it was standing in instead
  of building the tree there and reporting success. Only the default is
  second-guessed — an explicit `path=` is taken at its word.
- **Reading is out of scope**, tracked separately as
  **Reading is a separate reporting concern:** recurrence ranking is a
  `GROUP BY inventory_row` over this file, and regression detection additionally
  joins it against *this* repo's git history for when a fix landed.

### Conformance — `run_checks` alone is not a verification run

**Calling `run_checks` is not driving the tier.** The complete run is
[`self-heal-loop.md`](self-heal-loop.md): a run record, then heal-and-recheck per
finding, then a finding record for each — healed and unhealable alike. A caller
that imports `run_checks`, reads the findings and stops has done the *checking* and
none of the *recording*, and nothing in the return value hints at it: `run_checks`
is pure by contract, so its findings are correct, the output is correct, and the
run leaves no trace. That is exactly how a full prep session's telemetry was
generated and discarded while
the absence read as *not enough runs yet*.

This note is a mitigation, **not a detection**. A run that never enters this
module cannot be caught from inside it — nothing was called that could notice. What
the run record buys is the *next* best thing: an empty log now means no pass was
ever driven, rather than meaning nothing-or-everything. Distinguishing a bypassed
pass from a genuinely clean campaign is a read-time join against the pages the
campaign filed, which belongs to the campaign's reporting workflow.

## Adding a check (the extension point)

Later extensions add the remaining rows for the fight and keyed-site procedures,
and build-session. They grow this
library by **registering more checks** — a one-function, one-registration
operation:

```python
@register_check("build-session/enemies-line-arithmetic", "build-session")
def check_enemies_line_arithmetic(artifact: str) -> list[Finding]:
    # pure str -> list[Finding]; return [] when the promise holds
    ...
```

Write a pure `str -> list[Finding]` function, decorate it with its check id and
producing skill, and `run_checks` selects it whenever a caller requests that id.
Add a labeled fixture pair under `fixtures/` (one that passes → zero findings, one
that breaks → the expected finding) and a `test_*.py` case, mirroring the
encounter-meta required-lines reference check.

## How this ships

There is **one copy**, this directory, and it sits where it ships:

```
skills/build-session/scripts/mechanical_checker/
```

It used to live under `lib/`, reached by a relative symlink from each generator's
own `scripts/`, because three generators shared it. The generator fold left
`build-session` as the only consumer, so the indirection bought nothing and the
directory moved inside the skill that runs it.

Consequences are the ones the symlink arrangement was chosen for, now had
directly: `build-session` is self-contained at the consumer (selective-install-safe),
and this copy sits inside its skill's folder, so it is covered by that skill's
folder hash and version-pinned by the stock mechanism (no separate pin). There is
no longer a dereference-on-install assumption to document, and nothing for
`lib/test_symlink_integrity.py` to resolve — that guard now covers only the
`wiki-scaffold` template assets, which are still shared this way.

## Running the tests

Flat module layout, mirroring `skills/build-session/scripts/` prior art — no
package, no `__init__.py`. pytest inserts the test file's own directory on
`sys.path`, so `from checker import ...` resolves when tests run from within this
dir; at the consumer the materialised copy sits beside the generator's other
scripts and imports the same flat way.

```
# The gate — checks over shipped content, then the checker beside build-session's
# other script tests.
python -m pytest checks/ skills/build-session/scripts/

python -m pytest skills/build-session/scripts/mechanical_checker/  # this dir only
```
