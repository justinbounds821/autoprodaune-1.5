"""Tester agent for running tests and builds"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict


def run_tests(repo_dir: Path) -> Dict[str, object]:
    """
    Run pytest tests if tests directory exists

    Args:
        repo_dir: Repository directory

    Returns:
        Test result with stdout/stderr
    """
    tests_dir = repo_dir / "tests"
    if not tests_dir.exists():
        return {"ok": True, "message": "no tests directory"}

    proc = subprocess.run(
        ["pytest", "-q"],
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
    )
    
    return {
        "ok": proc.returncode == 0,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "code": proc.returncode,
    }


def build_frontend(frontend_dir: Path) -> Dict[str, object]:
    """
    Build frontend with npm

    Args:
        frontend_dir: Frontend directory path

    Returns:
        Build result with stdout/stderr
    """
    if not frontend_dir.exists():
        return {"ok": False, "error": f"missing frontend dir: {frontend_dir}"}

    # Install dependencies if node_modules missing
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        proc_i = subprocess.run(
            ["npm", "install"],
            cwd=str(frontend_dir),
            capture_output=True,
            text=True,
        )
        if proc_i.returncode != 0:
            return {
                "ok": False,
                "step": "npm install",
                "stdout": proc_i.stdout[-4000:],
                "stderr": proc_i.stderr[-4000:],
                "code": proc_i.returncode,
            }

    # Build
    proc_b = subprocess.run(
        ["npm", "run", "build"],
        cwd=str(frontend_dir),
        capture_output=True,
        text=True,
    )
    
    return {
        "ok": proc_b.returncode == 0,
        "stdout": proc_b.stdout[-8000:],
        "stderr": proc_b.stderr[-8000:],
        "code": proc_b.returncode,
    }

