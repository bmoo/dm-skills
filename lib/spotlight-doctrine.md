# Spotlight doctrine — shoot your monks

A build is a **statement**: *this is what I want to do at the table*. Most of
a statement is reactive or situational — a Monk with Deflect Attacks needs
someone shooting at them — so the DM decides whether it ever fires. Fights
that ignore statements waste the player's investment; fights that honor them
produce the moments campaigns are remembered by. The DM's job is to lose:
players countering your monsters isn't the game breaking, it *is* the game.

(Distilled from "Shoot Your Monks," an episode by the [Dungeon Dudes](https://www.youtube.com/@DungeonDudes)
(Monty Martin and Kelly McLaughlin, 2025), verified against the 2024 rules;
the vocabulary here follows the episode's where it does.)

## Fights only

This doctrine governs **fights** — the situations `combat-generator` builds.
Scenes, NPCs, and the rest of prep take no spotlight allocation, no coverage
pass, and no requirement that every PC receive a beat; character review
shapes them the way the resource document says it should, off-sheet.

- **The fiction picks the roster; the spotlight picks the presentation.**
  Choose enemies for the place and the faction, then stage them so a flagged
  ability *can* come up. Never bend the roster to the build — if the roster
  can't serve the first-choice spotlight, aim at a different PC or don't aim.
- **No fight must aim at anyone.** Plain, unengineered fights are the
  baseline that makes the aimed ones feel aimed.
- **Stage opportunities, never outcomes.** A fight's `Spotlight:` field names
  an opportunity and the conditions that make it available. A PC named there
  is an intended beneficiary; it never assigns the actor, an ability, or
  success. The players may resolve any fight another way — talking it out,
  routing around it — and that is a real victory, never a skipped fight.

## The texture palette

Give every designed fight exactly one **texture**, and rotate:

- **Aimed** — staged so one or two named PCs' flagged abilities can fire.
- **Puzzle** — one PC's ability is the key to winning; expect the players to
  take a few beats to notice the answer is on their own sheet.
- **Steamroll** — the party's cool tricks just win: Turn Undead vaporizes the
  horde, Fireball clears the room. A trounced encounter is fun, not a balance
  failure.
- **Plain** — fiction-first, nobody aimed at. Legitimate and necessary.
- **Curveball** — deliberately denies the party's usual tricks (the
  anti-magic guardian, the enemy that can't be stunned). **On request only**,
  roughly once per adventure: name whose tricks it denies, and follow it with
  a steamroll that lets the denied abilities shine extra hard.

## Anti-tell

Players learn engineered patterns fast — ranged enemies appear and the table
mutters "Monk fight." Defenses:

- **Never the same staging for the same PC twice running.** Prefer the class
  entry's less obvious pattern: not every Monk beat needs archers — a chase,
  verticality, or a stun-worthy lieutenant are all Monk food.
- **Let the staging emerge from terrain and enemy goals**; don't inject the
  signature prop.
- **Never counter by habit.** Immunities that nullify a build, enemies that
  always save — repeated denial reads as the DM playing against the players,
  and it's the fastest way to make an investment feel wasted.

## Legibility

Anti-tell hides the tell from veterans; **Legibility is its inverse** — it
governs *how plainly the DM points at an aimed beat*, calibrated to how much
D&D the player has under their belt. A newcomer can miss that a beat is
theirs even when it fires — staged for them, fired, and never read as
*theirs*, so it never lands as a win. The fix is not more staging; it is
telegraphing the staged beat loudly enough for *that* player to catch it.
Every Aimed or Puzzle beat carries both a texture (*what* fires) and a
legibility read (*how plainly it's signposted*).

Each PC carries a **Table experience** rung. The canonical vocabulary — a
three-rung ordinal — lives here and nowhere else:

- **`new`** — new to D&D. **Telegraph the beat explicitly**: name the opening
  in the fiction, or say plainly that this is their moment. *(A Deflect
  Attacks beat arrives as "the archers on the wall have you in their sights —
  and you know exactly what your hands do with an arrow; what do you do?")*
- **`learning`** — building fluency. **A light nudge** — surface the hook and
  let them make the connection: a nod toward the opening, not a spelled-out
  prompt.
- **`seasoned`** — reads the table. **Keep the tell subtle** — stage the
  opening and let them find it; signposting reads as heavy-handed. *(Same
  beat, seasoned: "the archers nock" — and nothing more.)* This is where
  Anti-tell governs.

The rung lives on each player page, at the top of its Spotlight-profile
player half — DM-observed, set by hand. It is **purely manual**: no skill
writes or graduates it (not catch-up, not party-sync). And it is **never
defaulted** — a skill that needs it and finds it missing asks the DM, naming
the three choices (`new` · `learning` · `seasoned`); an off-list value is
rejected loudly, never silently coerced.

## The flagging heuristic

An ability is **flagged** — spotlight-worthy in a fight, needing DM setup to
fire — when it is any of:

- **Reactive** — needs a trigger the DM controls: Deflect Attacks, Riposte,
  Countercharm, Counterspell.
- **Situational** — needs terrain, an enemy type, or a condition to matter:
  Danger Sense, Turn Undead, Devil's Sight, Acrobatic Movement.
- **A niche pick** — a chosen spell, feat, or invocation that begs a fight it
  can win: Counterspell, Repelling Blast, Spike Growth. A player's picks are
  statements too.

Tag every flag with the **staging** that fires it. Always-on output is not a
flag — though its *enablers* are (Sneak Attack isn't flagged; the shadows,
perch, and flanking ally that feed it are staging). The flagged list is
combat-relevant abilities only.

## The data ladder

Reading a PC for a fight's spotlight climbs down this ladder — take the
highest rung that is present and fresh. The ladder self-heals: the DM never
has to remember the dependency.

1. **The Spotlight profile** on the player page. Its *character half* is the
   flagged-ability list party-sync precomputes at sync time; its *player
   half* is observed play, maintained by catch-up from this campaign's
   sessions. Player half outranks character half; both outrank class-generic
   patterns.
2. **Profile missing or stale (>7 days)?** Derive the flags live: read the
   party cache wherever this repo keeps synced sheets, look up the build's
   features at its level via the sourcing chain in
   [`rules-sourcing.md`](rules-sourcing.md), and apply the flagging
   heuristic above. Offer to persist the result to the profile. Never
   auto-trigger a re-scrape of a third-party service — a real re-sync is the
   DM's call.
3. **No party cache at all?** Say so and offer a party-sync run. Don't
   spotlight from memory.

## Evidence and precedence

- **Interpretation** lives in the player pages' Spotlight profiles. Character
  half: the flagged list, written by party-sync at sync time. Player half:
  observed play, written by catch-up from this campaign's sessions only.
  Precedence: **observed play > build choices > class-generic patterns**.
- **Evidence** lives in the campaign record's structured combat data where
  the repo's guide says it keeps any. **Only this campaign's record feeds
  it** — never another campaign's data, even for the same players. The
  **variety check** reads it mechanically: don't repeat the recent fights'
  spotlight target, texture, or primary enemy type. Fallback: the
  `Spotlight:` lines of encounter-meta blocks on prepped and played sheets
  ([`encounter-meta-format.md`](encounter-meta-format.md)), with catch-up's
  fired/denied marks beside them.
- **Fired/denied history feeds pacing.** Recorded from actual play, never
  from prep alone: an opportunity repeatedly staged but never taken should
  get louder in future fights; one that fired big last session can rest.
