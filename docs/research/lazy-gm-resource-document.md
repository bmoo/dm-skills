# What the Lazy GM's Resource Document carries of the eight steps, and Shea's guidance on reducing prep

Research note for [issue #88](https://github.com/bmoo/dm-skills/issues/88),
part of the build-session retirement map
([#87](https://github.com/bmoo/dm-skills/issues/87)). Written 2026-09-13.

**Question.** The library is replacing `build-session` with a port of
sd-campaign's `lazy-dm` skill, and the shipped skill may cite only the
CC-BY-4.0 *Lazy GM's Resource Document*. For each of Shea's eight prep steps,
which concrete rules does the resource document actually state, and which
exist only in the books? What does Shea say about reducing the checklist and
about prep scale? What is the licence and attribution line? And where does the
current sd-campaign skill over-prescribe relative to the document?

**Method.** The resource document was fetched directly from slyflourish.com
(single self-contained HTML, "Updated 24 December 2024") and converted to
text; every quotation below is from that text. Shea's articles were fetched
from slyflourish.com the same way. The vendored book in
`~/dev/sd-campaign/reference/lazy-dm/` and the sd-campaign skill and audit
were read as context only, to tell document-carried from book-only; they
are not cited as sources and nothing is quoted from the book.

**Two licence facts shape everything below** (details in §3):

- The resource document is **CC BY 4.0** — the shipped skill may quote it,
  adapt it, and cite it, with the attribution line the document prescribes.
- Shea's **articles** on slyflourish.com carry a **CC BY-NC 4.0** footer.
  The library is CC BY 4.0 prose plus MIT code and is meant for anyone's use,
  so article text cannot be copied into the shipped skill. Articles can be
  *linked* as further reading and their guidance restated in the skill's own
  words; the book cannot be linked or quoted at all.

---

## 1. Per-step: what the resource document states versus what is book-only

Source for the "document states" column: *The Lazy GM's Resource Document*,
section "The Eight Steps of Lazy RPG Prep" and its eight sub-headings —
<https://slyflourish.com/lazy_gm_resource_document.html>. The whole
eight-step section is about 700 words; each step is one or two short
paragraphs. Quotations are exact.

| Step | What the resource document states | Book-only (Return of the Lazy Dungeon Master / Companion) — restate or drop |
| --- | --- | --- |
| 1. Review the characters | "Before we do anything else, it helps to spend a few minutes reviewing the player characters. What are their names? What do they want? What plays into their backgrounds? What do the players of these characters enjoy at the table?" and "You might not even write anything down during this step, but reviewing the characters helps wire them into your mind — and ensures that the rest of your preparation fits around them." Off-sheet by design; no output required. | The book's chapter adds the fuller "write down names, backgrounds, motivations" routine and its examples. Shea's 2023 review article adds the per-PC question "What hook can I include in the next session to draw this character into the game?" (article, BY-NC — restate, don't quote). Nothing numeric is book-only here. |
| 2. Create a strong start | "How a game starts is likely the most important piece of preparation we can do." "When you define where a game session starts, you figure out what's going on, what the initial focus of the session is, and how you can get close to the action. When in doubt, start with a fight." Plus a separate "Example Strong Starts" section (40 one-line starts across Cities and Towns, Sewers, Wilderness, Dungeons) opening with "A strong start kicks your game off in the middle of the action." | The "one sentence or short paragraph" length and the "immediate event, hook, action" three-part shape are book chapter material. The document carries the *idea* (in the middle of the action, close to the action, when in doubt a fight) but not that shape. Restate in the skill's own words or drop the three-part test. |
| 3. Outline potential scenes | "outline a short list of potential scenes that might unfold. This step exists mostly to make you feel as though you have a handle on the game before you start." "Usually, it's enough to come up with only a few words per scene, and to expect one or two scenes per hour of play. At other times, you might skip this step completely if you don't think you need it." | **Document-carried**: a few words per scene, one to two per hour, skippable. Book adds "one or two lines per hour" phrasing and the sequential-versus-branching discussion. Scene *cards* with callouts and aimed-at-PC titles are sd-campaign invention, not Shea. |
| 4. Define secrets and clues | "second only in importance to the strong start". "Secrets and clues are single short sentences that describe a clue, a piece of the story, or a piece of the world that the characters can discover during the game. You don't know exactly how the characters will discover these clues. As such, you'll want to keep these secrets and clues abstract from their place of discovery". "During this step, you might write down ten such secrets or clues." Plus a "Creating Secrets and Clues" section: four categories (Character, Historical, NPC and Villain, Plot and Story) of ten prompt questions each, prefaced "secrets are meant to serve you. Don't overthink them or worry about making them perfect." | **Document-carried**: ten, one sentence each, abstract from place of discovery. Note the document says "you *might* write down ten" — it is a target, not "exactly ten". Book-only: the chapter's "Write Down Ten Secrets Per Session" heading and fresh-slate-every-session advice; the 2023 article explicitly walks the fresh-slate advice back ("bring forward any secrets that have yet to be uncovered and are still relevant"). |
| 5. Develop fantastic locations | "Building evocative locations isn't easily improvised. As such, it's worth spending time writing out a handful of fantastic locations". "Each location can be thought of as a set, a room, or a backdrop for a single scene". "Describe each location with a short evocative title such as 'The Sunspire.' Then write down three fantastic aspects for it" with three example aspects. "whole dungeons can be built from a series of connected fantastic locations". | **Document-carried**: evocative name plus three aspects; "a handful". Book-only: "one or two locations per hour of play" and the three-for-two-hours / five-for-three / seven-for-four table; the Fate-aspect lineage; "when in doubt, scale — big things, old things". The 2023 article and the 15-minute article both relax three aspects to "one to three" or name-only for minor locations (BY-NC; restate). |
| 6. Outline important NPCs | "we'll outline those NPCs (nonplayer characters) most critical to the adventure, focusing on a name and a connection to the adventure, then wrapping the NPC in a character archetype from popular fiction. Many other NPCs — maybe even most of them — can be improvised right at the table." | **No count anywhere.** The document gives shape (name, connection, archetype) and no number. The "about four" figure comes from Shea's 2019 Markdown prep template article, which has four blank NPC slots (BY-NC, and a template not a rule); the book's worked example uses four. "Never more than five" is sd-campaign's house cap. A three-column table is sd-campaign's format, not Shea's. |
| 7. Choose relevant monsters | "What monsters are the characters most likely to face? What monsters make sense for a specific location and situation?" "understanding the loose relationship between monster challenge rating and character level can help you understand how a battle might go. Most of the time, you can just list a number of monsters and improvise encounters based on what's happening in the adventure. For boss battles, you might have to do more work. See Lazy Combat Encounter Building for more information." The document also carries the full "5e Quick Encounter Building" ratio tables and "Lazy Combat Encounter Building for 5e" (the Lazy Encounter Benchmark: deadly if total monster CR exceeds one quarter of total character levels, one half at 5th+), all built on SRD 5.1 CR. | **Document-carried**: the step completes with a list of monsters; a rough danger gauge is enough; extra work only for boss fights. Book-only: the chapter's "prepare to improvise combat encounters" and "prepare boss fights" sub-routines. The library's `combat-generator` handoff for costed fights is the map's agreed departure, not Shea. The document's CR arithmetic is SRD 5.1-era; the library sizes with 2024 rules through `combat-generator` and should not re-teach the benchmark. |
| 8. Select magic item rewards | "Players love magic items, and it's worthwhile to spend time preparing items they'll find interesting. This step also helps to directly impact the characters — by dropping an interesting part of the story literally into their hands. You can use a mixture of techniques to reward magic items, from selecting items randomly to selecting specific items based on the themes of the characters and the desires of the players. Magic items are also a great mechanism for delivering secrets and clues." | **Book-only: "one useful magic item per session."** The document never states an item cadence. Also book-only: the wish-list routine and the two-question test (does it fit the story; has it been a while). PC anchoring and "their last reward" recency are the map's agreed departure plus sd-campaign bookkeeping, not Shea. Document-carried: mixture of random and character-fit selection, and items as secret-delivery vehicles. |

Two further document-carried facts the skill can lean on:

- The document's own reduced form (see §2): "**The 5-Minute Reduced
  Checklist** — If you have very little time, reduce the checklist to the
  most important things you can prepare before it's time to run the game.
  Here are three example steps. Create a strong start / Define secrets and
  clues / Develop fantastic locations."
- "**The Lazy RPG Prep Checklist and Online Play** — These steps and
  processes work just as well whether you interact with your players online
  or around the table."

What the document does **not** carry at all: any prep time budget, any
page-count target, any per-session item cadence, any NPC count, any
location-per-hour count, the "immediate event / hook / action" strong-start
shape, and the 30–60-minutes-before-play review. Every one of those is book
or article material.

## 2. Shea on reducing the checklist and on prep scale

### Reducing the checklist

- **Document (CC BY 4.0):** the three-step "5-Minute Reduced Checklist"
  quoted above — strong start, secrets and clues, fantastic locations —
  offered as "three example steps", not as the only valid reduction. Step 3
  is explicitly marked skippable in its own paragraph ("you might skip this
  step completely if you don't think you need it"); step 1 "You might not
  even write anything down"; step 6 "Many other NPCs — maybe even most of
  them — can be improvised right at the table"; step 7 "Most of the time,
  you can just list a number of monsters".
- **Article, "Choosing the Right Steps from the Lazy DM Checklist" (2019),
  <https://slyflourish.com/choosing_the_right_steps.html>:** which steps
  survive depends on the game. A continuous homebrew campaign "likely needs
  most, if not all the steps, each session". A continuous published
  adventure can drop scenes, locations, NPCs, monsters, and items, leaving
  review the characters, strong start, and secrets and clues. A published
  one-shot keeps only scenes (for timing) and secrets. Closing advice:
  consider which steps help most, "focus on those, reduce or remove the
  rest".
- **Article, "The Eight Steps of the Lazy DM – 2023 Review",
  <https://slyflourish.com/eight_steps_2023.html>:** the steps are
  "modular"; "some of these steps don't serve you and are easily skipped.
  That's perfect." Secrets and clues "may be the main one you want to
  include" whatever else is kept. Ends "Focus on what matters and omit what
  doesn't."
- **Article, "Prepare a D&D Game in 15 Minutes" (2021),
  <https://slyflourish.com/refined_five_minute_game_prep.html>:** a
  15-minute version is strong start (5 min), three to five locations with a
  name and *one* aspect (5 min), up to ten secrets (5 min).
- **Article, "Using the Lazy DM's Eight Steps At the Table",
  <https://slyflourish.com/using_the_8_steps_at_the_table.html>:** "I
  typically reveal half of the ten in a session"; NPCs — "Some GMs can get
  away with just a name"; monsters — "most often it's a simple list of
  monsters ... and either links to digital stat blocks or page numbers".
  During prep, "consider what you needed to run the NPC during the game and
  what you ignored. Now skip the stuff you ignored."

The book's own reduce-the-checklist chapter says the same three steps and
adds a "what gets lost" walk-through per skipped step; the document's version
is the citable one and is sufficient.

### Prep scale

- **Time budget.** Not in the document. Shea's published figures: the book's
  front matter gives fifteen to thirty minutes for a four-hour game; the 2021
  15-minute article says "I find it takes me about 30 minutes to comfortably
  prepare for a game using the eight steps" and calls the old five-minute
  claim oversold; the 2020 "Spending a Whole Day Preparing a D&D Game"
  article (<https://slyflourish.com/whole_day_dnd_prep.html>) says "We don't
  often have more than 30 minutes to an hour to prepare" and reports that a
  whole day "led to diminishing returns". Safe restatement for the skill:
  about half an hour of prep for a four-hour session.
- **Page count of Shea's own notes.** Not in the document. The book's
  completed example (Scourge of Volixus) is described there as about as long
  as checklist notes ever get and still fitting "a page or two". Shea's 2019
  template article
  (<https://slyflourish.com/rotldm_template.html>) shows his actual
  Shadow of the Demon Lord notes: six one-line character entries, a
  one-sentence strong start, five one-line scenes, ten secrets, six
  locations as `Name: aspect, aspect, aspect`, four NPCs, a monster list, a
  treasure list. That is the scale the port should aim at: a sheet a DM
  reads in a couple of minutes.
- **"Prep what you can't improvise."** Shea does not use that exact
  sentence. The nearest citable statements: document, step 5 — "Building
  evocative locations isn't easily improvised"; 2023 article — the steps
  help GMs "prepare what they need to improvise at the table"; "Using the
  Eight Steps At the Table" — the steps "help GMs focus on the most valuable
  material one can prepare to help them improvise during their game" and
  "You're not planning the game when preparing them. You're not building a
  story." The 2025 "Improv Versus Prep" article
  (<https://slyflourish.com/improv_vs_prep.html>) gives the test the skill
  should adopt in its own words: look at what you actually used at the
  table, and next time prepare only that — "I know I can't come up with
  great secrets and clues to drop in my game on the fly ... So secrets are
  something I definitely prepare ahead of time. Same with strong starts."
- **Review before play.** The 30–60-minutes-before-the-table review is
  book-only (the "Our Preparation Notes So Far" chapter). The document does
  not state it. Keep it as the skill's own advice or drop it.

## 3. Licence and attribution

Source: the document's header,
<https://slyflourish.com/lazy_gm_resource_document.html>, exact text:

> This work is licensed under a Creative Commons Attribution 4.0
> International License. You are free to use this content in any manner
> permitted by that license as long as you include the following attribution
> statement in your own work:
>
> This work includes material taken from the Lazy GM's Resource Document by
> Michael E. Shea of SlyFlourish.com, available under a Creative Commons
> Attribution 4.0 International License.
>
> This work includes material taken from the System Reference Document 5.1
> ("SRD 5.1") by Wizards of the Coast LLC and available at
> https://dnd.wizards.com/resources/systems-reference-document. The SRD 5.1
> is licensed under the Creative Commons Attribution 4.0 International
> License available at https://creativecommons.org/licenses/by/4.0/legalcode.

The correct `NOTICE.md` line is therefore exactly:

> This work includes material taken from the Lazy GM's Resource Document by
> Michael E. Shea of SlyFlourish.com, available under a Creative Commons
> Attribution 4.0 International License.

`NOTICE.md` already carries that sentence verbatim under "Lazy GM's Resource
Document (Sly Flourish)"; the swap only needs its second paragraph changed
from `skills/build-session/` to `skills/prep-session/`. The library's own
SRD notice cites SRD 5.2.1, not 5.1; that is fine so long as the skill takes
no SRD 5.1 text *through* the resource document (its CR tables are the only
SRD-derived material in the eight-step area, and the port does not need
them).

Related provenance:

- The document says it is "taken from several books written by Michael E.
  Shea". Shea's 2023 article names them: "material from Return of the Lazy
  Dungeon Master, the Lazy DM's Workbook, and the Lazy DM's Companion ...
  available to read, copy, or use, even commercially, under a Creative
  Commons Attribution license." There is **no separate "Lazy DM's Companion
  SRD"**; the resource document *is* the CC release of the Companion
  material. Search of slyflourish.com and the shop found no other Companion
  SRD page.
- Crit.Tech's mirror (<https://github.com/crit-tech/LGMRD>) carries the same
  content as Markdown/JSON/EPUB under the same licence; cite the
  slyflourish.com page as canonical.
- Shea's **articles** end with: "This work is released under a Creative
  Commons Attribution-NonCommercial 4.0 International license ... by
  including the following statement in the new work: This work includes
  material taken from SlyFlourish.com by Michael E. Shea available under a
  Creative Commons Attribution-NonCommercial 4.0 International license."
  Do not paste article prose into the skill.
- The original 2012 *The Lazy Dungeon Master* is online at
  <https://slyflourish.com/the_lazy_dungeon_master_cc.html> under
  CC BY-NC-SA 4.0, with a 2023 note from Shea that some of its advice he "no
  longer believe[s] in". Not a citation target.

## 4. Where the sd-campaign skill over-prescribes relative to the document

Read against `~/dev/sd-campaign/.claude/skills/lazy-dm/SKILL.md` and its
audit of 2026-09-06 (context only). Each item names the skill's rule, then
what the document supports. The port ticket can treat this as its cut list.

1. **"Exactly ten" secrets, fresh list every session.** Document: "you
   might write down ten"; Shea (2023) now carries uncovered secrets forward.
   Port: "about ten", and carrying forward unrevealed ones is normal.
2. **"About four, never more than five" NPCs, three-column table.** Document
   gives no count and no table — name, connection, popular-fiction archetype.
   The map already sends the five-NPC cap to sd-campaign's handbook. Port:
   the NPCs who matter this session, each a name, a connection, an archetype;
   no cap, no mandated table.
3. **"Exactly three aspects", "one to two locations per hour", "big things,
   old things".** Document: three aspects, "a handful" of locations; the
   per-hour count and scale advice are book-only. Shea's later articles relax
   aspects for minor locations. Port: name plus up to three aspects, a
   handful.
4. **Strong start must carry "immediate event, hook, and action"; "a generic
   opener fails the step"; combat-by-default in prepared mode.** Document:
   start in the middle of the action, close to the action, "When in doubt,
   start with a fight". Port: keep "when in doubt, a fight" as the
   document's tiebreak, not a default; drop the three-part test or restate
   it as the skill's own gloss.
5. **Scene cards as callouts with aimed-at-PC titles, one bullet each,
   nested encounter blocks, `###` part headings, and the "expect half to go
   unused" doctrine.** Document: a few words per scene, one or two per hour,
   skippable outright. Port: a plain list; the card syntax is sd-campaign's
   renderer coupling, which the map says stays behind.
6. **Step 7 requires costed floating fights in "prepared" mode, with a
   two-mode scope decision made before step 2.** Document: the step
   completes with a list of monsters and a rough danger gauge; more work only
   for boss battles. The map keeps the `combat-generator` handoff for fights
   the DM wants costed, so the port should invert the default: list first,
   cost on request (the audit's ticket #131 said the same).
7. **Rewards: every item PC-anchored, overdue-PC-first ranking against a
   loot ledger, dndbeyond links, a mandated three-column table, "one useful
   item per session".** Document: mix random and character-fit selection;
   items carry secrets. PC-anchoring is the map's agreed seam; the ranking
   rule, ledger, link requirement, and table shape are sd-campaign
   machinery, and the per-session cadence is book-only. Port: anchored
   items, no ranking algorithm, no cadence.
8. **Step 1 as a "done when every expected PC is aimed at somewhere on the
   sheet" gate.** Document: review the characters so the rest of prep fits
   around them; nothing need be written. Port: keep it off-sheet and
   ungated; Shea's per-PC hook question is a good prompt, restated.
9. **One-page strictness, contents jump bar, whole-line-italic ban,
   semantic-minimality review on every delivery, `validate_sheet.py`.** The
   document says nothing about page length; Shea's own notes run a page or
   two. The map already keeps only the format lint. Port: "short enough to
   read in a few minutes" as advice, the lint as the only check.
10. **"Run all eight in order; report a deliberately skipped step."** The
    document and every article make steps optional and game-dependent, and
    the document ships a three-step reduced form. Port: default to all eight
    for a homebrew campaign (Shea's own advice for that case), and name the
    three-step reduction as a first-class mode rather than an exception to
    report.
11. **Citing the book by chapter.** Every `reference/lazy-dm/NN_*.md` link
    must go; the only citable source is the document URL, and the only
    quotable text is the document's.

## Sources

Primary (fetched 2026-09-13):

- The Lazy GM's Resource Document, Michael E. Shea, updated 24 December 2024, CC BY 4.0 — <https://slyflourish.com/lazy_gm_resource_document.html>
- Crit.Tech mirror in Markdown/JSON/EPUB — <https://github.com/crit-tech/LGMRD>
- The Eight Steps of the Lazy DM – 2023 Review — <https://slyflourish.com/eight_steps_2023.html>
- Choosing the Right Steps from the Lazy DM Checklist (2019) — <https://slyflourish.com/choosing_the_right_steps.html>
- Prepare a D&D Game in 15 Minutes (2021) — <https://slyflourish.com/refined_five_minute_game_prep.html>
- Lazy Dungeon Master Adventure Prep Template (2019) — <https://slyflourish.com/rotldm_template.html>
- Using the Lazy DM's Eight Steps At the Table — <https://slyflourish.com/using_the_8_steps_at_the_table.html>
- Spending a Whole Day Preparing a D&D Game (2020) — <https://slyflourish.com/whole_day_dnd_prep.html>
- Improv Versus Prep (2025) — <https://slyflourish.com/improv_vs_prep.html>
- Secrets and Clues, the Secret Weapon of the Lazy Dungeon Master — <https://slyflourish.com/sharing_secrets.html>
- The Lazy Dungeon Master (2012, CC BY-NC-SA 4.0) — <https://slyflourish.com/the_lazy_dungeon_master_cc.html>

Context only, not cited: `~/dev/sd-campaign/.claude/skills/lazy-dm/SKILL.md`,
`~/dev/sd-campaign/docs/lazy-dm-book-alignment-audit-2026-09-06.md`, and the
vendored book under `~/dev/sd-campaign/reference/lazy-dm/`.
