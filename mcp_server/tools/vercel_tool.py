from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional


def _which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def deploy_frontend(
    token: str,
    project_dir: str | Path,
    prod: bool = True,
    org_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Dict[str, object]:
    """Deploy frontend using Vercel CLI.

    Requires Vercel CLI installed and a valid token. Non-interactive flags are used.
    - token: Vercel token
    - project_dir: path to the frontend app (e.g., 02_FRONTEND_UI_CLEAN)
    - prod: deploy with --prod
    - org_id, project_id: optional scope info
    """
    vercel_bin = _which("vercel") or _which("vercel.cmd")
    if not vercel_bin:
        return {"ok": False, "error": "Vercel CLI not found. Install with: npm i -g vercel"}

    env = os.environ.copy()
    if token:
        env["VERCEL_TOKEN"] = token

    args = [vercel_bin, "deploy", "--yes"]
    if prod:
        args.append("--prod")
    if org_id:
        args += ["--scope", org_id]
    if project_id:
        # Not strictly required for CLI deploy, but include as metadata
        env["VERCEL_PROJECT_ID"] = project_id

    cwd = str(Path(project_dir).resolve())
    proc = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)
    ok = proc.returncode == 0
    return {
        "ok": ok,
        "code": proc.returncode,
        "stdout": proc.stdout[-8000:],
        "stderr": proc.stderr[-8000:],
    }
