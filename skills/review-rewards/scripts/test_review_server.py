"""Server-boundary tests: loopback binding, write confinement, path traversal,
malformed payloads — the promises the skill text makes about the localhost app,
exercised over real HTTP."""

import json

from conftest import http, running_server


def read_state(state_path):
    return json.loads(state_path.read_text(encoding="utf-8"))


def test_binds_loopback_only(review_files):
    data_path, state_path = review_files
    import review_server

    server = review_server.create_server(data_path, state_path, port=0)
    try:
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.server_close()


def test_serves_page_and_review_payload(review_files):
    data_path, state_path = review_files
    with running_server(data_path, state_path) as base:
        status, page = http("GET", base + "/")
        assert status == 200 and "Reward Review" in page
        status, payload = http("GET", base + "/api/review")
        assert status == 200
        names = {e["name"] for e in payload["data"]["entries"]}
        assert "Pearl of Power" in names
        assert payload["state"]["decisions"] == {}


def test_fresh_state_file_is_initialized(review_files):
    data_path, state_path = review_files
    with running_server(data_path, state_path):
        pass
    assert read_state(state_path)["decisions"] == {}


def test_valid_save_persists(review_files):
    data_path, state_path = review_files
    with running_server(data_path, state_path) as base:
        state = {
            "catalogVersion": json.loads(data_path.read_text())["catalogVersion"],
            "decisions": {"pearl-of-power--gm-guide-2024": {"decision": "approve"}},
        }
        status, body = http("POST", base + "/api/state", state)
        assert status == 200 and body == {"ok": True}
    saved = read_state(state_path)
    assert saved["decisions"]["pearl-of-power--gm-guide-2024"]["decision"] == "approve"


def test_malformed_json_rejected_without_write(review_files):
    data_path, state_path = review_files
    with running_server(data_path, state_path) as base:
        import urllib.request

        request = urllib.request.Request(
            base + "/api/state", data=b"{not json", method="POST"
        )
        import urllib.error

        try:
            urllib.request.urlopen(request)
            status = 200
        except urllib.error.HTTPError as error:
            status = error.code
            body = json.loads(error.read())
        assert status == 400
        assert any("malformed JSON" in e for e in body["errors"])
    assert read_state(state_path)["decisions"] == {}


def test_invalid_decision_rejected_without_write(review_files):
    data_path, state_path = review_files
    version = json.loads(data_path.read_text())["catalogVersion"]
    with running_server(data_path, state_path) as base:
        bad = {"catalogVersion": version,
               "decisions": {"pearl-of-power--gm-guide-2024": {"decision": "yeet"}}}
        status, body = http("POST", base + "/api/state", bad)
        assert status == 400
        assert any("unknown decision" in e for e in body["errors"])
    assert read_state(state_path)["decisions"] == {}


def test_stale_catalog_version_rejected(review_files):
    data_path, state_path = review_files
    with running_server(data_path, state_path) as base:
        stale = {"catalogVersion": "an-older-run", "decisions": {}}
        status, body = http("POST", base + "/api/state", stale)
        assert status == 400
        assert any("stale decision state" in e for e in body["errors"])


def test_path_traversal_urls_are_404(review_files):
    data_path, state_path = review_files
    with running_server(data_path, state_path) as base:
        for path in ("/../review_server.py", "/..%2f..%2fetc%2fpasswd",
                     "/etc/passwd", "/fixtures/review-data.json"):
            status, _ = http("GET", base + path)
            assert status == 404, path


def test_posts_to_other_routes_are_404(review_files):
    data_path, state_path = review_files
    with running_server(data_path, state_path) as base:
        status, _ = http("POST", base + "/api/anything", {"x": 1})
        assert status == 404


def test_write_confinement_no_other_files_created(review_files, tmp_path):
    data_path, state_path = review_files
    before = set(tmp_path.rglob("*"))
    version = json.loads(data_path.read_text())["catalogVersion"]
    with running_server(data_path, state_path) as base:
        # A hostile payload can name paths in its fields; the server may store
        # them as an unknown-field rejection but must never write anywhere but
        # the designated state file.
        evil = {"catalogVersion": version,
                "decisions": {"pearl-of-power--gm-guide-2024": {
                    "decision": "approve", "statePath": str(tmp_path / "evil.json")}}}
        status, _ = http("POST", base + "/api/state", evil)
        assert status == 400
        ok = {"catalogVersion": version,
              "decisions": {"pearl-of-power--gm-guide-2024": {"decision": "approve"}}}
        http("POST", base + "/api/state", ok)
    after = set(tmp_path.rglob("*"))
    assert after - before == {state_path}
