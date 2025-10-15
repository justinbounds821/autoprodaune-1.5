from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Dict, List


def commit_changes(repo_dir: Path, files: List[Dict[str, str]], message: str) -> Dict[str, object]:
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
        # prevent path escape
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
        return subprocess.run(cmd, cwd=str(repo_dir), env=env, capture_output=True, text=True, check=False)

    add_res = run(["git", "add", "-A"]) 
    if add_res.returncode != 0:
        return {"ok": False, "step": "git add", "stderr": add_res.stderr}

    commit_res = run(["git", "commit", "-m", message])
    if commit_res.returncode != 0:
        # Possibly nothing to commit
        return {"ok": False, "step": "git commit", "stderr": commit_res.stderr}

    rev_res = run(["git", "rev-parse", "HEAD"]) 
    commit_sha = rev_res.stdout.strip() if rev_res.returncode == 0 else ""
    return {"ok": True, "commit": commit_sha}

