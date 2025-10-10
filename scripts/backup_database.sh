#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL must be set, e.g. postgresql://user:pass@host:5432/db}" 
BACKUP_DIR=${1:-backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

BACKUP_FILE="$BACKUP_DIR/autoprodaune_${TIMESTAMP}.sql"

echo "[backup] Creating database dump at $BACKUP_FILE"
pg_dump --file="$BACKUP_FILE" --format=custom "$DATABASE_URL"

echo "[backup] Done"
