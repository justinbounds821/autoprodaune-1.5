"""
Orchestrator Client - 386 linii, 24 integrări
Client HTTP funcțional pentru comunicare cu MCP Orchestrator
"""
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class OrchestratorClient:
    """Client pentru comunicare cu MCP Orchestrator pe port 3030"""
    
    def __init__(self, base_url: str = "http://localhost:3030", timeout: int = 300):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Închide clientul HTTP"""
        await self.client.aclose()
    
    # ============= LINEAR INTEGRATION =============
    
    async def create_linear_issue(
        self,
        title: str,
        description: str,
        team_id: str,
        priority: int = 0,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Creează issue în Linear"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tools/linear/create-issue",
                json={
                    "title": title,
                    "description": description,
                    "teamId": team_id,
                    "priority": priority,
                    "labelIds": labels or []
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating Linear issue: {e}")
            raise
    
    async def update_linear_issue(
        self,
        issue_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        state_id: Optional[str] = None,
        priority: Optional[int] = None
    ) -> Dict[str, Any]:
        """Actualizează issue Linear"""
        try:
            payload = {"issueId": issue_id}
            if title:
                payload["title"] = title
            if description:
                payload["description"] = description
            if state_id:
                payload["stateId"] = state_id
            if priority is not None:
                payload["priority"] = priority
            
            response = await self.client.post(
                f"{self.base_url}/api/tools/linear/update-issue",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error updating Linear issue: {e}")
            raise
    
    async def list_linear_issues(
        self,
        team_id: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Listează issues Linear"""
        try:
            params = {"limit": limit}
            if team_id:
                params["teamId"] = team_id
            if state:
                params["state"] = state
            
            response = await self.client.get(
                f"{self.base_url}/api/tools/linear/issues",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error listing Linear issues: {e}")
            raise
    
    # ============= GITHUB INTEGRATION =============
    
    async def create_github_issue(
        self,
        repo: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Creează GitHub issue"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tools/github/create-issue",
                json={
                    "repo": repo,
                    "title": title,
                    "body": body,
                    "labels": labels or [],
                    "assignees": assignees or []
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating GitHub issue: {e}")
            raise
    
    async def create_github_pr(
        self,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: str
    ) -> Dict[str, Any]:
        """Creează GitHub Pull Request"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tools/github/create-pr",
                json={
                    "repo": repo,
                    "title": title,
                    "head": head,
                    "base": base,
                    "body": body
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating GitHub PR: {e}")
            raise
    
    async def github_commit(
        self,
        repo: str,
        branch: str,
        message: str,
        files: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Creează commit GitHub"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tools/github/commit",
                json={
                    "repo": repo,
                    "branch": branch,
                    "message": message,
                    "files": files
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating GitHub commit: {e}")
            raise
    
    # ============= SUPABASE INTEGRATION =============
    
    async def supabase_select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """SELECT din Supabase"""
        try:
            payload = {
                "table": table,
                "columns": columns
            }
            if filters:
                payload["filters"] = filters
            if limit:
                payload["limit"] = limit
            
            response = await self.client.post(
                f"{self.base_url}/api/tools/supabase/select",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error selecting from Supabase: {e}")
            raise
    
    async def supabase_insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """INSERT în Supabase"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tools/supabase/insert",
                json={
                    "table": table,
                    "data": data
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error inserting to Supabase: {e}")
            raise
    
    async def supabase_update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """UPDATE în Supabase"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tools/supabase/update",
                json={
                    "table": table,
                    "data": data,
                    "filters": filters
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error updating Supabase: {e}")
            raise
    
    async def supabase_delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """DELETE din Supabase"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tools/supabase/delete",
                json={
                    "table": table,
                    "filters": filters
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error deleting from Supabase: {e}")
            raise
    
    # ============= PLAYWRIGHT INTEGRATION =============
    
    async def browser_navigate(
        self,
        url: str,
        wait_for: Optional[str] = None
    ) -> Dict[str, Any]:
        """Navigare browser cu Playwright"""
        try:
            payload = {"url": url}
            if wait_for:
                payload["waitFor"] = wait_for
            
            response = await self.client.post(
                f"{self.base_url}/api/tools/playwright/goto",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error navigating browser: {e}")
            raise
    
    async def browser_click(
        self,
        selector: str
    ) -> Dict[str, Any]:
        """Click pe element"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tools/playwright/click",
                json={"selector": selector}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            raise
    
    async def browser_fill(
        self,
        selector: str,
        value: str
    ) -> Dict[str, Any]:
        """Completare formular"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tools/playwright/fill",
                json={
                    "selector": selector,
                    "value": value
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error filling form: {e}")
            raise
    
    async def browser_screenshot(
        self,
        path: Optional[str] = None,
        full_page: bool = False
    ) -> Dict[str, Any]:
        """Screenshot pagină"""
        try:
            payload = {"fullPage": full_page}
            if path:
                payload["path"] = path
            
            response = await self.client.post(
                f"{self.base_url}/api/tools/playwright/screenshot",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            raise
    
    # ============= DISCORD INTEGRATION =============
    
    async def send_discord_message(
        self,
        content: str,
        webhook_url: Optional[str] = None,
        embeds: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Trimite mesaj Discord"""
        try:
            payload = {"content": content}
            if webhook_url:
                payload["webhookUrl"] = webhook_url
            if embeds:
                payload["embeds"] = embeds
            
            response = await self.client.post(
                f"{self.base_url}/api/tools/discord/send",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
            raise
    
    # ============= FILESYSTEM OPERATIONS =============
    
    async def read_file(self, path: str) -> Dict[str, Any]:
        """Citește fișier"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tools/filesystem/read",
                json={"path": path}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise
    
    async def write_file(
        self,
        path: str,
        content: str
    ) -> Dict[str, Any]:
        """Scrie fișier"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/tools/filesystem/write",
                json={
                    "path": path,
                    "content": content
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            raise
    
    # ============= HEALTH CHECK =============
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifică starea orchestrator"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Orchestrator health check failed: {e}")
            raise
