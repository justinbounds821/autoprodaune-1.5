"""
OpenAPI schema customization for GPT Developer Mode compatibility
"""

from typing import Dict, Any


def customize_openapi_for_gpt(openapi_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Customize OpenAPI schema for optimal GPT integration

    Args:
        openapi_schema: Original OpenAPI schema

    Returns:
        Customized schema with GPT-friendly descriptions
    """

    # Update info section
    openapi_schema["info"]["x-gpt-integration"] = {
        "enabled": True,
        "version": "1.0",
        "capabilities": [
            "workflow_orchestration",
            "linear_integration",
            "github_integration",
            "supabase_integration",
            "browser_testing",
            "api_testing",
        ],
    }

    openapi_schema["info"]["description"] = """
# AutoPro FastMCP Server

Production-ready MCP server for AutoPro Daune project with full orchestrator integration.

## Features

- **Workflow Orchestration**: Execute complex multi-step workflows
- **Linear Integration**: Create and manage tasks
- **GitHub Integration**: Create issues and commits
- **Supabase Integration**: Query and verify database
- **Testing**: Browser E2E and API tests
- **GPT Developer Mode**: Special endpoints for GPT integration

## GPT Developer Mode Endpoints

These endpoints are optimized for GPT assistants:

- `POST /mcp/tools/gpt/orchestrate` - Orchestrate complete workflow
- `POST /mcp/tools/gpt/create_task` - Create Linear task
- `POST /mcp/tools/gpt/test` - Run tests (browser or API)
- `GET /mcp/tools/gpt/status` - Get system status

## Usage

1. Check system health: `GET /health`
2. Orchestrate workflow: `POST /mcp/tools/gpt/orchestrate`
3. Track progress via Linear and GitHub
4. Get comprehensive status: `GET /mcp/tools/gpt/status`

## Authentication

Currently uses orchestrator's configured credentials.
No direct authentication required for mcp_server endpoints.
"""

    # Add GPT-specific tags
    if "tags" not in openapi_schema:
        openapi_schema["tags"] = []

    gpt_tag = {
        "name": "GPT Developer Mode",
        "description": "Special endpoints optimized for GPT assistants with enhanced response formatting",
    }

    if gpt_tag not in openapi_schema["tags"]:
        openapi_schema["tags"].insert(0, gpt_tag)

    # Add example responses to GPT endpoints
    gpt_endpoints = [
        "/mcp/tools/gpt/orchestrate",
        "/mcp/tools/gpt/create_task",
        "/mcp/tools/gpt/test",
        "/mcp/tools/gpt/status",
    ]

    for path in openapi_schema.get("paths", {}).keys():
        if any(gpt_endpoint in path for gpt_endpoint in gpt_endpoints):
            for method in openapi_schema["paths"][path].keys():
                if method in ["get", "post", "put", "delete", "patch"]:
                    # Add tag
                    if "tags" not in openapi_schema["paths"][path][method]:
                        openapi_schema["paths"][path][method]["tags"] = []
                    if "GPT Developer Mode" not in openapi_schema["paths"][path][method]["tags"]:
                        openapi_schema["paths"][path][method]["tags"].append("GPT Developer Mode")

                    # Add GPT-friendly description
                    if "description" in openapi_schema["paths"][path][method]:
                        openapi_schema["paths"][path][method]["description"] += (
                            "\n\n**GPT Note**: This endpoint returns GPT-optimized responses."
                        )

    return openapi_schema
