# AutoPro FastMCP Server (Python / FastAPI)

## Quick Start
- Python 3.11+ recommended
- From repo root:
  - `cd mcp_server`
  - `python -m venv .venv && .\\.venv\\Scripts\\activate`
  - `pip install -r requirements.txt`
  - `copy .env.example .env` and fill values
  - `uvicorn mcp_server.main:app --host 127.0.0.1 --port 8055 --reload`

## Endpoints
- `GET /health` – server status
- `POST /mcp/execute` – accepts `{ task, context? }`, returns `task_id`
- `POST /mcp/task/create` – create a tracked task
- `GET /mcp/task/{id}/status` – task status/result
- `POST /mcp/tools/github/commit` – write+commit files to local git repo
- `POST /mcp/tools/supabase/query` – select/insert/update/delete via PostgREST
- `POST /mcp/tools/discord/notify` – send Discord webhook notification
- `POST /mcp/tools/fs/write` – write file
- `POST /mcp/tools/fs/read` – read file

## CLI
- `python mcp_server/cli/commands.py execute "Fix auth bug"`
- `python mcp_server/cli/commands.py status task_abc123`
- `python mcp_server/cli/commands.py supabase_query leads select '{"status":"new"}' '{}' "*"`
- `python mcp_server/cli/commands.py notify "Build finished" --level success`

Set `MCP_SERVER_URL` to point CLI at a remote server.

## Security
- Do not commit `.env`.
- Use the `.env.example` template; keep real tokens out of Git.

## Orchestrator Integration
- This server is complementary to the existing Node orchestrator.
- It can be called from Orchestrator (via HTTP), and can later call it via a subprocess bridge (placeholder in `mcp_server/main.py`).

