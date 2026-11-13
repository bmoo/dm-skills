---
name: encounter-simulator
description: >-
  Play a prepped fight many times with dice and report how it tends to go:
  how often each side meets its objective, how many rounds it runs, who
  drops, what it costs the party, and which single change moves the result
  most. Use when the DM asks how a fight will go, whether it is too deadly
  or too soft, what a complication, timer, or reinforcement wave changes,
  or wants a fight tested before the session, and to replay a fight the
  table already played against its record.
---

# Encounter Simulator

The XP budget says how big a fight is. This skill says how the fight tends
to go. You **compile** the fight once into a scenario file, the DM
**reviews** what you compiled, and a dice engine **rolls** the fight as
many times as asked. The engine makes no model call and reads only the
scenario file.

Reference files sit beside this one. Load each when its step says to:

- [`scenario-format.md`](scenario-format.md) is the one statement of the
  scenario file's shape and of what the engine does with each field.
- [`rules-sourcing.md`](rules-sourcing.md) is the lookup chain for every
  number you compile.

## Inputs

- **The fight.** A fight the combat-generator skill delivered (pinned or
  floating), a `> [!encounter-meta]` block on a prep sheet or node page
  with the prose around it, or a fight the DM describes by hand. From a
  hand-described fight, take the enemies, the ground, and what each side
  wants. Ask in one line for whichever of the three is missing.
- **The party.** Read the campaign repo's guide (`CLAUDE.md` or
  equivalent) for where player pages and the party cache live. When the
  repo does not say, ask the DM and offer to record the answer in its docs.
- **Combat evidence.** Where the guide names a home for structured combat
  data from played sessions, read it for Step 1's tactics cards and for
  the replay check. Use only this campaign's own record.

## Step 1: Compile the scenario

Open [`scenario-format.md`](scenario-format.md) and write
`<fight-slug>.scenario.json` beside the page that holds the fight. The
slug is the fight's title, or its place when it has no title, in lowercase
with hyphens. A fight that exists
only in chat compiles into the OS temp directory.

- **Combatants.** Look up every enemy through the chain in
  [`rules-sourcing.md`](rules-sourcing.md) and every player character from
  the party cache or the campaign's character tool. Copy the numbers. A
  number that no source supplies is a named gap: ask the DM for it, or
  write your guess into `assumptions` in plain words.
- **Actions.** Write one action for each thing a combatant can do on its
  turn, built from the seven effects. Fold an always-on rider (Sneak
  Attack, Rage damage) into the dice and name it in `assumptions`. Write a
  multiattack as `steps`. Write an extra-action feature (Action Surge) as
  a limited action whose `steps` list every attack of that whole turn, so
  one attack plus one surge is two steps. Mark everything
  else `unmodelled` with one sentence that says why. An honest gap in the
  report is worth more than a silent approximation.
- **Ground.** Make one zone for each area the fight's terrain names. For a
  floating fight, make one zone for each terrain role and keep the role
  names. Take distances from the prose. Where the prose gives none, link
  neighbouring zones at 30 feet and say so in `assumptions`.
- **Objectives and events.** Compile the fight's `Objective:` line and
  each complication into data, so the report can show whether the
  complication changes anything:

  | The fight says | Compile it as |
  |---|---|
  | A clock that favours one side | a `rounds` win condition for that side |
  | One target that matters | `defeat` with that `combatant` |
  | Leave with the prize, or get everyone out | `reach` a zone |
  | Reinforcements or waves | an `enter` event, with `unless_down` when someone must call them |
  | The ground changes or a hazard spreads | a `zone` event |
  | Enemies who do not fight to the death | `flee` on their tactics card |

- **Tactics cards.** Write the enemies' cards from the fight's tactics
  prose. Write each player character's card from how that player has
  played: the campaign's combat evidence first, the player page's observed
  style second. With neither, write a plain card (the character's usual
  attack, limited resources spent when hurt) and tell the DM the card is a
  guess.
- **Variants.** Add one variant for each complication with the
  complication removed, and one named `optimal play` that gives the party
  the cards a careful player would use. The engine adds the
  one-creature-more, one-creature-fewer, and who-acts-first variants
  itself.

Done when `python3 <this skill>/scripts/simulate.py check <scenario>`
prints `OK`. The check reports shape problems first, then ids and fights
that cannot be fought, so expect more than one round. Fix each problem in
the scenario file and run the check again.

## Step 2: Review with the DM

Run `python3 <this skill>/scripts/simulate.py review <scenario>` and show
the DM its output: every combatant's numbers and actions, each tactics
card, the events, the objectives, your assumptions, and everything marked
not modelled. Ask what is wrong or missing. Apply each correction to the
scenario file and run the check again.

Done when the DM says the compiled fight is the fight they prepped. Roll
nothing before that yes.

## Step 3: Roll

```
python3 <this skill>/scripts/simulate.py run <scenario> --runs 1000 --seed 1 --out <report.md>
```

Write the report to `<fight-slug>.report.md` in the OS temp directory. A
loose Markdown file inside a campaign wiki can fail that wiki's own
checks. The same seed gives the same report, so name the seed when you
quote a number. Use 1,000 runs unless the DM asks for another count.

## Step 4: Report

Read the report file and tell the DM, in this order:

1. How often each side met its objective, the spread of rounds, and what
   the fight cost the party.
2. Which player characters dropped to 0 hit points, and how often.
3. The change that moves the result most, and the other rows that are
   clear of noise. A row marked *within noise* is not a finding.
4. Everything under *Not modelled*, because those gaps bound how far the
   numbers can be trusted.
5. Where the two sample fights are, so the DM can check that a typical run
   and a bad run read like the fight they prepped.

Quote only numbers that the report contains. Then offer the next move: a
rerun with a change the DM names (add it as a variant, or edit the
scenario and review again), or a rebuild of the fight. Filing anything
onto a page is the DM's call, made once, after they have read the report.

## Replay check

A simulator that has never been checked against a real fight gives numbers
nobody can interpret. When the campaign keeps combat evidence, offer one
replay before the DM leans on a report:

1. Pick a fight the table already played, with enemies you can source.
2. Compile it as in Step 1 from what the DM knew **before** initiative.
   Take nothing from how the fight went: no rolled results, no rulings made
   mid-fight, no tactics seen only in that fight.
3. Write the record file (its shape closes `scenario-format.md`) from the
   played fight: rounds, damage dealt and taken, who dropped.
4. Run `python3 <this skill>/scripts/simulate.py replay <scenario> --record <record.json>`.
5. Tell the DM where each recorded number sits in the simulated spread and
   how wide that spread is. For each number outside the middle 80%, name
   the likely cause: something not modelled, a table ruling, or the dice.

One played fight is one sample. Report position and width, never "the
simulator is right".
