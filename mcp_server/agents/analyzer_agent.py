"""Analyzer agent for task analysis and file suggestion"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List


def _rg(pattern: str, cwd: Path) -> List[str]:
    """Run ripgrep to find files matching pattern"""
    try:
        proc = subprocess.run(
            ["rg", "-n", "--hidden", "--glob", "!node_modules/**", pattern],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode not in (0, 1):
            return []
        files = []
        for line in proc.stdout.splitlines():
            path = line.split(":", 1)[0].strip()
            if path and path not in files:
                files.append(path)
        return files
    except Exception:
        return []


def analyze_task(task_text: str, repo_dir: str | Path = ".") -> Dict[str, object]:
    """
    Analyze task and suggest relevant files

    Args:
        task_text: Task description
        repo_dir: Repository directory

    Returns:
        Analysis result with suggested files and plan
    """
    root = Path(repo_dir).resolve()
    text = task_text.lower()
    
    # Keyword mapping to common files
    keywords = [
        ("auth|login|jwt", ["services/api/app/routes/auth.py", "services/api/app/services/auth_service.py"]),
        ("lead|crm", ["services/api/app/routes/leads.py", "02_FRONTEND_UI_CLEAN/src/pages/LeadManagement.tsx"]),
        ("financial|invoice|factura", ["services/api/app/routes/financial.py", "02_FRONTEND_UI_CLEAN/src/pages/FinancialDashboard.tsx"]),
        ("video|heygen|moviepy", ["services/api/app/routes/video.py", "02_FRONTEND_UI_CLEAN/src/pages/ManoleVideoCreator.tsx"]),
        ("mcp|orchestrat", ["mcp_server/main.py", "mcp-orchestrator/src/http-bridge.ts"]),
    ]

    suggestions: List[str] = []
    for patt, defaults in keywords:
        if re.search(patt, text):
            suggestions.extend(defaults)

    # Ripgrep sweep for additional candidates
    for kw in set(re.findall(r"[a-zA-Z_]{3,}", text)):
        hits = _rg(kw, root)[:20]
        suggestions.extend(hits)

    # De-duplicate, keep within repo
    unique = []
    seen = set()
    for s in suggestions:
        if s not in seen and (root / s).exists():
            unique.append(s)
            seen.add(s)

    plan = [
        "read relevant files",
        "apply minimal patch",
        "run tests/build",
        "commit changes",
    ]
    
    return {
        "task": task_text,
        "suggested_files": unique[:50],
        "plan": plan,
    }
