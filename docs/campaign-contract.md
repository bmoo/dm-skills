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
combat-generator's *Filing format* section cites the block spec rather than
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
| Session records / prep home | Where played-session records and prep pages live (the page format itself is library-owned) | catch-up, build-session, combat-generator, dungeon-generator, review-rewards |
| Player pages / party cache | Where player characters are tracked, and where the synced party JSON lands | party-sync, spotlight, build-session, combat-generator, dungeon-generator, catch-up, review-rewards |
| Session transcripts | Where recordings/transcripts of play land, if the campaign keeps them | catch-up |
| Reward economy | What treasure and payment run on (gold? favors?) | dungeon-generator |
| Approved-items list | Which magic/notable items may be placed silently, and where the list lives (review-rewards rewrites it as the Approved Reward Pool) | dungeon-generator, review-rewards |
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
<name>`), but several skills reach across a skill boundary. This table is the
**master** declaration of every such edge, and `lib/dependency_clusters.py`
parses it: an undeclared `../<other-skill>/` reference anywhere in `skills/`
fails `pytest lib/`, as does a declared **load** edge whose path has since
disappeared. This file never ships, so the consumer-facing statement of the
same clusters — with the install command per cluster — lives in the README;
the lint holds that README's commands to the hard edges declared here.

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
| `combat-generator` | `spotlight` | load — hard | Step 2 climbs the data ladder in `spotlight/SKILL.md`; Step 5 opens `doctrine.md` (and `class-patterns.md` when the fight is aimed) and reads its Legibility axis. Three dangling links inside two mandatory steps — the fight never gets a texture. |
| `combat-generator` | `build-session` | citation — none | The encounter-meta block's shape is cited, never opened: *"This is a citation, not a file to open at run time."* The six labels are restated inline in the *Filing format* section. |
| `dungeon-generator` | `spotlight` | load — hard | Same two loads as combat-generator: Step 2's data ladder, Step 5's `doctrine.md` + `class-patterns.md` for the textures rotated across the site. |
| `dungeon-generator` | `combat-generator` | delegate — hard | Every fight is sized by invoking combat-generator's *Invoked as a delegate* interface; its `xp-budget.md` and `complications.md` are never loaded, so no link dangles. A default site is 2–4 combats, so a lone dungeon-generator stalls on the first one. |
| `dungeon-generator` | `build-session` | citation — none | The `Spotlight (scene):` shape is cited, never opened: *"This is a citation, not a file to open at run time."* Step 8's filing checklist restates the line's template inline, so the site files its non-combat beats with the format skill absent. |
| `build-session` | `spotlight` | delegate — degrades | Step 3 hands the session to spotlight's *Invoked as a delegate* interface for the session spotlight plan, guarded — *"if this repo has a spotlight skill"*. It touches none of spotlight's files, so nothing dangles; without the skill the page is built with no spotlight plan and no staged-beat annotations. |
| `build-session` | `combat-generator` | delegate — degrades | Step 5 hands fights off *"(if installed)"*. |
| `build-session` | `dungeon-generator` | delegate — degrades | Step 5 hands keyed sites off *"(if installed)"*, through its delegate interface. |
| `build-session` | `catch-up` | delegate — degrades | The pre-flight offers a catch-up run *"(if installed)"* before building on stale state. |
| `build-session` | `seed-clues` | delegate — degrades | Step 5 widens a thin clue slate *"(if installed)"* rather than padding it by hand. |
| `build-session` | `campaign-art` | delegate — degrades | Step 5's art pass *"(if installed)"*, with a stated ASCII fallback. |
| `party-sync` | `spotlight` | load — degrades | The Spotlight-profile half of a sync applies the flagging heuristic in `spotlight/doctrine.md`. The sync still runs — cache, Character section, backstory, bookkeeping — but rung 1 of the data ladder never gets written, so every generator skill falls to rung 2 and derives the flags live. |
| `catch-up` | `build-session` | citation — none | Names `build-session/session-page-format.md` as where the `Spotlight:` / `Spotlight (scene):` ledger shape is stated. catch-up reads the session *page*, not the format file. |
| `spotlight` | `combat-generator` | citation — none | The variety check's pre-play fallback names combat-generator's *Filing format* section as the format of the `Spotlight:` lines it reads off prepped pages. |
| `to-session-brief` | `seed-clues` | citation — none | The brief template's `Exit edge` line names seed-clues Step 5 as where that convention is stated. The brief is drafted and published without opening any of seed-clues' files, so nothing dangles when it is absent. |

Every hard edge points at `spotlight` or `combat-generator`, which is the one
cluster this library has: **spotlight + combat-generator + dungeon-generator**,
with `party-sync` and `build-session` attached softly. `build-session` is the
only skill whose every cross-skill edge is guarded, which is why the README's
`--skill build-session` example stays honest on its own.

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
| `> [!encounter-meta]` block | build-session (*session-page-format.md*, *The encounter-meta block*) — the shape ships beside the page format it lands on | combat-generator, whose *Filing format* section cites the spec and owns what goes in the fields; dungeon-generator, which files its fights in the same shape; catch-up, which reads its `Spotlight:` field as half the fired/denied ledger. The two code paths that read the block (`build-session/scripts/session_parser.py` and `lib/mechanical-checker/checker.py`) are pinned to the spec by `lib/encounter_meta_spec.py`, so a shape change fails `pytest lib/` until both move with it |
| The `Spotlight (scene):` line | build-session (*session-page-format.md*, Conventions) | dungeon-generator, which files one for a keyed area's non-combat beat; catch-up, which reads it as the other half of the fired/denied ledger — the non-fight one |
| `xp-budget.md`, `complications.md` | combat-generator (skill-internal) | Nobody loads these across a skill boundary any more — `dungeon-generator` and `build-session` size fights by invoking combat-generator's **delegate interface** (its *Invoked as a delegate* section), which owns these files. The coupling that must move together is now that interface, documented per edge in the skills, not these filenames |
| `doctrine.md`, `class-patterns.md` | spotlight | combat-generator, dungeon-generator, party-sync. `build-session` invokes spotlight's **delegate interface** for the session plan and loads neither file; `catch-up` reads the page's annotations and loads neither either |
| The **session spotlight plan** — transient, handed back in-run, never filed | spotlight (*Invoked as a delegate — the interface*) | build-session (Step 3), which invokes it and spends the plan inside the same run; combat-generator and dungeon-generator, which are handed a beat from it and spend that instead of allocating texture independently when called inside a prep run |
| The **findings-log record schema** — the `"run"` and `"finding"` lines of `.claude/validator-findings/findings.jsonl` | `lib/mechanical-checker/findings_log.py`, the canonical definition and the only *code* that writes it | `lib/judgement-checker/checker-launch-protocol.md`, which instructs the judgement tier to write **both** kinds **by hand** — it has no import path to the module — and so restates every field of both; `lib/mechanical-checker/self-heal-loop.md`, whose pseudocode carries the mechanical call sites; and the schema bullets in `lib/mechanical-checker/README.md`. A field added on one side only yields a log whose two tiers disagree, and nothing fails — the two writers never meet, so this coupling **is not pinned** today and this row is its whole mechanism. A guard on `lib/encounter_meta_spec.py`'s model looks feasible rather than ruled out: parse the fenced record objects out of the protocol and compare their key sets against what `findings_log.py` emits. Unbuilt, not impossible |

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

### Editing the rules-sourcing doctrine: edit both copies

One coupling in this library is a straight duplication rather than a shape with
an owner. `combat-generator` and `dungeon-generator` each carry their own
*"Rules sourcing — non-negotiable"* block — the same doctrine, near-verbatim, in
two skills. That is deliberate:
the doctrine must live inside each generator's own SKILL.md so a selective
install carries it. The sourcing *chain* the blocks point at is the opposite
shape — `lib/rules-sourcing.md` and the bundled SRD dataset (`lib/srd/`) ship
once and materialise into each skill by symlink, like the mechanical checker —
so the dataset has exactly one home. Neither doctrine copy is the original; they are peers, which is why
the duplication has no row in the table above.

So **an edit to one copy is an edit to both, in the same commit.**
`lib/doctrine_sync.py` enforces it and fails `pytest lib/` otherwise. It asserts
the two blocks differ *only* in the per-skill variations declared in that module
(dungeon-generator enumerates the item, trap and door content it places, and
points its browse rule at the step that shortlists), and that both still state
the three obligations — never from memory, browse the chosen source's catalog
before shortlisting, name the gap when nothing in the chain answers.

Declaring the differences rather than the shared text is what makes it catch a
sentence **added** to one copy, not just a clause deleted from one. When a new
difference is genuinely per-skill, the failure prints the word spans ready to
paste into the module's `PERMITTED` list with the reason; when it isn't — the
usual case — making the same edit in the other copy is the fix.
