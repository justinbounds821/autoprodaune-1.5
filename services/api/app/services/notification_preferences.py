"""Notification preference storage for AutoPro Daune.

This module provides a simple JSON-based persistence layer for notification
preferences. In production this can be swapped with Supabase/PostgreSQL, but a
local file keeps the feature fully functional in any environment.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

DEFAULT_PREFERENCES: Dict[str, Any] = {
    "email": True,
    "sms": False,
    "whatsapp": True,
    "in_app": True,
    "lead_updates": True,
    "video_updates": True,
    "financial_reports": True,
    "social_alerts": True,
    "digest_frequency": "daily",
    "quiet_hours_start": None,
    "quiet_hours_end": None,
}


class NotificationPreferencesManager:
    """Utility class that manages notification preferences stored on disk."""

    _lock = threading.Lock()
    _data_dir = Path(__file__).resolve().parent.parent / "data"
    _storage_file = _data_dir / "notification_preferences.json"

    @classmethod
    def _ensure_storage(cls) -> None:
        cls._data_dir.mkdir(parents=True, exist_ok=True)
        if not cls._storage_file.exists():
            cls._storage_file.write_text("{}", encoding="utf-8")

    @classmethod
    def _load(cls) -> Dict[str, Any]:
        cls._ensure_storage()
        try:
            raw = cls._storage_file.read_text(encoding="utf-8").strip()
            if not raw:
                return {}
            return json.loads(raw)
        except json.JSONDecodeError:
            # Corrupted file – reset to defaults.
            return {}

    @classmethod
    def _write(cls, data: Dict[str, Any]) -> None:
        cls._ensure_storage()
        cls._storage_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def _merge_with_defaults(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        merged = {**DEFAULT_PREFERENCES}
        for key, value in payload.items():
            if key in DEFAULT_PREFERENCES:
                merged[key] = value
        merged["updated_at"] = payload.get("updated_at") or datetime.utcnow().isoformat()
        return merged

    @classmethod
    def get_preferences(cls, user_id: str) -> Dict[str, Any]:
        """Return preferences for a specific user, falling back to defaults."""
        with cls._lock:
            data = cls._load()
            if user_id not in data:
                prefs = cls._merge_with_defaults({})
                data[user_id] = prefs
                cls._write(data)
                return prefs

            stored = data[user_id] or {}
            merged = cls._merge_with_defaults(stored)
            # Persist merged defaults if new keys were added.
            if merged != stored:
                data[user_id] = merged
                cls._write(data)
            return merged

    @classmethod
    def update_preferences(cls, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update and persist preferences for a user."""
        with cls._lock:
            data = cls._load()
            payload_with_timestamp = {**payload, "updated_at": datetime.utcnow().isoformat()}
            merged = cls._merge_with_defaults(payload_with_timestamp)
            data[user_id] = merged
            cls._write(data)
            return merged

    @classmethod
    def reset_preferences(cls, user_id: str) -> Dict[str, Any]:
        """Reset preferences for a user back to defaults."""
        with cls._lock:
            data = cls._load()
            defaults = cls._merge_with_defaults({})
            data[user_id] = defaults
            cls._write(data)
            return defaults

    @classmethod
    def list_preferences(cls) -> Dict[str, Any]:
        """Return the entire preference store. Useful for audits/admin."""
        with cls._lock:
            data = cls._load()
            # Ensure every entry respects defaults without mutating the store.
            return {user_id: cls._merge_with_defaults(pref) for user_id, pref in data.items()}


__all__ = [
    "NotificationPreferencesManager",
    "DEFAULT_PREFERENCES",
]
