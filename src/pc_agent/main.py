from __future__ import annotations

from .graph import build_graph
from .reporting import save_report_md

def run_request(*, request: str, apply: bool, yes: bool, interactive: bool, dry_run: bool):
    graph = build_graph()

    result = graph.invoke(
        {
            "request": request,
            "apply": apply,
            "yes": yes,
            "interactive": interactive,
            "dry_run": dry_run,
        }
    )

    # result already contains report_md; persist to /reports
    report_path = save_report_md(result["report_md"])
    print(result["report_md"])
    print(f"\nReport saved: {report_path}")
