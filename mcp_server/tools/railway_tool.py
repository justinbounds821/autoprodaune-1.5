from __future__ import annotations

import os
import shutil
import subprocess
from typing import Dict, Optional


def _which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def deploy_backend(token: str, project_id: str) -> Dict[str, object]:
    """Deploy backend using Railway CLI.

    Requires Railway CLI installed and a valid token.
    """
    railway_bin = _which("railway") or _which("railway.cmd")
    if not railway_bin:
        return {"ok": False, "error": "Railway CLI not found. Install with: npm i -g @railway/cli"}

    env = os.environ.copy()
    if token:
        env["RAILWAY_TOKEN"] = token

    # Deploy current repo directory; relies on project linking by ID
    args = [railway_bin, "up", "--project", project_id]
    proc = subprocess.run(args, env=env, capture_output=True, text=True)
    ok = proc.returncode == 0
    return {
        "ok": ok,
        "code": proc.returncode,
        "stdout": proc.stdout[-8000:],
        "stderr": proc.stderr[-8000:],
    }
