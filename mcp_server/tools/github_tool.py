"""GitHub integration tool for commits and issues"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import requests


def commit_changes(repo_dir: Path, files: List[Dict[str, str]], message: str) -> Dict[str, object]:
    """
    Write files and create Git commit

    Args:
        repo_dir: Repository directory
        files: List of {path, content} dicts
        message: Commit message

    Returns:
        Commit result with hash
    """
    repo_dir = repo_dir.resolve()
    git_dir = repo_dir / ".git"
    if not git_dir.exists():
        raise RuntimeError(f"Not a git repository: {repo_dir}")

    # Write files
    for f in files:
        rel = f.get("path", "").strip()
        content = f.get("content", "")
        if not rel:
            continue
            
        target = (repo_dir / rel).resolve()
        
        # Prevent path escape
        if repo_dir not in target.parents and repo_dir != target:
            raise RuntimeError(f"Refusing to write outside repo: {target}")
            
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    # Commit
    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", "mcp-bot")
    env.setdefault("GIT_AUTHOR_EMAIL", "bot@example.com")
    env.setdefault("GIT_COMMITTER_NAME", env["GIT_AUTHOR_NAME"])
    env.setdefault("GIT_COMMITTER_EMAIL", env["GIT_AUTHOR_EMAIL"])

    def run(cmd: List[str]):
        return subprocess.run(
            cmd,
            cwd=str(repo_dir),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    add_res = run(["git", "add", "-A"])
    if add_res.returncode != 0:
        return {"ok": False, "step": "git add", "stderr": add_res.stderr}

    commit_res = run(["git", "commit", "-m", message])
    if commit_res.returncode != 0:
        return {"ok": False, "step": "git commit", "stderr": commit_res.stderr}

    rev_res = run(["git", "rev-parse", "HEAD"])
    commit_sha = rev_res.stdout.strip() if rev_res.returncode == 0 else ""
    
    return {"ok": True, "commit": commit_sha}


def create_issue(
    owner_repo: str,
    token: str,
    title: str,
    body: str = "",
    labels: Optional[List[str]] = None,
) -> Dict[str, object]:
    """
    Create GitHub issue via REST API

    Args:
        owner_repo: Repository in format "owner/repo"
        token: GitHub token
        title: Issue title
        body: Issue body
        labels: Issue labels

    Returns:
        Issue result with URL
    """
    if not owner_repo or "/" not in owner_repo:
        return {"ok": False, "error": "Invalid repo format"}

    url = f"https://api.github.com/repos/{owner_repo}/issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    payload: Dict[str, object] = {"title": title}
    if body:
        payload["body"] = body
    if labels:
        payload["labels"] = labels

    r = requests.post(url, headers=headers, json=payload, timeout=30)
    
    try:
        data = r.json()
    except Exception:
        data = {"text": r.text}

    return {
        "ok": r.status_code in (200, 201),
        "status": r.status_code,
        "data": data,
    }

