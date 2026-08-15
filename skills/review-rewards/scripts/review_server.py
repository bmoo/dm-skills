"""The review-rewards localhost app: serve the review page, persist decisions.

Security posture, matching the skill text's promises:

- **Loopback only.** The socket binds ``127.0.0.1``; the page and the full
  official rules text it shows are never reachable off the machine.
- **Write confinement.** The only file this process ever writes is the state
  path fixed at startup (``--state``). No request field, header, or URL can
  redirect the write — the handler never maps request content to a filesystem
  path. Saves are atomic (temp file + rename) so a crash mid-write cannot
  leave a truncated state file.
- **Read confinement.** GET serves exactly two things: the bundled
  ``review.html`` beside this script, and the JSON API. URLs are matched
  against a fixed route table, never resolved against the filesystem, so
  traversal paths fall through to 404.
- **Validated saves.** Every POST body runs through ``review_state`` before
  touching disk; an invalid payload gets a 400 with the error list and writes
  nothing.

Usage::

    python review_server.py --data review-data.json --state decisions.json [--port 8377]

Prints the URL to hand the DM, then serves until interrupted.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import review_state

MAX_BODY_BYTES = 5 * 1024 * 1024
PAGE_PATH = Path(__file__).resolve().parent / "review.html"


def atomic_write_json(path: Path, value: object) -> None:
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp_name, path)
    except BaseException:
        os.unlink(tmp_name)
        raise


def create_server(data_path: Path, state_path: Path, port: int) -> ThreadingHTTPServer:
    """Build the configured server without starting it (tests use port 0)."""
    data = json.loads(data_path.read_text(encoding="utf-8"))
    data_errors = review_state.validate_review_data(data)
    if data_errors:
        raise SystemExit("invalid review data:\n  " + "\n  ".join(data_errors))

    state_path = state_path.resolve()
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state_errors = review_state.validate_state(state, data)
        if state_errors:
            raise SystemExit(
                "existing decision state does not match this review data "
                "(regenerate the catalog or remove the stale state file):\n  "
                + "\n  ".join(state_errors)
            )
    else:
        state = review_state.empty_state(data)
        atomic_write_json(state_path, state)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args) -> None:
            pass

        def _send_json(self, status: int, payload: object) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            route = self.path.split("?", 1)[0]
            if route in ("/", "/index.html"):
                body = PAGE_PATH.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif route == "/api/review":
                current = json.loads(state_path.read_text(encoding="utf-8"))
                self._send_json(200, {"data": data, "state": current})
            else:
                self._send_json(404, {"errors": ["not found"]})

        def do_POST(self) -> None:
            route = self.path.split("?", 1)[0]
            if route != "/api/state":
                self._send_json(404, {"errors": ["not found"]})
                return
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_BODY_BYTES:
                self._send_json(400, {"errors": ["missing or oversized request body"]})
                return
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                self._send_json(400, {"errors": [f"malformed JSON: {exc}"]})
                return
            errors = review_state.validate_state(payload, data)
            if errors:
                self._send_json(400, {"errors": errors})
                return
            atomic_write_json(state_path, payload)
            self._send_json(200, {"ok": True})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path, help="review-data.json path")
    parser.add_argument("--state", required=True, type=Path, help="decision-state json path")
    parser.add_argument("--port", type=int, default=8377)
    args = parser.parse_args(argv)

    server = create_server(args.data, args.state, args.port)
    host, port = server.server_address[:2]
    print(f"Review app: http://{host}:{port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
