"""Campaign-specific configuration for the OKF tooling.

Directory layout, catalog labels, and campaign conventions live here; the
scripts consume the same configuration across campaigns.
"""

# Bundle location relative to the repository root.
BUNDLE_ROOT = "."

# The catalog's H1; set this to your campaign's name.
WIKI_TITLE = "The Emberwick Vale"

# Opening prose in the generated root catalog.
WIKI_INTRO = (
    "This catalog lists the bundle's concepts and is generated from their"
    " frontmatter by `scripts/okf-index.py` — edit the concepts, not this file."
)

# Concept directories relative to the bundle root.
BUNDLE_DIRS = ["nodes", "story", "players", "sessions"]

# Concepts at the bundle root.
ROOT_CONCEPTS = ["wiki-schema.md"]

# Directories never walked for concepts, at any depth.
EXCLUDED = ["scripts", "docs", "media", ".claude", ".git", ".obsidian"]

# Catalog groups in display order: (directory, label, description).
GROUPS = [
    ("nodes", "Nodes", "The people, places, factions, and events the party can investigate."),
    ("nodes/locations", "Locations", "Places the campaign can visit."),
    ("nodes/factions", "Factions", "Organizations and groups."),
    ("nodes/npcs", "NPCs", "Non-player characters."),
    ("nodes/events", "Events", "Events and time-based phenomena."),
    ("story", "Story", "Campaign arcs, status, and open questions."),
    ("players", "Players", "Player characters."),
    ("sessions", "Sessions", "Session prep and recaps."),
]

# Cross-cutting tags from the campaign schema's suggested vocabulary.
SUGGESTED_TAGS = {
    "pc", "recurring", "antagonist", "patron", "hub", "historical", "played",
    "live-layer", "prep-sheet", "seeds", "dungeon", "rewards",
}

# Filler words inside hyphenated concept basenames that never stand alone as a
# setting tag: `the-trust` exempts `trust`, not `the`.
TAG_STOPWORDS = {"the", "of", "and", "a"}

# Expected type by immediate bundle-relative directory; extend for local layouts.
# Root concepts (ROOT_CONCEPTS) live under the "." key; without one their type
# is neither checked nor backfilled. Schema, readme, and seed-ideas concepts
# keep their own types regardless.
DIRECTORY_TYPES = {
    "nodes/locations": "location",
    "nodes/factions": "faction",
    "nodes/npcs": "npc",
    "nodes/events": "event",
    "story": "story",
    "players": "player",
    "sessions": "session",
}

# Default real-world game night proposed by catch-up; None means ask.
# Use a lowercase English weekday, e.g. "tuesday". The campaign guide owns
# the local timezone; writers use its offset at the next morning's midnight.
SESSION_WEEKDAY = None

# Legacy metadata migration. Set these before running okf-migrate.py; source
# timestamps are retained (date-only values become midnight UTC). Existing
# generated metadata wins over an obsolete source key, which is then removed.
# Missing source timestamps are left for a provenance-aware hand pass.
MIGRATION_SOURCE_KEY = "timestamp"  # e.g. "last_updated" in a bot-written bundle
MIGRATION_ACTOR = "human:brad"
MIGRATION_STATUS_MAP = {
    "stub": "draft", "prep": "draft", "active": "stable", "canon": "stable",
    "inactive": "deprecated", "superseded": "deprecated",
    "proposed": "draft", "accepted": "stable", "amended": "stable",
    "accepted (amended)": "stable",
}
# ADR lifecycle survives separately from the universal OKF status. Only
# concepts of MIGRATION_DECISION_TYPE (by frontmatter or directory) receive a
# `decision:`; a legacy status missing from this map is reported at migrate
# time so the gap is not first seen at the strict gate. `active` is the common
# v0.1 spelling of an ADR that is in force.
MIGRATION_DECISION_TYPE = "design-decision"
MIGRATION_DECISION_MAP = {
    "proposed": "proposed", "accepted": "accepted", "active": "accepted",
    "amended": "amended", "accepted (amended)": "amended",
}
# Backfill only missing type/title, using DIRECTORY_TYPES and H1.
MIGRATION_BACKFILL_TYPE = True
MIGRATION_BACKFILL_TITLE = True
