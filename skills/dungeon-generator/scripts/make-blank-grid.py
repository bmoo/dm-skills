#!/usr/bin/env python3
"""Draw the reference anchor for map renders — a blank 5-ft grid, or a
wireframe layout over it.

Stdlib-only (zlib + struct hand-rolled PNG). The anchor is handed to
gpt-image-2 as a --reference image: the model preserves what it is handed and
ignores what it is told, so everything that must survive is
drawn here, programmatically, and the dungeon is painted on top of it.

Usage:
    # blank grid (metric anchor only)
    python3 make-blank-grid.py --size 1536x2304 --pitch 48 --output grid.png

    # wireframe (metric + topology anchor; --fill paints the
    # negative space as solid earth)
    python3 make-blank-grid.py --size 1536x2304 --pitch 48 \
        --layout layout.json --fill --output wireframe.png

The layout JSON:

    {
      "rooms":     [{"id": "N1", "block": [c0, r0, c1, r1]}, ...],
      "corridors": [{"id": "E2", "path": [[c, r], [c, r], ...]}, ...]
    }

Room blocks are inclusive cell ranges. Corridor paths are orthogonal
waypoints, interpolated cell by cell; start and end the path one cell INSIDE
the rooms it joins — a wall opening exists only where consecutive path cells
actually cross a boundary, so a connection the path doesn't make cannot
appear open. A waypoint off the map edge opens the map-edge wall there (an
entrance mouth). Two corridors join by sharing a cell (route one path onto a
cell of the other).

The parchment field is a warm off-white; grid lines a light warm grey — visible
enough to survive repainting, faint enough not to fight the art.
"""
import argparse
import json
import random
import struct
import sys
import zlib

BACKGROUND = (0xF2, 0xEC, 0xDF)  # warm parchment
LINE = (0xB8, 0xAE, 0x9C)        # warm grey
MAJOR_EVERY = 0                  # no major-line emphasis by default

FLOOR = (0xDE, 0xD6, 0xC5)       # room/corridor fill — a shade under parchment
EARTH = (0x2E, 0x26, 0x1E)       # dark packed earth — the --fill surround
WALL = (0x4A, 0x44, 0x3C)        # dark warm grey
LABEL = (0x35, 0x30, 0x28)       # near-black warm
WALL_T = 5                       # wall thickness in px

# 5x7 bitmap glyphs for room IDs (N + digits; E for corridor use).
GLYPHS = {
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
}


def png_chunk(tag, data):
    chunk = tag + data
    return struct.pack(">I", len(data)) + chunk + struct.pack(
        ">I", zlib.crc32(chunk) & 0xFFFFFFFF
    )


def write_png(path, width, height, rows):
    raw = b"".join(b"\x00" + row for row in rows)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        fh.write(
            png_chunk(
                b"IHDR",
                struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0),
            )
        )
        fh.write(png_chunk(b"IDAT", zlib.compress(raw, 9)))
        fh.write(png_chunk(b"IEND", b""))


def interpolate(waypoints):
    """Orthogonal waypoints -> the full cell sequence, endpoints included."""
    cells = [tuple(waypoints[0])]
    for (c0, r0), (c1, r1) in zip(waypoints, waypoints[1:]):
        if c0 != c1 and r0 != r1:
            sys.exit(f"error: diagonal path step ({c0},{r0}) -> ({c1},{r1})")
        dc = (c1 > c0) - (c1 < c0)
        dr = (r1 > r0) - (r1 < r0)
        c, r = c0, r0
        while (c, r) != (c1, r1):
            c, r = c + dc, r + dr
            cells.append((c, r))
    return cells


def build_wireframe(layout, cols, rows):
    """Floor cells, room membership, and the set of open cell-boundaries."""
    room_of = {}
    for room in layout.get("rooms", []):
        c0, r0, c1, r1 = room["block"]
        for c in range(c0, c1 + 1):
            for r in range(r0, r1 + 1):
                if not (0 <= c < cols and 0 <= r < rows):
                    sys.exit(f"error: room {room['id']} cell ({c},{r}) off-grid")
                if (c, r) in room_of:
                    sys.exit(
                        f"error: rooms {room_of[(c, r)]} and {room['id']}"
                        f" overlap at ({c},{r})"
                    )
                room_of[(c, r)] = room["id"]

    floor = set(room_of)
    open_edges = set()  # frozenset of the two cells (one may be off-grid)
    for corridor in layout.get("corridors", []):
        cells = interpolate(corridor["path"])
        for cell in cells:
            c, r = cell
            if 0 <= c < cols and 0 <= r < rows:
                floor.add(cell)
        for a, b in zip(cells, cells[1:]):
            open_edges.add(frozenset((a, b)))

    return floor, room_of, open_edges


def draw_earth_fill(fb, width, height, pitch, floor):
    """Paint every non-floor cell as dark solid earth. The surround must ride
    the preserved channel like the geometry does: told to
    fill the margins itself, the model paints over the anchor's fainter
    lanes. Per-cell shade jitter reads as material rather than void; a
    slightly lighter halo hugs the footprint so the wall line separates."""
    rng = random.Random(99)
    cols, rows = width // pitch, height // pitch
    for c in range(cols):
        for r in range(rows):
            if (c, r) in floor:
                continue
            j = rng.randint(-6, 6)
            near = any(
                (c + dc, r + dr) in floor
                for dc in (-1, 0, 1) for dr in (-1, 0, 1)
            )
            base = 0x0A if near else 0x00
            color = tuple(min(255, v + j + base) for v in EARTH)
            fill_rect(fb, width, height, c * pitch, r * pitch,
                      pitch, pitch, color)


def draw_wireframe(fb, width, height, pitch, layout, fill=False):
    cols, rows = width // pitch, height // pitch
    floor, room_of, open_edges = build_wireframe(layout, cols, rows)

    for c, r in floor:
        fill_rect(fb, width, height, c * pitch, r * pitch, pitch, pitch, FLOOR)
    draw_grid(fb, width, height, pitch)
    if fill:
        draw_earth_fill(fb, width, height, pitch, floor)

    # Walls: every floor-cell side is walled unless the neighbor shares the
    # room, or a corridor path steps across that boundary.
    half = WALL_T // 2
    for c, r in sorted(floor):
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c + dc, r + dr)
            same_room = (
                (c, r) in room_of and n in room_of
                and room_of[(c, r)] == room_of[n]
            )
            if same_room or frozenset(((c, r), n)) in open_edges:
                continue
            x0, y0 = c * pitch, r * pitch
            if dc:  # vertical wall segment
                x = x0 + pitch if dc > 0 else x0
                fill_rect(fb, width, height, x - half, y0 - half,
                          WALL_T, pitch + WALL_T, WALL)
            else:   # horizontal wall segment
                y = y0 + pitch if dr > 0 else y0
                fill_rect(fb, width, height, x0 - half, y - half,
                          pitch + WALL_T, WALL_T, WALL)

    # Room ID labels, centered.
    scale = max(2, pitch // 16)
    for room in layout.get("rooms", []):
        c0, r0, c1, r1 = room["block"]
        text = room["id"]
        tw = len(text) * 6 * scale - scale  # 5px glyph + 1px space
        th = 7 * scale
        cx = (c0 + c1 + 1) * pitch // 2 - tw // 2
        cy = (r0 + r1 + 1) * pitch // 2 - th // 2
        draw_text(fb, width, height, cx, cy, text, scale, LABEL)


def fill_rect(fb, width, height, x, y, w, h, color):
    px = bytes(color)
    for yy in range(max(0, y), min(height, y + h)):
        row = fb[yy]
        x0, x1 = max(0, x), min(width, x + w)
        row[x0 * 3:x1 * 3] = px * (x1 - x0)


def draw_grid(fb, width, height, pitch):
    px = bytes(LINE)
    for y in range(height):
        row = fb[y]
        if y % pitch == 0:
            row[:] = px * width
        else:
            for x in range(0, width, pitch):
                row[x * 3:x * 3 + 3] = px


def draw_text(fb, width, height, x, y, text, scale, color):
    for i, ch in enumerate(text):
        glyph = GLYPHS.get(ch)
        if glyph is None:
            sys.exit(f"error: no glyph for {ch!r}")
        gx = x + i * 6 * scale
        for gr, bits in enumerate(glyph):
            for gc, bit in enumerate(bits):
                if bit == "1":
                    fill_rect(fb, width, height, gx + gc * scale,
                              y + gr * scale, scale, scale, color)


def main():
    parser = argparse.ArgumentParser(description="Draw a blank tactical grid PNG.")
    parser.add_argument(
        "--size",
        required=True,
        help="WIDTHxHEIGHT in pixels — must match the gpt-image-2 --size exactly.",
    )
    parser.add_argument(
        "--pitch",
        type=int,
        default=48,
        help="Grid pitch in pixels per 5-ft square (default 48).",
    )
    parser.add_argument("--output", required=True, help="Path to write the PNG.")
    parser.add_argument(
        "--layout",
        help="Optional layout JSON (rooms + corridors) to draw as a wireframe"
        " over the grid.",
    )
    parser.add_argument(
        "--fill",
        action="store_true",
        help="Fill non-floor cells with a dark solid-earth surround"
        " (requires --layout).",
    )
    args = parser.parse_args()

    try:
        width, height = (int(v) for v in args.size.lower().split("x"))
    except ValueError:
        sys.exit("error: --size must be WIDTHxHEIGHT, e.g. 1536x2304")

    fb = [bytearray(bytes(BACKGROUND) * width) for _ in range(height)]
    if args.layout:
        with open(args.layout) as fh:
            layout = json.load(fh)
        draw_wireframe(fb, width, height, args.pitch, layout, fill=args.fill)
    else:
        if args.fill:
            sys.exit("error: --fill requires --layout")
        draw_grid(fb, width, height, args.pitch)

    write_png(args.output, width, height, (bytes(row) for row in fb))
    cols, rws = width // args.pitch, height // args.pitch
    kind = "wireframe" if args.layout else "blank grid"
    print(f"saved: {args.output} ({kind}, {cols} x {rws} squares at {args.pitch} px)")


if __name__ == "__main__":
    main()
