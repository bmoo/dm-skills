"""HTML templates for session renderer.

Each function returns an HTML string fragment.
render_section is the recursive entry point for the section tree.
"""

import markdown
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
STYLES_PATH = SCRIPTS_DIR / "styles.css"
# Plugin root — two levels up from scripts/ to the dnd plugin root
PLUGIN_DIR = SCRIPTS_DIR.parent.parent.parent

_current_theme = "amber"


def _resolve_image_path(raw_path: str, base_path: str) -> str:
    """Resolve an image path, supporting $PLUGIN_DIR/ prefix for portability."""
    if raw_path.startswith("$PLUGIN_DIR/"):
        return str(PLUGIN_DIR / raw_path[len("$PLUGIN_DIR/"):])
    p = Path(raw_path)
    if p.is_absolute():
        return raw_path
    if base_path:
        return str(Path(base_path) / raw_path)
    return raw_path


def render_read_aloud(content: str) -> str:
    html_content = markdown.markdown(content)
    return f'<div class="read-aloud">{html_content}</div>'


def render_dm_sidebar(content: str) -> str:
    html_content = markdown.markdown(content)
    return f'<div class="dm-sidebar">{html_content}</div>'


def render_encounter_meta(content: str) -> str:
    html_content = markdown.markdown(content)
    return f'<div class="encounter-meta">{html_content}</div>'


def render_hazard(attrs: dict) -> str:
    """Render a hazard block with severity and level range."""
    name = attrs.get("name", "Hazard")
    severity = attrs.get("severity", "")
    levels = attrs.get("levels", "")
    description = attrs.get("description", "")
    meta = f"{severity} Hazard" if severity else "Hazard"
    if levels:
        meta += f" (Levels {levels})"
    desc_html = markdown.markdown(description) if description else ""
    return f'''<div class="hazard-block">
<div class="hazard-header"><span class="hazard-name">{name}</span><span class="hazard-meta">{meta}</span></div>
{desc_html}</div>'''


def render_contagion(attrs: dict) -> str:
    """Render a magical contagion/disease block."""
    name = attrs.get("name", "Contagion")
    ctype = attrs.get("type", "Magical Contagion")
    description = attrs.get("description", "")
    desc_html = markdown.markdown(description) if description else ""
    return f'''<div class="contagion-block">
<div class="contagion-header"><span class="contagion-name">{name}</span><span class="contagion-type">{ctype}</span></div>
{desc_html}</div>'''


def render_npc_quote(attrs: dict) -> str:
    """Render a pull-quote attributed to an NPC."""
    speaker = attrs.get("speaker", "")
    quote = attrs.get("quote", "")
    if not quote:
        return ""
    attr_html = f'<cite class="npc-quote-attribution">&mdash; {speaker}</cite>' if speaker else ""
    return f'''<blockquote class="npc-quote">
<p>{quote}</p>
{attr_html}</blockquote>'''


def render_sidebar_box(attrs: dict) -> str:
    """Render a sidebar callout box (lore, NPC, rules)."""
    title = attrs.get("title", "")
    content = attrs.get("content", "")
    content_html = markdown.markdown(content) if content else ""
    title_html = f'<div class="sidebar-box-title">{title}</div>' if title else ""
    return f'<div class="sidebar-box">{title_html}{content_html}</div>'


def render_page_break() -> str:
    """Render a page break for PDF output."""
    return '<div class="page-break"></div>'


def render_art(attrs: dict, base_path: str) -> str:
    """Render an inline illustration."""
    image = attrs.get("image", "")
    caption = attrs.get("caption", "")
    position = attrs.get("position", "center")  # center, left, right
    if not image:
        return ""
    img_path = _resolve_image_path(image, base_path)
    cap_html = f'<figcaption>{caption}</figcaption>' if caption else ""
    return f'<figure class="art art-{position}"><img src="{img_path}" alt="{caption}" />{cap_html}</figure>'


def render_map(attrs: dict, base_path: str, theme: str = "amber") -> str:
    source = attrs.get("source")
    image = attrs.get("image")
    player_image = attrs.get("player_image")
    labels_str = attrs.get("labels")
    title = attrs.get("title", "")
    if not source and not image:
        return ""
    img_path = _resolve_image_path(image, base_path) if image else ""
    if not img_path:
        return ""

    # If labels are provided and the image file exists, stamp badges
    if labels_str and Path(img_path).exists():
        try:
            from map_labeler.stamp import parse_labels_string, stamp_labels
            labels = parse_labels_string(labels_str)
            if labels:
                labeled_path = str(Path(img_path).parent / (Path(img_path).stem + "_labeled.jpg"))
                stamp_labels(img_path, labels, labeled_path, theme=theme)
                img_path = labeled_path
        except Exception as e:
            import sys
            print(f"Warning: map label stamping failed: {e}", file=sys.stderr)

    caption = f'<figcaption>{title}</figcaption>' if title else ""
    source_html = f'<div class="map-source">{source}</div>' if source else ""
    # Player map variant link (backward compat - shown when no labels are used)
    player_html = ""
    if player_image and not labels_str:
        player_path = _resolve_image_path(player_image, base_path)
        player_html = f'<div class="map-player-note">Player version: <code>{player_path}</code></div>'
    return f'<figure class="map-container"><img src="{img_path}" alt="{title}" />{caption}{source_html}{player_html}</figure>'


def render_page_header(frontmatter: dict, base_path: str = "") -> str:
    title = frontmatter.get("title", "Untitled")
    level = frontmatter.get("level", "")
    sessions = frontmatter.get("estimated_sessions", "")
    setting = frontmatter.get("setting", "")
    splash = frontmatter.get("splash", "")
    region = frontmatter.get("region", "")
    tagline = frontmatter.get("tagline", "")

    chapter_num = frontmatter.get("chapter_number", frontmatter.get("session_number", ""))

    # Splash image
    splash_html = ""
    if splash:
        splash_path = _resolve_image_path(splash, base_path)
        splash_html = f'<div class="splash-image"><img src="{splash_path}" alt="{title}" /></div>'

    # Title with chapter number prefix
    title_prefix = f"Chapter {chapter_num}: " if chapter_num else ""

    # Region tag ("A LOCATION (REGION) ADVENTURE FOR")
    region_html = ""
    if region:
        region_html = f'<div class="region-tag">A Location ({region}) Adventure for</div>'

    # Tagline
    tagline_html = ""
    if tagline:
        tagline_html = f'<p class="adventure-tagline">{tagline}</p>'

    # Badge + meta line (side by side)
    badge_meta_html = ""
    if level or sessions or setting:
        badge = ""
        if level:
            theme = frontmatter.get("theme", "")
            point_name = theme if theme else "default"
            point_path = SCRIPTS_DIR / f"badge_point_{point_name}.png"
            if not point_path.exists():
                point_path = SCRIPTS_DIR / "badge_point_default.png"
            badge = f'''<div class="level-badge-wrap">
<div class="level-badge"><span class="badge-label">Built for</span><span class="badge-level">Level {level}</span><span class="badge-label">Characters</span></div>
<img class="badge-point" src="file://{point_path}" />
</div>'''

        meta_parts = []
        if sessions:
            meta_parts.append(f'Sized to {sessions} night(s) of play.')
        if setting:
            meta_parts.append(f'It takes place in {setting}.')
        meta_html = "".join(f'<p class="adventure-meta">{p}</p>' for p in meta_parts)
        meta = f'<div class="adventure-meta-wrap">{meta_html}</div>' if meta_html else ""

        badge_meta_html = f'<div class="badge-meta-row">{badge}{meta}</div>'

    return f'''<header class="adventure-header">
{region_html}
<h1 class="adventure-title">{title_prefix}{title}</h1>
{badge_meta_html}
{tagline_html}
{splash_html}
</header>'''


def _render_element(element: dict, base_path: str) -> str:
    t = element["type"]
    if t == "read-aloud":
        return render_read_aloud(element["content"])
    elif t == "dm-sidebar":
        return render_dm_sidebar(element["content"])
    elif t == "encounter-meta":
        return render_encounter_meta(element["content"])
    elif t == "map":
        return render_map(element.get("attrs", {}), base_path, theme=_current_theme)
    elif t == "art":
        return render_art(element.get("attrs", {}), base_path)
    elif t == "hazard":
        return render_hazard(element.get("attrs", {}))
    elif t == "contagion":
        return render_contagion(element.get("attrs", {}))
    elif t == "npc-quote":
        return render_npc_quote(element.get("attrs", {}))
    elif t == "sidebar":
        return render_sidebar_box(element.get("attrs", {}))
    elif t == "page-break":
        return render_page_break()
    elif t == "text":
        return markdown.markdown(element["content"], extensions=["tables"])
    return ""


def _section_class(section: dict) -> str:
    title = section.get("title", "")
    if section["level"] == 3 and ":" in title:
        prefix = title.split(":")[0].strip()
        if prefix and prefix[-1].isdigit():
            return "room"
    if section["level"] == 4:
        return "stat-block"
    return ""


def render_section(section: dict, base_path: str) -> str:
    level = min(section["level"], 6)
    tag = f"h{level}"
    css = _section_class(section)
    cls = f' class="{css}"' if css else ""
    parts = [f"<section{cls}>", f"<{tag}>{section['title']}</{tag}>"]

    elements = section.get("elements", [])
    if elements:
        for el in elements:
            parts.append(_render_element(el, base_path))
    elif section.get("body"):
        parts.append(markdown.markdown(section["body"], extensions=["tables"]))

    for child in section.get("children", []):
        parts.append(render_section(child, base_path))

    parts.append("</section>")
    return "\n".join(parts)


def render_document(body_html: str, frontmatter: dict) -> str:
    title = frontmatter.get("title", "Session")
    css = ""
    if STYLES_PATH.exists():
        css = STYLES_PATH.read_text(encoding="utf-8")
        # Resolve relative URLs in CSS to absolute paths for WeasyPrint
        texture_path = SCRIPTS_DIR / "background_texture.png"
        css = css.replace(
            'url("background_texture.png")',
            f'url("file://{texture_path}")',
        )
    theme = frontmatter.get("theme", "")
    theme_attr = f' data-theme="{theme}"' if theme else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>{title}</title>
<style>{css}</style></head>
<body{theme_attr}>{body_html}</body></html>'''
