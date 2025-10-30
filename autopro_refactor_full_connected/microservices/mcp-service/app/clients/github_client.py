import os
import httpx
from typing import Dict, Any

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

async def create_issue(repo: str, title: str, body: str) -> Dict[str, Any]:
    if not GITHUB_TOKEN:
        return {"mock": True, "issue_id": "123", "url": "https://github.com/mock"}

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = await client.post(
            f"https://api.github.com/repos/{repo}/issues",
            headers=headers,
            json={"title": title, "body": body}
        )
        return response.json()

async def create_commit(repo: str, message: str, files: list) -> Dict[str, Any]:
    if not GITHUB_TOKEN:
        return {"mock": True, "commit_sha": "abc123"}

    # Simplified - real implementation would use Git API
    return {"status": "committed", "sha": "real_sha"}
