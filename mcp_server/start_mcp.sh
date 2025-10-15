#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-127.0.0.1}"
PORT="${2:-8055}"

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "[MCP] Created .env from .env.example (fill tokens)"
fi

echo "[MCP] Starting server on http://$HOST:$PORT"
python -m uvicorn mcp_server.main:app --host "$HOST" --port "$PORT" --reload

