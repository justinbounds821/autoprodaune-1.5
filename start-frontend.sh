#!/usr/bin/env bash
set -euo pipefail

# Start React frontend (Vite) for AutoPro Daune
# Usage: ./start-frontend.sh

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
FE_DIR="$ROOT_DIR/02_FRONTEND_UI_CLEAN"

if [ ! -f "$ROOT_DIR/.env" ] && [ -f "$ROOT_DIR/env.example" ]; then
  echo "ℹ️  Using env.example to seed .env at repo root (edit if needed)"
  cp "$ROOT_DIR/env.example" "$ROOT_DIR/.env"
fi

pushd "$FE_DIR" >/dev/null

if [ -f package-lock.json ]; then
  echo "✅ Installing frontend dependencies (npm ci if lock present)"
  npm ci || npm install
else
  echo "✅ Installing frontend dependencies"
  npm install
fi

# Ensure vite points to backend on 8001 (already proxied in vite.config.ts)
export VITE_API_URL=${VITE_API_URL:-http://127.0.0.1:8001}
export VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://127.0.0.1:8001}
export VITE_ENV=${VITE_ENV:-development}

exec npm run dev
