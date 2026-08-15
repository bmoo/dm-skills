from templates import (render_read_aloud, render_dm_sidebar, render_encounter_meta,
                        render_map, render_page_header, render_document, render_section,
                        render_hazard, render_contagion, render_npc_quote,
                        render_sidebar_box, render_page_break)

def test_render_read_aloud():
    html = render_read_aloud("A grand hall stretches before you.")
    assert 'class="read-aloud"' in html
    assert "grand hall" in html

def test_render_dm_sidebar():
    html = render_dm_sidebar("**Between Sessions**\nAsk each player.")
    assert 'class="dm-sidebar"' in html
    assert "Between Sessions" in html

def test_render_encounter_meta():
    html = render_encounter_meta("**Party:** 5 Level 1\n**Enemies:** 1 Goblin")
    assert 'class="encounter-meta"' in html

def test_render_map_with_image():
    html = render_map({"title": "Cave Complex", "image": "maps/cave.png"}, base_path="/tmp")
    assert 'class="map-container"' in html
    assert "Cave Complex" in html

def test_render_map_without_source_or_image():
    html = render_map({"title": "My Map"}, base_path="/tmp")
    assert html == ""  # No source or image = no map rendered

def test_render_page_header():
    fm = {"title": "Death at Sunset", "level": 1, "estimated_sessions": "1-2",
          "setting": "any heavily forested region"}
    html = render_page_header(fm)
    assert "Death at Sunset" in html
    assert "Level 1" in html

def test_render_document_wraps_in_html():
    html = render_document("<p>content</p>", {"title": "Test"})
    assert "<html" in html
    assert "<style>" in html
    assert "content" in html

def test_render_section_with_elements():
    section = {
        "title": "R1: Entry Hall", "level": 3, "children": [],
        "body": "The hall is 30 feet wide.",
        "elements": [
            {"type": "read-aloud", "content": "A grand hall stretches before you."},
            {"type": "text", "content": "The hall is 30 feet wide."},
        ],
    }
    html = render_section(section, base_path="/tmp")
    assert "read-aloud" in html
    assert "grand hall" in html
    assert "30 feet wide" in html
    assert "R1: Entry Hall" in html

def test_render_section_recursive_children():
    section = {
        "title": "Cave System", "level": 1, "body": "",
        "elements": [],
        "children": [{
            "title": "Cave Locations", "level": 2, "body": "",
            "elements": [],
            "children": [{
                "title": "C1: Entrance", "level": 3,
                "body": "A narrow opening.", "elements": [], "children": [],
            }],
        }],
    }
    html = render_section(section, base_path="/tmp")
    assert "Cave System" in html
    assert "Cave Locations" in html
    assert "C1: Entrance" in html

def test_render_section_key_npcs_table():
    section = {
        "title": "Key NPCs", "level": 1,
        "body": "| Name | Role | Stat Block | Location |\n|---|---|---|---|\n| Joon | Guide | Druid | H1 |",
        "elements": [], "children": [],
    }
    html = render_section(section, base_path="/tmp")
    assert "<table" in html
    assert "Joon" in html


def test_render_hazard():
    html = render_hazard({"name": "Bile Lichen", "severity": "Deadly", "levels": "1-4",
                          "description": "Toxic spores fill the air."})
    assert 'class="hazard-block"' in html
    assert "Bile Lichen" in html
    assert "Deadly Hazard" in html
    assert "Levels 1-4" in html
    assert "Toxic spores" in html


def test_render_hazard_minimal():
    html = render_hazard({"name": "Sinkhole"})
    assert "Sinkhole" in html
    assert "Hazard" in html


def test_render_contagion():
    html = render_contagion({"name": "Shaking Plague", "type": "Magical Contagion",
                             "description": "Victims develop tremors."})
    assert 'class="contagion-block"' in html
    assert "Shaking Plague" in html
    assert "Magical Contagion" in html
    assert "tremors" in html


def test_render_npc_quote():
    html = render_npc_quote({"speaker": "Sheriff Markham",
                             "quote": "Winter always takes its toll."})
    assert 'class="npc-quote"' in html
    assert "Winter always takes its toll." in html
    assert "Sheriff Markham" in html


def test_render_npc_quote_empty():
    html = render_npc_quote({})
    assert html == ""


def test_render_sidebar_box():
    html = render_sidebar_box({"title": "Karlach Cliffgate",
                               "content": "A tiefling barbarian."})
    assert 'class="sidebar-box"' in html
    assert "Karlach Cliffgate" in html
    assert "tiefling" in html


def test_render_page_break():
    html = render_page_break()
    assert 'class="page-break"' in html


def test_render_page_header_with_region_and_tagline():
    fm = {"title": "Tide of Teeth", "level": 3,
          "region": "Baldur's Gate", "tagline": "Solve a dockside murder."}
    html = render_page_header(fm)
    assert "Tide of Teeth" in html
    assert "region-tag" in html
    assert "Baldur" in html
    assert "adventure-tagline" in html
    assert "dockside murder" in html


def test_render_map_with_player_variant():
    html = render_map({"title": "Warehouse", "image": "maps/warehouse-dm.jpg",
                       "player_image": "maps/warehouse-player.jpg"}, base_path="/tmp")
    assert "Warehouse" in html
    assert "map-player-note" in html
    assert "warehouse-player" in html


def test_render_map_with_source():
    html = render_map({"title": "Cave", "image": "maps/cave.png",
                       "source": "DMG Appendix B"}, base_path="/tmp")
    assert "DMG Appendix B" in html
    assert "map-source" in html


def test_render_section_with_new_directives():
    """All new directive types render without errors in a section."""
    section = {
        "title": "Test Section", "level": 2, "body": "", "children": [],
        "elements": [
            {"type": "hazard", "attrs": {"name": "Trap", "severity": "Nuisance", "levels": "1-4"}},
            {"type": "npc-quote", "attrs": {"speaker": "Alias", "quote": "Stay sharp."}},
            {"type": "sidebar", "attrs": {"title": "Lore", "content": "Ancient ruins."}},
            {"type": "page-break"},
            {"type": "text", "content": "Some body text."},
        ],
    }
    html = render_section(section, base_path="/tmp")
    assert "hazard-block" in html
    assert "npc-quote" in html
    assert "sidebar-box" in html
    assert "page-break" in html
    assert "body text" in html


def test_render_map_with_labels_stamps_image(tmp_path):
    """When labels are present and image exists, render_map produces a stamped image."""
    from PIL import Image as PILImage
    img = PILImage.new("RGB", (100, 100), (200, 200, 200))
    img_path = str(tmp_path / "player.jpg")
    img.save(img_path)

    attrs = {
        "title": "Test Map",
        "image": img_path,
        "labels": "A1(50,50)",
    }
    html = render_map(attrs, base_path=str(tmp_path), theme="ocean")
    assert 'class="map-container"' in html
    assert "Test Map" in html
    assert "_labeled.jpg" in html

def test_render_map_with_labels_missing_image():
    """When labels are present but image file doesn't exist, fall back gracefully."""
    attrs = {
        "title": "Ghost Map",
        "image": "/nonexistent/map.jpg",
        "labels": "A1(50,50)",
    }
    html = render_map(attrs, base_path="/tmp", theme="ocean")
    assert 'class="map-container"' in html
    assert "Ghost Map" in html
    assert "_labeled" not in html
