from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict


def run_tests(repo_dir: Path) -> Dict[str, object]:
    # Very lightweight pytest runner (if tests exist)
    tests_dir = repo_dir / "tests"
    if not tests_dir.exists():
        return {"ok": True, "message": "no tests directory"}
    proc = subprocess.run(["pytest", "-q"], cwd=str(repo_dir), capture_output=True, text=True)
    return {
        "ok": proc.returncode == 0,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "code": proc.returncode,
    }


def build_frontend(frontend_dir: Path) -> Dict[str, object]:
    """Run npm install if needed and build via `npm run build`.

    Returns stdout/stderr and exit code; ok==True if build succeeded.
    """
    if not frontend_dir.exists():
        return {"ok": False, "error": f"missing frontend dir: {frontend_dir}"}
    # Install dependencies only if node_modules is missing
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        proc_i = subprocess.run(["npm", "install"], cwd=str(frontend_dir), capture_output=True, text=True)
        if proc_i.returncode != 0:
            return {"ok": False, "step": "npm install", "stdout": proc_i.stdout[-4000:], "stderr": proc_i.stderr[-4000:], "code": proc_i.returncode}
    proc_b = subprocess.run(["npm", "run", "build"], cwd=str(frontend_dir), capture_output=True, text=True)
    return {"ok": proc_b.returncode == 0, "stdout": proc_b.stdout[-8000:], "stderr": proc_b.stderr[-8000:], "code": proc_b.returncode}
