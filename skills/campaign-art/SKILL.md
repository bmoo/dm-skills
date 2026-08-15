---
name: campaign-art
description: >-
  Generate illustrations for a campaign record using OpenAI's gpt-image-2
  model — NPC portraits, location establishing art, item and artifact
  studies, and scene illustrations. Use this skill whenever the DM wants to
  create, generate, illustrate, draw, render, or "make a picture/portrait/
  artwork" of anything in the campaign — an NPC, a location, a magic item,
  an event, or a freeform idea — or wants to visualize a campaign page.
---

# Campaign Art

Generate illustrations for the campaign record with OpenAI's `gpt-image-2`
model, then save them into the campaign's media directory. This skill turns a
campaign page (or a freeform description) into a finished PNG.

**Discovery first:** the campaign repo's guide (`CLAUDE.md` or equivalent, and
the docs it points to) owns two conventions this skill needs — **where images
live** (the media directory) and, optionally, a **style anchor**: an existing
image whose look keeps the campaign visually coherent. If the repo doesn't
declare a media directory, ask the DM and offer to record the answer in its
docs; a missing style anchor just means every image takes an explicit style
direction.

## Step 1 — Pin down the subject and the style

**Subject** — one of:

- An existing campaign page — an NPC, a location, an item, an
  event/phenomenon.
- A freeform description the DM gives you directly.

When the subject is a page, **read the whole page**. The page text is your
richest and most canon-accurate prompt source — use its words, don't invent.

**Style** — there is no locked house style; every image takes a style
direction. If the DM hasn't given one, ask for it. If the campaign's docs
name a style anchor image, offer its look as a quick default. For tight
consistency with an existing image (a recurring NPC, a returning location),
pass that image as a `--reference` (Step 4).

## Step 2 — Build the prompt

`gpt-image-2` reasons about composition before it paints, so it rewards
detailed, well-structured prompts. Compose the prompt from these labelled
parts — write them as flowing sentences, not literally as a form:

```
Shot & subject:   shot type + who/what it is — age, build, posture
Appearance:       face, hair, skin, marks; clothing/material in concrete detail
Action & framing: pose, what they hold, what's in frame, where the camera sits
Setting:          environment that grounds the subject in the campaign
Light & mood:     time of day, quality of light, emotional tone
Palette:          the dominant colours
Style:            the DM's style direction — rendering medium and influences
Exclude:          no text, captions, watermarks, or frame/border — unless asked
```

Pull the concrete details (an NPC's dress, a location's geography) straight
from the page. Ground every image in the campaign's setting as its reference
pages establish it — and let the page's tone carry any strangeness the
setting hides; don't force the uncanny where the page is plain.

**Frame it by subject type:**

- **NPC portrait** — three-quarter or full-body, subject centred and clearly the
  focus; environment hints at their role or faction without overwhelming them.
  Portrait orientation.
- **Location** — wide establishing shot, no people (or one small figure for
  scale); render it as a *campaign site* that conveys the page's mood, true to
  the setting's real geography where the campaign has one. Landscape
  orientation.
- **Item or artifact** — a focused study of the object; clean or softly
  atmospheric background so the item reads clearly; close framing. Square.
- **Scene or event** — a composed moment with one clear focal action; characters
  legible in the environment; stage it like a film still. Landscape orientation.

## Step 3 — Choose the size

Pass `--size` explicitly, matched to the subject:

| Subject              | Size        | Notes                          |
|----------------------|-------------|--------------------------------|
| NPC portrait         | `1024x1536` | portrait orientation           |
| Location / scene     | `1536x1024` | landscape establishing shot    |
| Item / artifact      | `1024x1024` | square study                   |

For extra detail, double the dimensions (`1536x2304`, `2304x1536`,
`1536x1536`) — all valid. Constraints: both edges multiples of 16, aspect ratio
≤ 3:1. Default `--quality` to `high`; drop to `medium` only to iterate cheaply
on composition before a final `high` render.

## Step 4 — Run the generator

The bundled script needs no dependencies and reads `OPENAI_API_KEY` from the
environment — a personal secret: it lives in your shell environment or a
user-level location, never in the campaign repo.

```bash
python3 <this skill's folder>/scripts/generate_image.py \
  --prompt "<the full prompt from Step 2>" \
  --output <media-dir>/<name>.png \
  --size 1024x1536 \
  --quality high
```

Run it from the repo root with a **generous Bash timeout (~300000 ms)** — the
model reasons before it paints, so a call commonly takes a minute or more.

**Reference images** — add `--reference <path>` (repeatable) to guide the
generation off existing art. This switches to the editing endpoint and is the
best way to keep a recurring character or location on-model — pass the style
anchor or the subject's previous image.

**Naming** — save into the media directory with a descriptive kebab-case
basename. Match the page basename so the pairing is obvious:
`npcs/silver-fox.md` → `silver-fox.png`. For an additional image of the same
subject, add a descriptive suffix: `silver-fox-hideout.png`.

## Step 5 — Check and report

After the script prints `saved: …`:

1. **Read the PNG** to eyeball it — right subject, faithful to the page, no
   garbled text or obvious artifacts. If it misses, adjust the prompt and re-run
   (or re-run as-is for a different take — generation is non-deterministic).
2. **Report the embed snippet** for the DM to paste, in standard Markdown
   image syntax with alt text and a path relative to the target page —
   e.g. for a page in `nodes/npcs/`:
   `![Silver Fox](../../Media/images/silver-fox.png)`.
3. **Offer**, but don't assume: to insert the embed at a sensible spot in the
   page and, if the repo keeps a change log, add an entry. Wait for the DM to
   say yes.

## Troubleshooting

- **HTTP 400 / size error** — check `--size`: both edges must be multiples of
  16 and the aspect ratio ≤ 3:1.
- **HTTP 401** — `OPENAI_API_KEY` is missing or invalid.
- **Moderation block** — rephrase the prompt; describe the subject without
  language that trips content filters.
