# Spotlight doctrine — shoot your monks

A build is a **statement**: *this is what I want to do at the table*. Most of
a statement is reactive or situational — a Monk with Deflect Attacks needs
someone shooting at them — so the DM decides whether it ever fires. Design
that ignores statements wastes the player's investment; design that honors
them produces the moments campaigns are remembered by. The DM's job is to
lose: players countering your monsters isn't the game breaking, it *is* the
game.

(Distilled from "Shoot Your Monks," an episode by the [Dungeon Dudes](https://www.youtube.com/@DungeonDudes)
(Monty Martin and Kelly McLaughlin, 2025), verified against the 2024 rules;
the vocabulary here follows the episode's where it does.)

## The session budget

Spotlight is budgeted at the **session and scenario-group level, not per
situation**:

- **Every PC gets a beat somewhere across a scenario group — in any pillar.**
  The Rogue's beat may be the impossible lock, not a fight; a social scene
  where the Bard's charm *works* spends the budget as legitimately as a fight
  staged for Deflect Attacks.
- **No single situation must aim at anyone.** Plain, unengineered situations
  are the baseline that makes the aimed ones feel aimed.
- **The fiction picks the roster; the spotlight picks the presentation.**
  Choose enemies, NPCs, and obstacles for the place and the faction, then
  stage them so the flagged ability comes up. Never bend the roster to the
  build — if the roster can't serve the first-choice spotlight, aim at a
  different PC.

## The texture palette

Give every designed situation exactly one **texture**, and rotate:

- **Aimed** — staged so one or two named PCs' flagged abilities fire.
- **Puzzle** — one PC's ability is the key to winning; expect the players to
  take a few beats to notice the answer is on their own sheet.
- **Steamroll** — the party's cool tricks just win: Turn Undead vaporizes the
  horde, Fireball clears the room, or the Bard talks the whole fight out of
  existence. A trounced encounter is fun, not a balance failure — and price a
  social win as a real victory, never a skipped scene.
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
  always save, the guard who "doesn't need" the Bard's distraction — repeated
  denial reads as the DM playing against the players, and it's the fastest
  way to make an investment feel wasted.

## Legibility

Anti-tell hides the tell from veterans; **Legibility is its inverse** — it
governs *how plainly the DM points at an aimed beat*, calibrated to how much
D&D the player has under their belt. A newcomer can miss that a beat is
theirs even when it fires. The canonical failure: a brand-new player's
*Speak with Animals* pulls the night's richest clue out of a pen of
frightened sheep — the beat was staged for them and it fired — but they
don't read the moment as *theirs*, and it never lands as a win. The fix is
not more staging; it is telegraphing the staged beat loudly enough for
*that* player to catch it.

**Legibility is orthogonal to the texture palette.** Texture picks *what*
fires (Aimed, Puzzle, …); legibility picks *how plainly the DM signposts it*.
The two never collide — every Aimed or Puzzle beat carries both a texture and
a legibility read.

Each PC carries a **Table experience** rung. The canonical vocabulary — a
three-rung ordinal — lives here and nowhere else:

- **`new`** — new to D&D. **Telegraph the beat explicitly**: name the opening
  in the fiction, or say plainly that this is their moment, so they recognize
  it's theirs and take it up. *(New-vs-seasoned, same beat: to a `new`
  player the sheep's answer arrives as "the sheep are agitated — you're the
  only one who can ask them what they saw; what do you do?")*
- **`learning`** — building fluency. **A light nudge** — surface the hook and
  let them make the connection: a nod toward the opening, not a spelled-out
  prompt.
- **`seasoned`** — reads the table. **Keep the tell subtle** — stage the
  opening and let them find it; signposting reads as heavy-handed. *(Same
  beat, seasoned: "the sheep are milling and bleating at the far fence" — and
  nothing more.)* This is where Anti-tell governs.

The rung lives on each player page, at the top of its Spotlight-profile
player half — DM-observed, set by hand. It is **purely manual**: no skill
writes or graduates it (not catch-up, not party-sync). And it is **never
defaulted** — a prep skill that needs it and finds it missing asks the DM,
naming the three choices (`new` · `learning` · `seasoned`); an off-list
value is rejected loudly, never silently coerced.

## The flagging heuristic

An ability is **flagged** — spotlight-worthy, needing DM setup to fire — when
it is any of:

- **Reactive** — needs a trigger the DM controls: Deflect Attacks, Riposte,
  Countercharm, Counterspell.
- **Situational** — needs terrain, an enemy type, or a condition to matter:
  Danger Sense, Turn Undead, Devil's Sight, Acrobatic Movement.
- **A niche pick** — a chosen spell, feat, or invocation that begs a scene it
  can win: Detect Thoughts, Arcane Lock, Speak with Animals. A player's picks
  are statements too.

Tag every flag with the **pillar** it lives in (combat / social /
exploration) and the **staging** that fires it. Always-on output is not a
flag — though its *enablers* are (Sneak Attack isn't flagged; the shadows,
perch, and flanking ally that feed it are staging).

## Evidence and precedence

- **Interpretation** lives in the player pages' Spotlight profiles. Character
  half: the flagged list, written by party-sync at sync time. Player half:
  observed play, written by catch-up from this campaign's transcripts only.
  Precedence: **observed play > build choices > class-generic patterns**.
- **Evidence** lives in the campaign record's structured combat data — the
  encounter ledger and per-session JSONs. The **variety check** reads it
  mechanically: don't repeat the recent fights' spotlight target, texture, or
  primary enemy type. Fallback before played sessions exist: `Spotlight:`
  lines in prepped encounter-meta blocks.
- **Fired/denied history feeds pacing.** A statement repeatedly staged but
  never fired should get louder in future prep; one that fired big last
  session can rest.
