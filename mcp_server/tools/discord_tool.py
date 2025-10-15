from __future__ import annotations

from typing import Optional
import requests


def send_discord_message(url: str, message: str, title: Optional[str] = None, level: str = "info") -> bool:
    color_map = {
        "info": 0x3498db,
        "success": 0x2ecc71,
        "warning": 0xf1c40f,
        "error": 0xe74c3c,
    }
    data = {
        "content": None,
        "embeds": [
            {
                "title": title or "MCP Notification",
                "description": message,
                "color": color_map.get(level, color_map["info"]),
            }
        ],
    }
    r = requests.post(url, json=data, timeout=15)
    return r.status_code in (200, 204)

