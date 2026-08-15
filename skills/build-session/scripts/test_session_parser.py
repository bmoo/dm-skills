import pytest
from pathlib import Path
from session_parser import parse_session, parse_session_text

FIXTURES = Path(__file__).parent / "fixtures"

def test_parse_frontmatter():
    result = parse_session(FIXTURES / "minimal.md")
    assert result["frontmatter"]["title"] == "Test Adventure"
    assert result["frontmatter"]["level"] == 1

def test_parse_frontmatter_optional_fields():
    result = parse_session(FIXTURES / "minimal.md")
    assert result["frontmatter"].get("campaign") is None

def test_missing_frontmatter():
    result = parse_session_text("# Just a header\n\nSome text.")
    assert result["frontmatter"] == {}
    assert len(result["sections"]) == 1

def test_parse_top_level_sections():
    result = parse_session(FIXTURES / "minimal.md")
    sections = result["sections"]
    assert len(sections) == 2
    assert sections[0]["title"] == "Key Plot Points"
    assert sections[0]["level"] == 1
    assert "**The Hook.**" in sections[0]["body"]

def test_section_tree_nesting():
    md = """---
title: Test
---

# Cave System

## Cave Features

### Light
The cave is dark.

## Cave Locations

### C1: Entrance
A narrow opening.

### C2: Main Chamber

#### Goblin Scout
*Small Fey*
- AC 15, HP 7
"""
    result = parse_session_text(md)
    cave = result["sections"][0]
    assert cave["title"] == "Cave System"
    assert len(cave["children"]) == 2  # Features + Locations

    locations = cave["children"][1]
    assert locations["title"] == "Cave Locations"
    assert len(locations["children"]) == 2  # C1 + C2

    c2 = locations["children"][1]
    assert c2["title"] == "C2: Main Chamber"
    assert len(c2["children"]) == 1  # Goblin Scout stat block
    assert c2["children"][0]["title"] == "Goblin Scout"
    assert c2["children"][0]["level"] == 4

def test_extract_read_aloud_directive():
    md = """---
title: Test
---

# Location

> [!read-aloud]
> A grand hall stretches before you.
> Torches flicker on the walls.

The hall is 30 feet wide.
"""
    result = parse_session_text(md)
    room = result["sections"][0]
    elements = room["elements"]
    assert any(e["type"] == "read-aloud" for e in elements)
    ra = next(e for e in elements if e["type"] == "read-aloud")
    assert "grand hall" in ra["content"]

def test_extract_dm_sidebar_directive():
    md = """---
title: Test
---

# Conclusion

> [!dm-sidebar]
> **Between Sessions**
> Ask each player how they felt.

"""
    result = parse_session_text(md)
    elements = result["sections"][0]["elements"]
    assert any(e["type"] == "dm-sidebar" for e in elements)

def test_extract_map_directive():
    md = """---
title: Test
---

# Cave

> [!map]
> title: Cave Complex
> source: dmg/cave-complex-1

"""
    result = parse_session_text(md)
    elements = result["sections"][0]["elements"]
    map_el = next(e for e in elements if e["type"] == "map")
    assert map_el["attrs"]["title"] == "Cave Complex"
    assert map_el["attrs"]["source"] == "dmg/cave-complex-1"

def test_extract_encounter_meta_directive():
    md = """---
title: Test
---

# Fight

> [!encounter-meta]
> **Party:** 5 Level 1 characters
> **Enemies:** 1 Goblin Boss (CR 1)
> **XP Budget:** 200 XP

"""
    result = parse_session_text(md)
    elements = result["sections"][0]["elements"]
    assert any(e["type"] == "encounter-meta" for e in elements)


def test_extract_hazard_directive():
    md = """---
title: Test
---

# Desert

> [!hazard]
> name: Lightning Strikes
> severity: Deadly
> levels: 5-10
> description: Bolts of lightning arc from the sky.

"""
    result = parse_session_text(md)
    elements = result["sections"][0]["elements"]
    hazard = next(e for e in elements if e["type"] == "hazard")
    assert hazard["attrs"]["name"] == "Lightning Strikes"
    assert hazard["attrs"]["severity"] == "Deadly"
    assert hazard["attrs"]["levels"] == "5-10"


def test_extract_contagion_directive():
    md = """---
title: Test
---

# Plague

> [!contagion]
> name: Shaking Plague
> type: Magical Contagion
> description: Victims develop uncontrollable tremors.

"""
    result = parse_session_text(md)
    elements = result["sections"][0]["elements"]
    con = next(e for e in elements if e["type"] == "contagion")
    assert con["attrs"]["name"] == "Shaking Plague"
    assert con["attrs"]["type"] == "Magical Contagion"


def test_extract_npc_quote_directive():
    md = """---
title: Test
---

# Journey

> [!npc-quote]
> speaker: Sheriff Markham
> quote: Winter always takes its toll.

"""
    result = parse_session_text(md)
    elements = result["sections"][0]["elements"]
    quote = next(e for e in elements if e["type"] == "npc-quote")
    assert quote["attrs"]["speaker"] == "Sheriff Markham"
    assert quote["attrs"]["quote"] == "Winter always takes its toll."


def test_extract_sidebar_directive():
    md = """---
title: Test
---

# Lore

> [!sidebar]
> title: Karlach Cliffgate
> content: A tiefling barbarian from Avernus.

"""
    result = parse_session_text(md)
    elements = result["sections"][0]["elements"]
    sb = next(e for e in elements if e["type"] == "sidebar")
    assert sb["attrs"]["title"] == "Karlach Cliffgate"
    assert "tiefling" in sb["attrs"]["content"]


def test_extract_page_break_directive():
    md = """---
title: Test
---

# Part One

Some text.

> [!page-break]

# Part Two

More text.
"""
    result = parse_session_text(md)
    # page-break becomes an element in Part One's body
    elements = result["sections"][0]["elements"]
    assert any(e["type"] == "page-break" for e in elements)


def test_extract_art_directive():
    md = """---
title: Test
---

# Scene

> [!art]
> image: goblin-battle.jpg
> caption: Goblins attack the party
> position: right

"""
    result = parse_session_text(md)
    elements = result["sections"][0]["elements"]
    art = next(e for e in elements if e["type"] == "art")
    assert art["attrs"]["image"] == "goblin-battle.jpg"
    assert art["attrs"]["caption"] == "Goblins attack the party"
    assert art["attrs"]["position"] == "right"


def test_extract_art_embed_shape():
    md = """---
title: Test
---

# Scene

> [!art-left]
> ![Jimmy at the turnstile](../Media/images/turnstile.png)
> *"One price, kid: good for every day you're here."*

"""
    result = parse_session_text(md)
    elements = result["sections"][0]["elements"]
    art = next(e for e in elements if e["type"] == "art")
    assert art["attrs"]["image"] == "../Media/images/turnstile.png"
    # the bare line (colon and all) is the caption, italics stripped
    assert art["attrs"]["caption"] == '"One price, kid: good for every day you\'re here."'
    assert art["attrs"]["position"] == "left"


def test_extract_art_embed_alt_text_caption_fallback():
    md = """---
title: Test
---

# Scene

> [!art]
> ![The Archive fight](archive.png)

"""
    result = parse_session_text(md)
    elements = result["sections"][0]["elements"]
    art = next(e for e in elements if e["type"] == "art")
    assert art["attrs"]["image"] == "archive.png"
    assert art["attrs"]["caption"] == "The Archive fight"
    assert "position" not in art["attrs"]
