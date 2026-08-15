"""Campaign-specific configuration for the wiki tooling.

Everything the check and index scripts know about *this* campaign lives here:
which directories make up the wiki, how they are labelled in the catalog, and
the prose the root catalog opens with. The scripts themselves are taxonomy-
agnostic — add a directory here and both tools pick it up.
"""

# The catalog's H1 and opening prose. Set the title to your campaign's name.
WIKI_TITLE = "Campaign Wiki"

WIKI_INTRO = (
    "Every page below is a wiki page with YAML frontmatter and a markdown"
    " body. This catalog is generated from that frontmatter by"
    " `scripts/wiki-index.py` — edit the pages, not this file."
)

# Directories that make up the wiki, relative to the repo root. Everything
# else in the repo (tooling, media, working docs) sits outside the wiki.
WIKI_DIRS = ["nodes", "story", "players", "sessions"]

# Wiki pages that live at the repo root.
WIKI_ROOT_FILES = ["wiki-schema.md"]

# Directories never walked for wiki pages, at any depth.
EXCLUDED = ["scripts", "docs", "Media", ".claude", ".git", ".obsidian"]

# Display names for wiki directories, in catalog order. A directory listed
# here gets its own index.md and its own section in the root catalog.
GROUPS = [
    ("nodes", "Nodes"),
    ("nodes/locations", "Locations"),
    ("nodes/factions", "Factions"),
    ("nodes/npcs", "NPCs"),
    ("nodes/events", "Events"),
    ("story", "Story"),
    ("players", "Players"),
    ("sessions", "Sessions"),
]
