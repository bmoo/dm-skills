# Definition of done — the shared verification protocol

The two-part gate every build-session procedure runs over its drafted
artifact — the session page, a fight's encounter block, a keyed-site
package — before its report or offer forms. The caller's own text names
what varies: the check ids and their context, the criteria and the
inputs the checker gets, and which promises arrived already checked from
a delegated build (its *inheritance split*). Everything below is
invariant.

Checking is not filing, in both parts: the checks run over the artifact
you hold in context, and the DM's yes stays the sole trigger that writes
to a page.

## Part 1 — the mechanical self-check

Run the caller's check-id list through `run_checks` — the runnable
checks live at [`scripts/mechanical_checker`](scripts/mechanical_checker),
and each id's promise is documented there. A facet not in the caller's
fixed shapes is invisible to its check — compile to shape before
running.

- **Self-heal, silently.** Drive each finding through the shared
  [`self-heal-loop.md`](scripts/mechanical_checker/self-heal-loop.md) —
  re-derive the failing fact — up to **three attempts per check**,
  re-running that check after each. A finding that heals is telemetry
  and never reaches the DM: this is arithmetic you fix, not arithmetic
  you ask the DM to adjudicate.
- **Escalate what won't heal.** A check still failing after three
  attempts is **unhealable** — surface it in the caller's report/offer
  as a terminal mechanical escalation: which check, expected vs.
  actual, where in the artifact, how many attempts. A compiler is
  certain — no confidence hedge.
- **File nothing.** The loop's only writes are out-of-band: a **run
  record** for the pass, then each finding — healed and unhealable
  alike — to the validator findings log, per `self-heal-loop.md`. The
  artifact stays untouched until the DM's yes.

This is the deterministic slice of done. The subjective promises are
Part 2 — run it after the self-check, before the caller reports or
offers.

## Part 2 — the fresh check

The subjective promises need a grader that isn't you: you mark your own
homework, and you mark it kindly. Once the artifact is drafted and
self-healed, launch **one fresh-context checker**, one round. This
gates *completion*, not filing: the caller's report/offer forms only
when the check has run and its findings are answered.

**The criteria live in the skill text.** There is no separate rubric:
the checker grades the artifact against the completion criteria written
where each promise is stated, named as their inventory rows.

- **Launch it fresh — output, criteria, roster, nothing else.** Start a
  genuinely fresh-context, **read-only** checker and hand it only: the
  artifact exactly as it stands, the criteria passages the caller
  names, the party roster, and any computed inputs the caller lists
  (facts any reader could re-derive, never your reasoning). Withhold
  everything else — chain of thought, heal telemetry, any note arguing
  the artifact is good: a checker that sees only what a reader sees
  grades what a reader gets.
- **One round, one verdict, evidence required.** The checker returns a
  plain `approve | disapprove`; its default when it cannot tell is
  **disapprove**, and there are no waivers. Every finding cites its
  inventory row, where on the artifact it sits, the **quoted span** it
  fired on, and a one-line **reason** — and carries **no fix**. A
  verdict with nothing behind it cannot be argued with, audited, or
  used to judge the checker itself later.
- **Log the pass.** Through the shared library's `findings_log` module:
  one `log_run("build-session", <the criteria row ids graded>,
  tier="judgement", verdict=<the verdict>)`, and one
  `log_finding("build-session", <row id>, tier="judgement",
  disposition="raised", output_anchor=<where>, quoted_span=<the span>,
  reason=<the reason>)` per finding.
- **On `disapprove`, one fix pass — no re-grade.** Refine the artifact
  against the findings once (the promise-pointers *are* the
  instruction; you own *how* to fix), marking each finding `fixed` /
  `skipped` / `no_change_needed`. Do not launch a second checker: one
  fresh read is the signal; re-grading your own fix re-opens the
  negotiation the fresh context existed to close.
- **Survivors enrich the caller's one offer.** Findings you skipped or
  could not fix fold into the existing report/offer — promise-pointers,
  quoted spans, and your outcome ledger: *"N issues I couldn't
  resolve — file anyway, or take over."* — in the same enriched list
  as any unhealed mechanical escalation from Part 1. An `approve`
  leaves the offer indistinguishable from today's.
