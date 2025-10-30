import os
import httpx
from typing import Dict, Any

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

async def query_table(table: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"mock": True, "data": [{"id": 1, "name": "Test"}]}

    async with httpx.AsyncClient() as client:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers=headers,
            params=filters or {}
        )
        return response.json()
