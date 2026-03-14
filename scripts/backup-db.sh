#!/usr/bin/env bash
# backup-db.sh — pg_dump PostgreSQL to backup dir with 7-day retention
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/home/docker/backups}"
DB_USER="${DB_USER:-devuser}"
DB_NAME="${DB_NAME:-devdb}"
DATE=$(date +%Y-%m-%d_%H%M)
RETAIN_DAYS=7

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

mkdir -p "$BACKUP_DIR"

log "Backing up ${DB_NAME}..."
DB_CONTAINER="${DB_CONTAINER:-postgres}"
if docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -Fc "$DB_NAME" \
    | gzip > "$BACKUP_DIR/${DB_NAME}_${DATE}.dump.gz"; then
    log "Backup OK: ${DB_NAME}_${DATE}.dump.gz"
else
    log "ERROR: Backup failed"
    exit 1
fi

log "Cleaning up backups older than ${RETAIN_DAYS} days..."
find "$BACKUP_DIR" -name "*.dump.gz" -mtime +${RETAIN_DAYS} -delete

log "Done. Current backups:"
ls -lh "$BACKUP_DIR"/*.dump.gz 2>/dev/null || log "No backup files found"
