---
name: to-session-brief
description: >-
  Turn the current planning conversation into a session brief — the contract
  of hard-to-reverse decisions a session build is held to — and publish it to
  the campaign's issue tracker.
disable-model-invocation: true
---

# To Session Brief

Produce a **session brief** from the current conversation and the campaign
record: the contract of hard-to-reverse decisions the session build is bound
by. **Synthesize, never invent** — every Locked line traces to something the
DM has already said or something the record already holds, and the checkpoint
in step 2 is the only question you put to the DM. A decision nobody has made
is handed back there as an open question, so a thin brief is a legitimate
output.

The bar for a Locked line is the *generation* horizon, not the table horizon
— the template's Locked preamble states the rule.

## Process

1. **Read the campaign record.** Explore the campaign repo to understand
   where play stands, if you haven't already: its own guide, the
   planning-method handbook that guide points at, the glossary, and any
   standing decision records covering what tonight touches. Write the brief
   in the campaign's domain vocabulary, and respect the decisions already on
   the record.

2. **Draft the Locked lines and put them in front of the DM.** Show the
   actual lines, not a summary of them, and name what the conversation and
   the record left genuinely open. Nothing is published before the DM's yes.

3. **Write the brief from the template below and publish it.** Before
   publishing, answer one question:

   > **Is every object, vehicle or rule the premise depends on either locked
   > here or already on the record?**

   If something the premise cannot run without is neither, it needs a Locked
   line — the premise's own mechanism is the thing a brief is most likely to
   leave free.

   Then publish: a **top-level** ticket on the campaign repo's own issue
   tracker — the repo this skill is installed in, not this library's — with
   no parent and the `ready-for-agent` triage label. The tracker and
   triage-label vocabulary are provided in your context. There is no draft
   state and no status field: **a published brief is in force.**

<brief-template>

# Session Brief — <session name>

Session: <n>  ·  Party level: <x>

## Locked

Each line is a proposition about the finished page — something a reader who has
never seen this conversation can mark pass or fail. If a line cannot be marked,
it is not a constraint; delete it.

Write a line only for what a regeneration could not undo. A decision that is
wrong-but-editable does not belong here even when it matters. Under
`NPC commitments`, name only those an edit could not route around.

### Canon — what becomes true, and cannot be un-trued by editing
- **Premise.** One sentence: what is happening tonight and why the party is in it.
  *(graded by build-session's fresh check: does the page enact it)*
- **Introduced canon.** Facts tonight asserts that the record does not already
  hold — or "none; all derived." *(checked as a diff against the campaign canon
  record, which the checker is handed)*
- **Environmental ground rules.** The named ground rules of tonight's place,
  stated before any room or NPC is keyed — with its home: node canon /
  campaign reference / **introduced here**. Or "none; standard play."
- **NPC commitments.** Per named NPC: identity, allegiance, and whether they
  survive.
- **Timeline commitments.** The question that resolves tonight, either way —
  with the schedule as optional fill where one exists.

### Web — what the clue web can no longer route around
- **Revelation paid down.** Which one tonight advances, and to what state.
- **Destination node(s).** Where the session is aimed. Earlier leads already
  point into these.
- **Exit edge.** Where the party can leave toward, per `seed-clues` Step 5.

### Layout — what the geography commits to
- **Map topology.** The shape.
- **Fit to established geography.** *(graded by build-session's fresh check)*

## Not tonight

Named and deliberately excluded, so their absence reads as a decision rather
than an oversight.

</brief-template>
