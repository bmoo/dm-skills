---
name: groom-wiki
description: >
  Groom a campaign wiki after session absorption or on demand: apply mechanical
  maintenance and place unresolved findings where prep reads them. Use
  --dry-run to preview without writing.
---

# Groom the wiki

Run maintenance in the campaign repository. A normal run writes its fixes,
findings, and one `Lint` entry directly; it commits nothing and creates no
report file. The DM reads the maintained wiki, not a report to adjudicate.

## 1. Discover the bundle and mode

Read the campaign guide (`CLAUDE.md` or equivalent) and its schema pointer.
Locate the installed `scripts/okf-groom.py` and `scripts/okf_config.py`; use
the config's `BUNDLE_ROOT`, directory/type map, and included concepts rather
than assuming the wiki is the repository root or uses `nodes/`. The commands
below run from the repository root; substitute the discovered script path
when necessary. Read the schema's frontmatter, seed promotion, rebuild test,
callout, session horizon, and log conventions. If this bundle lacks the
groomer tooling or those conventions, name what is missing and stop without
bootstrapping or migrating it. No companion skill is required.

Capture the starting content and existing working changes in memory so this
run can be distinguished from the DM's edits, including uncommitted files.
Use that baseline to review promotions and preserve prior findings.

**Dry run:** `/groom-wiki --dry-run` follows the same reading and judgement
steps, using script report mode and proposed edits held in context. It places
and logs nothing: no concept edits, indexes, logs, report files, temporary
evidence files, or checker telemetry. Pass evidence on stdin. Give the fresh
checker the proposed result in context with read-only access to source files.

**Done when:** the bundle, schema, starting state, and write/report mode are
known.

## 2. Mechanical findings

Run `python3 scripts/okf-groom.py --fix`; in dry run, run
`python3 scripts/okf-groom.py` instead. Retain all stable finding ids and
locations in context, including findings that remain after fixes.

`groom/missing-target` exempts reserved `index.md` and `log.md` files at
every level. Preserve broken links, including historical log entries;
report missing targets on concepts without stripping them. Read the
campaign schema's *Callouts* and *Session horizon* sections for placement
shapes and dates. Where no live layer exists, keep orphan findings in the
command output and `Lint` entry; create no report file or live layer.

The script normalizes links, backfills missing titles and committed
provenance, promotes eligible seeds, regenerates indexes, and places mechanical
findings. Keep `groom/orphan` and `groom/not-in-index` separate. Staleness is
a log-only finding: the groomer never sets or refreshes `stale_after` or
`next_session`. Backfilled `generated.at` comes from the last commit; leave
it absent for uncommitted content rather than inventing history. Mechanical
link, index, and finding placement alone do not change last-writer metadata.

**Done when:** the command completed, its changes are accounted for against
the baseline, and every remaining finding has its schema-defined placement
or a place in the final `Lint` entry.

## 3. Judgement

Read the bundle's authored prose, seed inboxes, live layer when present, and
every promoted seed with its original references. Apply the schema's rebuild
test. Move identifiable unplayed session output back to its owning session,
preserving the content; when ownership cannot be established, retain it and
record the unresolved location. Restore session-bound promotions to their
original inbox sections and reverse only this run's anchor rewrites. Give
each retained promotion a useful plain-sentence description.

For recurring names without a concept, check existing titles, aliases, and
seed headings first. Seed the established facts, with source links, in the
inbox for the entity's discovered type. Session-only names stay on their
session page. Meaningful authored additions or moves follow the schema's
frontmatter and record `generated` with actor `dm-skills/groom-wiki` and the
current offset timestamp; this describes this edit, not invented provenance.

For contradictions, run `python3 scripts/okf-groom.py --candidates`. Read
the authored claims in each returned entity's referring concepts. For each
genuine disagreement, send an object (or array) with bundle-relative paths
`entity`, `left`, `right` and exact, unique prose passages `left_claim`,
`right_claim` on stdin to
`python3 scripts/okf-groom.py --place-contradiction - --fix`.
Both sides must be in that entity's returned referrers. The command validates
the evidence, places both schema-shaped callouts beside the claims, and
reuses existing pairs. If validation fails, reread the passages and correct
the evidence rather than placing approximate quotations. In dry run, omit
`--fix` to validate without placement and retain proposed pairs in context.

The following six rows are the completion criteria for the fresh check:

| Check id | Done when |
|---|---|
| `groom-wiki/contradiction-scope` | Every disagreement found in the returned candidate set has paired callouts. The set is entity-scoped, at most 25 entities ranked by newest referring `generated.at`; comparisons are node–node or node–live-layer, skipping deprecated concepts and all sessions. Generated evidence is not treated as a new claim. |
| `groom-wiki/contradiction-evidence` | Each pair sits beside the conflicting passages, quotes both claims verbatim, and links the peer with its current status (omitted status means stable), in the schema's shape without duplicate pairs. |
| `groom-wiki/durable-promotions` | Every retained promotion has life beyond its introducing session, lives in the correct directory as a draft concept with useful metadata, and leaves no copied seed behind; references follow its new location. No session-bound seed was promoted, regardless of size or reference count. |
| `groom-wiki/rebuild-test` | No unplayed session output sits on a node concept: rebuilding the session reads the node's durable situation and produces session-specific material on the session page. Played history remains valid node content. |
| `groom-wiki/recurring-names` | Every recurring name found in authored prose without an existing concept or seed has an evidence-backed seed in the right inbox; aliases are accounted for and session-only names stay session-scoped. |
| `groom-wiki/unresolved-preserved` | No flagged disagreement was resolved, winner chosen, deprecation proposed, or existing callout pair cleared by this run. Broken links and unrelated authored material survive; findings remain at the schema-defined locations. |

## 4. One fresh check

After the judgement edits, launch **one fresh-context, read-only checker**.
Give it only the six criteria above, the discovered schema/config, baseline
and resulting content (proposed content for dry run), the candidate list, and
the source passages/references needed to check the changes and name coverage.
Withhold your reasoning and claims that the work is good. The checker may
read the bundle to verify coverage; it writes nothing.

Require one `approve | disapprove` verdict, defaulting to `disapprove` when
uncertain. Every finding must name its check id and location, quote the
failing span, and give a one-line reason with no proposed fix. On
`disapprove`, make **one fix pass, no re-grade**, recording each finding as
`fixed`, `skipped`, or `no_change_needed` in context. Retain unresolved
findings for the closing entry and summary; never settle canon to pass a row.
If a fresh checker is unavailable, state that the gate is incomplete rather
than substituting self-approval.

This gates completion of maintenance already authorized by the invocation;
there is no additional permission-to-file step. **Done when:** the single
fresh verdict has been received and every finding has an outcome.

## 5. Finish

In a normal run, regenerate indexes after judgement changes with
`python3 scripts/okf-index.py`, then run
`python3 scripts/okf-check.py --strict` and the groomer in report mode to
account for remaining findings. Append **one `Lint` entry** to the discovered
bundle log using the schema's date grouping: 1–3 sentences linking what was
placed and where, noting staleness, orphans without a live layer, and any
unresolved checks. Include the fresh verdict and fix outcomes concisely.
Create no separate report. Leave the working changes uncommitted.

In dry run, present the proposed placements and unresolved findings in the
run, including the fresh verdict; perform no writing or logging step.

**Done when:** the run's changes or proposals are accounted for, a normal
run has exactly one `Lint` entry, and any remaining limitation is explicit.
Close briefly with the locations touched and unresolved limitations; a clean
run needs no report for the DM to read.
