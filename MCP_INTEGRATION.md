# MCP Integration Guide

## With Cursor MCP Orchestrator (Node)
- Call this server via HTTP from orchestrator tools.
- Example (API Test): POST `http://127.0.0.1:8055/mcp/execute` with `{ "task": "Fix auth bug" }`.
- Bridge back to orchestrator can be added later via subprocess (`node <index.js> ...`).

## With Local Dev
- Start: `mcp_server/START_MCP_SERVER.ps1` (Windows) or `mcp_server/start_mcp.sh` (Unix)
- Use CLI: `python mcp_server/cli/commands.py execute "Task"`

## Token Handling
- Copy `mcp_server/.env.example` to `.env`, fill tokens.
- Do not commit `.env`.

