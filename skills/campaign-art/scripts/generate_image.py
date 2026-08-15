#!/usr/bin/env python3
"""Generate an image with OpenAI's gpt-image-2 model and save it to disk.

Stdlib-only — no `openai` SDK required. Reads OPENAI_API_KEY from the environment.

Text-to-image:
    python3 generate_image.py --prompt "..." --output Media/images/foo.png

Image-guided (one or more reference images; uses the /images/edits endpoint):
    python3 generate_image.py --prompt "..." --output Media/images/foo.png \\
        --reference <existing-image.png>

The model reasons about composition before it paints, so a call can take a minute
or more. Run it with a generous timeout.
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid

GENERATIONS_URL = "https://api.openai.com/v1/images/generations"
EDITS_URL = "https://api.openai.com/v1/images/edits"
DEFAULT_MODEL = "gpt-image-2"
TIMEOUT_SECONDS = 600


def api_key():
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("error: OPENAI_API_KEY is not set in the environment.")
    return key


def send(req):
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        sys.exit(f"error: OpenAI API returned HTTP {e.code}:\n{detail}")
    except urllib.error.URLError as e:
        sys.exit(f"error: could not reach the OpenAI API: {e.reason}")


def post_json(url, payload, key):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), method="POST"
    )
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    return send(req)


def post_multipart(url, fields, files, key):
    """POST a multipart/form-data body. `files` is a list of (field, path)."""
    boundary = uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        body += f"{value}\r\n".encode()
    for name, path in files:
        filename = os.path.basename(path)
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as fh:
            content = fh.read()
        body += f"--{boundary}\r\n".encode()
        body += (
            f'Content-Disposition: form-data; name="{name}"; '
            f'filename="{filename}"\r\n'
        ).encode()
        body += f"Content-Type: {ctype}\r\n\r\n".encode()
        body += content + b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    return send(req)


def main():
    parser = argparse.ArgumentParser(
        description="Generate an image with gpt-image-2."
    )
    parser.add_argument("--prompt", required=True, help="Full image prompt.")
    parser.add_argument("--output", required=True, help="Path to write the PNG.")
    parser.add_argument(
        "--size",
        default="1024x1536",
        help="WIDTHxHEIGHT or 'auto'. Default 1024x1536 (portrait). "
        "Edges must be multiples of 16, ratio <= 3:1.",
    )
    parser.add_argument(
        "--quality",
        default="high",
        choices=["low", "medium", "high", "auto"],
        help="Render quality. Default high.",
    )
    parser.add_argument(
        "--reference",
        action="append",
        default=[],
        metavar="PATH",
        help="Reference image to guide generation. Repeatable. "
        "When supplied, the /images/edits endpoint is used.",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL, help=f"Default {DEFAULT_MODEL}."
    )
    args = parser.parse_args()

    key = api_key()

    if args.reference:
        for ref in args.reference:
            if not os.path.isfile(ref):
                sys.exit(f"error: reference image not found: {ref}")
        fields = {
            "model": args.model,
            "prompt": args.prompt,
            "size": args.size,
            "quality": args.quality,
        }
        files = [("image[]", ref) for ref in args.reference]
        result = post_multipart(EDITS_URL, fields, files, key)
    else:
        payload = {
            "model": args.model,
            "prompt": args.prompt,
            "size": args.size,
            "quality": args.quality,
        }
        result = post_json(GENERATIONS_URL, payload, key)

    try:
        b64 = result["data"][0]["b64_json"]
    except (KeyError, IndexError, TypeError):
        sys.exit(
            "error: unexpected API response:\n"
            + json.dumps(result, indent=2)
        )

    out_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as fh:
        fh.write(base64.b64decode(b64))

    print(f"saved: {args.output}")
    usage = result.get("usage")
    if usage:
        print(f"usage: {json.dumps(usage)}")


if __name__ == "__main__":
    main()
