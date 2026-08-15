import sys
from pathlib import Path

# Allow bare imports (from graph import ...) when tests are collected from parent dir
sys.path.insert(0, str(Path(__file__).parent))
