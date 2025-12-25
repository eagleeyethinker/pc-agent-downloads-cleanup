from __future__ import annotations

import os

def default_allowed_roots():
    user = os.path.expanduser("~")
    return [
        os.path.join(user, "Downloads"),
        os.path.join(user, "Documents"),
    ]

def ensure_allowed(path: str, allowed_roots: list[str]):
    p = os.path.abspath(path)
    for root in allowed_roots:
        r = os.path.abspath(root)
        if p.startswith(r):
            return
    raise PermissionError(f"Path not allowed: {path}. Allowed roots: {allowed_roots}")

def ensure_folder(path: str):
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
