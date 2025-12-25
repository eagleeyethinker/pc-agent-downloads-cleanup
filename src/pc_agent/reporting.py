from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

def save_report_md(report_md: str) -> str:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = reports_dir / f"downloads_cleanup_{ts}.md"
    path.write_text(report_md, encoding="utf-8")
    return str(path)
