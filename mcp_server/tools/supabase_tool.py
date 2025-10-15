from __future__ import annotations

from typing import Any, Dict
from urllib.parse import urlencode

import requests


def _headers(api_key: str) -> Dict[str, str]:
    return {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _filter_params(filters: Dict[str, Any]) -> Dict[str, str]:
    params: Dict[str, str] = {}
    for k, v in filters.items():
        params[k] = f"eq.{v}"
    return params


def run_supabase_action(
    base_url: str,
    api_key: str,
    table: str,
    action: str,
    filters: Dict[str, Any],
    values: Dict[str, Any],
    select: str = "*",
) -> Any:
    if not base_url or not api_key:
        raise ValueError("Missing Supabase URL or API key")
    url = f"{base_url.rstrip('/')}/rest/v1/{table}"
    headers = _headers(api_key)
    params: Dict[str, str] = {}

    if action == "select":
        params = {"select": select}
        params.update(_filter_params(filters))
        resp = requests.get(url, headers=headers, params=params, timeout=30)
    elif action == "insert":
        headers["Prefer"] = "return=representation"
        resp = requests.post(url, headers=headers, json=values, timeout=30)
    elif action == "update":
        headers["Prefer"] = "return=representation"
        params.update(_filter_params(filters))
        resp = requests.patch(url, headers=headers, params=params, json=values, timeout=30)
    elif action == "delete":
        params.update(_filter_params(filters))
        resp = requests.delete(url, headers=headers, params=params, timeout=30)
    else:
        raise ValueError(f"Unsupported action: {action}")

    if resp.status_code >= 400:
        raise RuntimeError(f"Supabase error {resp.status_code}: {resp.text}")
    try:
        return resp.json()
    except Exception:
        return {"ok": True}


def log_task_event(base_url: str, api_key: str, event: Dict[str, Any]) -> bool:
    """Insert a task event into `mcp_tasks` table if available.

    Expected columns: task_id (text), title (text), status (text), result (jsonb), created_at (timestamp default now()).
    If the table is missing or access fails, returns False but does not raise.
    """
    if not base_url or not api_key:
        return False
    url = f"{base_url.rstrip('/')}/rest/v1/mcp_tasks"
    headers = _headers(api_key)
    headers["Prefer"] = "return=minimal"
    try:
        r = requests.post(url, headers=headers, json=event, timeout=15)
        return r.status_code < 400
    except Exception:
        return False
