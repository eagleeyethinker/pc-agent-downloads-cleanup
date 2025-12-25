from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph, END

from .llm import parse_request_params
from .tools.fs_tools import (
    scan_folder,
    get_big_files,
    propose_cleanup,
    apply_actions,
)
from .util.safety import default_allowed_roots


State = Dict[str, Any]

def parse_node(state: State) -> State:
    request = state["request"]
    params = parse_request_params(request)
    state["params"] = params
    return state

def plan_node(state: State) -> State:
    params = state["params"]

    allowed = default_allowed_roots()
    target = params["target_dir"]

    items = scan_folder(target_dir=target, allowed_roots=allowed)
    state["scan"] = items

    big_files = get_big_files(items, threshold_bytes=params["big_file_threshold_bytes"])
    state["big_files"] = big_files

    proposed = propose_cleanup(
        items,
        target_dir=target,
        archive_installers_older_than_days=params["archive_installers_older_than_days"],
        allowed_roots=allowed,
    )
    state["proposed_actions"] = proposed
    return state

def approve_node(state: State) -> State:
    # Human-in-the-loop: optionally choose subset of actions
    apply_flag = bool(state.get("apply"))
    interactive = bool(state.get("interactive"))
    yes = bool(state.get("yes"))

    proposed = state.get("proposed_actions", [])

    # If not applying, skip
    if not apply_flag:
        state["approved_actions"] = []
        return state

    # If --yes, approve all
    if yes and not interactive:
        state["approved_actions"] = proposed
        return state

    # If interactive, choose actions
    if interactive:
        chosen = []
        if not proposed:
            state["approved_actions"] = []
            return state

        print("\nSelect actions to apply:")
        for i, a in enumerate(proposed, start=1):
            print(f"  {i}. {a['op']}: {a['src']} -> {a['dst']}")

        raw = input("\nEnter numbers (comma-separated) or 'all' or blank to cancel: ").strip().lower()
        if raw == "all":
            chosen = proposed
        elif raw == "":
            chosen = []
        else:
            picks = set()
            for part in raw.split(","):
                part = part.strip()
                if part.isdigit():
                    picks.add(int(part))
            for i, a in enumerate(proposed, start=1):
                if i in picks:
                    chosen.append(a)

        state["approved_actions"] = chosen
        return state

    # Default prompt (y/N) for all
    if proposed:
        print("\nProposed actions:")
        for i, a in enumerate(proposed, start=1):
            print(f"  {i}. {a['op']}: {a['src']} -> {a['dst']}")
        ans = input("\nApply these actions? (y/N): ").strip().lower()
        state["approved_actions"] = proposed if ans == "y" else []
    else:
        state["approved_actions"] = []
    return state

def execute_node(state: State) -> State:
    approved = state.get("approved_actions", [])
    if not approved:
        state["executed_actions"] = []
        return state

    executed = apply_actions(approved)
    state["executed_actions"] = executed
    return state

def report_node(state: State) -> State:
    params = state["params"]
    big_files = state.get("big_files", [])
    proposed = state.get("proposed_actions", [])
    executed = state.get("executed_actions", [])

    # Build report markdown
    lines = []
    lines.append("# Downloads Cleanup Report")
    lines.append(f"- Target: `{params['target_dir']}`")
    lines.append(f"- Files scanned: **{len(state.get('scan', []))}**")
    lines.append(f"- Total size: **{state.get('total_size_human', 'n/a')}**")
    lines.append(f"- Big-file threshold: **{params['big_file_threshold_human']}**")
    lines.append(f"- Parser used: **{params.get('_parser','unknown')}**")
    lines.append("")
    lines.append("## Big Files")
    if not big_files:
        lines.append("- None")
    else:
        for bf in big_files:
            lines.append(f"- {bf['size_human']} — `{bf['path']}`")

    lines.append("")
    lines.append("## Proposed Actions (requiring approval)")
    if not proposed:
        lines.append("- None")
    else:
        for a in proposed:
            lines.append(f"- {a['op']}: `{a['src']}` → `{a['dst']}`")

    lines.append("")
    lines.append("## Executed Actions")
    if not executed:
        lines.append("- None")
    else:
        for a in executed:
            lines.append(f"- {a['op']}: `{a['src']}` → `{a['dst']}`")

    state["report_md"] = "\n".join(lines) + "\n"
    return state

def build_graph():
    g = StateGraph(State)
    g.add_node("parse", parse_node)
    g.add_node("plan", plan_node)
    g.add_node("approve", approve_node)
    g.add_node("execute", execute_node)
    g.add_node("report", report_node)

    g.set_entry_point("parse")
    g.add_edge("parse", "plan")
    g.add_edge("plan", "approve")
    g.add_edge("approve", "execute")
    g.add_edge("execute", "report")
    g.add_edge("report", END)

    return g.compile()
