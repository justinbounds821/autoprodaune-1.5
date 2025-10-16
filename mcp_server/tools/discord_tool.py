"""Discord notification tool"""

from __future__ import annotations

from typing import Optional

import requests


def send_discord_message(
    url: str,
    message: str,
    title: Optional[str] = None,
    level: str = "info",
) -> bool:
    """
    Send Discord webhook notification

    Args:
        url: Discord webhook URL
        message: Message content
        title: Embed title
        level: Message level (info, success, warning, error)

    Returns:
        True if successful
    """
    color_map = {
        "info": 0x3498DB,
        "success": 0x2ECC71,
        "warning": 0xF1C40F,
        "error": 0xE74C3C,
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

