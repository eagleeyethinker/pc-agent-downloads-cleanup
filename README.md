
---

# PC Downloads Cleanup Agent (LangGraph)

A **local, agentic AI assistant** that safely cleans your Windows *Downloads* folder using **LangGraph**, with optional human-in-the-loop control.

---

## Install (Dev Mode)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
```

**Defaults**

* **Human-in-the-loop:** enabled by default
* **Full autonomy:** `--apply --yes`

---

## How to Run (PowerShell)

From your activated virtual environment:

### Dry Run (no changes applied)

```powershell
pc-agent --dry-run "Clean up my Downloads: archive installers older than 30 days and show big files > 1GB"
```

### Apply with One Confirmation Prompt

```powershell
pc-agent --apply "Clean up my Downloads: archive installers older than 30 days and show big files > 1GB"
```

### Apply with Per-Action Selection (Interactive)

```powershell
pc-agent --apply --interactive "Clean up my Downloads: archive installers older than 30 days and show big files > 1GB"
```

### Apply with No Prompts (Full Autonomy)

```powershell
pc-agent --apply --yes "Clean up my Downloads: archive installers older than 30 days and show big files > 1GB"
```

---

## Reports

Markdown reports are saved under:

```text
./reports/
```

Each run produces an auditable record of:

* detected files
* proposed actions
* approved actions
* executed results

---

## Reinstall Cleanly (Important)

From the repo root:

```powershell
deactivate   # if needed
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
```

Then verify:

```powershell
pc-agent --help
pc-agent "Clean up my Downloads: archive installers older than 30 days and show big files > 1GB"
```

---

## Why This Is Still “Agentic AI” (Even One-Time)

**An agent is defined by behavior — not uptime.**

This system already has:

1. **Goal interpretation** (LLM or structured parser)
2. **Environment inspection** (filesystem scanning)
3. **Planning** (proposed actions)
4. **Tool use** (file move/archive operations)
5. **Human-in-the-loop control**
6. **Memory** (persistent Markdown reports)

That absolutely qualifies as an **agentic system**.

---

## Automation (Optional)

### Windows Task Scheduler (Recommended)

You can schedule the agent to run:

* daily
* weekly
* monthly

With any desired autonomy level (`--dry-run`, `--apply`, or `--apply --yes`).

---