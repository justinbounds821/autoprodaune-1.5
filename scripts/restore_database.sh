#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL must be set}"
BACKUP_FILE=${1:?Usage: restore_database.sh <backup_file>}

echo "[restore] Restoring database from $BACKUP_FILE"
pg_restore --clean --if-exists --no-owner --dbname="$DATABASE_URL" "$BACKUP_FILE"

echo "[restore] Completed"
