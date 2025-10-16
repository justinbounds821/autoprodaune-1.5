"""CLI commands for MCP Server"""

from __future__ import annotations

import json
import os
from typing import Optional

import requests
import typer

app = typer.Typer(help="AutoPro FastMCP CLI")


def _server_url() -> str:
    """Get MCP server URL from environment"""
    return os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8012")


@app.command()
def execute(task: str, context: Optional[str] = typer.Option(None, help="JSON context")):
    """Execute a free-form MCP task"""
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
    """Check task status"""
    r = requests.get(f"{_server_url()}/mcp/task/{task_id}/status", timeout=30)
    typer.echo(r.text)


@app.command()
def orchestrate(command: str, project: str, branch: str):
    """Orchestrate workflow via MCP"""
    payload = {
        "command": command,
        "context": {
            "project": project,
            "branch": branch,
        },
    }
    r = requests.post(f"{_server_url()}/mcp/workflows/orchestrate", json=payload, timeout=300)
    typer.echo(r.text)


@app.command()
def health():
    """Check MCP server health"""
    r = requests.get(f"{_server_url()}/health", timeout=10)
    typer.echo(r.text)


@app.command()
def linear_create(title: str, description: str = ""):
    """Create Linear task"""
    payload = {"title": title, "description": description}
    r = requests.post(f"{_server_url()}/mcp/tools/linear/task", json=payload, timeout=60)
    typer.echo(r.text)


@app.command()
def github_issue(title: str, body: str = ""):
    """Create GitHub issue"""
    payload = {"title": title, "body": body}
    r = requests.post(f"{_server_url()}/mcp/tools/github/issue", json=payload, timeout=60)
    typer.echo(r.text)


if __name__ == "__main__":
    app()
