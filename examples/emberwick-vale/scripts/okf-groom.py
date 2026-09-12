#!/usr/bin/env python3
"""Report OKF maintenance findings; --fix applies safe maintenance, never commits.

--candidates emits the entity-scoped JSON input for a semantic judgement pass.
--place-contradiction FILE (or - for stdin) accepts one object or a list of objects with keys
entity, left, right, left_claim, right_claim (paths are bundle-relative).
Claims must be exact, unique prose passages. With --fix, place both callouts;
without it, validate and report only. Neither mode decides whether claims conflict.
"""
import sys
sys.dont_write_bytecode = True

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
from urllib.parse import quote, unquote, urlsplit

import okf_bundle as wiki

START = '<!-- groom-wiki:loose-ends:start -->'
END = '<!-- groom-wiki:loose-ends:end -->'
LOOSE = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.S)
EVIDENCE = re.compile(r'^> (?:\[!contradiction\]|\[!warning\] groom/)[^\n]*(?:\n>[^\n]*)*', re.M)


def prose(text):
    """Remove generated edges/evidence while retaining original source offsets."""
    blank = lambda m: re.sub(r'[^\r\n]', ' ', m[0])
    return wiki.markdown_prose(EVIDENCE.sub(blank, LOOSE.sub(blank, text)))


def read_text(path):
    with Path(path).open(encoding='utf-8', newline='') as stream:
        return stream.read()


def concepts():
    result = {}
    for rel in wiki.page_paths():
        text = read_text(Path(wiki.bundle_root()) / rel)
        fm, body = wiki.split_frontmatter(text)
        result[rel] = {'text': text, 'body': body,
                       'fm': wiki.parse_frontmatter(fm) if fm is not None else
                       (None if text.startswith(('---\n', '---\r\n')) else {})}
    return result


def node(path, page):
    return (page['fm'] or {}).get('type') in {'npc', 'location', 'faction', 'event'}


def live_layer(pages):
    tagged = [p for p, page in pages.items()
              if 'live-layer' in (page['fm'] or {}).get('tags', [])]
    if len(tagged) == 1:
        return tagged[0]
    default = 'story/campaign-status.md'
    return default if default in pages else None


def local(destination):
    return not destination.startswith('//') and not re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', destination)


def concept_links(text):
    """Graph edges are concept links, never inline images or image-only refs."""
    visible = prose(text)
    for link in wiki.markdown_links(visible):
        prefix = visible[:link.start]
        if re.search(r'!\[(?:\\.|[^\]\n]|\[[^\]\n]*\])*\]\(\s*<?$', prefix):
            continue
        definition = re.search(r'^ {0,3}\[([^\]\n]+)\]:[ \t]*<?$', prefix, re.M)
        if definition:
            label = definition[1]
            without_images = re.sub(r'!\[[^\]\n]*\](?:\[[^\]\n]*\])?', '', visible)
            uses = re.search(r'\[' + re.escape(label) + r'\](?!:)', without_images, re.I)
            if not uses:
                continue
        yield link


def edges(pages):
    result = {p: set() for p in pages}
    for source, page in pages.items():
        for link in concept_links(page['body']):
            target = wiki.resolve_local_link(Path(source), link.destination)
            if target is not None and str(target) in result and str(target) != source:
                result[str(target)].add(source)
    return result


def instant(value):
    try:
        date = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return date if date.utcoffset() is not None else None
    except ValueError:
        return None


def contradiction_candidates(pages):
    """Eligible entities, ranked by newest referring generated.at, capped at 25."""
    live = live_layer(pages)
    eligible = {p for p, page in pages.items()
                if (node(p, page) or p == live)
                and (page['fm'] or {}).get('status') != 'deprecated'
                and (page['fm'] or {}).get('type') != 'session'}
    result = []
    for entity, refs in edges(pages).items():
        if (pages[entity]['fm'] or {}).get('status') == 'deprecated':
            continue
        refs = sorted(refs & eligible)
        if len(refs) < 2 or not any(node(p, pages[p]) for p in refs):
            continue
        dates = [instant(((pages[p]['fm'] or {}).get('generated') or {}).get('at'))
                 for p in refs if isinstance((pages[p]['fm'] or {}).get('generated', {}), dict)]
        newest = max((date for date in dates if date), default=datetime.min.replace(tzinfo=timezone.utc))
        result.append({'entity': entity, 'referrers': refs, 'newest': newest.isoformat()})
    return sorted(result, key=lambda c: (-instant(c['newest']).timestamp(), c['entity']))[:25]


def place_contradiction(pages, evidence, fix=False):
    """Validate exact evidence and place or refresh its paired callouts."""
    entity, left, right, a, b = (evidence[k] for k in
                                ('entity', 'left', 'right', 'left_claim', 'right_claim'))
    scope = {c['entity']: c['referrers'] for c in contradiction_candidates(pages)}
    if left == right or left not in scope.get(entity, []) or right not in scope.get(entity, []):
        raise ValueError('contradiction pair is outside the current entity scope')
    if not node(left, pages[left]) and not node(right, pages[right]):
        raise ValueError('a contradiction pair must include a node')
    identity = json.dumps([entity, sorted([(left, a), (right, b)])], ensure_ascii=False)
    marker = '<!-- groom-wiki:contradiction:' + hashlib.sha256(identity.encode()).hexdigest()[:20] + ' -->'
    updates = {}
    for here, other, claim, peer in ((left, right, a, b), (right, left, b, a)):
        text = pages[here]['text']
        visible = prose(pages[here]['body'])
        if not claim or visible.count(claim) != 1:
            raise ValueError(f'{here}: claim must occur exactly once outside generated evidence/code')
        title = (pages[other]['fm'] or {}).get('title') or other
        status = (pages[other]['fm'] or {}).get('status') or 'stable'
        entity_title = (pages[entity]['fm'] or {}).get('title') or entity
        block = (f'{marker}\n> [!contradiction] Unresolved: {entity_title}\n'
                 f'> Here: "{claim}"\n'
                 f'> Other: [{title}](/{quote(other, safe="/")}) (status: {status}): "{peer}"')
        block = re.sub(r'\n(?!>|<!--)', '\n> ', block)
        existing = re.search(re.escape(marker) + r'\r?\n> \[!contradiction\][^\n]*(?:\n>[^\n]*)*', text)
        if existing:
            updated = text[:existing.start()] + block + text[existing.end():]
            if updated != text:
                updates[here] = updated
            continue
        if marker in text:
            raise ValueError(f'{here}: generated contradiction marker has no callout')
        if block.split('\n', 1)[1] in text:
            continue
        body_offset = len(text) - len(pages[here]['body'])
        at = body_offset + visible.index(claim) + len(claim)
        end = text.find('\n', at)
        end = len(text) if end < 0 else end
        updates[here] = text[:end] + '\n\n' + block + text[end:]
    if fix:
        for path, text in updates.items():
            (Path(wiki.bundle_root()) / path).write_text(text, encoding='utf-8')
    return sorted(updates)


def committed_at(path):
    result = subprocess.run(['git', 'log', '-1', '--format=%cI', '--', str(path)],
                            cwd=wiki.bundle_root(), capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ''


def backfill(path, page):
    fm = page['fm']
    if fm is None:
        return page['text']  # malformed YAML needs a human; never overwrite it
    updates = {}
    if not fm.get('title'):
        heading = wiki.first_heading(page['body'])
        if heading:
            updates['title'] = heading
    if not fm.get('generated'):
        date = committed_at(path)
        if date:
            updates['generated'] = {'by': 'dm-skills/groom-wiki', 'at': date}
    return wiki.edit_frontmatter(page['text'], updates) if updates else page['text']


def heading_anchors(text):
    """ATX heading offsets and fragments, including repeated-heading suffixes."""
    used = set()
    for heading in re.finditer(r'^ {0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$', prose(text), re.M):
        slug = re.sub(r'[^\w\s-]', '', heading[1].lower()).replace(' ', '-')
        anchor, suffix = slug, 0
        while anchor in used:
            suffix += 1
            anchor = f'{slug}-{suffix}'
        used.add(anchor)
        yield heading.start(), anchor


def seed_sections(page):
    visible = prose(page['body'])
    headers = list(re.finditer(r'^## ([^\n]+)\n', visible, re.M))
    anchors = dict(heading_anchors(page['body']))
    for i, header in enumerate(headers):
        end = headers[i + 1].start() if i + 1 < len(headers) else len(visible)
        title = header[1].strip()
        yield title, anchors[header.start()], header.start(), end, page['body'][header.end():end]


def seed_plans(pages):
    plans = []
    for path, page in pages.items():
        if (page['fm'] or {}).get('type') != 'seed-ideas':
            continue
        for title, anchor, start, end, body in seed_sections(page):
            refs = set()
            for source, referrer in pages.items():
                if source == path:
                    continue
                for link in concept_links(referrer['body']):
                    if (wiki.resolve_local_link(Path(source), link.destination) == Path(path)
                            and unquote(urlsplit(link.destination).fragment) == anchor):
                        refs.add(source)
            if len(re.findall(r'\b\w+\b', prose(body))) <= 150 and len(refs) < 3:
                continue
            target = str(Path(path).with_name(anchor + '.md'))
            bound = (wiki.inferred_type(Path(target)) == 'session' or bool(re.search(
                r'\b(?:boxed text|encounter budget|session.only|session.bound|only (?:in|for) (?:this |the )?session)\b',
                prose(body), re.I)) or (refs and all((pages[r]['fm'] or {}).get('type') == 'session' for r in refs)))
            safe = (not bound and wiki.inferred_type(Path(target)) not in (None, 'seed-ideas')
                    and bool(anchor) and Path(target).name not in wiki.RESERVED
                    and not (Path(wiki.bundle_root()) / target).exists())
            plans.append(dict(source=path, target=target, title=title, anchor=anchor,
                              start=start, end=end, body=body, safe=safe))
    return plans


def promote(plans, pages):
    """Move eligible H2 sections and rewrite all links to their former anchors."""
    root = Path(wiki.bundle_root())
    safe, targets = [], set()
    for plan in plans:
        if plan['safe'] and plan['target'] not in targets:
            safe.append(plan)
            targets.add(plan['target'])
    mapping = {}
    for plan in safe:
        old = [anchor for start, anchor in heading_anchors(pages[plan['source']]['body'])
               if plan['start'] <= start < plan['end']]
        new = [anchor for _, anchor in heading_anchors('# ' + plan['title'] + '\n' + plan['body'])]
        for index, (before, after) in enumerate(zip(old, new)):
            mapping[(plan['source'], before)] = (plan['target'], after if index else '')
    for source in sorted({p['source'] for p in safe}):
        text = pages[source]['text']
        offset = len(text) - len(pages[source]['body'])
        moving = [p for p in safe if p['source'] == source]
        for plan in sorted(moving, key=lambda p: -p['start']):
            text = text[:offset + plan['start']] + text[offset + plan['end']:]
            new = wiki.edit_frontmatter('# ' + plan['title'] + '\n' + plan['body'],
                                        {'type': wiki.inferred_type(Path(plan['target'])),
                                         'title': plan['title'], 'description': '',
                                         'tags': [], 'status': 'draft'})
            # Same directory, so every relative target retains its original meaning.
            new = wiki.rewrite_local_links(Path(source), new)
            (root / plan['target']).write_text(new, encoding='utf-8')
        # Removing repeated headings can renumber fragments still in the inbox.
        retained = [anchor for start, anchor in heading_anchors(pages[source]['body'])
                    if not any(p['start'] <= start < p['end'] for p in moving)]
        remaining = [anchor for _, anchor in heading_anchors(text[offset:])]
        for before, after in zip(retained, remaining):
            if before != after:
                mapping[(source, before)] = (source, after)
        (root / source).write_text(text, encoding='utf-8')
    for path in wiki.page_paths() + wiki.reserved_paths():
        file = root / path
        text = read_text(file)
        updated = text
        for link in reversed(list(wiki.markdown_links(text))):
            target = wiki.resolve_local_link(Path(path), link.destination)
            parts = urlsplit(link.destination)
            replacement = mapping.get((str(target), unquote(parts.fragment)))
            if replacement:
                destination, anchor = replacement
                dest = ('/' + quote(destination, safe='/')
                        + ('?' + parts.query if parts.query else '')
                        + ('#' + quote(anchor) if anchor else ''))
                updated = updated[:link.start] + dest + updated[link.end:]
        if updated != text:
            file.write_text(updated, encoding='utf-8')


def loose_text(text, orphans, pages):
    lines = [START, '## Loose ends', '']
    lines += [f'- [{(pages[p]["fm"] or {}).get("title") or p}](/{quote(p, safe="/")}) — orphan node'
              for p in sorted(orphans)] or ['No orphan nodes.']
    block = '\n'.join(lines + [END])
    if LOOSE.search(text):
        return LOOSE.sub(lambda _: block, text, count=1)
    return text + ('\n' if text.endswith('\n') else '\n\n') + block + '\n'


def groom(fix=False, now=None):
    now = now or datetime.now(timezone.utc)
    findings = []
    def report(rule, path, detail):
        findings.append((f'groom/{rule}', path, detail))
    root = Path(wiki.bundle_root())
    pages = concepts()
    for path, page in pages.items():
        updated = backfill(path, page)
        if updated != page['text']:
            report('frontmatter-backfill', path, 'backfill missing title / committed provenance')
        linked = wiki.rewrite_local_links(Path(path), updated)
        if linked != updated:
            report('link-form', path, 'normalize existing local targets to bundle-root links')
        if fix and linked != page['text']:
            (root / path).write_text(linked, encoding='utf-8')
    for path in wiki.reserved_paths():
        if Path(path).name != 'log.md':
            continue  # catalogs have their own generated directory-link grammar
        text = read_text(root / path)
        updated = wiki.rewrite_local_links(Path(path), text)
        if updated != text:
            report('link-form', path, 'normalize existing local targets to bundle-root links')
            if fix:
                (root / path).write_text(updated, encoding='utf-8')
    if fix:
        pages = concepts()
    plans = seed_plans(pages)
    for plan in plans:
        report('seed-promoted', plan['source'] + '#' + plan['anchor'],
               plan['target'] if plan['safe'] else 'review required: session scope, type, or target collision')
    if fix:
        promote(plans, concepts())
        pages = concepts()
    incoming = edges(pages)
    catalog = set()
    for path in wiki.reserved_paths():
        if Path(path).name == 'index.md':
            for link in wiki.markdown_links(read_text(root / path)):
                target = wiki.resolve_local_link(Path(path), link.destination)
                if target:
                    catalog.add(str(target))
    orphans = []
    warnings = {}
    for path, page in pages.items():
        fm = page['fm'] or {}
        if node(path, page) and not incoming[path]:
            orphans.append(path)
            report('orphan', path, 'no incoming concept links')
        if path not in catalog:
            report('not-in-index', path, 'absent from existing catalogs')
        stale = instant(fm.get('stale_after'))
        if stale is not None and now >= stale:
            report('stale', path, f'stale_after: {fm["stale_after"]}')
        for link in wiki.markdown_links(prose(page['body'])):
            if not local(link.destination):
                continue
            target = wiki.resolve_local_link(Path(path), link.destination)
            if target is None:
                report('missing-target', path, link.destination)
                warnings.setdefault(path, []).append(('missing-target', link.destination))
            elif node(path, page) and str(target) in pages:
                target_fm = pages[str(target)]['fm'] or {}
                if target_fm.get('type') == 'session' and target_fm.get('status') == 'draft':
                    report('node-links-draft-session', path, str(target))
                    warnings.setdefault(path, []).append(('node-links-draft-session', str(target)))
    if fix:
        for path, entries in warnings.items():
            text = read_text(root / path)
            for rule, target in sorted(set(entries)):
                block = f'> [!warning] groom/{rule}\n> Unresolved link: `{target}`'
                if block not in text:
                    text += ('\n' if text.endswith('\n') else '\n\n') + block + '\n'
            if text != read_text(root / path):
                (root / path).write_text(text, encoding='utf-8')
        pages = concepts()
    live = live_layer(pages)
    if live:
        text = pages[live]['text']
        updated = loose_text(text, orphans, pages)
        if updated != text:
            report('loose-ends-written', live, f'{len(orphans)} orphan nodes')
            if fix:
                (root / live).write_text(updated, encoding='utf-8')
    indexer = runpy.run_path(str(Path(__file__).with_name('okf-index.py')))
    for path, text in sorted(indexer['rendered_targets']().items()):
        file = root / path
        if not file.exists() or read_text(file) != text:
            report('index-regenerated', path, 'catalog differs from concepts')
            if fix:
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(text, encoding='utf-8')
    return sorted(set(findings))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fix', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--candidates', action='store_true')
    parser.add_argument('--place-contradiction', metavar='JSON_FILE', help='evidence JSON file, or - for stdin')
    parser.add_argument('--now', help='offset ISO instant; defaults to current time')
    args = parser.parse_args()
    if args.fix and args.dry_run:
        parser.error('--fix and --dry-run are mutually exclusive')
    if args.candidates:
        print(json.dumps(contradiction_candidates(concepts()), indent=2))
        return 0
    if args.place_contradiction:
        try:
            evidence = json.loads(sys.stdin.read() if args.place_contradiction == '-' else
                                  Path(args.place_contradiction).read_text(encoding='utf-8'))
            for pair in evidence if isinstance(evidence, list) else [evidence]:
                changed = place_contradiction(concepts(), pair, args.fix)
                for path in changed:
                    print(f'groom/contradiction {path}: paired evidence')
        except (KeyError, TypeError, ValueError) as exc:
            parser.error(str(exc))
        return 0
    now = instant(args.now) if args.now else None
    if args.now and now is None:
        parser.error('--now requires an ISO datetime with UTC offset')
    for rule, path, detail in groom(args.fix, now):
        print(f'{rule} {path}: {detail}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
