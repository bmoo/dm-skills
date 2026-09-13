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
method vocabulary (nodes, clue webs, revelations, live layer), Shea's eight
steps as the prep procedure, and the skill's output formats — the prep
sheet's shape (prep-session's *Sheet format and filing*, held by its format
lint) and the `> [!encounter-meta]` block that files onto sheets and node
pages (`lib/encounter-meta-format.md`, shipped by symlink into
combat-generator, whose *Filing format* section cites the spec rather than
restating it and owns what goes in its fields), all library-owned;
campaign-side tooling that parses them adapts when the library updates. Those
are install-time decisions, not per-campaign negotiations. Campaigns own where
sheets live and the house rules layered on top of the steps, in their method
handbook. Which skills have to be installed *together* for those assumptions
to hold is never an install-time decision: every skill installs alone and
degrades gracefully when an optional companion is absent.

| Slot | What the campaign's docs should answer | Read by |
|---|---|---|
| Method handbook | Where the repo's planning-method conventions live (the guide should point at it) | all planning skills |
| Live layer + progress marker | What's in motion — timelines, threads, revelation tracking — and the canonical marker of campaign progress; next session date, session horizon, and groomer loose ends / contradictions when the campaign schema defines them | catch-up, prep-session, groom-wiki |
| Session records / prep home | Where played-session records and prep sheets live (the sheet's shape itself is library-owned) | catch-up, prep-session, review-rewards |
| Player pages / party cache | Where player characters are tracked, and where the synced party JSON lands | party-sync, prep-session, combat-generator, catch-up, review-rewards |
| Session transcripts | Where recordings/transcripts of play land, if the campaign keeps them | catch-up |
| Reward economy | What treasure and payment run on (gold? favors?) | prep-session (the rewards step) |
| Approved-items list | Which magic/notable items may be placed silently, and where the list lives (review-rewards rewrites it as the Approved Reward Pool) | prep-session (the rewards step), review-rewards |
| Reward review state | Where the review-rewards app's tracked JSON state lives — versioned, outside the wiki/site bundle (fallback: `rewards-review/` at the campaign root) | review-rewards |
| Combat evidence | Where structured combat data from played sessions lands, if kept (fallback: encounter-meta `Spotlight:` lines with catch-up's fired/denied marks) | combat-generator |
| Media dir + style anchor | Where images live; optionally an existing image that anchors the house style | campaign-art |
| Sync camp | How changes land — direct to main, or PR flow | party-sync (and any skill that commits) |

A skill with no rows of its own (seed-clues) resolves everything through the
method handbook and the repo guide. See the per-skill SKILL.md for the
authoritative probe text on every slot.

## Sync obligations — maintainers only

The library-owned formats above are coupled across skills, so a shape change
is a breaking change: it lands in one commit with everything that reads it,
called out in the commit message so campaign-side parsers can adapt. Each
skill carries a pointer here at its coupling site; the obligations themselves
live here, out of the shipped skill bodies.

| Shape | Owned by | Must move in the same commit |
|---|---|---|
| `> [!encounter-meta]` block | the library (`lib/encounter-meta-format.md`), shipped by symlink into combat-generator | combat-generator's SKILL.md, whose *Filing format* section cites the spec and owns what goes in the fields; prep-session, which embeds the block as-is under its scenes and *Relevant Monsters*; catch-up, which marks the block's `Spotlight:` opportunity fired or denied after play. The one code path that reads the block is the mechanical checker (`skills/combat-generator/scripts/mechanical_checker/checker.py`). |
| `xp-budget.md`, `complications.md` | combat-generator (skill-internal) | Nobody loads these across a skill boundary — they sit beside the fight steps inside combat-generator, and prep-session sizes fights by invoking `/combat-generator`, which owns these files |
| `spotlight-doctrine.md`, `class-patterns.md` — the data ladder lives inside `spotlight-doctrine.md` | the library (`lib/spotlight-doctrine.md`, `lib/class-patterns.md`), shipped by symlink into combat-generator | combat-generator loads them beside itself; party-sync loads `spotlight-doctrine.md` across the skill boundary (`../combat-generator/`, guarded, *"if that skill is installed"*); `catch-up` and `prep-session` load neither |
| The **findings-log record schema** — the `"run"` and `"finding"` lines of `.claude/validator-findings/findings.jsonl` | combat-generator's `scripts/mechanical_checker/findings_log.py`, the canonical definition and the only code that writes it — both tiers call it since the verification-chain cut gave the judgement tier real parameters (`verdict`, `quoted_span`, `reason`) | `self-heal-loop.md` beside the module, whose pseudocode carries the mechanical call sites; the fresh-check log instructions in the verification protocol (`skills/combat-generator/verification.md`, Part 2), which combat-generator's procedure runs; and the schema bullets in the module's `README.md`. The old unpinned by-hand judgement writer is retired; a field change now lands in the module and its tests first |
| The **verification protocol** — the two-part done-gate | combat-generator (`skills/combat-generator/verification.md`), skill-internal since the checker move | combat-generator's SKILL.md, whose definition-of-done section runs it and names its own check ids and criteria |
| `contradiction` callouts and the generated `Loose ends` section | the campaign schema (`lib/wiki-scaffold/template/wiki-schema.md` in the shipped scaffold) | `groom-wiki` / `okf-groom.py`, which place findings; `catch-up`, which clears settled callout pairs and invokes the groomer to refresh loose ends; `prep-session`, which reads both shapes. Cross-skill invocation is guarded with "if installed". |
| Live-layer `next_session` and live-layer/prep `stale_after` | the campaign schema's *Session horizon* rule; `okf_config.py` supplies `SESSION_WEEKDAY` | `catch-up` (next date and live-layer horizon, clearing the played session's horizon); `prep-session` (sheet horizon and date rollover after cancellation); `groom-wiki` / `okf-groom.py` (reads and reports staleness without setting dates). |

### When a shape change lands: sweep for the phrase it falsifies

This table is prose, and nothing consults it — which is how `d1a08f9` changed a
fact in one skill's SKILL.md and left six other locations asserting the old
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
content — combat-generator, prep-session, party-sync, review-rewards — like
the bundled SRD dataset (`lib/srd/`) and the mechanical checker. An edit to the doctrine
is an ordinary single-file edit.
