from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from typing import Dict, List

from ..util.safety import ensure_allowed, ensure_folder
from ..util.human import human_bytes


def scan_folder(*, target_dir: str, allowed_roots: List[str]) -> List[Dict]:
    ensure_allowed(target_dir, allowed_roots)

    items: List[Dict] = []
    root = Path(target_dir)

    for p in root.rglob("*"):
        try:
            if p.is_file():
                st = p.stat()
                items.append(
                    {
                        "path": str(p),
                        "size_bytes": int(st.st_size),
                        "mtime": float(st.st_mtime),
                    }
                )
        except (OSError, PermissionError):
            continue
    return items


def get_big_files(items: List[Dict], *, threshold_bytes: int) -> List[Dict]:
    out = []
    for it in items:
        if it["size_bytes"] >= threshold_bytes:
            out.append(
                {
                    "path": it["path"],
                    "size_bytes": it["size_bytes"],
                    "size_human": human_bytes(it["size_bytes"]),
                }
            )
    # Sort descending
    out.sort(key=lambda x: x["size_bytes"], reverse=True)
    return out


INSTALLER_EXTS = {".exe", ".msi", ".msix"}


def propose_cleanup(
    items: List[Dict],
    *,
    target_dir: str,
    archive_installers_older_than_days: int,
    allowed_roots: List[str],
) -> List[Dict]:
    ensure_allowed(target_dir, allowed_roots)

    archive_dir = os.path.join(target_dir, "_archive_installers")
    cutoff = time.time() - (archive_installers_older_than_days * 86400)

    actions: List[Dict] = []
    for it in items:
        p = Path(it["path"])
        if p.suffix.lower() in INSTALLER_EXTS and it["mtime"] < cutoff:
            dst = os.path.join(archive_dir, p.name)
            actions.append({"op": "move", "src": str(p), "dst": dst})
    return actions


def apply_actions(actions: List[Dict]) -> List[Dict]:
    executed: List[Dict] = []
    for a in actions:
        op = a["op"]
        if op == "move":
            move_file(a["src"], a["dst"])
            executed.append(a)
    return executed


def move_file(src: str, dst: str):
    ensure_folder(os.path.dirname(dst))
    shutil.move(src, dst)


def delete_file(path: str):
    os.remove(path)


def rename_file(src: str, dst: str):
    ensure_folder(os.path.dirname(dst))
    os.replace(src, dst)
