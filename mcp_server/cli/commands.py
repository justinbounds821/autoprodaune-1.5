from __future__ import annotations

import json
import os
from typing import Optional

import requests
import typer


app = typer.Typer(help="AutoPro FastMCP CLI")


def _server_url() -> str:
    return os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8055")


@app.command()
def execute(task: str, context: Optional[str] = typer.Option(None, help="JSON context")):
    """Execute a free-form MCP task."""
    payload = {"task": task}
    if context:
        try:
            payload["context"] = json.loads(context)
        except Exception as e:
            typer.echo(f"Invalid context JSON: {e}")
            raise typer.Exit(2)
    r = requests.post(f"{_server_url()}/mcp/execute", json=payload, timeout=30)
    typer.echo(r.text)


@app.command()
def status(task_id: str):
    """Check task status."""
    r = requests.get(f"{_server_url()}/mcp/task/{task_id}/status", timeout=30)
    typer.echo(r.text)


@app.command()
def supabase_query(table: str, action: str = "select", filters: str = "{}", values: str = "{}", select: str = "*"):
    """Run a Supabase table action.

    FILTERS and VALUES should be JSON strings.
    """
    try:
        filters_obj = json.loads(filters)
        values_obj = json.loads(values)
    except Exception as e:
        typer.echo(f"Invalid JSON: {e}")
        raise typer.Exit(2)
    payload = {"table": table, "action": action, "filters": filters_obj, "values": values_obj, "select": select}
    r = requests.post(f"{_server_url()}/mcp/tools/supabase/query", json=payload, timeout=60)
    typer.echo(r.text)


@app.command()
def notify(message: str, title: Optional[str] = None, level: str = "info"):
    """Send a Discord notification via configured webhook."""
    payload = {"message": message, "title": title, "level": level}
    r = requests.post(f"{_server_url()}/mcp/tools/discord/notify", json=payload, timeout=30)
    typer.echo(r.text)


if __name__ == "__main__":
    app()

