"""The primary end-to-end seam: fixture catalog → served review app → browser
decisions saved over HTTP → process restart → graveyard restore → ingest →
final Approved Reward Pool. Everything the DM or a session builder can observe,
nothing about internal structure."""

import json

import ingest

from conftest import http, running_server


def get_review(base):
    status, payload = http("GET", base + "/api/review")
    assert status == 200
    return payload


def post_state(base, state):
    status, body = http("POST", base + "/api/state", state)
    assert status == 200, body
    return body


def test_full_review_workflow(review_files, tmp_path, capsys):
    data_path, state_path = review_files
    data = json.loads(data_path.read_text(encoding="utf-8"))
    version = data["catalogVersion"]

    # --- Serve: the page and payload carry everything the review must show.
    with running_server(data_path, state_path) as base:
        status, page = http("GET", base + "/")
        assert status == 200
        # Rendering hooks for every reviewable surface the skill promises.
        for hook in ("Active review", "Awarded items", "read-only",
                     "Graveyard", "details", "Unreviewed", "Approve / Keep Eligible",
                     "Defer", "Remove", "Restore to active review"):
            assert hook in page, hook

        payload = get_review(base)
        by_origin = {}
        for entry in payload["data"]["entries"]:
            by_origin.setdefault(entry["origin"], []).append(entry)
        assert by_origin["existing"] and by_origin["candidate"]
        assert by_origin["awarded"] and by_origin["graveyard"]
        # Full official text, targeting rationale, and gear comparison ride
        # every reviewable entry.
        for entry in by_origin["candidate"]:
            assert entry["rulesText"] and entry["target"] and entry["fitNote"]
            assert "gearRelation" in entry
        # The invocation-level depth override is what generated this catalog;
        # the served payload preserves it for the page header.
        assert payload["data"]["requestedDepth"] == {"perPC": 2, "party": 1}

        # --- The DM reviews: decisions accumulate save by save.
        state = {"catalogVersion": version, "decisions": {}}
        state["decisions"]["lantern-of-tracking--gm-guide-2024"] = {"decision": "approve"}
        post_state(base, state)
        state["decisions"]["pearl-of-power--gm-guide-2024"] = {"decision": "approve"}
        state["decisions"]["staff-of-the-adder--gm-guide-2024"] = {"decision": "remove"}
        state["decisions"]["sentinel-shield--gm-guide-2024"] = {
            "decision": "defer", "deferCondition": "after the Trust Job resolves"}
        post_state(base, state)

    # --- Restart: a new server process over the same files sees every decision.
    with running_server(data_path, state_path) as base:
        payload = get_review(base)
        saved = payload["state"]["decisions"]
        assert saved["pearl-of-power--gm-guide-2024"]["decision"] == "approve"
        assert saved["sentinel-shield--gm-guide-2024"]["deferCondition"] == \
            "after the Trust Job resolves"

        # --- Restore from the graveyard, then approve the restored item.
        state = payload["state"]
        state["decisions"]["boots-of-elvenkind--gm-guide-2024"] = {"decision": "unreviewed"}
        post_state(base, state)
        state["decisions"]["boots-of-elvenkind--gm-guide-2024"] = {"decision": "approve"}
        post_state(base, state)

    # --- Ingest: the DM said done; the pool comes out in consumer shape.
    pool_path = tmp_path / "approved-reward-pool.md"
    assert ingest.main(["--data", str(data_path), "--state", str(state_path),
                        "--pool-out", str(pool_path)]) == 0
    pool = pool_path.read_text(encoding="utf-8")
    report = capsys.readouterr().out

    eligible_lines = [l for l in pool.splitlines() if l.startswith("- **")]
    assert sorted(eligible_lines) == sorted([
        "- **Lantern of Tracking** (common, no attunement) — the whole party — "
        "Still level-appropriate; the party's wilderness legs keep it useful.",
        "- **Pearl of Power** (uncommon, requires attunement by a spellcaster) — Avery — "
        "Slot recovery is strong for every Druid play style, circle unknown or not.",
        "- **Boots of Elvenkind** (uncommon, no attunement) — Rook — "
        "Removed last review as redundant with his Stealth expertise.",
    ])
    # Deferred and removed items are not Eligible Now; awarded stays history.
    assert "Sentinel Shield" not in pool
    assert "Staff of the Adder" not in pool
    assert "Potion of Healing" not in pool
    # No full official text leaks into the consumer contract.
    assert "Fixture text standing in" not in pool

    # The completion report names every change.
    assert "Pearl of Power" in report and "Boots of Elvenkind" in report
    assert "**Deferred (1):**" in report and "**Removed (1):**" in report
