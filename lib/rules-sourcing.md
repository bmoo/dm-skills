# Rules sourcing — the doctrine and the chain

Where rules content — stat blocks, XP values, class features, spells, item
text, trap and door mechanics — comes from. **This file is the library's one
statement of the sourcing doctrine**; every skill that places rules content
follows it.

- **MUST** source all rules content — monster stat blocks, XP values, item
  text, trap and door mechanics, any rules detail — from the chain below,
  never from training-data memory (the 2024 rules differ from 2014). Look up
  every creature and item you place; confirm a creature's XP before you
  spend it.
- **MUST** browse the chosen source's catalog (its listings, filtered by
  type/CR/etc.) *before* shortlisting — never shortlist from memory, which
  silently defaults to famous core-book entries and ignores what the table's
  sources actually offer.

## The chain

Take the first rung that answers; never skip past the chain to training-data
memory.

1. **The campaign's own content tools.** If this environment has a D&D content
   lookup tool installed (an MCP server or similar), use it. Whatever the
   table has plugged in is the authority on its own content — prefer it
   without comment on where its content comes from.
2. **The bundled SRD.** The [`srd/`](srd/) directory beside this file carries
   the complete System Reference Document 5.2 dataset as JSON, one file per
   content type (`creatures.json`, `spells.json`, `classes.json`, `feats.json`,
   `items.json`, `weapons.json`, `armor.json`, and the rest — see
   [`srd/ATTRIBUTION.md`](srd/ATTRIBUTION.md) for provenance and license).
   Look entities up by their `name` field; a creature's XP rides on its
   challenge rating.
3. **Neither answers?** The content is outside the SRD and no tool carries it.
   Tell the DM exactly which numbers could not be sourced — never fill the gap
   from memory. The table's own books cover the rest.

The dataset is imported from Open5e's `srd-2024` document (CC-BY-4.0). To
refresh it after WotC errata, re-run the import against
`https://api.open5e.com/v2/` and keep `ATTRIBUTION.md` beside the data.
