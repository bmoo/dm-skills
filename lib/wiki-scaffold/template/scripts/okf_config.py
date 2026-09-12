"""Campaign-specific configuration for the OKF tooling.

Directory layout, catalog labels, and campaign conventions live here; the
scripts consume the same configuration across campaigns.
"""

# Bundle location relative to the repository root.
BUNDLE_ROOT = "."

# The catalog's H1; set this to your campaign's name.
WIKI_TITLE = "Campaign Wiki"

# Opening prose in the generated root catalog.
WIKI_INTRO = (
    "Every concept below carries YAML frontmatter and a markdown"
    " body. This catalog is generated from that frontmatter by"
    " `scripts/okf-index.py` — edit the concepts, not this file."
)

# Directories inside the bundle; tooling and working docs stay outside it.
BUNDLE_DIRS = ["nodes", "story", "players", "sessions"]

# Concepts at the bundle root, outside the configured directories.
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

# Expected type by immediate bundle-relative directory; extend for local layouts.
DIRECTORY_TYPES = {
    "nodes/locations": "location",
    "nodes/factions": "faction",
    "nodes/npcs": "npc",
    "nodes/events": "event",
    "story": "story",
    "players": "player",
    "sessions": "session",
}

# Expected type for root concepts; schema and readme concepts keep their own types.
ROOT_TYPE = "reference"

# Default real-world game night proposed by catch-up; None means ask.
# Use a lowercase English weekday, e.g. "tuesday". The campaign guide owns
# the local timezone; writers use its offset at the next morning's midnight.
SESSION_WEEKDAY = None
