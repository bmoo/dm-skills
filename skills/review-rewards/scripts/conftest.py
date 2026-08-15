"""Shared helpers for the review-rewards app tests.

``running_server`` boots the real ``review_server`` on an ephemeral loopback
port in a daemon thread — the same code path the skill runs, minus the fixed
port — and tears it down after the test. Tests talk to it over real HTTP so
the seam they exercise is the one the DM's browser uses.
"""

from __future__ import annotations

import contextlib
import json
import shutil
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

import review_server

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def review_files(tmp_path):
    """A writable copy of the fixture catalog plus a state path beside it."""
    data_path = tmp_path / "review-data.json"
    shutil.copy(FIXTURES / "review-data.json", data_path)
    return data_path, tmp_path / "decisions.json"


@contextlib.contextmanager
def running_server(data_path: Path, state_path: Path):
    server = review_server.create_server(data_path, state_path, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def http(method: str, url: str, payload=None):
    """(status, parsed-or-raw body) for a request against the test server."""
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method=method)
    if body is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read()
            status = response.status
    except urllib.error.HTTPError as error:
        raw = error.read()
        status = error.code
    content = raw.decode("utf-8")
    try:
        return status, json.loads(content)
    except json.JSONDecodeError:
        return status, content
