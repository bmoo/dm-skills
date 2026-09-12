"""Exercise the installed groomer, including no-write and rerun contracts."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from wiki_scaffold_lint import TEMPLATE

FIXTURES = TEMPLATE.parent / 'fixtures/groom'
NOW = '2026-09-12T00:00:00+00:00'


def run(root, *args, script='okf-groom.py'):
    return subprocess.run([sys.executable, str(root / 'scripts' / script), *args],
                          cwd=root.parent, text=True, capture_output=True)


def write(root, path, text):
    file = root / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text, encoding='utf-8')


def page(title='A', body='', fm='', kind='npc'):
    return (f'---\ntype: {kind}\ntitle: {title}\ndescription: A campaign concept.\n'
            f'{fm}---\n# {title}\n\n{body}\n')


def campaign(tmp_path, files):
    root = tmp_path / 'campaign'
    shutil.copytree(TEMPLATE / 'scripts', root / 'scripts',
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for path, text in files.items():
        write(root, path, text)
    assert run(root, script='okf-index.py').returncode == 0
    return root


def fixture(tmp_path, rule, state):
    data = json.loads((FIXTURES / f'{rule}-{state}.json').read_text())
    root = campaign(tmp_path, data['files'])
    for path, text in data.get('after_index', {}).items():
        write(root, path, text)
    return root


def check_id(tmp_path, rule):
    for state in ('passing', 'failing'):
        root = fixture(tmp_path / state, rule, state)
        before = snapshot(root)
        result = run(root, '--now', NOW)
        assert result.returncode == 0, result.stderr
        assert (f'groom/{rule} ' in result.stdout) == (state == 'failing'), result.stdout
        assert snapshot(root) == before


def snapshot(root):
    return {str(p.relative_to(root)): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file()}


def test_groom_link_form(tmp_path):
    check_id(tmp_path, 'link-form')


def test_groom_frontmatter_backfill(tmp_path):
    check_id(tmp_path, 'frontmatter-backfill')


def test_groom_index_regenerated(tmp_path):
    check_id(tmp_path, 'index-regenerated')


def test_groom_seed_promoted(tmp_path):
    check_id(tmp_path, 'seed-promoted')


def test_groom_missing_target(tmp_path):
    check_id(tmp_path, 'missing-target')
    root = fixture(tmp_path / 'fix', 'missing-target', 'failing')
    logs = {p: p.read_bytes() for p in root.rglob('log.md')}
    first = run(root, '--fix')
    assert first.returncode == 0, first.stderr
    assert 'groom/missing-target log.md' not in first.stdout
    assert 'groom/missing-target nodes/log.md' not in first.stdout
    assert '[Missing](/nodes/npcs/missing.md)' in (root / 'nodes/npcs/a.md').read_text()
    assert logs == {p: p.read_bytes() for p in logs}
    text = (root / 'nodes/npcs/a.md').read_bytes()
    assert run(root, '--fix').returncode == 0
    assert (root / 'nodes/npcs/a.md').read_bytes() == text
    assert b'> [!warning] groom/missing-target' in text


def test_groom_orphan(tmp_path):
    check_id(tmp_path, 'orphan')


def test_groom_not_in_index(tmp_path):
    check_id(tmp_path, 'not-in-index')
    root = fixture(tmp_path / 'fix', 'not-in-index', 'failing')
    assert run(root, '--fix').returncode == 0
    after = run(root)
    assert 'groom/not-in-index' not in after.stdout
    assert 'groom/orphan' in after.stdout


def test_groom_stale(tmp_path):
    check_id(tmp_path, 'stale')
    root = fixture(tmp_path / 'fix', 'stale', 'failing')
    before = snapshot(root)
    result = run(root, '--fix', '--now', '2026-09-11T17:00:00-07:00')
    assert 'groom/stale' in result.stdout
    assert snapshot(root) == before
    write(root, 'nodes/npcs/a.md', page(fm='stale_after: bad-date\n'))
    assert run(root).returncode == 0


def test_groom_node_links_draft_session(tmp_path):
    check_id(tmp_path, 'node-links-draft-session')
    root = fixture(tmp_path / 'fix', 'node-links-draft-session', 'failing')
    assert run(root, '--fix').returncode == 0
    assert '> [!warning] groom/node-links-draft-session' in (root / 'nodes/npcs/a.md').read_text()


def test_groom_loose_ends_written(tmp_path):
    check_id(tmp_path, 'loose-ends-written')
    root = fixture(tmp_path / 'fix', 'loose-ends-written', 'failing')
    path = root / 'story/campaign-status.md'
    before = path.read_text()
    assert run(root, '--fix').returncode == 0
    after = path.read_text()
    assert before.split('<!-- groom-wiki:loose-ends:start -->')[0] == after.split('<!-- groom-wiki:loose-ends:start -->')[0]
    assert before.split('<!-- groom-wiki:loose-ends:end -->')[1] == after.split('<!-- groom-wiki:loose-ends:end -->')[1]
    again = run(root, '--fix')
    assert 'groom/orphan nodes/npcs/a.md' in again.stdout
    assert 'groom/loose-ends-written' not in again.stdout
    assert path.read_text() == after


def test_no_live_layer_or_dry_run_writes(tmp_path):
    root = campaign(tmp_path, {'nodes/npcs/a.md': page()})
    before = snapshot(root)
    result = run(root, '--fix')
    assert result.returncode == 0, result.stderr
    assert 'groom/orphan' in result.stdout
    assert snapshot(root) == before
    write(root, 'nodes/npcs/a.md', '# Missing metadata\n')
    before = snapshot(root)
    assert run(root, '--dry-run').returncode == 0
    assert snapshot(root) == before
    assert not list(root.rglob('__pycache__'))


def test_backfill_uses_last_commit_and_preserves_metadata(tmp_path):
    root = campaign(tmp_path, {'nodes/npcs/a.md': '---\ntype: npc\ncustom: keep\n---\n# A\n'})
    assert run(root, '--fix').returncode == 0
    text = (root / 'nodes/npcs/a.md').read_text()
    assert 'title: "A"' in text and 'generated:' not in text and 'custom: keep' in text
    for args in (['init'], ['config', 'user.email', 'fixture@example.invalid'],
                 ['config', 'user.name', 'Fixture'], ['add', '.'], ['commit', '-m', 'Fixture']):
        assert subprocess.run(['git', *args], cwd=root, capture_output=True).returncode == 0
    date = subprocess.check_output(['git', 'log', '-1', '--format=%cI'], cwd=root, text=True).strip()
    assert run(root, '--fix').returncode == 0
    text = (root / 'nodes/npcs/a.md').read_text()
    assert date in text and 'dm-skills/groom-wiki' in text and 'custom: keep' in text
    assert run(root, '--fix').returncode == 0
    assert (root / 'nodes/npcs/a.md').read_text() == text


def test_seed_move_threshold_anchors_and_session_safeguards(tmp_path):
    inbox = 'nodes/npcs/ideas.md'
    root = campaign(tmp_path, {
        inbox: page('Ideas', kind='seed-ideas', body='## Herald\n\n' + 'durable '*151 + '\n[Self](#herald)\n[B](b.md)\n\n## Short\n\nTiny.\n'),
        'nodes/npcs/b.md': page('B', body='[Herald](ideas.md#herald)'),
        'sessions/prep.md': page('Prep', kind='session', body='[Herald](/nodes/npcs/ideas.md#herald)'),
    })
    result = run(root, '--fix')
    assert result.returncode == 0, result.stderr
    promoted = (root / 'nodes/npcs/herald.md').read_text()
    assert 'status: "draft"' in promoted and '# Herald' in promoted
    assert '](/nodes/npcs/herald.md)' in promoted and '](/nodes/npcs/b.md)' in promoted
    assert '## Herald' not in (root / inbox).read_text()
    assert '## Short' in (root / inbox).read_text()
    assert '#herald' not in (root / 'sessions/prep.md').read_text()
    before = {p: value[0] for p, value in snapshot(root).items()}
    assert run(root, '--fix').returncode == 0
    assert {p: value[0] for p, value in snapshot(root).items()} == before
    for name, body in [('bound', 'Only for this session. ' + 'prep '*151), ('collision', 'durable '*151)]:
        write(root, inbox, page('Ideas', kind='seed-ideas', body=f'## {name.title()}\n\n{body}'))
        if name == 'collision':
            write(root, 'nodes/npcs/collision.md', page('Existing'))
        original = (root / inbox).read_text()
        assert run(root, '--fix').returncode == 0
        assert (root / inbox).read_text() == original


def test_seed_three_distinct_referrers_and_long_unlinked_seed(tmp_path):
    inbox = 'nodes/npcs/ideas.md'
    files = {inbox: page('Ideas', kind='seed-ideas', body='## Herald\n\nA short durable idea.\n')}
    for name in 'abc':
        files[f'nodes/npcs/{name}.md'] = page(name, body='[Seed](/nodes/npcs/ideas.md#herald)')
    root = campaign(tmp_path / 'three', files)
    assert run(root, '--fix').returncode == 0
    assert (root / 'nodes/npcs/herald.md').exists()
    files = {inbox: page('Ideas', kind='seed-ideas', body='## Herald\n\n' + 'durable '*151)}
    root = campaign(tmp_path / 'long', files)
    assert run(root, '--fix').returncode == 0
    assert (root / 'nodes/npcs/herald.md').exists()
    files[inbox] = page('Ideas', kind='seed-ideas', body='## Herald\n\nShort.')
    files['nodes/npcs/a.md'] = page(body='[Seed](/nodes/npcs/ideas.md#herald) '*3)
    root = campaign(tmp_path / 'repeats', files)
    assert run(root, '--fix').returncode == 0
    assert not (root / 'nodes/npcs/herald.md').exists()


def test_contradiction_scope_cap_ranking_placement_and_idempotence(tmp_path):
    entity = 'nodes/npcs/entity.md'
    left, right = 'nodes/npcs/a.md', 'story/campaign-status.md'
    files = {entity: page('Entity'),
             left: page('A', body='The bell is red.\n\n[Entity](/nodes/npcs/entity.md)', fm='status: draft\n'),
             right: page('Live', kind='story', body='The bell is blue.\n\n[Entity](/nodes/npcs/entity.md)'),
             'sessions/prep.md': page('Prep', kind='session', body='[Entity](/nodes/npcs/entity.md)', fm='status: draft\n'),
             'nodes/npcs/old.md': page('Old', body='[Entity](/nodes/npcs/entity.md)', fm='status: deprecated\n')}
    root = campaign(tmp_path, files)
    candidates = json.loads(run(root, '--candidates').stdout)
    assert candidates[0]['referrers'] == [left, right]
    evidence = {'entity': entity, 'left': left, 'right': right,
                'left_claim': 'The bell is red.', 'right_claim': 'The bell is blue.'}
    data = tmp_path / 'evidence.json'
    data.write_text(json.dumps(evidence))
    before = snapshot(root)
    assert run(root, '--place-contradiction', str(data)).returncode == 0
    assert snapshot(root) == before
    result = run(root, '--place-contradiction', str(data), '--fix')
    assert result.returncode == 0, result.stderr
    a, b = (root / left).read_text(), (root / right).read_text()
    assert '> Here: "The bell is red."' in a
    assert '> Other: [Live](/story/campaign-status.md) (status: stable): "The bell is blue."' in a
    assert '> Other: [A](/nodes/npcs/a.md) (status: draft): "The bell is red."' in b
    assert run(root, '--place-contradiction', str(data), '--fix').returncode == 0
    assert (root / left).read_text() == a and (root / right).read_text() == b
    # Evidence links do not add an incoming edge from A to the live layer.
    assert json.loads(run(root, '--candidates').stdout) == candidates
    evidence['left_claim'] = 'Invented claim'
    data.write_text(json.dumps(evidence))
    before = snapshot(root)
    assert run(root, '--place-contradiction', str(data), '--fix').returncode != 0
    assert snapshot(root) == before
    for n in range(27):
        target = f'nodes/npcs/entity-{n:02}.md'
        write(root, target, page(f'Entity {n}'))
        for suffix in 'xy':
            write(root, f'nodes/npcs/ref-{n:02}-{suffix}.md', page(body=f'[E](/{target})',
                fm=f'generated: {{by: test, at: 2026-09-{n+1:02}T00:00:00+00:00}}\n'))
    candidates = json.loads(run(root, '--candidates').stdout)
    assert len(candidates) == 25
    assert candidates[0]['entity'] == 'nodes/npcs/entity-26.md'
    assert candidates[-1]['entity'] == 'nodes/npcs/entity-02.md'


def test_flat_configured_nodes_and_stdin_placement(tmp_path):
    root = campaign(tmp_path, {})
    with (root / 'scripts/okf_config.py').open('a') as stream:
        stream.write('\nBUNDLE_DIRS = ["npcs", "story", "sessions"]\n'
                     'DIRECTORY_TYPES = {"npcs": "npc", "story": "story", "sessions": "session"}\n'
                     'GROUPS = [("npcs", "People", "Campaign people."), ("story", "Story", "State.")]\n')
    for path, text in {
        'npcs/entity.md': page('Entity'),
        'npcs/a.md': page('A', body='The bell is red.\n\n[E](/npcs/entity.md)\n[Prep](/sessions/prep.md)'),
        'story/campaign-status.md': page('Live', kind='story', body='The bell is blue.\n\n[E](/npcs/entity.md)'),
        'sessions/prep.md': page('Prep', kind='session', fm='status: draft\n'),
        'npcs/npcs-seed-ideas.md': page('Ideas', kind='seed-ideas', body='## Herald\n\n' + 'durable '*151),
    }.items():
        write(root, path, text)
    report = run(root)
    assert 'groom/orphan npcs/a.md' in report.stdout
    assert 'groom/node-links-draft-session npcs/a.md' in report.stdout
    assert json.loads(run(root, '--candidates').stdout)[0]['entity'] == 'npcs/entity.md'
    evidence = {'entity': 'npcs/entity.md', 'left': 'npcs/a.md', 'right': 'story/campaign-status.md',
                'left_claim': 'The bell is red.', 'right_claim': 'The bell is blue.'}
    before = snapshot(root)
    result = subprocess.run([sys.executable, str(root / 'scripts/okf-groom.py'),
                             '--place-contradiction', '-'], input=json.dumps(evidence),
                            text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert snapshot(root) == before
    assert run(root, '--fix').returncode == 0
    promoted = (root / 'npcs/herald.md').read_text()
    assert 'type: "npc"' in promoted and 'seed-ideas' not in promoted


def test_generated_evidence_and_images_never_connect_orphans(tmp_path):
    root = campaign(tmp_path, {
        'nodes/npcs/a.md': page('A'),
        'story/ref.md': page('Ref', kind='story', body=(
            '![Inline](/nodes/npcs/a.md)\n\n![Portrait][picture]\n\n[picture]: /nodes/npcs/a.md\n\n'
            '> [!contradiction] Unresolved: A\n> Here: "Claim."\n'
            '> Other: [A](/nodes/npcs/a.md) (status: stable): "Other."\n')),
    })
    result = run(root)
    assert result.returncode == 0, result.stderr
    assert 'groom/orphan nodes/npcs/a.md' in result.stdout


def test_nested_bundle_and_configured_session_inbox(tmp_path):
    root = campaign(tmp_path, {'nodes/npcs/a.md': page()})
    bundle = root / 'wiki'
    bundle.mkdir()
    for name in ('nodes', 'index.md'):
        shutil.move(root / name, bundle / name)
    with (root / 'scripts/okf_config.py').open('a') as stream:
        stream.write('\nBUNDLE_ROOT = "wiki"\nBUNDLE_DIRS.append("games")\n'
                     'DIRECTORY_TYPES["games"] = "session"\n'
                     'GROUPS.append(("games", "Games", "Session records."))\n')
    write(bundle, 'games/games-seed-ideas.md', page('Ideas', kind='seed-ideas',
          body='## Herald\n\n' + 'durable '*151))
    write(bundle, 'log.md', '# Log\n\n[A](nodes/npcs/a.md) and [Lost](lost.md).\n')
    before = snapshot(root)
    assert run(root, '--dry-run').returncode == 0
    assert snapshot(root) == before
    result = run(root, '--fix')
    assert result.returncode == 0, result.stderr
    assert 'review required' in result.stdout
    assert not (bundle / 'games/herald.md').exists()
    assert '[A](/nodes/npcs/a.md) and [Lost](lost.md)' in (bundle / 'log.md').read_text()
    assert not (root / 'index.md').exists()


def test_loose_region_preserves_crlf_surroundings(tmp_path):
    root = fixture(tmp_path, 'loose-ends-written', 'failing')
    live = root / 'story/campaign-status.md'
    original = live.read_bytes().replace(b'\n', b'\r\n')
    live.write_bytes(original)
    assert run(root, '--fix').returncode == 0
    updated = live.read_bytes()
    start, end = b'<!-- groom-wiki:loose-ends:start -->', b'<!-- groom-wiki:loose-ends:end -->'
    assert updated.split(start)[0] == original.split(start)[0]
    assert updated.split(end)[1] == original.split(end)[1]
