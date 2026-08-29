# Campaign contract — author's menu

The library's skills learn a campaign by **discovery**: they read the campaign
repo's own guide (`CLAUDE.md` or equivalent) and the docs it points to. There
is no manifest, no required directory, page type, or heading. When a skill
can't resolve a slot from the repo's docs, it degrades per its stated fallback
or asks the DM inline, offering to record the answer in the campaign's docs so
the next run discovers it.

No required layout does not mean no *default* one. The wiki bootstrap copies
`lib/wiki-scaffold/template/` into a fresh campaign repo
(`lib/wiki-scaffold/README.md` — "a starting wiki for planning and running the
campaign") — the `nodes/{locations,factions,npcs,events}` skeleton, `story/`,
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
output formats — notably the session-page format with its PDF renderer
(build-session's `session-page-format.md` plus `render.md`) and the
`> [!encounter-meta]` block that files onto those pages
(`lib/encounter-meta-format.md`, shipped by symlink into each skill that
composes or reads the block; the combat-generator skill's *Filing format*
section cites the spec rather than restating it, and owns what goes in its
fields), all library-owned;
campaign-side tooling that parses them adapts when the library updates. Those
are install-time decisions, not per-campaign negotiations. The session page's
*skeleton* is likewise library-owned (the WotC 2024 adventure-chapter
convention); campaigns own where session pages live and the method rules
layered on top. Which skills have to be installed *together* for those
assumptions to hold is never an install-time decision: every skill installs
alone and degrades gracefully when an optional companion is absent.

| Slot | What the campaign's docs should answer | Read by |
|---|---|---|
| Method handbook | Where the repo's planning-method conventions live (the guide should point at it) | all planning skills |
| Live layer + progress marker | What's in motion — timelines, threads, revelation tracking — and the canonical marker of campaign progress | catch-up, build-session |
| Session records / prep home | Where played-session records and prep pages live (the page format itself is library-owned) | catch-up, build-session, review-rewards |
| Player pages / party cache | Where player characters are tracked, and where the synced party JSON lands | party-sync, build-session, combat-generator, catch-up, review-rewards |
| Session transcripts | Where recordings/transcripts of play land, if the campaign keeps them | catch-up |
| Reward economy | What treasure and payment run on (gold? favors?) | build-session (the keyed-site procedure) |
| Approved-items list | Which magic/notable items may be placed silently, and where the list lives (review-rewards rewrites it as the Approved Reward Pool) | build-session (the keyed-site procedure), review-rewards |
| Reward review state | Where the review-rewards app's tracked JSON state lives — versioned, outside the wiki/site bundle (fallback: `rewards-review/` at the campaign root) | review-rewards |
| Combat evidence | Where structured combat data from played sessions lands, if kept (fallback: encounter-meta `Spotlight:` lines) | build-session, combat-generator |
| Media dir + style anchor | Where images live; optionally an existing image that anchors the house style | campaign-art |
| Sync camp | How changes land — direct to main, or PR flow | party-sync (and any skill that commits) |

Skills with no rows of their own (seed-clues, to-session-brief) resolve
everything through the method handbook and the repo guide. `to-session-brief`
reads that record and publishes to the campaign repo's **tracker**, so it lands
nothing in the record and claims no slot. See the per-skill SKILL.md for the
authoritative probe text on every slot.

## Sync obligations — maintainers only

The library-owned formats above are coupled across skills, so a shape change
is a breaking change: it lands in one commit with everything that reads it,
called out in the commit message so campaign-side parsers can adapt. Each
skill carries a pointer here at its coupling site; the obligations themselves
live here, out of the shipped skill bodies.

| Shape | Owned by | Must move in the same commit |
|---|---|---|
| `> [!encounter-meta]` block | the library (`lib/encounter-meta-format.md`), shipped by symlink into combat-generator and build-session — so each skill installs alone with the shape it needs | combat-generator's SKILL.md, whose *Filing format* section cites the spec and owns what goes in the fields; build-session's keyed-site procedure (`dungeon.md`), which files its fights in the same shape, and its `session-page-format.md`, which cites the spec for the page's fights; catch-up, which reads its `Spotlight:` field as half the fired/denied ledger. The two code paths that read the block are `build-session/scripts/session_parser.py` and the mechanical checker (`lib/mechanical-checker/checker.py`). |
| The `Spotlight (scene):` line | build-session (*session-page-format.md*, Conventions) | build-session's keyed-site procedure (`dungeon.md`), which files one for a keyed area's non-combat beat; catch-up, which reads it as the other half of the fired/denied ledger — the non-fight one |
| `xp-budget.md`, `complications.md` | combat-generator (skill-internal) | Nobody loads these across a skill boundary — they sit beside the fight steps inside combat-generator, and build-session's page and keyed-site flows size fights by invoking `/combat-generator`, which owns these files |
| `spotlight-doctrine.md`, `class-patterns.md` — the data ladder lives inside `spotlight-doctrine.md` | the library (`lib/spotlight-doctrine.md`, `lib/class-patterns.md`), shipped by symlink into build-session and combat-generator | build-session's spotlight and keyed-site procedures (`spotlight.md`, `dungeon.md`) and the combat-generator skill load them beside themselves; party-sync loads `spotlight-doctrine.md` across the skill boundary (guarded, *"if that skill is installed"*); `catch-up` reads the page's annotations and loads neither |
| The **session spotlight plan** — transient, handed back in-run, never filed | build-session (`spotlight.md`, *Allocating the plan*) | build-session's Step 3, which loads `spotlight.md` and spends the plan inside the same run; the keyed-site procedure and the combat-generator skill, which are handed a beat from it and spend that instead of allocating texture independently inside a session build |
| The **findings-log record schema** — the `"run"` and `"finding"` lines of `.claude/validator-findings/findings.jsonl` | `lib/mechanical-checker/findings_log.py`, the canonical definition and the only code that writes it — both tiers call it since the verification-chain cut gave the judgement tier real parameters (`verdict`, `quoted_span`, `reason`) | `lib/mechanical-checker/self-heal-loop.md`, whose pseudocode carries the mechanical call sites; the fresh-check log instructions in the shared protocol (`lib/verification.md`, Part 2), which build-session's and combat-generator's procedures run; and the schema bullets in `lib/mechanical-checker/README.md`. The old unpinned by-hand judgement writer is retired; a field change now lands in the module and its tests first |
| The **shared verification protocol** — the two-part done-gate | the library (`lib/verification.md`), shipped by symlink into build-session and combat-generator | every definition-of-done section that runs it and names its own check ids and criteria: build-session's SKILL.md Steps 6–7 and `dungeon.md`, and combat-generator's SKILL.md |

The session-page skeleton's own coupling (`render.md` and
`scripts/session_parser.py`) stays noted inside build-session, where the
parser lives. Of the two block-shaped conventions, the `Spotlight (scene):`
line stays in `session-page-format.md` and the encounter-meta block lives in
`lib/encounter-meta-format.md`; their deliberate separation (a scene line
never sits inside an encounter-meta block, so the fight-variety ledger stays
fights-only) is stated once in the block's own file, which the page format
cites.

### When a shape change lands: sweep for the phrase it falsifies

This table is prose, and nothing consults it — which is how `d1a08f9` changed a
fact in `build-session/SKILL.md` and left six other locations asserting the old
one. Reading it is a step a human has to remember, and no check covers the
omission.

So a commit that changes what a coupled shape asserts carries two things: the
change, and the consumers named in the row above. Before calling it done, grep
the tree for the sentence it just falsified — the failure that actually occurs
is a **reversal** stated in words that survived somewhere.

### The rules-sourcing doctrine has one copy

The *"Rules sourcing — non-negotiable"* block used to be duplicated across the
two generator skills, with `lib/doctrine_sync.py` holding the copies together.
The generator merge retired both the duplication and the guard, and the
combat-generator hoist moved the statement to its final home: the doctrine
now lives once, at the top of `lib/rules-sourcing.md`, beside the chain it
binds, and materialises by symlink into every skill that places rules
content — combat-generator, build-session (whose keyed-site procedure
`dungeon.md` points at it), party-sync, review-rewards — like the bundled
SRD dataset (`lib/srd/`) and the mechanical checker. An edit to the doctrine
is an ordinary single-file edit.
