#!/usr/bin/env bash
set -euo pipefail

# Start FastAPI backend for AutoPro Daune
# Usage: ./start-backend.sh

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_DIR="$ROOT_DIR/services/api"

if [ ! -f "$ROOT_DIR/.env" ] && [ -f "$ROOT_DIR/env.example" ]; then
  echo "⚠️  .env not found at repo root. Copying env.example to .env (edit it!)"
  cp "$ROOT_DIR/env.example" "$ROOT_DIR/.env"
fi

if [ -f "$ROOT_DIR/.env" ]; then
  echo "✅ .env file found"
fi

export $(grep -v '^#' "$ROOT_DIR/.env" | xargs -d '\n' -r)

if [ -f "$API_DIR/requirements.txt" ]; then
  echo "✅ Ensuring Python dependencies (venv optional)"
  python3 -m pip install -U pip >/dev/null
  python3 -m pip install -r "$API_DIR/requirements.txt"
fi

# Default host/port
: "${HOST:=127.0.0.1}"
: "${PORT:=8001}"

# Run uvicorn
exec python3 -m uvicorn services.api.app.main:app --host "$HOST" --port "$PORT" --reload
