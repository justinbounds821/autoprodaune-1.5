"""
HTTP Client for communicating with MCP Orchestrator
Provides a Pythonic interface to all orchestrator tools
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class OrchestratorClient:
    """Client for MCP Orchestrator HTTP Bridge"""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 300):
        """
        Initialize orchestrator client

        Args:
            base_url: Base URL of orchestrator (default: env ORCHESTRATOR_URL or http://127.0.0.1:3030)
            timeout: Request timeout in seconds (default: 300)
        """
        self.base_url = base_url or os.getenv("ORCHESTRATOR_URL", "http://127.0.0.1:3030")
        self.timeout = timeout

        # Configure session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _call_tool(self, tool: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an orchestrator tool

        Args:
            tool: Tool name
            payload: Tool payload

        Returns:
            Tool result

        Raises:
            RuntimeError: If tool call fails
        """
        try:
            url = f"{self.base_url}/mcp/orchestrator/call"
            response = self.session.post(
                url,
                json={"tool": tool, "payload": payload},
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()

            if not result.get("ok"):
                raise RuntimeError(f"Tool {tool} failed: {result.get('error', 'Unknown error')}")

            return result
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to call orchestrator tool {tool}: {str(e)}")

    # ==================== WORKFLOW ORCHESTRATION ====================

    def orchestrate_workflow(
        self,
        command: str,
        context: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate a complete workflow

        Args:
            command: High-level command (e.g., "FIX AND TEST ALL CRITICAL ISSUES")
            context: Project context
            options: Orchestration options

        Returns:
            Workflow result with tasks, prompts, etc.
        """
        payload = {
            "command": command,
            "context": context,
            "options": options or {},
        }
        return self._call_tool("orchestrate_workflow", payload)

    # ==================== LINEAR TOOLS ====================

    def linear_create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: int = 0,
        labels: Optional[List[str]] = None,
        epic_id: Optional[str] = None,
        assignee: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create Linear task

        Args:
            title: Task title
            description: Task description
            priority: Priority (0-4, 0=no priority, 1=urgent, 4=low)
            labels: Labels
            epic_id: Parent epic ID
            assignee: Assignee user ID

        Returns:
            Task result with task_id and url
        """
        payload = {
            "title": title,
            "description": description,
            "priority": priority,
            "labels": labels or [],
            "epic_id": epic_id,
            "assignee": assignee,
        }
        return self._call_tool("linear_create_task", payload)

    def linear_update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update Linear task

        Args:
            task_id: Linear task ID
            status: New status
            comment: Comment to add

        Returns:
            Update result
        """
        payload = {
            "task_id": task_id,
            "status": status,
            "comment": comment,
        }
        return self._call_tool("linear_update_task", payload)

    def linear_list_tasks(self, limit: int = 50) -> Dict[str, Any]:
        """
        List Linear tasks

        Args:
            limit: Max number of tasks

        Returns:
            List of tasks
        """
        payload = {"limit": limit}
        return self._call_tool("linear_list_tasks", payload)

    # ==================== GITHUB TOOLS ====================

    def github_create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        linear_task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create GitHub issue

        Args:
            title: Issue title
            body: Issue body (markdown)
            labels: Labels
            assignees: Assignees
            linear_task_id: Linear task ID to link

        Returns:
            Issue result with issue_number and url
        """
        payload = {
            "title": title,
            "body": body,
            "labels": labels or [],
            "assignees": assignees or [],
            "linear_task_id": linear_task_id,
        }
        return self._call_tool("github_create_issue", payload)

    def github_commit(
        self,
        message: str,
        files: Optional[List[str]] = None,
        linear_task_id: Optional[str] = None,
        github_issue_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create Git commit

        Args:
            message: Commit message
            files: Files to commit (None = all changes)
            linear_task_id: Linear task ID for reference
            github_issue_number: GitHub issue number for reference

        Returns:
            Commit result with commit_hash
        """
        payload = {
            "message": message,
            "files": files,
            "linear_task_id": linear_task_id,
            "github_issue_number": github_issue_number,
        }
        return self._call_tool("github_commit", payload)

    # ==================== SUPABASE TOOLS ====================

    def supabase_query(
        self,
        table: str,
        operation: str,
        filters: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute Supabase query

        Args:
            table: Table name
            operation: Operation (select, insert, update, delete)
            filters: Query filters
            data: Data for insert/update
            limit: Result limit

        Returns:
            Query result
        """
        payload = {
            "table": table,
            "operation": operation,
            "filters": filters or {},
            "data": data or {},
            "limit": limit,
        }
        return self._call_tool("supabase_query", payload)

    def supabase_verify_fix(
        self,
        table: str,
        expected: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Verify that a fix worked by querying database

        Args:
            table: Table to check
            expected: Expected record fields
            description: What you are verifying

        Returns:
            Verification result
        """
        payload = {
            "table": table,
            "expected": expected,
            "description": description,
        }
        return self._call_tool("supabase_verify_fix", payload)

    # ==================== TESTING TOOLS ====================

    def browser_test(
        self,
        test_name: str,
        url: str,
        steps: List[Dict[str, Any]],
        verify_in_db: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute browser-based E2E test using Playwright

        Args:
            test_name: Test name
            url: Starting URL
            steps: Test steps (action, selector, value, timeout)
            verify_in_db: Optional database verification

        Returns:
            Test result
        """
        payload = {
            "test_name": test_name,
            "url": url,
            "steps": steps,
            "verify_in_db": verify_in_db,
        }
        return self._call_tool("browser_test", payload)

    def api_test(
        self,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200,
        expected_response: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Test API endpoint

        Args:
            method: HTTP method
            url: API endpoint URL
            body: Request body
            headers: Request headers
            expected_status: Expected status code
            expected_response: Expected response fields

        Returns:
            Test result
        """
        payload = {
            "method": method,
            "url": url,
            "body": body,
            "headers": headers,
            "expected_status": expected_status,
            "expected_response": expected_response,
        }
        return self._call_tool("api_test", payload)

    # ==================== UTILITY TOOLS ====================

    def system_health_check(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Check health of AutoPro Daune system

        Args:
            detailed: Return detailed health info

        Returns:
            Health status
        """
        payload = {"detailed": detailed}
        return self._call_tool("system_health_check", payload)

    def ping(self) -> bool:
        """
        Ping orchestrator to check if it's alive

        Returns:
            True if orchestrator is responding
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


# Global singleton instance
_orchestrator_client: Optional[OrchestratorClient] = None


def get_orchestrator_client() -> OrchestratorClient:
    """Get global orchestrator client instance"""
    global _orchestrator_client
    if _orchestrator_client is None:
        _orchestrator_client = OrchestratorClient()
    return _orchestrator_client

