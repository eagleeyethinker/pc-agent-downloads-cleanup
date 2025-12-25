import os
import typer
from dotenv import load_dotenv

from .main import run_request

# Load .env early so OPENAI_API_KEY is present before anything imports llm
load_dotenv()

app = typer.Typer(
    add_completion=False,
    pretty_exceptions_enable=False,       # less noise
    pretty_exceptions_show_locals=False,  # no giant locals dump
)

@app.command()
def run(
    request: str = typer.Argument(..., help="Natural language request"),
    apply: bool = typer.Option(False, "--apply", help="Apply proposed actions"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not apply actions"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Auto-confirm prompts"),
    interactive: bool = typer.Option(False, "--interactive", help="Select actions interactively"),
):
    # If dry-run, force apply False
    if dry_run:
        apply = False

    run_request(
        request=request,
        apply=apply,
        yes=yes,
        interactive=interactive,
        dry_run=dry_run,
    )

if __name__ == "__main__":
    app()
