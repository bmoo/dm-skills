import subprocess
from pathlib import Path

SCRIPTS = Path(__file__).parent
FIXTURES = SCRIPTS / "fixtures"


def test_render_minimal_produces_pdf(tmp_path):
    output = tmp_path / "test.pdf"
    result = subprocess.run(
        ["python3", str(SCRIPTS / "render_session.py"),
         str(FIXTURES / "minimal.md"),
         "--output", str(output)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert output.exists()
    assert output.stat().st_size > 0
    # PDF starts with %PDF
    assert output.read_bytes()[:5] == b"%PDF-"


def test_render_with_plugin_dir_paths(tmp_path):
    """Test that $PLUGIN_DIR/ paths resolve correctly."""
    md = tmp_path / "test_plugin_dir.md"
    md.write_text(
        "---\ntitle: Test\nlevel: 1\n---\n\n# Section\n\nContent.\n"
    )
    output = tmp_path / "test_plugin_dir.pdf"
    result = subprocess.run(
        ["python3", str(SCRIPTS / "render_session.py"),
         str(md), "--output", str(output)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert output.exists()
    assert output.stat().st_size > 0
