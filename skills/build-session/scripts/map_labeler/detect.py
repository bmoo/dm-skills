"""
Map label detection and placement for dungeon maps.

Finds where a labeled DM map's room labels sit (by diffing against the
unlabeled player version of the same map), then stamps area codes at
those positions.

Algorithm:
1. Compute luminance diff (player - DM) to find dark-text-on-light-floor labels
2. Divide into a grid of cells, sum significant diff per cell
3. Find local maxima (cells with more diff than all neighbors)
4. Merge nearby peaks and rank by score
5. Place badges at the top N positions

Usage:
    python3 detect.py find <dm_map> <player_map> [-n 8] [-o viz.jpg]
    python3 detect.py label <dm_map> <player_map> -o labeled.jpg [--labels A1 A2 ...]
    python3 detect.py score <dm_map> <player_map> [-n 8]
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


# ---------------------------------------------------------------------------
# Core: find label positions via luminance diff
# ---------------------------------------------------------------------------

def find_label_positions(dm_path: str, player_path: str,
                         n_labels: int | None = None,
                         diff_threshold: int = 40,
                         cell_size: tuple[int, int] = (100, 200),
                         min_score: int = 500,
                         merge_radius: int = 250,
                         border_margin: float = 0.10) -> list[dict]:
    """
    Find label positions by diffing DM and player maps.

    Args:
        n_labels: Expected number of labels. If None, auto-detect using
                  score gap analysis (largest ratio between consecutive scores).
        diff_threshold: Minimum per-pixel luminance diff to count as significant.
        cell_size: (height, width) of grid cells for aggregation.
        min_score: Minimum cell score to consider as a peak.
        merge_radius: Merge peaks within this pixel distance.
        border_margin: Fraction of image to exclude as border (0.10 = 10%).

    Returns list of {centroid: (x, y), score: float} sorted spatially.
    """
    dm_gray = np.array(Image.open(dm_path).convert("L"), dtype=np.int16)
    player_gray = np.array(Image.open(player_path).convert("L"), dtype=np.int16)
    h, w = dm_gray.shape

    # Absolute luminance diff: catches both dark text and light text/outlines
    lum_diff = np.abs(player_gray - dm_gray).astype(np.uint8)

    # Exclude border zone
    my = int(h * border_margin)
    mx = int(w * border_margin)
    lum_diff[:my, :] = 0
    lum_diff[-my:, :] = 0
    lum_diff[:, :mx] = 0
    lum_diff[:, -mx:] = 0

    # Grid-based scoring
    cell_h, cell_w = cell_size
    grid_h, grid_w = h // cell_h, w // cell_w
    cell_scores = np.zeros((grid_h, grid_w))

    for gy in range(grid_h):
        for gx in range(grid_w):
            region = lum_diff[gy * cell_h:(gy + 1) * cell_h,
                              gx * cell_w:(gx + 1) * cell_w]
            significant = region[region > diff_threshold]
            cell_scores[gy, gx] = significant.sum() if len(significant) > 0 else 0

    # Find local maxima
    peaks = []
    for gy in range(1, grid_h - 1):
        for gx in range(1, grid_w - 1):
            val = cell_scores[gy, gx]
            if val < min_score:
                continue
            neighborhood = cell_scores[gy - 1:gy + 2, gx - 1:gx + 2]
            if val >= neighborhood.max():
                cx = gx * cell_w + cell_w // 2
                cy = gy * cell_h + cell_h // 2
                peaks.append({"centroid": (cx, cy), "score": float(val)})

    # Merge nearby peaks (keep highest score)
    peaks.sort(key=lambda p: -p["score"])
    merged = []
    for p in peaks:
        too_close = any(
            (p["centroid"][0] - m["centroid"][0]) ** 2 +
            (p["centroid"][1] - m["centroid"][1]) ** 2 < merge_radius ** 2
            for m in merged
        )
        if not too_close:
            merged.append(p)

    # Select top N labels
    if n_labels is not None:
        merged = merged[:n_labels]
    else:
        merged = _auto_select(merged)

    # Sort spatially: top-to-bottom, left-to-right
    merged.sort(key=lambda r: (r["centroid"][1] // 200, r["centroid"][0]))
    return merged


def _auto_select(peaks: list[dict]) -> list[dict]:
    """
    Auto-select labels by finding the first significant score gap.

    Scans from the top of the score distribution and picks the first gap
    where the ratio exceeds 3x. This catches the boundary between real
    labels (high scores) and noise (low scores) without being fooled by
    tiny-score gaps at the tail.

    Falls back to 2x threshold if no 3x gap exists, then keeps all if
    no significant gap is found.
    """
    if len(peaks) <= 2:
        return peaks

    scores = [p["score"] for p in peaks]

    # Find first gap > 3x (strong signal)
    for i in range(1, len(scores)):
        if scores[i] <= 0:
            return peaks[:i]
        if scores[i - 1] / scores[i] > 3.0:
            return peaks[:i]

    # Fall back: first gap > 2x
    for i in range(1, len(scores)):
        if scores[i] <= 0:
            return peaks[:i]
        if scores[i - 1] / scores[i] > 2.0:
            return peaks[:i]

    return peaks


# ---------------------------------------------------------------------------
# Label placement
# ---------------------------------------------------------------------------

def place_labels(player_path: str, positions: list[dict], labels: list[str],
                 output_path: str, theme_color: str = "#B8860B",
                 font_size: int = 36) -> str:
    """Place area code badges on the player map at the given positions."""
    img = Image.open(player_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()

    r = int(theme_color[1:3], 16)
    g = int(theme_color[3:5], 16)
    b = int(theme_color[5:7], 16)

    for i, pos in enumerate(positions):
        if i >= len(labels):
            break
        label = labels[i]
        cx, cy = pos["centroid"]

        bbox = font.getbbox(label)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad = 8
        draw.rounded_rectangle(
            [cx - tw // 2 - pad, cy - th // 2 - pad,
             cx + tw // 2 + pad, cy + th // 2 + pad],
            radius=6, fill=(r, g, b, 200),
            outline=(255, 255, 255, 220), width=2,
        )
        draw.text((cx - tw // 2, cy - th // 2 - 2), label,
                  fill=(255, 255, 255, 255), font=font)

    img = Image.alpha_composite(img, overlay)
    img.convert("RGB").save(output_path)
    return output_path


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_placement(detected: list[dict], dm_path: str, player_path: str,
                    match_radius: int = 200) -> dict:
    """
    Score detected positions by treating the diff-extracted positions as
    ground truth. Re-extracts GT with no label limit for comparison.
    """
    # Get all possible label positions (no limit) as ground truth
    gt = find_label_positions(dm_path, player_path, n_labels=None)

    if not gt or not detected:
        return {"matched": 0, "total_gt": len(gt), "total_detected": len(detected),
                "recall": 0.0, "precision": 0.0, "avg_distance": 0.0}

    gt_arr = np.array([g["centroid"] for g in gt], dtype=np.float64)
    det_arr = np.array([d["centroid"] for d in detected], dtype=np.float64)

    diffs = gt_arr[:, np.newaxis, :] - det_arr[np.newaxis, :, :]
    dists = np.sqrt((diffs ** 2).sum(axis=2))

    matches = []
    used_gt, used_det = set(), set()

    while True:
        if len(used_gt) >= len(gt) or len(used_det) >= len(detected):
            break
        masked = dists.copy()
        for g in used_gt:
            masked[g, :] = np.inf
        for d in used_det:
            masked[:, d] = np.inf
        idx = np.unravel_index(masked.argmin(), masked.shape)
        d = masked[idx]
        if d > match_radius:
            break
        matches.append((int(idx[0]), int(idx[1]), float(d)))
        used_gt.add(int(idx[0]))
        used_det.add(int(idx[1]))

    n = len(matches)
    return {
        "matched": n,
        "total_gt": len(gt),
        "total_detected": len(detected),
        "recall": n / len(gt) if gt else 0,
        "precision": n / len(detected) if detected else 0,
        "avg_distance": float(np.mean([d for _, _, d in matches])) if matches else 0,
    }


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def visualize(player_path: str, positions: list[dict], output_path: str,
              labels: list[str] | None = None):
    """Draw detected positions as numbered markers on the player map."""
    img = Image.open(player_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    except (OSError, IOError):
        font = ImageFont.load_default()

    for i, pos in enumerate(positions):
        cx, cy = pos["centroid"]
        draw.ellipse([cx - 18, cy - 18, cx + 18, cy + 18],
                     fill=(0, 100, 255), outline="white", width=2)
        label = labels[i] if labels and i < len(labels) else str(i)
        draw.text((cx - 8, cy - 10), label, fill="white", font=font)

    draw.rectangle([10, 10, 420, 48], fill="black")
    draw.text((20, 14), f"Found {len(positions)} label positions",
              fill="yellow", font=font)
    img.save(output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Map label detection and placement")
    sub = parser.add_subparsers(dest="command")

    p_find = sub.add_parser("find", help="Find label positions from DM/player pair")
    p_find.add_argument("dm_map")
    p_find.add_argument("player_map")
    p_find.add_argument("-n", type=int, default=None, help="Expected label count")
    p_find.add_argument("--output", "-o", help="Save visualization")
    p_find.add_argument("--json", action="store_true")

    p_label = sub.add_parser("label", help="Place area codes on player map")
    p_label.add_argument("dm_map")
    p_label.add_argument("player_map")
    p_label.add_argument("--output", "-o", required=True)
    p_label.add_argument("-n", type=int, default=None)
    p_label.add_argument("--labels", nargs="+")
    p_label.add_argument("--color", default="#B8860B")

    p_score = sub.add_parser("score", help="Score label detection accuracy")
    p_score.add_argument("dm_map")
    p_score.add_argument("player_map")
    p_score.add_argument("-n", type=int, default=None)

    args = parser.parse_args()

    if args.command == "find":
        positions = find_label_positions(args.dm_map, args.player_map,
                                         n_labels=args.n)
        if args.json:
            print(json.dumps(positions, indent=2))
        else:
            print(f"Found {len(positions)} labels:")
            for i, p in enumerate(positions):
                print(f"  {i}: ({p['centroid'][0]:4d}, {p['centroid'][1]:4d}) "
                      f"score={p['score']:.0f}")
        if args.output:
            visualize(args.player_map, positions, args.output)
            print(f"\nVisualization: {args.output}")

    elif args.command == "label":
        positions = find_label_positions(args.dm_map, args.player_map,
                                         n_labels=args.n)
        labels = args.labels or [f"A{i + 1}" for i in range(len(positions))]
        place_labels(args.player_map, positions, labels, args.output, args.color)
        print(f"Placed {min(len(labels), len(positions))} labels → {args.output}")

    elif args.command == "score":
        positions = find_label_positions(args.dm_map, args.player_map,
                                         n_labels=args.n)
        result = score_placement(positions, args.dm_map, args.player_map)
        print(f"Detected: {result['total_detected']}  "
              f"GT: {result['total_gt']}  "
              f"Matched: {result['matched']}")
        print(f"Precision: {result['precision']:.0%}  "
              f"Recall: {result['recall']:.0%}  "
              f"Avg dist: {result['avg_distance']:.0f}px")


if __name__ == "__main__":
    main()
