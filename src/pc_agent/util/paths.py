from __future__ import annotations
import os
from pathlib import Path


def default_downloads_dir() -> str:
    # Windows-friendly default
    home = Path.home()
    return str(home / "Downloads")


def default_allowed_roots() -> list[str]:
    home = Path.home()
    roots = [
        str(home / "Downloads"),
        str(home / "Documents"),
    ]
    # Normalize to absolute, resolved paths
    out: list[str] = []
    for r in roots:
        try:
            out.append(str(Path(r).resolve()))
        except Exception:
            out.append(os.path.abspath(r))
    return out
