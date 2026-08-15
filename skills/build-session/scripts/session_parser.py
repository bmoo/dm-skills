"""Session markdown parser.

Parses structured session prep markdown into a tree:
- frontmatter: dict of YAML metadata
- sections: list of top-level section nodes

Each node: {title, level, body, elements, children: [sub-sections]}

elements is an ordered list of content blocks:
  {"type": "text", "content": "..."}
  {"type": "read-aloud", "content": "..."}
  {"type": "dm-sidebar", "content": "..."}
  {"type": "encounter-meta", "content": "..."}
  {"type": "map", "attrs": {"key": "value", ...}}

Art callouts ([!art], and the float aliases [!art-left]/[!art-right], which
normalize to type "art" with attrs["position"] preset) accept two authored
shapes: key: value attrs (image/caption/position), or the embed shape — a
markdown image line plus an optional caption line, as session pages author
for the site renderer.
"""

import re
import yaml
from pathlib import Path

_DIRECTIVE_TYPES = {
    "read-aloud", "dm-sidebar", "encounter-meta", "map", "art",
    "art-left", "art-right",
    "hazard", "contagion", "npc-quote", "sidebar", "page-break",
}

# art-left / art-right are art with a preset float position
_ART_ALIASES = {"art-left": "left", "art-right": "right"}

# Directives whose body lines are parsed as key: value attrs (not markdown content)
_KV_DIRECTIVES = {"map", "art", "art-left", "art-right", "hazard", "contagion",
                  "npc-quote", "sidebar"}

# Directives that have no body at all
_EMPTY_DIRECTIVES = {"page-break"}


def parse_session(path: Path) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    return parse_session_text(text)


def parse_session_text(text: str) -> dict:
    frontmatter, body = _split_frontmatter(text)
    flat = _split_sections_flat(body)
    sections = _nest_sections(flat)
    return {"frontmatter": frontmatter, "sections": sections}


def _split_frontmatter(text: str) -> tuple[dict, str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}, text
    fm = yaml.safe_load(match.group(1)) or {}
    return fm, text[match.end():]


def _extract_elements(body: str) -> list[dict]:
    """Parse body text into an ordered list of text and directive elements."""
    elements = []
    lines = body.split("\n")
    i = 0
    text_lines = []

    while i < len(lines):
        line = lines[i]
        # Check for a directive opener: > [!type-name]
        m = re.match(r"^> \[!([a-z0-9-]+)\]\s*$", line)
        if m and m.group(1) in _DIRECTIVE_TYPES:
            # Flush accumulated text
            text_block = "\n".join(text_lines).strip()
            if text_block:
                elements.append({"type": "text", "content": text_block})
            text_lines = []

            directive_type = m.group(1)
            i += 1

            if directive_type in _EMPTY_DIRECTIVES:
                elements.append({"type": directive_type})
            else:
                content_lines = []
                # Collect subsequent blockquote lines
                while i < len(lines) and lines[i].startswith("> "):
                    content_lines.append(lines[i][2:])  # strip "> " prefix
                    i += 1

                if directive_type in _KV_DIRECTIVES:
                    attrs = {}
                    embed_mode = False
                    for content_line in content_lines:
                        # Art callouts also accept the embed shape: a markdown
                        # image line plus an optional caption line (the shape
                        # session pages author for the site renderer). Once in
                        # embed mode, remaining lines are caption text, never
                        # key: value attrs.
                        img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", content_line)
                        if img and directive_type in ("art", "art-left", "art-right"):
                            attrs["image"] = img.group(2)
                            attrs.setdefault("caption", img.group(1))
                            embed_mode = True
                            continue
                        if embed_mode:
                            if content_line.strip():
                                attrs["caption"] = content_line.strip().strip("*_")
                            continue
                        kv = re.match(r"^([^:]+):\s*(.+)$", content_line)
                        if kv:
                            attrs[kv.group(1).strip()] = kv.group(2).strip()
                    if directive_type in _ART_ALIASES:
                        attrs.setdefault("position", _ART_ALIASES[directive_type])
                        directive_type = "art"
                    elements.append({"type": directive_type, "attrs": attrs})
                else:
                    content = "\n".join(content_lines).strip()
                    elements.append({"type": directive_type, "content": content})
        else:
            text_lines.append(line)
            i += 1

    # Flush any remaining text
    text_block = "\n".join(text_lines).strip()
    if text_block:
        elements.append({"type": "text", "content": text_block})

    return elements


def _split_sections_flat(body: str) -> list[dict]:
    pattern = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(body))
    if not matches:
        return []
    sections = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        section_body = body[start:end].strip()
        sections.append({
            "title": match.group(2).strip(),
            "level": len(match.group(1)),
            "body": section_body,
            "elements": _extract_elements(section_body),
            "children": [],
        })
    return sections


def _nest_sections(flat: list[dict]) -> list[dict]:
    root, stack = [], []
    for section in flat:
        while stack and stack[-1]["level"] >= section["level"]:
            stack.pop()
        if stack:
            stack[-1]["children"].append(section)
        else:
            root.append(section)
        stack.append(section)
    return root
