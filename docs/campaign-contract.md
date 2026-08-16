# Campaign contract — author's menu

The library's skills learn a campaign by **discovery**: they read the campaign
repo's own guide (`CLAUDE.md` or equivalent) and the docs it points to. There
is no manifest, no required directory, page type, or heading. When a skill
can't resolve a slot from the repo's docs, it degrades per its stated fallback
or asks the DM inline, offering to record the answer in the campaign's docs so
the next run discovers it.

No required layout does not mean no *default* one. The wiki bootstrap copies
`lib/wiki-scaffold/template/` into a fresh campaign repo
(`lib/wiki-scaffold/README.md` — "copied verbatim into the consumer repo
**root**") — the `nodes/{locations,factions,npcs,events}` skeleton, `story/`,
`sessions/`, `players/`, `log.md`, `wiki-schema.md`, and the `scripts/`
catalog-and-check tooling — and, with the consumer's consent, appends the
guide block that points discovery at it
(`lib/wiki-scaffold/claude-md-block.md` — "**`wiki-schema.md` is the
schema**"). That scaffold is the **default realization** of the slots below:
discovery stays the mechanism, and in a bootstrapped repo the scaffold is
simply the answer discovery finds — session records under `sessions/`, player
pages under `players/`, the log in `log.md`, and the `nodes/` directories
where the clue-web sections and node paths that shipped skills lean on in
practice actually live. A campaign that renames or rearranges any of it stays
in contract so long as its guide says where things went; the scaffold saves a
fresh campaign from answering the menu below cold, it does not shrink the
menu.

This table is the campaign author's menu: the named slots skills probe for,
and which installed skill reads each one. It **indexes** the per-skill text —
each skill carries its own probes and absent-behaviors inline in its SKILL.md —
and this file never ships in an install payload.

Installing a skill accepts its foundational assumptions: the Don't Prep Plots
method vocabulary (nodes, clue webs, revelations, live layer) and the skill's
output formats — notably the session-page format with its PDF renderer and the
`> [!encounter-meta]` block that files onto those pages (build-session's
`session-page-format.md`, which specifies both, plus `render.md`;
the fight procedure's *Filing format* section (build-session's `combat.md`)
cites the block spec rather than
restating it, and owns what goes in its fields), all library-owned;
campaign-side tooling that parses them adapts when the library updates. Those
are install-time decisions, not per-campaign negotiations. The session page's
*skeleton* is likewise library-owned (the WotC 2024 adventure-chapter
convention); campaigns own where session pages live and the method rules
layered on top. Which skills have to be installed *together* for those
assumptions to hold is the other install-time decision — see
[Dependency clusters](#dependency-clusters--what-a-selective-install-needs)
below.

| Slot | What the campaign's docs should answer | Read by |
|---|---|---|
| Method handbook | Where the repo's planning-method conventions live (the guide should point at it) | all planning skills |
| Live layer + progress marker | What's in motion — timelines, threads, revelation tracking — and the canonical marker of campaign progress | catch-up, build-session |
| Session records / prep home | Where played-session records and prep pages live (the page format itself is library-owned) | catch-up, build-session, review-rewards |
| Player pages / party cache | Where player characters are tracked, and where the synced party JSON lands | party-sync, spotlight, build-session, catch-up, review-rewards |
| Session transcripts | Where recordings/transcripts of play land, if the campaign keeps them | catch-up |
| Reward economy | What treasure and payment run on (gold? favors?) | build-session (the keyed-site procedure) |
| Approved-items list | Which magic/notable items may be placed silently, and where the list lives (review-rewards rewrites it as the Approved Reward Pool) | build-session (the keyed-site procedure), review-rewards |
| Reward review state | Where the review-rewards app's tracked JSON state lives — versioned, outside the wiki/site bundle (fallback: `rewards-review/` at the campaign root) | review-rewards |
| Combat evidence | Where structured combat data from played sessions lands, if kept (fallback: encounter-meta `Spotlight:` lines) | spotlight |
| Media dir + style anchor | Where images live; optionally an existing image that anchors the house style | campaign-art |
| Sync camp | How changes land — direct to main, or PR flow | party-sync (and any skill that commits) |

Skills with no rows of their own (seed-clues, to-session-brief) resolve
everything through the method handbook and the repo guide. `to-session-brief`
reads that record and publishes to the campaign repo's **tracker**, so it lands
nothing in the record and claims no slot. See the per-skill SKILL.md for the
authoritative probe text on every slot.


## Dependency clusters — what a selective install needs

The CLI installs one skill at a time (`npx skills add bmoo/dm-skills --skill
<name>`), and some skills reach across a skill boundary. This table is the
**master** declaration of every such edge, and `lib/dependency_clusters.py`
parses it: an undeclared `../<other-skill>/` reference anywhere in `skills/`
fails `pytest lib/`, as does a declared **load** edge whose path has since
disappeared. This file never ships. While any edge is **hard**, the
consumer-facing statement of the cluster — with its install command — lives in
the README and the lint holds those commands to the table; since the generator
merge folded combat-generator and dungeon-generator into build-session, every
declared edge degrades, so the README carries no cluster section.

Three couplings, and they fail differently on a selective install:

- **load** — the skill text tells the reader to open a sibling's file by
  relative path. Absent, the link dangles mid-step.
- **delegate** — the skill invokes a sibling *skill* and never touches its
  files. Nothing dangles; the run stalls at a delegate that isn't there.
- **citation** — a pointer to where a shape is specified, explicitly not a
  file to open at run time. Absent, nothing breaks at run time; only the
  maintainer's trail to the spec goes cold.

**hard** means the dependent skill cannot finish its stated job without the
sibling; **degrades** means the guarded part is skipped and the rest of the run
stands.

| Skill | Needs | Coupling | Without it |
|---|---|---|---|
| `build-session` | `spotlight` | load — degrades | Step 3 hands the session to spotlight's *Invoked as a delegate* interface for the session spotlight plan, and the fight and keyed-site procedures (`combat.md`, `dungeon.md`) open `doctrine.md`, `class-patterns.md`, and the data ladder in `spotlight/SKILL.md`, every site guarded by *"if that skill is installed"*. Without spotlight the page is built with no spotlight plan and no staged-beat annotations, and fights are still sized but keep the `plain` texture. |
| `build-session` | `catch-up` | delegate — degrades | The pre-flight offers a catch-up run *"(if installed)"* before building on stale state. |
| `build-session` | `seed-clues` | delegate — degrades | Step 5 widens a thin clue slate *"(if installed)"* rather than padding it by hand. |
| `build-session` | `campaign-art` | delegate — degrades | Step 5's art pass *"(if installed)"*, with a stated ASCII fallback. |
| `party-sync` | `spotlight` | load — degrades | The Spotlight-profile half of a sync applies the flagging heuristic in `spotlight/doctrine.md`. The sync still runs — cache, Character section, backstory, bookkeeping — but rung 1 of the data ladder never gets written, so the generator flows fall to rung 2 and derive the flags live. |
| `catch-up` | `build-session` | citation — none | Names `build-session/session-page-format.md` as where the `Spotlight:` / `Spotlight (scene):` ledger shape is stated. catch-up reads the session *page*, not the format file. |
| `spotlight` | `build-session` | citation — none | The variety check's pre-play fallback names the *Filing format* section of build-session's `combat.md` as the format of the `Spotlight:` lines it reads off prepped pages. |
| `to-session-brief` | `seed-clues` | citation — none | The brief template's `Exit edge` line names seed-clues Step 5 as where that convention is stated. The brief is drafted and published without opening any of seed-clues' files, so nothing dangles when it is absent. |

No hard edge remains — the generator merge collapsed the old
spotlight + combat-generator + dungeon-generator cluster into build-session's
own reference files, and both of the surviving cross-skill loads are guarded.
Any skill installs alone and degrades per its row above.

The lint pins the *presence* of an edge and the README's agreement with it. It
cannot judge whether an edge is a load or a citation, or whether it is hard —
those columns are prose, and they are only as true as the last person to read
the surrounding step.

## Sync obligations — maintainers only

The library-owned formats above are coupled across skills, so a shape change
is a breaking change: it lands in one commit with everything that reads it,
called out in the commit message so campaign-side parsers can adapt. Each
skill carries a pointer here at its coupling site; the obligations themselves
live here, out of the shipped skill bodies.

| Shape | Owned by | Must move in the same commit |
|---|---|---|
| `> [!encounter-meta]` block | build-session (*session-page-format.md*, *The encounter-meta block*) — the shape ships beside the page format it lands on | build-session's fight procedure (`combat.md`), whose *Filing format* section cites the spec and owns what goes in the fields; its keyed-site procedure (`dungeon.md`), which files its fights in the same shape; catch-up, which reads its `Spotlight:` field as half the fired/denied ledger. The two code paths that read the block (`build-session/scripts/session_parser.py` and `lib/mechanical-checker/checker.py`) are pinned to the spec by `lib/encounter_meta_spec.py`, so a shape change fails `pytest lib/` until both move with it |
| The `Spotlight (scene):` line | build-session (*session-page-format.md*, Conventions) | build-session's keyed-site procedure (`dungeon.md`), which files one for a keyed area's non-combat beat; catch-up, which reads it as the other half of the fired/denied ledger — the non-fight one |
| `xp-budget.md`, `complications.md` | build-session's fight procedure (`combat.md`, skill-internal) | Nobody loads these across a skill boundary any more — since the generator merge they sit beside the fight procedure inside build-session, and the page and keyed-site flows size fights by following `combat.md`, which owns these files |
| `doctrine.md`, `class-patterns.md` | spotlight | build-session's fight and keyed-site procedures (guarded, *"if that skill is installed"*) and party-sync. build-session's Step 3 invokes spotlight's **delegate interface** for the session plan and loads neither file there; `catch-up` reads the page's annotations and loads neither either |
| The **session spotlight plan** — transient, handed back in-run, never filed | spotlight (*Invoked as a delegate — the interface*) | build-session (Step 3), which invokes it and spends the plan inside the same run; the fight and keyed-site procedures, which are handed a beat from it and spend that instead of allocating texture independently inside a session build |
| The **findings-log record schema** — the `"run"` and `"finding"` lines of `.claude/validator-findings/findings.jsonl` | `lib/mechanical-checker/findings_log.py`, the canonical definition and the only code that writes it — both tiers call it since the verification-chain cut gave the judgement tier real parameters (`verdict`, `quoted_span`, `reason`) | `lib/mechanical-checker/self-heal-loop.md`, whose pseudocode carries the mechanical call sites; the fresh-check log instructions in build-session's SKILL.md, `combat.md` and `dungeon.md`; and the schema bullets in `lib/mechanical-checker/README.md`. The old unpinned by-hand judgement writer is retired; a field change now lands in the module and its tests first |

The session-page skeleton's own coupling (`render.md` and
`scripts/session_parser.py`) stays noted inside build-session, where the
parser lives. `session-page-format.md` now houses both block-shaped
conventions: the encounter-meta block and the `Spotlight (scene):` line, whose
deliberate separation (a scene line never sits inside an encounter-meta block,
so the fight-variety ledger stays fights-only) is stated there once, beside
both shapes.

### When a shape change lands: retire the phrase it falsifies

This table is prose, and nothing consults it — which is how `d1a08f9` changed a
fact in `build-session/SKILL.md` and left six other locations asserting the old
one. The mechanical half of
that obligation lives in `lib/retired_phrases.py`
: a denylist of sentences the
library **used to** assert, grepped over every tracked file, failing `pytest lib/`
if one survives anywhere.

So a commit that changes what a coupled shape asserts carries three things, not
two: the change, the consumers named in the row above, **and an entry in
`RETIRED` for the sentence it just falsified** — with the commit that retired it
in the comment beside it. The entry is what turns "I updated everything" from a
claim into an assertion: it fails on arrival if any copy is still out there, so
adding it is how you find the one you missed.

It is deliberately dumb — a string denylist, not a dependency graph over prose.
It only catches a **reversal** stated in words that survived somewhere; that is
the failure that actually occurs. `lib/retired_phrases.py` documents the two
rules an entry must satisfy.

### The rules-sourcing doctrine has one copy

The *"Rules sourcing — non-negotiable"* block used to be duplicated across the
two generator skills, with `lib/doctrine_sync.py` holding the copies together.
The generator merge retired both the duplication and the guard: the doctrine
now lives once, in build-session's `combat.md`, and the keyed-site procedure
(`dungeon.md`) points at it. The sourcing *chain* the block points at keeps
its own single home — `lib/rules-sourcing.md` and the bundled SRD dataset
(`lib/srd/`) ship once and materialise into the skill by symlink, like the
mechanical checker. An edit to the doctrine is now an ordinary single-file
edit; the citation-anchor sweep still holds every phrase the inventory cites
in it.
