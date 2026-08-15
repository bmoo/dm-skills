"""Session renderer: markdown → styled PDF.

Usage: python3 render_session.py input.md [--output output.pdf]
"""

import argparse
import sys
from pathlib import Path

from session_parser import parse_session
from resolver import resolve_references_in_text
from templates import render_document, render_page_header, render_section


def _collect_images(sections, out):
    """Recursively collect all image paths from art and map elements."""
    for s in sections:
        for el in s.get("elements", []):
            if el.get("type") in ("art", "map"):
                img = el.get("attrs", {}).get("image")
                if img:
                    out.append(img)
        _collect_images(s.get("children", []), out)


def _resolve_tree(sections):
    """Resolve DDB references throughout the section tree."""
    for section in sections:
        section["body"] = resolve_references_in_text(section["body"])
        for element in section.get("elements", []):
            if "content" in element:
                element["content"] = resolve_references_in_text(element["content"])
        _resolve_tree(section.get("children", []))


def main():
    ap = argparse.ArgumentParser(description="Render session markdown to PDF")
    ap.add_argument("input", type=Path, help="Session markdown file")
    ap.add_argument("--output", "-o", type=Path, default=None,
                    help="Output PDF path (default: same name as input with .pdf)")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        return 1

    output = args.output or args.input.with_suffix(".pdf")

    # Parse
    data = parse_session(args.input)

    # Resolve references
    _resolve_tree(data["sections"])

    # Check for duplicate images (splash + inline art + maps)
    image_paths = []
    splash = data["frontmatter"].get("splash", "")
    if splash:
        image_paths.append(splash)
    _collect_images(data["sections"], image_paths)
    seen = set()
    for p in image_paths:
        basename = Path(p).name
        if basename in seen:
            print(f"Warning: image '{basename}' used more than once", file=sys.stderr)
        seen.add(basename)

    # Render HTML
    base_path = str(args.input.parent)
    import templates
    templates._current_theme = data["frontmatter"].get("theme", "amber")
    header_html = render_page_header(data["frontmatter"], base_path=base_path)
    sections_html = "\n".join(
        render_section(s, base_path=str(args.input.parent))
        for s in data["sections"]
    )
    full_html = render_document(header_html + sections_html, data["frontmatter"])

    # Convert to PDF
    from weasyprint import HTML
    HTML(string=full_html, base_url=str(args.input.parent)).write_pdf(str(output))

    print(f"Rendered: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
