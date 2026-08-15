# Review state — the two JSON files

The shapes the bundled app enforces. `scripts/review_state.py` is the
enforcing validator — both the server and `ingest.py` run it, so a payload
that drifts from this page is rejected, never silently accepted.
`scripts/fixtures/review-data.json` is a complete worked example.

## `review-data.json` — the catalog (agent-authored, written once per review)

| Field | Shape | Meaning |
|---|---|---|
| `catalogVersion` | string | Stamp it fresh every generation (ISO time plus a short suffix). Decision state echoes it; a mismatch is stale and refuses to ingest. |
| `partyLevel` | int | From the campaign record — it is authoritative for level. |
| `proposalStandard` | string | The one-sentence standard candidates were held to; copied into the pool header. |
| `protectedChallenges` | list of strings | One short clause per prepared challenge — its name plus the core mechanic rewards must not cancel. Copied verbatim into the pool header, so keep it a clause, never the prep paragraph. |
| `requestedDepth` | `{"perPC": n, "party": n}` | The depth this run was asked for (default 5/5, or the DM's override). |
| `entries` | list | One object per item, all origins mixed. |

Each entry:

| Field | Required | Meaning |
|---|---|---|
| `id` | always | Unique slug, `<item-name>--<source-slug>`. Duplicate ids, or two entries sharing name+source, are ambiguous identity and fail validation. |
| `name`, `source`, `rarity`, `attunement` | always | Authoritative item name and provenance. `attunement` is the human string ("no attunement", "requires attunement by a druid"). |
| `rulesText` | always | The **full official rules text, verbatim** — the DM approves the actual item, never a paraphrase. |
| `origin` | always | `existing` (already in the pool), `candidate` (new this review), `awarded` (read-only history, for loot parity), `graveyard` (removed in a prior review; stays collapsed until restored). |
| `target`, `fitNote` | all origins except `awarded` | One active PC's name or `party`, plus the one concise campaign sentence: how it helps that target. |
| `gearRelation`, `challengeNote` | optional | Relationship to existing gear; any Protected Challenge interaction. |
| `owner` | optional | For `awarded` entries: who holds it. |

## `decisions.json` — the decision state (server-written only)

```json
{
  "catalogVersion": "<echoed from the catalog>",
  "decisions": {
    "<entry id>": {
      "decision": "unreviewed | approve | defer | remove",
      "note": "optional",
      "deferCondition": "optional; only with decision defer"
    }
  }
}
```

The localhost server is the only writer. Graveyard semantics: a
graveyard-origin entry **with no record stays removed**; an explicit record —
even `unreviewed` — is the DM restoring it into active review.

## Carrying decisions forward

The files persist between reviews (tracked in git, outside the wiki bundle).
When generating a new catalog, read the previous one plus its decisions:

- prior `approve` on `existing`/`candidate` entries → this catalog's `existing` entries;
- prior `remove` (and unrestored `graveyard`) → this catalog's `graveyard`
  entries, excluded from ordinary candidate research;
- prior `defer` → re-propose as `candidate` only when its condition has been
  met, carrying the old note into `fitNote` context.

Then stamp a new `catalogVersion`; the old `decisions.json` is superseded (the
server refuses to start over a stale one — delete it after its content is
folded into the new catalog).
