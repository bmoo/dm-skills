"""Generate background_texture.png — the parchment page-background tile.

Deterministic (fixed seed), so the committed PNG is reproducible:

    python3 make_background_texture.py

Near-white paper: low-amplitude blurred grain, sparse darker specks, and a
few faint short fiber strokes. Written beside this script at 500x300, the
size styles.css tiles.
"""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

W, H = 500, 300
BASE = (250, 250, 248)

rng = random.Random(20260810)

# Blurred per-pixel grain, a few luminance points around the base tone.
grain = Image.new("L", (W, H))
grain.putdata([rng.randint(118, 138) for _ in range(W * H)])
grain = grain.filter(ImageFilter.GaussianBlur(1.2))

img = Image.new("RGB", (W, H), BASE)
px, gpx = img.load(), grain.load()
for y in range(H):
    for x in range(W):
        d = (gpx[x, y] - 128) // 3
        r, g, b = BASE
        px[x, y] = (r + d, g + d, b + d)

draw = ImageDraw.Draw(img)

# Sparse specks.
for _ in range(90):
    x, y = rng.randrange(W), rng.randrange(H)
    tone = rng.randint(215, 238)
    draw.point((x, y), fill=(tone, tone - 2, tone - 6))

# Faint short fibers.
for _ in range(28):
    x, y = rng.randrange(W), rng.randrange(H)
    dx, dy = rng.randint(-14, 14), rng.randint(-6, 6)
    tone = rng.randint(228, 242)
    draw.line((x, y, x + dx, y + dy), fill=(tone, tone - 2, tone - 5), width=1)

img = img.filter(ImageFilter.GaussianBlur(0.4))
img.save(Path(__file__).parent / "background_texture.png")
