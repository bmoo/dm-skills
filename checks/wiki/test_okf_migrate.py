"""Migration's shipped bundle fixture and installed-runtime preservation checks."""

import shutil
import subprocess
import sys

import pytest

from wiki_scaffold_lint import TEMPLATE

FIXTURES = TEMPLATE.parent / "fixtures/migration"


def install(tmp_path, *, nested=False, config="", alternate_source=False):
    repo = tmp_path / "campaign"
    repo.mkdir()
    bundle = repo / "wiki" if nested else repo
    shutil.copytree(FIXTURES / "input", bundle, dirs_exist_ok=True)
    shutil.copytree(TEMPLATE / "scripts", repo / "scripts")
    if alternate_source:
        for path in bundle.rglob("*.md"):
            path.write_text(path.read_text().replace("timestamp:", "last_updated:"))
    with (repo / "scripts/okf_config.py").open("a") as stream:
        if nested:
            stream.write('\nBUNDLE_ROOT = "wiki"\n')
        stream.write("\n" + config)
    return repo, bundle


def run(repo, script="okf-migrate.py", *args):
    return subprocess.run(
        [sys.executable, str(repo / "scripts" / script), *args],
        cwd=repo.parent, capture_output=True, text=True,
    )


def snapshot(root):
    return {str(p.relative_to(root)): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


def test_fixture_matches_expected_strict_clean_and_idempotent(tmp_path):
    repo, bundle = install(tmp_path)
    result = run(repo)
    assert result.returncode == 0, result.stderr
    for expected in (FIXTURES / "expected").rglob("*"):
        if expected.is_file():
            actual = bundle / expected.relative_to(FIXTURES / "expected")
            assert actual.read_bytes() == expected.read_bytes(), str(actual)
    before = snapshot(repo)
    assert run(repo).returncode == 0
    assert snapshot(repo) == before
    checked = run(repo, "okf-check.py", "--strict")
    assert checked.returncode == 0, checked.stdout + checked.stderr
    assert "[lost report](missing/report.md#old)" in (bundle / "log.md").read_text()
    assert "[old file](gone.md)" in (bundle / "nodes/npcs/log.md").read_text()


def test_second_config_uses_other_source_actor_types_and_status_map(tmp_path):
    repo, bundle = install(tmp_path, nested=True, alternate_source=True, config='''
MIGRATION_SOURCE_KEY = "last_updated"
MIGRATION_ACTOR = "campaignbot/postsession"
MIGRATION_STATUS_MAP = dict(MIGRATION_STATUS_MAP, prep="stable")
BUNDLE_DIRS.append("party")
DIRECTORY_TYPES["party"] = "player"
DIRECTORY_TYPES["."] = "reference"
ROOT_CONCEPTS.append("overview.md")
''')
    party = bundle / "party"
    party.mkdir()
    text = '---\ndescription: A campaign record.\ntags: []\nstatus: active\nlast_updated: 2026-08-09\n---\n\n# Visitor\n'
    (party / "Visitor Name.md").write_text(text + '\n[Overview](../overview.md)\n')
    (bundle / "overview.md").write_text(text + '\n[Visitor](party/Visitor%20Name.md)\n')
    result = run(repo)
    assert result.returncode == 0, result.stderr
    for path in bundle.rglob("*.md"):
        migrated = path.read_text()
        assert "last_updated:" not in migrated
        assert "human:brad" not in migrated
    scout = (bundle / "nodes/npcs/scout.md").read_text()
    assert '"by": "campaignbot/postsession"' in scout
    assert 'status: "stable"' in scout
    assert 'type: "player"' in (party / "Visitor Name.md").read_text()
    assert 'type: "reference"' in (bundle / "overview.md").read_text()
    assert '(/party/Visitor%20Name.md)' in (bundle / "overview.md").read_text()
    checked = run(repo, "okf-check.py", "--strict")
    assert checked.returncode == 0, checked.stdout + checked.stderr
    before = snapshot(repo)
    assert run(repo).returncode == 0
    assert snapshot(repo) == before


@pytest.mark.parametrize(("status", "mapped", "decision"), [
    ("stub", "draft", None), ("prep", "draft", None),
    ("active", "stable", None), ("canon", "stable", None),
    ("inactive", "deprecated", None), ("superseded", "deprecated", None),
    ("proposed", "draft", "proposed"), ("accepted", "stable", "accepted"),
    ("amended", "stable", "amended"), ("accepted (amended)", "stable", "amended"),
])
def test_status_and_adr_decision_maps(tmp_path, status, mapped, decision):
    repo, bundle = install(tmp_path)
    path = bundle / "story/council.md"
    path.write_text(path.read_text().replace("accepted (amended)", status))
    assert run(repo).returncode == 0
    result = path.read_text()
    assert f'status: "{mapped}"' in result
    assert (f'decision: "{decision}"' in result) if decision else "decision:" not in result


def test_preserves_extensions_existing_provenance_and_unknown_values(tmp_path):
    repo, bundle = install(tmp_path, config='MIGRATION_BACKFILL_TYPE = False\nMIGRATION_BACKFILL_TITLE = False\n')
    path = bundle / "nodes/npcs/scout.md"
    unknown = "# Untouched extension bytes\ncustom:\n  enabled: false\n  number: 007\n  sources: [{name: 'a', rank: 0.70}]\n"
    provenance = "generated:\n  by: human:original\n  at: 2020-01-02T00:00:00Z\n"
    path.write_text('---\nstatus: unusual\ntags: [npc, prep, strange]\ntimestamp: invalid-but-obsolete\n' + unknown + provenance + '---\n\n# Scout\n')
    council = bundle / "story/council.md"
    council.write_text(council.read_text().replace('type: story\n', "type: story\ndecision: amended\n"))
    assert run(repo).returncode == 0
    result = path.read_text()
    assert unknown + provenance in result
    assert "timestamp:" not in result
    assert 'tags: ["npc", "strange"]' in result
    assert "status: unusual" in result
    assert "type:" not in result and "title:" not in result
    assert "decision: amended\n" in council.read_text()
    # Missing provenance is never guessed from the clock.
    path.write_text('---\ntype: npc\n---\n# Scout\n')
    assert run(repo).returncode == 0
    assert path.read_text() == '---\ntype: npc\n---\n# Scout\n'


@pytest.mark.parametrize("bad", [
    '---\ntags: [unfinished\n---\n# Bad\n',
    '---\ntimestamp: 2026-02-31\n---\n# Bad\n',
    '---\ntimestamp: 2026-09-12T12:00:00\n---\n# Bad\n',
    '---\ntimestamp: 2026-08-01\n# Unclosed\n',
    '---\ntags: canon, prep\n---\n# Bad\n',
    '---\nstatus: accepted\ndecision: proposed\n---\n# Conflict\n',
])
def test_invalid_metadata_aborts_all_writes(tmp_path, bad):
    repo, bundle = install(tmp_path)
    (bundle / "story/z-invalid.md").write_text(bad)
    before = snapshot(repo)
    result = run(repo)
    assert result.returncode == 1
    assert "no files changed" in result.stderr
    assert snapshot(repo) == before


def test_link_resolution_preserves_broken_external_and_outside_targets(tmp_path):
    repo, bundle = install(tmp_path)
    path = bundle / "nodes/npcs/scout.md"
    (repo.parent / "outside.md").write_text("# Outside\n")
    (bundle / "media/escape.md").symlink_to(repo.parent / "outside.md")
    (bundle / "media/Map (old).svg").write_text("<svg/>\n")
    preserved = '''
[missing](<missing file.md#anchor> "Missing")
[outside](../../../outside.md)
[escape](../../media/escape.md)
[web](https://example.com/x)
[protocol](//example.com/x)
[email](mailto:dm@example.com)
[data](data:image/png;base64,abc)
[existing](/nodes/npcs/scout.md#friends)
'''
    path.write_text(path.read_text() + preserved + '\n![escaped](../../media/Map%20\\(old\\).svg)\n[dir](../../media/)\n')
    assert run(repo).returncode == 0
    text = path.read_text()
    assert preserved in text
    assert '![escaped](/media/Map%20%28old%29.svg)' in text
    assert '[dir](/media/)' in text


def test_crlf_and_unrelated_log_comments_survive(tmp_path):
    repo, bundle = install(tmp_path)
    path = bundle / "nodes/npcs/scout.md"
    old = path.read_text().replace('\n', '\r\n')
    path.write_bytes(old.encode())
    log = bundle / "log.md"
    log.write_text('<!-- Keep this editorial note. -->\n# Log\n\n## 2026-08-10\n\n* **Update**: [Scout](nodes/npcs/scout.md)\n')
    assert run(repo).returncode == 0
    expected = (FIXTURES / "expected/nodes/npcs/scout.md").read_text().replace('\n', '\r\n').encode()
    assert path.read_bytes() == expected
    assert log.read_text().startswith('<!-- Keep this editorial note. -->\n')


def test_missing_frontmatter_and_block_tags_preserve_body_and_comments(tmp_path):
    repo, bundle = install(tmp_path)
    path = bundle / "nodes/npcs/scout.md"
    body = "```md\n# Wrong title\n```\n\n# C# visitor ###\n\n[Root](../../)\n"
    path.write_text(body)
    assert run(repo).returncode == 0
    text = path.read_text()
    assert text.startswith('---\ntype: "npc"\ntitle: "C# visitor"\n---\n')
    assert text.endswith(body.replace('[Root](../../)', '[Root](/)'))
    path.write_text('---\ntype: npc\ntags:\n- stub\n# Keep this note.\n- recurring\n- canon\nunknown: 007\n---\n# Scout\n')
    assert run(repo).returncode == 0
    assert 'tags: ["recurring"]\n# Keep this note.\nunknown: 007\n' in path.read_text()


def test_symlink_concept_cannot_migrate_outside_bundle(tmp_path):
    repo, bundle = install(tmp_path)
    outside = repo.parent / "outside.md"
    outside.write_text('---\ntimestamp: 2026-08-09\nstatus: active\n---\n# Outside\n')
    (bundle / "nodes/npcs/outside.md").symlink_to(outside)
    before = snapshot(repo.parent)
    result = run(repo)
    assert result.returncode == 1
    assert snapshot(repo.parent) == before
