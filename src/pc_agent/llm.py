from __future__ import annotations

import os
import re
from typing import Dict

from .util.safety import default_allowed_roots

# Optional LLM
def _has_openai_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))

def parse_request_params(request: str) -> Dict:
    """
    Returns:
      target_dir
      archive_installers_older_than_days
      big_file_threshold_bytes
      big_file_threshold_human
      _parser
    """

    # 1) Always try deterministic parsing first (works even without LLM)
    params = _parse_fallback(request)
    if params:
        params["_parser"] = "fallback_no_llm"
        return params

    # 2) If fallback fails and we have a key, you can add an LLM parser later.
    # For now keep it simple (stable project).
    out = {
        "target_dir": os.path.join(os.path.expanduser("~"), "Downloads"),
        "archive_installers_older_than_days": 90,
        "big_file_threshold_bytes": 1 * 1024**3,
        "big_file_threshold_human": "1.00 GB",
        "_parser": "fallback_default",
    }
    return out


def _parse_fallback(request: str):
    # defaults
    target_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    days = 90
    threshold_bytes = 1 * 1024**3

    # archive older than X days
    m = re.search(r"older\s+than\s+(\d+)\s*day", request, re.IGNORECASE)
    if m:
        days = int(m.group(1))

    # big files > 1GB / 500MB / 50 KB
    m = re.search(r"(?:big\s+files|files)\s*>\s*([\d.]+)\s*(kb|k|mb|m|gb|g|tb|t)\b", request, re.IGNORECASE)
    if m:
        num = float(m.group(1))
        unit = m.group(2).lower()
        mult = {
            "kb": 1024, "k": 1024,
            "mb": 1024**2, "m": 1024**2,
            "gb": 1024**3, "g": 1024**3,
            "tb": 1024**4, "t": 1024**4,
        }[unit]
        threshold_bytes = int(num * mult)

    human = _human(threshold_bytes)

    return {
        "target_dir": target_dir,
        "archive_installers_older_than_days": days,
        "big_file_threshold_bytes": threshold_bytes,
        "big_file_threshold_human": human,
    }


def _human(n: int) -> str:
    x = float(n)
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if x < 1024 or u == "TB":
            return f"{x:.2f} {u}"
        x /= 1024
    return f"{n} B"
