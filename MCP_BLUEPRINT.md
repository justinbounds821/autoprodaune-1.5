# MCP Blueprint (FastMCP Server)

- Language: Python (FastAPI)
- Interfaces: REST API (primary), CLI (secondary), Discord webhook (notifications)
- Purpose: Complement Node Orchestrator; provide local automation tools (Git, Supabase, Filesystem), task tracking, and simple bridging hooks.

## Modules
- API: `mcp_server/main.py`
- Config: `mcp_server/config.py`
- Tools: `mcp_server/tools/*`
- Agents: `mcp_server/agents/*` (stubs for analyze / code / test)
- CLI: `mcp_server/cli/commands.py`

## Endpoints (v0)
- POST `/mcp/execute` – enqueue a generic task
- POST `/mcp/task/create` – register a task
- GET `/mcp/task/{id}/status` – retrieve status
- POST `/mcp/tools/github/commit` – write+commit files
- POST `/mcp/tools/supabase/query` – CRUD via PostgREST
- POST `/mcp/tools/discord/notify` – Discord webhook
- FS read/write

## Storage
- File-based tasks DB: `mcp_server/data/tasks.json`

## Security
- Tokens loaded from `mcp_server/.env` (not committed)

