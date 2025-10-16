"""Supabase integration tool for database operations"""

from __future__ import annotations

import time
from typing import Any, Dict

import requests


def _headers(api_key: str) -> Dict[str, str]:
    """Generate Supabase request headers"""
    return {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _filter_params(filters: Dict[str, Any]) -> Dict[str, str]:
    """
    Build PostgREST filter params

    Supports:
    - simple equality: {"col": "value"} -> col=eq.value
    - explicit operator dict: {"col": {"op":"ilike", "value":"%foo%"}}
    - pass-through operator string: {"col": "ilike.%foo%"}
    """
    params: Dict[str, str] = {}
    for k, v in filters.items():
        if isinstance(v, dict) and "op" in v:
            op = str(v.get("op", "eq"))
            val = v.get("value", "")
            params[k] = f"{op}.{val}"
        elif isinstance(v, str) and any(
            v.startswith(p + ".") for p in ("eq", "neq", "gt", "gte", "lt", "lte", "like", "ilike", "is")
        ):
            params[k] = v
        else:
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
    """
    Execute Supabase action via PostgREST

    Args:
        base_url: Supabase project URL
        api_key: API key
        table: Table name
        action: Action (select, insert, update, delete)
        filters: Query filters
        values: Data for insert/update
        select: Columns to select

    Returns:
        Query result

    Raises:
        ValueError: If credentials missing
        RuntimeError: If query fails
    """
    if not base_url or not api_key:
        raise ValueError("Missing Supabase URL or API key")

    url = f"{base_url.rstrip('/')}/rest/v1/{table}"
    headers = _headers(api_key)
    params: Dict[str, str] = {}

    def _req_with_retry(method: str, url: str, **kwargs):
        last = None
        for _ in range(3):
            try:
                return requests.request(method, url, timeout=30, **kwargs)
            except Exception as e:
                last = e
                time.sleep(0.5)
        raise last

    if action == "select":
        params = {"select": select}
        params.update(_filter_params(filters))
        resp = _req_with_retry("GET", url, headers=headers, params=params)
    elif action == "insert":
        headers["Prefer"] = "return=representation"
        resp = _req_with_retry("POST", url, headers=headers, json=values)
    elif action == "update":
        headers["Prefer"] = "return=representation"
        params.update(_filter_params(filters))
        resp = _req_with_retry("PATCH", url, headers=headers, params=params, json=values)
    elif action == "delete":
        params.update(_filter_params(filters))
        resp = _req_with_retry("DELETE", url, headers=headers, params=params)
    else:
        raise ValueError(f"Unsupported action: {action}")

    if resp.status_code >= 400:
        raise RuntimeError(f"Supabase error {resp.status_code}: {resp.text}")

    try:
        return resp.json()
    except Exception:
        return {"ok": True}


def log_task_event(base_url: str, api_key: str, event: Dict[str, Any]) -> bool:
    """
    Log task event to mcp_tasks table

    Args:
        base_url: Supabase project URL
        api_key: API key
        event: Event data

    Returns:
        True if successful, False otherwise
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

