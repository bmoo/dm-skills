# judgement-checker

The **judgement tier** of the runtime output-verification back-pressure loop. Where the sibling
[`mechanical-checker`](../mechanical-checker/README.md) catches promise-breaks a
compiler can see — arithmetic, counts, format, graph properties — this tier
catches the ones only a reader can: *interpretable*, *no undefined coinage*,
*every NPC row is named*. No regex sees those, so the generator hands its finished
output to a **fresh-context checker subagent** that grades it against the skill's
own promises and returns a verdict the generator must satisfy before it may offer
to file.

This directory is **reusable prose, not code.** It is the machinery the three
generators (combat, dungeon, session) each reuse verbatim to
ship their own rubric — identical across all three generators. The one thing that
is *not* here is any generator's actual rubric: those are per-skill and are
authored **beside that skill's `SKILL.md`** as part of each generator's own build (see
[Where the real rubrics live](#where-the-real-rubrics-live) below).

## What is here

Four protocol files — the reusable machinery — plus a worked reference.

| File | What it defines |
|---|---|
| [`checker-launch-protocol.md`](checker-launch-protocol.md) | How a generator launches the fresh-context checker, and the **independence** rule that keeps it adversarial: it is handed **only** (output, rubric subset, party roster) — never the generator's reasoning. |
| [`verdict-contract.md`](verdict-contract.md) | The **two verdict channels**, both derived from Claude Code's `ReportFindings` shape: the judgement verdict (checker → loop) and the terminal mechanical-escalation (generator → DM, the sibling tier's channel, referenced not reimplemented). |
| [`rubric-format.md`](rubric-format.md) | The **beside-file rubric format** — a row's schema (inventory id · promise text · criteria · anchors · optional corpus pointer), derived from the inventory so drift is structurally impossible. |
| [`back-pressure-driver.md`](back-pressure-driver.md) | The **loop**: on `disapprove` the same generator invocation refines and re-drives — unless a finding cites a `build-session/brief-*` row, which **regenerates** the page with a **fresh builder** and a capped carry-forward; a fresh checker each round, up to 3 rounds, generator owns cross-round `outcome` memory, exhaustion → enriched file-offer. |
| [`reference/`](reference/) | A worked **format example** on inventory row **`build-session/npc-rows-named`** ("every NPC row is named") plus two fixture outputs, proving the path end to end — what an `approve` and a `disapprove` verdict look like against a real row. This is an *example of the format*, not a shippable rubric. |

Read them in that order: the launch protocol frames what the checker is, the
verdict contract fixes what it returns, the rubric format fixes what it grades
against, and the driver fixes how the generator acts on the verdict.

## Where the real rubrics live

The reference under [`reference/`](reference/) is a **format example** — one row,
worked, so the format is legible. The **real per-skill rubrics are authored beside
each generator's `SKILL.md`**, not here:

- `skills/combat-generator/` — its judgement rubric.
- `skills/dungeon-generator/` — its judgement rubric.
- `skills/build-session/` — its judgement rubrics.
  It carries **two**: `judgement-rubric.md`, the Standards axis, and
  `spec-axis-rubric.md` —
  the whole rubric of the **Spec checker**, which runs in parallel against
  tonight's brief and whose verdict is never merged into the Standards one.

Each of those rubrics is written **in the format this directory defines** and is
**derived from [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md)** —
never hand-copied — so an inventory row and its rubric row cannot drift apart. A
rubric filed in *this* shared directory instead of beside its `SKILL.md` would be
the wrong home: it would ship into all three generators and let a session page be
graded against combat's promises. Keep per-skill rubrics per-skill.

## How this ships — dereference-on-install (mirrors the mechanical tier)

There is **one canonical copy**, this directory. Each generator carries a
**relative symlink** to it inside its own `scripts/`, exactly as it carries one to
`mechanical-checker`:

```
skills/combat-generator/scripts/judgement_checker  -> ../../../lib/judgement-checker
skills/dungeon-generator/scripts/judgement_checker -> ../../../lib/judgement-checker
skills/build-session/scripts/judgement_checker     -> ../../../lib/judgement-checker
```

The `skills` CLI copies skill dirs with **dereference-on**, so each install
materialises the symlink into a **real, independent copy** inside the installed
skill. Consequences, identical to the mechanical tier's: each generator is
self-contained at the consumer (selective-install-safe — installing one generator
materialises its own real copy of this prose); and each materialised copy sits
inside its skill's folder, so it is covered by that skill's folder hash and
version-pinned by the stock mechanism (no separate pin, per spec §"Version-pinning").

The post-install dereference cannot be tested from this repo. The in-repo guard
that stands in for it is [`../test_symlink_integrity.py`](../test_symlink_integrity.py)
(one level **up**, so it does not itself ship): it resolves each `judgement_checker`
symlink, asserts it points inside the repo at exactly this directory, and asserts
**byte-identity** of the files reached *through* the symlink versus these canonical
files — the same resolve-and-compare guard first built for `mechanical_checker`,
parametrized to cover both libraries. It is the real defense against a
silently-skipped broken symlink.

## No unit-test seam — by design

Unlike the mechanical tier, this tier has **no pytest seam**. Its checks are
subjective by definition — a model reads the output and forms a judgement — so
there is no pure `str -> list[Finding]` function to assert over. Its "done" is a
coherent, reusable, structurally-correct set of authored artifacts, and its
testing seam is the golden-corpus verdict-match harness, which is **edit-time**
work for the evaluation harness,
not table-time work that runs here (spec §"Testing Decisions"). The byte-identity
guard above still runs under `python -m pytest lib/` — it guards the *ship*, not
the judgement.
