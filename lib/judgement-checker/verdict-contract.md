# Verdict contract — two channels off `ReportFindings`

The loop carries **two verdict channels**. Both derive from Claude Code's
`ReportFindings` shape — a parseable, ranked verdict whose `outcome` field already
models re-report-after-fix (`fixed` / `skipped` / `no_change_needed`). The prose
`code-review` shape was rejected in the spec: the generator needs a
**machine-actionable** verdict, not paragraphs.

For reference, `ReportFindings` carries a top-level `findings[]` (ranked,
most-severe first) and a `level`; each finding carries `category`,
`short_summary`, `summary`, `failure_scenario`, `file`, `line`, and — only when
re-reporting after a fix — `outcome` (`fixed | skipped | no_change_needed`), plus
an optional `verdict` (`CONFIRMED | PLAUSIBLE`). Both channels below are stated as
what they **add to** and **constrain on** that shape.

---

## Channel 1 — Judgement verdict (checker subagent → back-pressure loop)

The [fresh-context checker](checker-launch-protocol.md) returns this. It drives the
[back-pressure loop](back-pressure-driver.md).

### Top-level: a plain `approve | disapprove` (an addition)

`ReportFindings` has no verdict field of its own — it is a findings list plus a
`level`. This channel **adds** a checker-owned top-level verdict, exactly two
values:

```
approve      — the checker could not disprove the output against its rubric subset.
disapprove   — the checker found at least one broken promise, OR could not tell.
```

**No third state.** "Uncertain" is not a verdict — **disapprove-on-uncertainty**
lives here: when the checker cannot tell whether a promise holds, it returns
`disapprove` (spec user story 5). There is no channel for a shrug. `approve` with
a non-empty findings list is a contradiction and is treated as `disapprove`.

### Beneath the verdict: advisory findings, ranked

The findings are `ReportFindings` findings, **ranked most-severe first**, with
three constraints this channel pins:

| Concern | Where it rides on `ReportFindings` | Rule |
|---|---|---|
| **Promise-pointer** (required) | an **added, required field** — `promise` — the judgement analogue of the mechanical `Finding.check_id`. `ReportFindings` has no native field for an inventory-row id (`category` is a kebab-case slug of finding *type*, not an identifier — do not overload it), so the pointer is added, exactly as the top-level `approve \| disapprove` verdict is added. Its value is the **inventory row id** — e.g. `build-session/npc-rows-named`, `dungeon-generator/lead-interpretability`. | **No finding without a promise-pointer.** Every finding cites the exact [`docs/eval-assertion-inventory.md`](../../docs/eval-assertion-inventory.md) row it breaks in its `promise` field. A finding that cannot name a broken row is not a finding — the checker may only grade against the rubric it was handed, and every rubric row *is* an inventory row. |
| **Output-location anchor** (required) | `file` + `line` | Names **where in the output** the break is — the section/heading/row/line a reader would look at. (The sibling mechanical channel calls this same concept `output_location`; same anchor, so a finding from either tier reads the same way.) The checker grades one output artifact, so `file` is that artifact / its section, not a repo path. |
| **No concrete fix** (forbidden) | `summary`, `short_summary`, `failure_scenario` | These state **the defect only** — what promise broke and how a reader would see it break. They **must not** contain a remedy, a rewrite, or an instruction to change specific text. The checker names *which* promise broke; the generator owns *how* to fix it (spec user story 19). A fix living in `summary` violates this contract. |

`failure_scenario` states the reader-facing consequence ("a player reading the
Key NPCs table meets a row with no name and cannot refer to the NPC") — the defect,
never its cure.

### `outcome` — owned by the generator, never the checker

The checker emits findings **fresh each round with `outcome` unset** — it has no
memory of prior rounds (a new fresh checker each round; see the driver). The
`outcome` field (`fixed | skipped | no_change_needed`) is written by the
**generator**, which owns cross-round memory: after a round the generator marks
each prior finding's fate and carries that ledger forward. This split is what keeps
independence intact — the checker never learns what the generator did with a
previous verdict. See [`back-pressure-driver.md`](back-pressure-driver.md).

---

## Channel 2 — Terminal mechanical-escalation (generator → DM)

This is the **sibling deterministic tier's** channel, documented here so the
two-channel contract lives in one place. It is **not** built or re-implemented in
this shared judgement layer — it is owned by
[`../mechanical-checker`](../mechanical-checker/README.md) and its downstream
extensions. Stated for completeness:

- **Direction:** generator → DM, for the **unhealable deterministic case only**.
  Healed mechanical failures are silent telemetry — never surfaced to the DM, but
  **appended to the durable findings log**
  ([`findings_log.py`](../mechanical-checker/findings_log.py)) rather than discarded;
  only a mechanical break that survived its self-heal
  attempts escalates here.
- **Shape:** a **list** of failed checks. Each entry wraps an existing
  `Finding` — `(check_id, expected, actual, output_location)` — and **adds
  `heal-attempts-tried`** (what the generator already tried, so the DM can act
  without re-deriving it; spec user story 3).
- **No confidence field.** The deterministic tier is certain by construction —
  a compiler does not hedge — so there is nothing to qualify. Contrast Channel 1,
  whose disapprove-on-uncertainty *is* its confidence handling, folded into the
  verdict rather than a separate field.

The two channels never merge: Channel 1 gates *completion* (the file-offer does
not form until the judgement loop exhausts); Channel 2 is a *terminal* report of
mechanical breaks the generator could not heal. Both feed the same enriched
file-offer at the end, but they are produced by different tiers and carry
different certainty.

---

## Why both derive from one shape

One parseable verdict shape across both tiers means a finding reads the same
whether a compiler or a reader found it: an id for *what broke*, an anchor for
*where*, and a defect statement that stops short of prescribing the fix. The
generator consumes both with the same machinery, and the DM — at the exhausted
offer — reads one enriched list, not two dialects.
