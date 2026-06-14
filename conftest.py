"""Make the repo root importable so `runner` / `librarian` resolve under plain pytest."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
