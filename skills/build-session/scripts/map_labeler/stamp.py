"""Badge stamping for player maps.

Parses a labels string like "A1(3300,1350) A2(700,1850)" and stamps
themed badges onto a player map image.
"""

import re
from PIL import Image, ImageDraw, ImageFont

THEME_COLORS = {
    "ocean": "#1a6b8a",
    "forest": "#2d5a3d",
    "amber": "#b8860b",
    "violet": "#6b3fa0",
    "bronze": "#8b6914",
    "frost": "#4a7c8c",
    "ember": "#a0522d",
    "shadow": "#4a4a5a",
    "jade": "#2d6b4a",
}

_LABEL_PATTERN = re.compile(r"(\w+)\((\d+),(\d+)\)")


def parse_labels_string(labels: str | None) -> list[tuple[str, int, int]]:
    """Parse 'A1(3300,1350) A2(700,1850)' into [(code, x, y), ...]."""
    if not labels:
        return []
    return [(m.group(1), int(m.group(2)), int(m.group(3)))
            for m in _LABEL_PATTERN.finditer(labels)]


def stamp_labels(image_path: str, labels: list[tuple[str, int, int]],
                 output_path: str, theme: str = "amber") -> str:
    """Stamp area code badges onto a map image.

    Args:
        image_path: Path to the unlabeled player map.
        labels: List of (code, x, y) tuples.
        output_path: Where to save the stamped image.
        theme: Theme name for badge color (from THEME_COLORS).

    Returns:
        The output_path.
    """
    color_hex = THEME_COLORS.get(theme, THEME_COLORS["amber"])
    r = int(color_hex[1:3], 16)
    g = int(color_hex[3:5], 16)
    b = int(color_hex[5:7], 16)

    img = Image.open(image_path).convert("RGBA")

    # Scale font to image width (90pt at 4096px)
    font_size = max(24, int(img.width * 90 / 4096))
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    pad = max(8, font_size // 6)
    border_w = max(2, font_size // 22)
    shadow_offset = max(2, font_size // 22)
    corner_radius = max(4, font_size // 9)

    for code, cx, cy in labels:
        bbox = font.getbbox(code)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x1 = cx - tw // 2 - pad
        y1 = cy - th // 2 - pad
        x2 = cx + tw // 2 + pad
        y2 = cy + th // 2 + pad

        # Drop shadow
        draw.rounded_rectangle(
            [x1 + shadow_offset, y1 + shadow_offset,
             x2 + shadow_offset, y2 + shadow_offset],
            radius=corner_radius, fill=(0, 0, 0, 120))
        # Badge background
        draw.rounded_rectangle(
            [x1, y1, x2, y2], radius=corner_radius,
            fill=(r, g, b, 220), outline=(255, 255, 255, 240),
            width=border_w)
        # Label text
        draw.text((cx - tw // 2, cy - th // 2 - 2), code,
                  fill=(255, 255, 255, 255), font=font)

    result = Image.alpha_composite(img, overlay)
    result.convert("RGB").save(output_path)
    return output_path
