from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Tuple

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def period_bounds(period: str, *, now: datetime | None = None) -> Tuple[str, str]:
    """
    întoarce (start_iso, end_iso) în UTC pentru perioade scurte:
      'today' | 'yesterday' | '7d' | '30d' | 'mtd' | 'ytd'
    acceptă și 'Nd' cu N>0.
    """
    now = now or _now_utc()
    end = now

    key = period.lower().strip()
    if key == "today":
        start = datetime(end.year, end.month, end.day, tzinfo=end.tzinfo)
    elif key == "yesterday":
        y = end - timedelta(days=1)
        start = datetime(y.year, y.month, y.day, tzinfo=y.tzinfo)
        end = datetime(end.year, end.month, end.day, tzinfo=end.tzinfo)
    elif key == "mtd":
        start = datetime(end.year, end.month, 1, tzinfo=end.tzinfo)
    elif key == "ytd":
        start = datetime(end.year, 1, 1, tzinfo=end.tzinfo)
    elif key.endswith("d") and key[:-1].isdigit():
        days = int(key[:-1])
        start = end - timedelta(days=days)
    else:
        # fallback 7d
        start = end - timedelta(days=7)

    return start.isoformat(), end.isoformat()

def normalize_provider(val: str | None) -> str | None:
    """normalizare provider -> 'WhatsApp' (nu 'Whatsapp'/'wa'/etc.)"""
    if not val:
        return None
    v = val.strip().lower()
    if v in {"whatsapp","wa","whatapp","wapp"}:
        return "WhatsApp"
    return val
