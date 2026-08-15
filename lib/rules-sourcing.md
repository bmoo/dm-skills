# Rules sourcing — the lookup chain

Where rules content — stat blocks, XP values, class features, spells, item
text — comes from. Take the first rung that answers; never skip past the chain
to training-data memory.

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
