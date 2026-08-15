import tempfile
from pathlib import Path
from PIL import Image
from stamp import stamp_labels, parse_labels_string, THEME_COLORS

def test_parse_labels_string():
    result = parse_labels_string("A1(3300,1350) A2(700,1850) A3(1900,1350)")
    assert result == [("A1", 3300, 1350), ("A2", 700, 1850), ("A3", 1900, 1350)]

def test_parse_labels_string_multi_char_codes():
    result = parse_labels_string("A10(100,200) B2(300,400)")
    assert result == [("A10", 100, 200), ("B2", 300, 400)]

def test_parse_labels_empty():
    assert parse_labels_string("") == []
    assert parse_labels_string(None) == []

def test_stamp_labels_creates_image_with_badges():
    bg_color = (200, 200, 200)
    img = Image.new("RGB", (800, 600), bg_color)
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img.save(f.name)
        input_path = f.name

    labels = [("A1", 400, 300)]
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        output_path = f.name

    stamp_labels(input_path, labels, output_path, theme="ocean")
    result = Image.open(output_path)
    assert result.size == (800, 600)
    center_pixel = result.getpixel((400, 300))
    assert center_pixel != bg_color, "Badge should have changed pixels at label position"

def test_theme_colors_all_present():
    expected = {"ocean", "forest", "amber", "violet", "bronze", "frost", "ember", "shadow", "jade"}
    assert set(THEME_COLORS.keys()) == expected
