"""Unit tests for the shared validators — the security-critical boundary the
skill's promises lean on (invalid decision enums, ambiguous item identity,
stale provenance, awarded read-only, malformed shapes)."""

import copy
import json
from pathlib import Path

import review_state

FIXTURE = json.loads(
    (Path(__file__).resolve().parent / "fixtures" / "review-data.json").read_text()
)


def valid_state(**decisions):
    return {"catalogVersion": FIXTURE["catalogVersion"], "decisions": decisions}


def test_fixture_review_data_is_valid():
    assert review_state.validate_review_data(FIXTURE) == []


def test_review_data_must_be_object():
    assert review_state.validate_review_data([1, 2]) == ["review data must be a JSON object"]


def test_review_data_missing_top_level_fields():
    errors = review_state.validate_review_data({})
    assert any("catalogVersion" in e for e in errors)
    assert any("entries" in e for e in errors)


def test_entry_missing_required_field():
    data = copy.deepcopy(FIXTURE)
    del data["entries"][0]["rulesText"]
    assert any("rulesText" in e for e in review_state.validate_review_data(data))


def test_duplicate_id_is_ambiguous_identity():
    data = copy.deepcopy(FIXTURE)
    data["entries"].append(copy.deepcopy(data["entries"][1]))
    errors = review_state.validate_review_data(data)
    assert any("ambiguous item identity: duplicate id" in e for e in errors)


def test_same_name_and_source_is_ambiguous_identity():
    data = copy.deepcopy(FIXTURE)
    clone = copy.deepcopy(data["entries"][1])
    clone["id"] = "a-different-id"
    data["entries"].append(clone)
    errors = review_state.validate_review_data(data)
    assert any("appears twice" in e for e in errors)


def test_unknown_origin_rejected():
    data = copy.deepcopy(FIXTURE)
    data["entries"][0]["origin"] = "wishlist"
    assert any("unknown origin" in e for e in review_state.validate_review_data(data))


def test_awarded_entries_need_no_target_or_fit_note():
    awarded = [e for e in FIXTURE["entries"] if e["origin"] == "awarded"]
    assert awarded and "target" not in awarded[0]
    assert review_state.validate_review_data(FIXTURE) == []


def test_valid_state_passes():
    state = valid_state(**{
        "pearl-of-power--gm-guide-2024": {"decision": "approve", "note": "she'll love it"},
        "immovable-rod--gm-guide-2024": {
            "decision": "defer", "deferCondition": "after the Trust Job resolves",
        },
    })
    assert review_state.validate_state(state, FIXTURE) == []


def test_unknown_decision_enum_rejected():
    state = valid_state(**{"pearl-of-power--gm-guide-2024": {"decision": "maybe"}})
    assert any("unknown decision 'maybe'" in e for e in review_state.validate_state(state, FIXTURE))


def test_unknown_item_id_rejected():
    state = valid_state(**{"vorpal-sword--nowhere": {"decision": "approve"}})
    assert any("unknown item id" in e for e in review_state.validate_state(state, FIXTURE))


def test_awarded_items_are_read_only():
    state = valid_state(**{"potion-of-healing--awarded-session-1": {"decision": "approve"}})
    errors = review_state.validate_state(state, FIXTURE)
    assert any("read-only awarded item" in e for e in errors)


def test_stale_catalog_version_rejected():
    state = {"catalogVersion": "an-older-run", "decisions": {}}
    assert any("stale decision state" in e for e in review_state.validate_state(state, FIXTURE))


def test_defer_condition_requires_defer_decision():
    state = valid_state(**{
        "pearl-of-power--gm-guide-2024": {"decision": "approve", "deferCondition": "level 5"},
    })
    errors = review_state.validate_state(state, FIXTURE)
    assert any("whose decision is not 'defer'" in e for e in errors)


def test_unexpected_record_fields_rejected():
    state = valid_state(**{
        "pearl-of-power--gm-guide-2024": {"decision": "approve", "statePath": "/etc/passwd"},
    })
    errors = review_state.validate_state(state, FIXTURE)
    assert any("unknown field(s)" in e for e in errors)


def test_untouched_graveyard_entry_stays_removed():
    entry = next(e for e in FIXTURE["entries"] if e["origin"] == "graveyard")
    assert review_state.decision_for(entry, valid_state()) == "remove"


def test_explicit_record_restores_graveyard_entry():
    entry = next(e for e in FIXTURE["entries"] if e["origin"] == "graveyard")
    state = valid_state(**{entry["id"]: {"decision": "unreviewed"}})
    assert review_state.decision_for(entry, state) == "unreviewed"
