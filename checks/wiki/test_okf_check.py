"""Each stable checker id has isolated fixtures exercised as an installed tool."""

from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from wiki_scaffold_lint import TEMPLATE

FIXTURES = TEMPLATE.parent / "fixtures"
ERROR_IDS = {"okf/frontmatter-parses", "okf/type-present", "okf/reserved-file-shape"}


@pytest.fixture
def campaign(tmp_path):
    root = tmp_path / "campaign"
    shutil.copytree(TEMPLATE / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    return root


def run_check(root, *args):
    return subprocess.run([sys.executable, str(root / "scripts/okf-check.py"), *args],
                          cwd=root.parent, capture_output=True, text=True)


def ids(result):
    assert not result.stderr, result.stderr
    return set(re.findall(r"\[((?:okf|wiki)/[a-z-]+)\]", result.stdout))


def concept(root, text):
    path = root / "nodes/npcs/example.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def baseline():
    return (FIXTURES / "okf/type-present/pass.md").read_text()


def assert_fixture(root, check_id):
    fixture = FIXTURES / check_id
    for outcome in ("pass", "fail"):
        if check_id == "okf/reserved-file-shape":
            shutil.copytree(fixture / outcome, root, dirs_exist_ok=True)
        else:
            concept(root, (fixture / f"{outcome}.md").read_text())
        result = run_check(root, "--warnings")
        assert ids(result) == (set() if outcome == "pass" else {check_id}), result.stdout
        assert result.returncode == int(outcome == "fail" and check_id in ERROR_IDS), result.stdout
        strict = run_check(root, "--strict")
        assert ids(strict) == ids(result), strict.stdout
        assert strict.returncode == int(outcome == "fail"), strict.stdout


def test_okf_frontmatter_parses(campaign):
    assert_fixture(campaign, "okf/frontmatter-parses")


def test_okf_type_present(campaign):
    assert_fixture(campaign, "okf/type-present")


def test_okf_reserved_file_shape(campaign):
    assert_fixture(campaign, "okf/reserved-file-shape")


def test_okf_expected_keys(campaign):
    assert_fixture(campaign, "okf/expected-keys")


def test_okf_generated_by(campaign):
    assert_fixture(campaign, "okf/generated-by")


def test_okf_timestamp_offset(campaign):
    assert_fixture(campaign, "okf/timestamp-offset")


def test_okf_actor_shape(campaign):
    assert_fixture(campaign, "okf/actor-shape")


def test_okf_status_enum(campaign):
    assert_fixture(campaign, "okf/status-enum")


def test_okf_legacy_timestamp(campaign):
    assert_fixture(campaign, "okf/legacy-timestamp")


def test_wiki_type_matches_directory(campaign):
    assert_fixture(campaign, "wiki/type-matches-directory")


@pytest.mark.parametrize("root_types,expected", [
    ("", set()),
    ('DIRECTORY_TYPES["."] = "reference"', set()),
    ('DIRECTORY_TYPES["."] = "hub"', {"wiki/type-matches-directory"}),
])
def test_root_concept_type_is_checked_only_when_configured(campaign, root_types, expected):
    with (campaign / "scripts/okf_config.py").open("a") as stream:
        stream.write(f'\nROOT_CONCEPTS.append("overview.md")\n{root_types}\n')
    (campaign / "overview.md").write_text(baseline().replace("type: npc", "type: reference"))
    assert ids(run_check(campaign, "--warnings")) == expected


def test_wiki_tags_suggested(campaign):
    assert_fixture(campaign, "wiki/tags-suggested")


def test_wiki_description_plain(campaign):
    assert_fixture(campaign, "wiki/description-plain")


def test_wiki_link_form(campaign):
    assert_fixture(campaign, "wiki/link-form")


def test_warning_only_bundle_exits_zero_without_flags(campaign):
    concept(campaign, baseline().replace('status: draft', 'status: active'))
    result = run_check(campaign)
    assert result.returncode == 0
    assert "1 warning(s)" in result.stdout
    assert run_check(campaign, "--strict").returncode == 1


@pytest.mark.parametrize("text,expected", [
    ("# Missing frontmatter\n", {"okf/frontmatter-parses"}),
    ("---\n---\n# Empty frontmatter\n", {"okf/type-present", "okf/expected-keys"}),
    ("---\ntype: npc\n---", {"okf/expected-keys"}),
    ("---\ntype: [npc]\n---\n", {"okf/type-present", "okf/expected-keys", "wiki/type-matches-directory"}),
])
def test_frontmatter_error_boundaries(campaign, text, expected):
    concept(campaign, text)
    assert ids(run_check(campaign, "--warnings")) == expected


@pytest.mark.parametrize("metadata,expected", [
    ('verified: {by: human:brad, at: 2026-09-12T00:00:00Z}', set()),
    ('verified:\n  - by: process:review\n    at: 2026-09-12T00:00:00+01:00', set()),
    ('verified: {by: human:brad, at: 2026-09-12T00:00:00}', {'okf/timestamp-offset'}),
    ('verified: [{by: brad, at: 2026-09-12T00:00:00Z}]', {'okf/actor-shape'}),
    ('verified: {by: brad, at: 2026-09-12T00:00:00Z}', {'okf/actor-shape'}),
    ('stale_after: 2026-02-30T00:00:00Z', {'okf/timestamp-offset'}),
    ('stale_after: 2026-09-12T00:00:00Z\nnext_session: 2026-09-11', set()),
    ('generated: []', {'okf/generated-by'}),
    ('tags: [{name: recurring}]', {'wiki/tags-suggested'}),
    ('status: [draft]', {'okf/status-enum'}),
])
def test_optional_metadata_warnings_do_not_crash_or_reject(campaign, metadata, expected):
    concept(campaign, baseline().replace('---\n\n# Example', metadata + '\n---\n\n# Example'))
    result = run_check(campaign, "--warnings")
    assert result.returncode == 0
    assert ids(result) == expected


def test_tag_may_equal_an_existing_concept_basename(campaign):
    concept(campaign, baseline().replace('[recurring]', '[the-warden]'))
    (campaign / "nodes/npcs/the-warden.md").write_text(baseline())
    assert run_check(campaign, "--strict").returncode == 0


@pytest.mark.parametrize("tag,expected", [
    ("wardens", set()),                 # a word of the basename
    ("canyons", set()),                 # the last word, not a prefix
    ("wardens-of-the-canyons", set()),  # the whole basename
    ("wardens-of", set()),              # a hyphen-delimited prefix
    ("trust", set()),                   # a word after a leading stopword
    ("the", {"wiki/tags-suggested"}),   # a bare stopword segment
    ("of", {"wiki/tags-suggested"}),
    ("marsh", {"wiki/tags-suggested"}), # no concept mentions it
    ("of-the", {"wiki/tags-suggested"}),  # neither a word nor a prefix
])
def test_tag_may_equal_a_word_or_prefix_of_an_existing_concept_basename(campaign, tag, expected):
    concept(campaign, baseline().replace('[recurring]', f'[{tag}]'))
    for name in ("wardens-of-the-canyons", "the-trust"):
        (campaign / f"nodes/npcs/{name}.md").write_text(baseline())
    result = run_check(campaign, "--warnings")
    assert result.returncode == 0
    assert ids(result) == expected, result.stdout


@pytest.mark.parametrize('link', [
    '[Missing](unwritten.md)', '![Map](../media/map.png)', '[Section](other.md#details)',
    '[Name](<a spaced file.md> "A title")', '[Name](folder/a(b).md)',
    '[Name][ref]\n\n[ref]: missing.md "Title"',
])
def test_relative_link_forms_only_warn(campaign, link):
    concept(campaign, baseline() + '\n' + link)
    result = run_check(campaign, "--warnings")
    assert result.returncode == 0
    assert ids(result) == {'wiki/link-form'}


def test_link_examples_and_external_uri_schemes_are_ignored(campaign):
    concept(campaign, baseline() + '''
[Link](https://example.com) [Email](mailto:brad@example.com)
[File](file:///tmp/example.md) [Phone](tel:+12345)
[CDN](//example.com/map.png) [Future](/missing.md#anchor) [Here](#a-heading)
`[Example](relative.md)` and ``[Example](relative.md)``.

```markdown
[Example](relative.md)
```

~~~markdown
[Example](relative.md)
~~~

    [Example](relative.md)

<!-- [Example](relative.md) -->
''')
    assert run_check(campaign, "--strict").returncode == 0


@pytest.mark.parametrize('path,text,valid', [
    ('index.md', '---\nokf_version: "9.9"\n---\n# Index\n* [Future](/future.md) - Future.\n', True),
    ('index.md', '---\nwrong: [\n---\n# Index\n* [Future](/future.md)\n', False),
    ('index.md', '---\nokf_version: "0.2"\n# Index\n* [Future](/future.md)\n', False),
    ('nodes/npcs/index.md', '---\nokf_version: "0.2"\n---\n# Index\n* [Future](/future.md)\n', False),
    ('index.md', '# Index\n', False),
    ('log.md', '# Log\n## 2026-02-30\n* Entry\n', False),
    ('nodes/npcs/log.md', '# Log\n## 2026-01-01\n* Entry\n## 2026-02-01\n* Entry\n', False),
    ('log.md', '---\ncustom: metadata\n---\n# Log\n## 2026-09-12\n* Unlabelled entry.\n', True),
    ('log.md', '<!--\n## YYYY-MM-DD\n-->\n# Log\n', True),
])
def test_reserved_shape_at_any_depth(campaign, path, text, valid):
    target = campaign / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    result = run_check(campaign, '--strict')
    assert result.returncode == (0 if valid else 1), result.stdout
    assert ids(result) == (set() if valid else {'okf/reserved-file-shape'})


def test_checker_is_read_only_with_nested_bundle_and_flat_type_config(campaign):
    config = campaign / 'scripts/okf_config.py'
    with config.open('a') as stream:
        stream.write('''
BUNDLE_ROOT = "wiki"
BUNDLE_DIRS = ["party", "analysis"]
ROOT_CONCEPTS = ["hub.md"]
DIRECTORY_TYPES = {"party": "player", "analysis": "analysis"}
''')
    bundle = campaign / 'wiki'
    (bundle / 'party').mkdir(parents=True)
    (bundle / 'hub.md').write_text(baseline().replace('type: npc', 'type: reference'))
    (bundle / 'party/old friend.md').write_text(baseline().replace('type: npc', 'type: player'))
    (bundle / 'party/log.md').write_text('# Log\n## 2026-09-12\n* Entry\n')
    # Excluded tooling and files outside the bundle are not concepts.
    (bundle / 'party/scripts').mkdir()
    (bundle / 'party/scripts/notes.md').write_text('no frontmatter')
    (campaign / 'not-a-concept.md').write_text('no frontmatter')
    before = {p.relative_to(campaign): (p.read_bytes(), p.stat().st_mtime_ns)
              for p in campaign.rglob('*') if p.is_file()}
    result = run_check(campaign, '--strict')
    assert result.returncode == 0, result.stdout
    assert '2 concepts, 1 reserved files' in result.stdout
    after = {p.relative_to(campaign): (p.read_bytes(), p.stat().st_mtime_ns)
             for p in campaign.rglob('*') if p.is_file()}
    assert after == before
