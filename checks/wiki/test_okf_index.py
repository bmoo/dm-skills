"""Run the shipped catalog generator against disposable campaign bundles."""

import re
import shutil
import subprocess
import sys

import pytest

from wiki_scaffold_lint import TEMPLATE


@pytest.fixture
def campaign(tmp_path):
    root = tmp_path / "campaign"
    shutil.copytree(TEMPLATE, root)
    return root


def run_index(campaign, *args):
    return subprocess.run(
        [sys.executable, str(campaign / "scripts/okf-index.py"), *args],
        cwd=campaign, capture_output=True, text=True,
    )


def write_concept(path, title, description="A campaign concept."):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntype: npc\ntitle: {title}\ndescription: {description}\n"
        "tags: []\nstatus: draft\n"
        "generated: {by: dm-skills/setup, at: 2026-09-12T00:00:00-07:00}\n"
        f"---\n\n# {title}\n", encoding="utf-8",
    )


def test_catalog_version_root_concepts_and_bundle_relative_entries(campaign):
    assert run_index(campaign).returncode == 0
    root_index = (campaign / "index.md").read_text()
    assert root_index.startswith('---\nokf_version: "0.2"\n---\n')
    assert "* [Campaign Wiki Schema](/wiki-schema.md) - " in root_index
    assert "* [NPC Seed Ideas](/nodes/npcs/npcs-seed-ideas.md) - " in root_index
    for index in campaign.rglob("index.md"):
        text = index.read_text()
        if index != campaign / "index.md":
            assert not text.startswith("---")
        for line in text.splitlines():
            if line.startswith("* "):
                assert re.fullmatch(r"\* \[.+\]\((?:/[^ ]+\.md|[^ /]+/)\) - .+", line)
                assert "— *" not in line
    nested = (campaign / "nodes/npcs/index.md").read_text()
    assert "](/nodes/npcs/npcs-seed-ideas.md) - " in nested


def test_group_descriptions_and_encoded_paths_with_seeds_last(campaign):
    config = campaign / "scripts/okf_config.py"
    with config.open("a") as stream:
        stream.write('\nGROUPS.append(("nodes/old town", "Old Town", "A custom group description."))\n')
    write_concept(campaign / "nodes/old town/first guard.md", "First Guard")
    write_concept(campaign / "nodes/npcs/zebra.md", "Zebra")
    write_concept(campaign / "nodes/npcs/alpha.md", "Alpha")
    assert run_index(campaign).returncode == 0
    assert "* [Old Town](old%20town/) - A custom group description." in (
        campaign / "nodes/index.md"
    ).read_text()
    expected = "* [First Guard](/nodes/old%20town/first%20guard.md) - A campaign concept."
    assert expected in (campaign / "index.md").read_text()
    assert expected in (campaign / "nodes/old town/index.md").read_text()
    entries = [line for line in (campaign / "nodes/npcs/index.md").read_text().splitlines()
               if line.startswith("* ")]
    assert [re.search(r"\[([^]]+)\]", line)[1] for line in entries] == [
        "Alpha", "Zebra", "NPC Seed Ideas",
    ]


def test_check_detects_changed_frontmatter_without_writing(campaign):
    assert run_index(campaign).returncode == 0
    assert run_index(campaign, "--check").returncode == 0
    before = {p: p.read_bytes() for p in campaign.rglob("index.md")}
    write_concept(campaign / "nodes/npcs/alpha.md", "Alpha", "A newly arrived patron.")
    check = run_index(campaign, "--check")
    assert check.returncode == 1
    assert "stale  index.md" in check.stdout
    assert "stale  nodes/npcs/index.md" in check.stdout
    assert {p: p.read_bytes() for p in campaign.rglob("index.md")} == before
    assert run_index(campaign).returncode == 0
    assert run_index(campaign, "--check").returncode == 0


def test_configured_bundle_root_and_root_concept(campaign):
    bundle = campaign / "wiki"
    bundle.mkdir()
    for name in ("nodes", "story", "players", "sessions", "wiki-schema.md", "log.md"):
        shutil.move(campaign / name, bundle / name)
    with (campaign / "scripts/okf_config.py").open("a") as stream:
        stream.write('\nBUNDLE_ROOT = "wiki"\nROOT_CONCEPTS.append("campaign notes.md")\n')
    write_concept(bundle / "campaign notes.md", "Campaign Notes")
    assert run_index(campaign).returncode == 0
    assert not (campaign / "index.md").exists()
    assert "* [Campaign Notes](/campaign%20notes.md) - " in (bundle / "index.md").read_text()
    assert run_index(campaign, "--check").returncode == 0
