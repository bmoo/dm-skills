"""Ingest tests: the Approved Reward Pool comes out in its narrow consumer
shape, refusals write nothing, and the change report matches the decisions."""

import json

import ingest

from conftest import FIXTURES


def load_fixture():
    return json.loads((FIXTURES / "review-data.json").read_text(encoding="utf-8"))


def write_pair(tmp_path, data, state):
    data_path = tmp_path / "review-data.json"
    state_path = tmp_path / "decisions.json"
    data_path.write_text(json.dumps(data), encoding="utf-8")
    state_path.write_text(json.dumps(state), encoding="utf-8")
    return data_path, state_path


def full_decision_state(data):
    return {
        "catalogVersion": data["catalogVersion"],
        "decisions": {
            "lantern-of-tracking--gm-guide-2024": {"decision": "approve", "note": "still earning its slot"},
            "pearl-of-power--gm-guide-2024": {"decision": "approve"},
            "staff-of-the-adder--gm-guide-2024": {"decision": "remove", "note": "not exciting"},
            "sentinel-shield--gm-guide-2024": {
                "decision": "defer", "deferCondition": "after the Trust Job resolves",
            },
        },
    }


def test_pool_contains_exactly_approved_items_in_consumer_shape(tmp_path, capsys):
    data = load_fixture()
    data_path, state_path = write_pair(tmp_path, data, full_decision_state(data))
    pool_path = tmp_path / "approved-reward-pool.md"
    assert ingest.main(["--data", str(data_path), "--state", str(state_path),
                        "--pool-out", str(pool_path)]) == 0
    pool = pool_path.read_text(encoding="utf-8")

    assert "# Approved Reward Pool" in pool
    assert "**Proposal standard:**" in pool
    assert "Reviewed at party level 3." in pool
    assert "The Unlit Lantern delve" in pool and "The Trust Job" in pool
    assert "## Eligible Now" in pool
    # Exactly the approved/retained items, each in the entry shape.
    assert "- **Lantern of Tracking** (common, no attunement) — the whole party — " in pool
    assert "- **Pearl of Power** (uncommon, requires attunement by a spellcaster) — Avery — " in pool
    # Deferred, removed, graveyard, and awarded items never appear as Eligible Now.
    for absent in ("Sentinel Shield", "Staff of the Adder",
                   "Boots of Elvenkind", "Potion of Healing"):
        assert absent not in pool
    # The narrow contract carries no rules text, notes, or deferral conditions.
    assert "Fixture text standing in" not in pool
    assert "still earning its slot" not in pool
    assert "after the Trust Job resolves" not in pool


def test_change_report_buckets(tmp_path, capsys):
    data = load_fixture()
    data_path, state_path = write_pair(tmp_path, data, full_decision_state(data))
    ingest.main(["--data", str(data_path), "--state", str(state_path),
                 "--pool-out", str(tmp_path / "pool.md")])
    report = capsys.readouterr().out
    assert "**Additions (1):**" in report and "Pearl of Power" in report
    assert "**Retained (1):**" in report and "Lantern of Tracking" in report
    assert "**Deferred (1):**" in report and "until: after the Trust Job resolves" in report
    assert "**Removed (1):**" in report and "Staff of the Adder" in report
    # Immovable Rod was never marked; untouched graveyard boots are not a change.
    assert "**Left unreviewed (1):**" in report and "Immovable Rod" in report
    assert "Boots of Elvenkind" not in report


def test_restored_and_approved_graveyard_item_becomes_eligible(tmp_path):
    data = load_fixture()
    state = {
        "catalogVersion": data["catalogVersion"],
        "decisions": {"boots-of-elvenkind--gm-guide-2024": {"decision": "approve"}},
    }
    data_path, state_path = write_pair(tmp_path, data, state)
    pool_path = tmp_path / "pool.md"
    assert ingest.main(["--data", str(data_path), "--state", str(state_path),
                        "--pool-out", str(pool_path)]) == 0
    assert "Boots of Elvenkind" in pool_path.read_text(encoding="utf-8")


def test_empty_pool_renders_none_marker(tmp_path):
    data = load_fixture()
    state = {"catalogVersion": data["catalogVersion"], "decisions": {}}
    data_path, state_path = write_pair(tmp_path, data, state)
    pool_path = tmp_path / "pool.md"
    ingest.main(["--data", str(data_path), "--state", str(state_path),
                 "--pool-out", str(pool_path)])
    assert "*(none — no items are currently approved for silent placement)*" in \
        pool_path.read_text(encoding="utf-8")


def test_invalid_state_refused_and_nothing_written(tmp_path, capsys):
    data = load_fixture()
    state = {"catalogVersion": data["catalogVersion"],
             "decisions": {"pearl-of-power--gm-guide-2024": {"decision": "yeet"}}}
    data_path, state_path = write_pair(tmp_path, data, state)
    pool_path = tmp_path / "pool.md"
    assert ingest.main(["--data", str(data_path), "--state", str(state_path),
                        "--pool-out", str(pool_path)]) == 1
    assert not pool_path.exists()
    assert "ingest refused" in capsys.readouterr().err


def test_stale_provenance_refused(tmp_path):
    data = load_fixture()
    state = {"catalogVersion": "an-older-run", "decisions": {}}
    data_path, state_path = write_pair(tmp_path, data, state)
    pool_path = tmp_path / "pool.md"
    assert ingest.main(["--data", str(data_path), "--state", str(state_path),
                        "--pool-out", str(pool_path)]) == 1
    assert not pool_path.exists()


def test_malformed_state_file_refused(tmp_path):
    data = load_fixture()
    data_path = tmp_path / "review-data.json"
    data_path.write_text(json.dumps(data), encoding="utf-8")
    state_path = tmp_path / "decisions.json"
    state_path.write_text("{broken", encoding="utf-8")
    pool_path = tmp_path / "pool.md"
    assert ingest.main(["--data", str(data_path), "--state", str(state_path),
                        "--pool-out", str(pool_path)]) == 1
    assert not pool_path.exists()
