"""Railway deployment tool"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Dict, Optional


def _which(cmd: str) -> Optional[str]:
    """Find command in PATH"""
    return shutil.which(cmd)


def deploy_backend(token: str, project_id: str) -> Dict[str, object]:
    """
    Deploy backend using Railway CLI

    Args:
        token: Railway token
        project_id: Project ID

    Returns:
        Deployment result
    """
    railway_bin = _which("railway") or _which("railway.cmd")
    if not railway_bin:
        return {"ok": False, "error": "Railway CLI not found. Install with: npm i -g @railway/cli"}

    env = os.environ.copy()
    if token:
        env["RAILWAY_TOKEN"] = token

    args = [railway_bin, "up", "--project", project_id]
    proc = subprocess.run(args, env=env, capture_output=True, text=True)
    
    return {
        "ok": proc.returncode == 0,
        "code": proc.returncode,
        "stdout": proc.stdout[-8000:],
        "stderr": proc.stderr[-8000:],
    }
