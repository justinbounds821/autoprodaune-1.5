import os
import httpx
from typing import Dict, Any

LINEAR_API_KEY = os.getenv("LINEAR_API_KEY", "")

async def create_task(title: str, description: str, priority: int = 0) -> Dict[str, Any]:
    if not LINEAR_API_KEY:
        return {"mock": True, "task_id": "TASK-123", "url": "https://linear.app/mock"}

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": LINEAR_API_KEY,
            "Content-Type": "application/json"
        }
        query = '''
        mutation CreateIssue($title: String!, $description: String!) {
            issueCreate(input: {title: $title, description: $description}) {
                issue { id url }
            }
        }
        '''
        response = await client.post(
            "https://api.linear.app/graphql",
            headers=headers,
            json={"query": query, "variables": {"title": title, "description": description}}
        )
        return response.json()
