from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List


def write_changes(repo_dir: Path, changes: List[Dict[str, str]]) -> Dict[str, object]:
    applied = 0
    details = []
    for ch in changes:
        path = ch.get("path")
        content = ch.get("content", "")
        if not path:
            continue
        target = (repo_dir / path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        applied += 1
        details.append({"path": path, "bytes": len(content)})
    return {"applied": applied, "details": details}


def create_branch(repo_dir: Path, branch: str) -> Dict[str, object]:
    proc = subprocess.run(["git", "checkout", "-B", branch], cwd=str(repo_dir), capture_output=True, text=True)
    return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr, "code": proc.returncode}


def commit(repo_dir: Path, message: str) -> Dict[str, object]:
    add = subprocess.run(["git", "add", "-A"], cwd=str(repo_dir), capture_output=True, text=True)
    if add.returncode != 0:
        return {"ok": False, "step": "add", "stderr": add.stderr}
    commit = subprocess.run(["git", "commit", "-m", message], cwd=str(repo_dir), capture_output=True, text=True)
    return {"ok": commit.returncode == 0, "stdout": commit.stdout, "stderr": commit.stderr, "code": commit.returncode}
