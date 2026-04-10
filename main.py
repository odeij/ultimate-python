#!/usr/bin/env python3
"""Ultimate Python — Interactive Shell

Entry point.  Run with:
    python main.py
    make
    make run
    ./main.py  (after chmod +x main.py)
"""
from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency check — give a clear message before anything else imports
# ---------------------------------------------------------------------------

_MISSING: list[str] = []

try:
    import rich  # noqa: F401
except ImportError:
    _MISSING.append("rich")

try:
    import yaml  # noqa: F401
except ImportError:
    _MISSING.append("PyYAML")

if _MISSING:
    print("\n  ✗  Missing required packages: " + ", ".join(_MISSING))
    print("  Run:  pip install -r requirements.txt")
    print("  or:   make install\n")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Minimum Python version check
# ---------------------------------------------------------------------------

if sys.version_info < (3, 10):
    print(f"\n  ✗  Python 3.10+ required (you have {sys.version})")
    print("  This project uses match/case and union type syntax.\n")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Resolve repo root relative to this file so the app works regardless
    # of the current working directory.
    repo_root = Path(__file__).resolve().parent

    from cli.app import App

    App(repo_root).run()
