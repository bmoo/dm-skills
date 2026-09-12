# Groomer skill and schema text handoff

Exact edits for [Skill and schema text edits the groomer requires](https://github.com/bmoo/dm-skills/issues/68),
for inclusion in [Assemble the ready-for-agent spec](https://github.com/bmoo/dm-skills/issues/66).
This is a wording artifact; applying it belongs to the implementation of that spec.

Baseline: dm-skills main `4da6bc8729e6260ee183f9911abb70088375927f`, with the
[v0.2 schema draft](https://github.com/bmoo/dm-skills/blob/8306da26217b86fea32f7ec43286318eb9600425/lib/wiki-scaffold/template/wiki-schema.md)
applied first. Script names below are the final names from
[Checker and index generator design for v0.2](https://github.com/bmoo/dm-skills/issues/61).
The remaining authorities are
[Groomer skill design: auto-fix versus report, and its mechanical checks](https://github.com/bmoo/dm-skills/issues/62),
[stale_after ownership across catch-up, build-session, and lazy-dm](https://github.com/bmoo/dm-skills/issues/65),
and the [sd-campaign migration plan](https://github.com/bmoo/dm-skills/issues/63).

## Schema: frontmatter and scheduling

In `lib/wiki-scaffold/template/wiki-schema.md`, replace the `Optional:` block
through the current `stale_after` bullet, stopping before `Two format rules`, with:

```markdown
Expected when known, omitted otherwise:

- `next_session:` — on the live layer, the next real-world session night as
  a `YYYY-MM-DD` date. This is a campaign extension, not a timestamp or an
  in-fiction date. See *Session horizon* below.

Optional:

- `stale_after:` — an absolute instant at which a concept becomes stale
  (§5.5). On the live layer and unplayed session prep, use the *Session
  horizon* rule below. The groomer reports staleness; it never sets the value.
```

Insert this section before `## Tags`:

```markdown
## Session horizon

The live layer (`story/campaign-status.md` in this scaffold) owns
`next_session`. Its `stale_after` is midnight at the start of the following
calendar day, with the campaign's local UTC offset for that instant. For
example, `next_session: 2026-09-15` in America/Los_Angeles yields
`stale_after: 2026-09-16T00:00:00-07:00`. Stale means `now >= stale_after`:
a session night has passed and catch-up may be owed.

At the end of an absorption, catch-up proposes the next future occurrence
of `SESSION_WEEKDAY` from `scripts/okf_config.py` and confirms the date with
the DM. An unset weekday means ask for the date. Use the campaign's local
timezone from its guide; ask if it is unknown. If the next date is unknown,
omit `next_session` and remove the live layer's `stale_after`; prep built
from that live layer also omits `stale_after`.

At build time, a session page or durable prep sheet copies the live layer's
`stale_after`, provided `next_session` is known. A sheet delivered only in
chat creates no metadata-bearing file. When catch-up absorbs a played
session, its record becomes `status: stable`, gains the `played` tag and
the actual `session_date`, and loses `stale_after`. Apply the same lifecycle
to any companion prep sheet for that played session. History has no session
horizon.

Before prep, if the live layer is stale, ask whether the session on
`next_session` was played. If yes, finish catch-up before building. If no,
roll `next_session` to the next future configured weekday (ask for a date
when unset), recompute the live layer's `stale_after`, and use that value
on the prep being built or refreshed. A date the DM supplies overrides the
weekday. Keep the progress-marker check too: it detects unabsorbed play
before the midnight boundary.

| Field | Writer | Clearer | Reader |
|---|---|---|---|
| Live-layer `next_session` | catch-up after absorption; prep skill after postponement or cancellation | either writer when the next date is unknown | catch-up and the prep skill |
| Live-layer `stale_after` | the same writer, using the date rule above | the same writer when `next_session` is unknown | prep skill; groomer |
| Session/prep-sheet `stale_after` | prep skill, copied from the live layer | catch-up on absorption; prep skill when rebuilding without a known next date | groomer |

Here the prep skill is `build-session`, or a campaign-local skill such as
sd-campaign's `lazy-dm`. These are field ownership rules, not requirements
to install every skill. A bundle without a live layer uses neither field.
```

In the frontmatter section, replace the checker command with
`python3 scripts/okf-check.py --strict` and the index command with
`python3 scripts/okf-index.py`. Replace the sentence about checker failures with:

```markdown
Run `python3 scripts/okf-check.py --strict` before committing — the checker's
three error classes are missing or unparseable frontmatter, empty `type`,
and malformed reserved files (§11); strict mode also fails on warnings.
Run `python3 scripts/okf-index.py` after any batch of changes — the catalog
is built from each concept's `title` and `description`.
```

In *Link conventions*, replace the missing-target bullet with:

```markdown
- A link whose target does not exist is not a conformance error (§6.1).
  The groomer flags it as `groom/missing-target` and preserves the link.
  Reserved `index.md` and `log.md` files are exempt from this finding at
  every level; historical log links stay as history.
```

## Schema: findings in place

Add to the kinds listed under `## Callouts`:

```markdown
- `contradiction` — an unresolved disagreement between concepts, in the
  paired shape below. DM-facing; it records evidence without choosing canon.
```

Insert these subsections at the end of *Callouts*, before *Reference tokens*:

```markdown
### Contradictions

The groomer places a callout beside each conflicting passage, on both
concepts. Quote both claims verbatim and link the other concept, with its
current status; an omitted status means `stable`. On the second concept,
swap `Here` and `Other` and link back to the first:

> [!contradiction] Unresolved: <entity or fact>
> Here: "<verbatim claim on this concept>"
> Other: [<concept title>](/path/to/other.md) (status: <draft|stable>): "<verbatim conflicting claim>"

Keep distinct disagreements in separate callouts. Reuse an existing pair
for the same passages on rerun rather than adding duplicates. Callout
quotes are evidence, not additional assertions to scan for contradictions.
Only a human edit or catch-up absorbing play that settles the fact clears
a pair. Catch-up reconciles the fact first, updates its owning prose, then
removes both matching callouts; it leaves unrelated callouts in place.

Detection covers node against node and node against the live layer. Skip
`deprecated` concepts on both sides. Sessions are exempt: draft prep can
propose change, and played history is catch-up's input. Scope each run to
entities linked by at least two concepts, taking at most 25 entities ranked
by the newest `generated.at` among their referring concepts. The groomer
records disagreements and never chooses a winner.

### Loose ends

The groomer lists orphan nodes in a generated section on the live layer,
which the prep skill reads when selecting situations. The section is a
link index, not newly authored hooks or a report file:

<!-- groom-wiki:loose-ends:start -->
## Loose ends

- [<node title>](/nodes/category/node.md) — orphan node
<!-- groom-wiki:loose-ends:end -->

The markers delimit the whole generated section, including its heading.
Replace only that region on rerun, with one entry per orphan in path order.
An empty result is the same marked section with `No orphan nodes.` in place
of the list. Leave all other live-layer text intact. The groomer computes
orphans from concept links, excluding generated catalogs and this generated
section so neither can make an orphan appear connected. Keep
`groom/orphan` separate from `groom/not-in-index`: regenerating the catalog
does not connect a node to the campaign.

Catch-up may incorporate an orphan through absorbed play; its final groomer
run refreshes the section. Prep reads it without hand-editing it. In a bundle
with no live layer, print orphan findings and include them in the `Lint`
entry; create no live layer or substitute report file.
```

The placeholder paths and quotes above illustrate the exact block grammar;
writers replace them with real concept paths and verbatim evidence.

## Campaign contract

Append these rows to *Must move in the same commit* in
`docs/campaign-contract.md`:

```markdown
| `contradiction` callouts and the generated `Loose ends` section | the campaign schema (`lib/wiki-scaffold/template/wiki-schema.md` in the shipped scaffold) | `groom-wiki` / `okf-groom.py`, which place findings; `catch-up`, which clears settled callout pairs and invokes the groomer to refresh loose ends; `build-session`, which reads both shapes. sd-campaign's local `lazy-dm` reads the same shapes and moves through its companion ticket. Cross-skill invocation is guarded with "if installed". |
| Live-layer `next_session` and live-layer/prep `stale_after` | the campaign schema's *Session horizon* rule; `okf_config.py` supplies `SESSION_WEEKDAY` | `catch-up` (next date and live-layer horizon, clearing the played session's horizon); `build-session` and sd-campaign's local `lazy-dm` (prep horizon and date rollover after cancellation); `groom-wiki` / `okf-groom.py` (reads and reports staleness without setting dates). |
```

Extend the existing *Live layer + progress marker* slot with
`next session date, session horizon, and groomer loose ends / contradictions
when the campaign schema defines them`; add `groom-wiki` to its readers.
This keeps discovery as the contract for campaigns that use another layout.

## catch-up

In `skills/catch-up/SKILL.md`, add after the introductory discovery paragraph:

```markdown
Read the campaign schema the guide points to before changing concept
metadata or groomer findings. In a scaffolded wiki this is `wiki-schema.md`:
its *Session horizon* and *Callouts* sections own the field and block shapes.
Use the discovered campaign conventions where these features are absent.
```

In Step 4, before its completion criterion, insert:

```markdown
For an OKF v0.2 session record, set `status: stable`, add the `played` tag,
set `session_date` to the actual date of play, and remove `stale_after` per
the schema. Do the same for any companion sheet for that played session.
Meaningful edits record `generated` using the schema's last-writer rule
(`dm-skills/catch-up`); preserve unrelated metadata.
```

At the end of Step 5's three rings, before `Per the hard rules`, insert:

```markdown
If the reconciled session settles a fact marked by a contradiction callout,
update the owning prose and clear that callout and its counterpart on the
linked concept, per the schema. Clear only the settled pair. An unresolved
discrepancy stays visible on both concepts; absorbing a newer session alone
does not choose its resolution.
```

Replace the Step 5 handoff paragraph beginning `Per the hard rules` with:

```markdown
Per the hard rules, new content a consequence demands — a node needing
enrichment, a revelation left short because the party burned a clue's
source — goes on the handoff list for the repo's node-building or
clue-seeding skill. Moving an existing eligible seed into its own concept
is the groomer's schema-governed maintenance; authoring new content remains
a handoff.
```

In Step 6, before its completion criterion, insert:

```markdown
After the last session in this absorption, confirm the next real-world
session date with the DM, proposing `SESSION_WEEKDAY` from the discovered
OKF config when set. Write `next_session` and recompute the live layer's
`stale_after` per the schema's *Session horizon* rule. When the next date is
unknown, omit both fields. This date is separate from the in-fiction clock.
```

Replace Step 7 from `Re-walk Steps 5–6` through its completion criterion with:

```markdown
Re-walk Steps 5–6 against the actual files, not memory. Write the absorption
log entry and handoff flags. As the final maintenance step, invoke
`/groom-wiki` if installed, after the session and live layer are current.
It refreshes loose ends and places any surviving disagreements where prep
will meet them. If absent, name the skipped grooming in the closing summary;
absorption still completes. Close with the handoffs and, if multiple
sessions were absorbed or the ripple ran wide, offer an integrity-audit pass.
**Done when:** the re-walk finds no unpropagated settled fact, session and
live-layer horizons follow the schema, and the final groomer run completed
or its absence was named. Unsettled callouts remain visible.
```

## build-session

In `skills/build-session/SKILL.md`, after the opening progress-marker
paragraph in Step 1, insert:

```markdown
Discover the live layer's schema through the campaign guide before this
check. When it defines `next_session` and `stale_after`, also check the
live-layer horizon: if `now >= stale_after`, ask whether the session on
`next_session` was played. Yes: finish `catch-up` (if installed) before
building; if it is absent, ask the DM to bring the record current first.
No: roll the date forward and rewrite the live-layer horizon per the
schema's *Session horizon* rule, then use that value for this build's prep.
This supplements the progress marker, including for a lean-sheet build.
```

After the numbered ground-rule discovery list in Step 1, insert:

```markdown
Read the live layer's generated loose-ends section, when present, and any
contradiction callouts on the concepts this build touches. Their shapes
and ownership live in the campaign schema. Use loose ends as candidates
within the brief's scope. Carry an unresolved contradiction as a prep gap;
ask for a ruling if it blocks the build, and leave its callouts intact.
```

After Step 4's opening paragraph, insert:

```markdown
For an OKF v0.2 page, draft frontmatter per the discovered schema:
`status: draft`, `generated` using `dm-skills/build-session` and the current
offset timestamp, and `stale_after` copied from the live layer per its
*Session horizon* rule (omitted without a known `next_session`). Apply this
to each session page built or refreshed. Follow the existing filing gate
for the drafted page.
```

In Step 3's *Lean-sheet exit*, after the sentence about the durable Key NPCs
roster, insert:

```markdown
An in-chat sheet creates no file or frontmatter. If this run refreshes the
roster on an existing unplayed OKF session page, also refresh that page's
`stale_after` from the live layer per the schema's *Session horizon* rule;
omit it when the next date is unknown. Record the meaningful edit with
`generated` per the schema, using `dm-skills/build-session`.
```

## Config and tool discovery

In the renamed `lib/wiki-scaffold/template/scripts/okf_config.py`, add:

```python
# Default real-world game night proposed by catch-up; None means ask.
# Use a lowercase English weekday, e.g. "tuesday". The campaign guide owns
# the local timezone; writers use its offset at the next morning's midnight.
SESSION_WEEKDAY = None
```

In `skills/setup/SKILL.md` Phase 2's offer, replace
`catalog + conformance scripts (scripts/)` with:

```markdown
catalog, conformance, and maintenance scripts (`scripts/okf-index.py`,
`scripts/okf-check.py`, `scripts/okf-groom.py`, and the migration tool
`scripts/okf-migrate.py`)
```

Step 3 names `scripts/okf_config.py` instead of `scripts/wiki_config.py`;
the sole setup edit remains `WIKI_TITLE`. `SESSION_WEEKDAY` defaults to unset.
Replace Step 5 with:

```markdown
5. **Start green.** From the repo root run `python3 scripts/okf-index.py`,
   then `python3 scripts/okf-check.py --strict`. The phase is done when the
   check exits clean — zero errors, zero warnings — on the freshly
   generated catalog. Anything it flags on a fresh copy is yours to fix
   before handing over, not the DM's.
```

Before setup's closing paragraph, insert:

```markdown
For later maintenance, `/groom-wiki` (if installed) runs the mechanical
fixes and reads the wiki for findings that need judgement. Its
`--dry-run` mode writes nothing. `python3 scripts/okf-groom.py` is the
mechanical report-only entry point; add `--fix` to apply its safe fixes.
Setup's start-green gate remains the index generator and strict checker.
```

In `lib/wiki-scaffold/README.md`, rename all three existing `wiki_*` /
`wiki-*` tool references to their `okf_*` / `okf-*` names, add `--strict`
to the checker command, and add these bullets under *Start here*:

```markdown
- Use `/groom-wiki`, if installed, to apply mechanical fixes and place
  findings where prep reads them; `/groom-wiki --dry-run` writes nothing.
  The script alone, `python3 scripts/okf-groom.py`, reports mechanical
  findings; add `--fix` to apply its safe fixes.
- `scripts/okf-migrate.py` converts an existing bundle during a planned
  migration; it is not part of routine grooming.
- Optionally set `SESSION_WEEKDAY` in `scripts/okf_config.py`; catch-up
  uses it to propose the next date. The schema owns the session horizon.
```

In `lib/wiki-scaffold/claude-md-block.md`, replace the last two bullets with:

```markdown
- Regenerate the catalog after every batch of wiki changes —
  `python3 scripts/okf-index.py`. It is built from frontmatter, so it is
  never hand-edited; keep each concept's `title` and `description` current.
- Check before committing — `python3 scripts/okf-check.py --strict`.
- Groom after session absorption, or on demand: `/groom-wiki` if installed
  applies mechanical fixes and places findings per `wiki-schema.md`.
  `/groom-wiki --dry-run` writes nothing. The script-only entry point is
  `python3 scripts/okf-groom.py` (reports); `--fix` applies mechanical fixes.
  Catch-up owns the after-absorption invocation, so do not invoke it twice.
- For a planned migration of an existing bundle, use `scripts/okf-migrate.py`
  with the migration plan; it is separate from routine maintenance.
```

## Groomer implementation handoff

The new skill and script are implemented from the groomer design. Add this
exact instruction to the skill's mechanical-findings section:

```markdown
`groom/missing-target` exempts reserved `index.md` and `log.md` files at
every level. Preserve broken links, including historical log entries;
report missing targets on concepts without stripping them. Read the
campaign schema's *Callouts* and *Session horizon* sections for placement
shapes and dates. Where no live layer exists, keep orphan findings in the
command output and `Lint` entry; create no report file or live layer.
```

The script's missing-target traversal uses the same reserved-file exclusion.
Its `--fix` implementation and skill judgement pass must use the exact
marked section and paired callouts specified here. The plain `--dry-run`
skill mode performs neither placement nor logging; it presents proposed
findings in the run. Preserve the resolved design's auto-fix/report split,
seed eligibility safeguards, one-round fresh check, and no-commit behavior.

The separate [vocabulary sweep](https://github.com/bmoo/dm-skills/issues/69)
owns the `CONTEXT.md` edits and page-to-concept sweep. Its handoff should
include the groomer design's requested **Groomer** entry when the skill lands.
This artifact keeps “session page” for the existing output and uses “concept”
for the schema-level object; it does not resolve the broader vocabulary task.

## Companion lazy-dm change

Filed as [Write v0.2 frontmatter and links from lazy-dm](https://github.com/bmoo/sd-campaign/issues/135).
The ticket carries the exact local insertions and points back to this
wayfinder task for the shared schema. It replaces the migration plan's
instruction to file that ticket during spec assembly; the assembler reuses
the filed ticket.

## Verification when implemented

Apply the coupled schema, skills, config, and tooling changes together.
Update the shipped scaffold checks for final script names and strict mode,
including setup's unchanged preflight coverage. Add a reserved-file
missing-target fixture with broken links in both a root and a nested log
plus a concept whose missing link must still be reported. Verify generated
loose ends remain orphans across reruns, replace only the marked region,
and produce no live layer when none exists. These exercise shipped runtime
behavior, not this handoff document's prose.

Walk the skill wording against these cases: midnight boundary; night-of-game
catch-up; played versus cancelled session; unset weekday or unknown next
date; timezone offset change; companion sheet absorbed; no groomer installed;
paired contradiction settled versus still disputed; and an in-chat lean
sheet. Confirm the shared schema supplies each outcome and no skill invents
an independent date rule.

Run the repository's content gate after implementation:
`pytest checks/ lib/mechanical-checker skills/build-session/scripts/`.
The [example rewrite](https://github.com/bmoo/dm-skills/issues/67) follows these
changes and recopies the schema and scripts; it is not part of this wording
artifact. No runtime tests are claimed by this planning-only handoff.
