"""Exercise the shipped dependency-free frontmatter parser."""

import runpy

import pytest

from wiki_scaffold_lint import TEMPLATE


@pytest.fixture
def parse_frontmatter(monkeypatch):
    scripts = TEMPLATE / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    return runpy.run_path(str(scripts / "okf_bundle.py"))["parse_frontmatter"]


def test_frontmatter_combines_flow_maps_block_lists_and_quoted_colons(parse_frontmatter):
    fields = parse_frontmatter('''type: npc
    title: "The Warden: a friend"
    generated: {by: dm-skills/setup, at: 2026-09-12T00:00:00-07:00}
    tags:
      - recurring
      - "warden: ally"
    verified:
      - by: human:brad
        at: 2026-09-12T00:00:00-07:00
    aliases: [Warden, 'Old Warden']
'''.replace("\n    ", "\n"))
    assert fields == {
        "type": "npc",
        "title": "The Warden: a friend",
        "generated": {"by": "dm-skills/setup", "at": "2026-09-12T00:00:00-07:00"},
        "tags": ["recurring", "warden: ally"],
        "verified": [{"by": "human:brad", "at": "2026-09-12T00:00:00-07:00"}],
        "aliases": ["Warden", "Old Warden"],
    }


def test_frontmatter_nested_containers_and_indentless_list(parse_frontmatter):
    assert parse_frontmatter('''generated:
  by: process:import
  at: 2026-09-12T00:00:00Z
tags:
- recurring
sources: [{id: "book, chapter: 2", pages: [1, 2]}]
''') == {
        "generated": {"by": "process:import", "at": "2026-09-12T00:00:00Z"},
        "tags": ["recurring"],
        "sources": [{"id": "book, chapter: 2", "pages": ["1", "2"]}],
    }


@pytest.mark.parametrize("frontmatter", [
    "type: npc\n  title: unexpected indentation",
    "type: npc\nthis is not a mapping",
    "- npc\n- location",
    "generated: {missing separator}",
    "generated: {by: process:import",
    "tags: [recurring",
    "tags: [recurring, [hub]",
    'title: "unterminated',
    'aliases: ["unterminated, recurring]',
    "aliases: ['unterminated, recurring]",
    "tags: [hub,, recurring]",
])
def test_unparseable_frontmatter_returns_none(parse_frontmatter, frontmatter):
    assert parse_frontmatter(frontmatter) is None


def test_quoted_escapes_inside_flow_collections(parse_frontmatter):
    assert parse_frontmatter(r'''aliases: ["The \"Warden\": ally", 'Warden''s friend']
title: "A colon: and a \\backslash"
''') == {
        "aliases": ['The "Warden": ally', "Warden's friend"],
        "title": "A colon: and a \\backslash",
    }


@pytest.mark.parametrize('text,expected', [
    ('---\n---\nBody', ('', 'Body')),
    ('---\ntype: npc\n---', ('type: npc', '')),
    ('---\r\ntype: npc\r\n---\r\nBody', ('type: npc', 'Body')),
    ('---\ntype: npc\nNo delimiter', (None, '---\ntype: npc\nNo delimiter')),
])
def test_frontmatter_delimiter_boundaries(monkeypatch, text, expected):
    scripts = TEMPLATE / 'scripts'
    monkeypatch.syspath_prepend(str(scripts))
    split = runpy.run_path(str(scripts / 'okf_bundle.py'))['split_frontmatter']
    assert split(text) == expected


def test_markdown_destination_offsets_preserve_surrounding_syntax(monkeypatch):
    scripts = TEMPLATE / 'scripts'
    monkeypatch.syspath_prepend(str(scripts))
    links = runpy.run_path(str(scripts / 'okf_bundle.py'))['markdown_links']
    text = '''[Person](../people/the-warden.md#history "Title")
![Map](<../media/a map.png> "Map")
[Parenthesis](a(b).md)
[Reference][r]
[r]: ../notes.md "Notes"
`[Example](do-not-rewrite.md)`

```markdown
[Example](do-not-rewrite.md)
```
'''
    destinations = list(links(text))
    assert [link.destination for link in destinations] == [
        '../people/the-warden.md#history', '../media/a map.png', 'a(b).md', '../notes.md',
    ]
    rewritten = text
    for link in reversed(destinations):
        assert text[link.start:link.end] == link.destination
        rewritten = rewritten[:link.start] + '/replacement.md' + rewritten[link.end:]
    assert rewritten == '''[Person](/replacement.md "Title")
![Map](</replacement.md> "Map")
[Parenthesis](/replacement.md)
[Reference][r]
[r]: /replacement.md "Notes"
`[Example](do-not-rewrite.md)`

```markdown
[Example](do-not-rewrite.md)
```
'''
