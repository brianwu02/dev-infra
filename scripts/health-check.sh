#!/usr/bin/env bash
# health-check.sh — Quick health check of the dev infrastructure
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}OK${NC}    $1"; }
warn() { echo -e "  ${YELLOW}WARN${NC}  $1"; }
fail() { echo -e "  ${RED}FAIL${NC}  $1"; }

echo "=== Container Health ==="
EXPECTED="dev-box timescaledb homepage netdata watchtower dozzle uptime-kuma"
for c in $EXPECTED; do
    status=$(docker inspect -f '{{.State.Status}}' "$c" 2>/dev/null || echo "missing")
    if [ "$status" = "running" ]; then
        ok "$c"
    elif [ "$status" = "missing" ]; then
        fail "$c (not found)"
    else
        warn "$c ($status)"
    fi
done

echo ""
echo "=== Disk Usage ==="
df -h / 2>/dev/null | tail -n +2 | while read -r line; do
    pct=$(echo "$line" | awk '{print $5}' | tr -d '%')
    mp=$(echo "$line" | awk '{print $6}')
    if [ "$pct" -gt 90 ]; then
        fail "$mp at ${pct}%"
    elif [ "$pct" -gt 80 ]; then
        warn "$mp at ${pct}%"
    else
        ok "$mp at ${pct}%"
    fi
done

echo ""
echo "=== Memory ==="
mem_pct=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')
swap_pct=$(free | awk '/Swap:/ {if ($2 > 0) printf "%.0f", $3/$2 * 100; else print "0"}')
if [ "$mem_pct" -gt 90 ]; then fail "RAM at ${mem_pct}%"; elif [ "$mem_pct" -gt 80 ]; then warn "RAM at ${mem_pct}%"; else ok "RAM at ${mem_pct}%"; fi
if [ "$swap_pct" -gt 50 ]; then warn "Swap at ${swap_pct}%"; else ok "Swap at ${swap_pct}%"; fi

echo ""
echo "=== Network Services ==="
check_url() {
    local name=$1 url=$2
    if curl -sk -o /dev/null -w '' --connect-timeout 3 "$url" 2>/dev/null; then
        ok "$name"
    else
        fail "$name ($url)"
    fi
}
check_url "Homepage"    "http://localhost:3000"
check_url "Netdata"     "http://localhost:19999"
check_url "Dozzle"      "http://localhost:9999"
check_url "Uptime Kuma" "http://localhost:3001"

echo ""
echo "=== Database ==="
DB_CONTAINER="${DB_CONTAINER:-timescaledb}"
if docker exec "$DB_CONTAINER" pg_isready -U "${DB_USER:-devuser}" -q 2>/dev/null; then
    ok "TimescaleDB accepting connections"
else
    fail "TimescaleDB not ready"
fi

echo ""
echo "=== Recent Backups ==="
BACKUP_DIR="${BACKUP_DIR:-/home/docker/backups}"
if ls "$BACKUP_DIR"/*.dump.gz 1>/dev/null 2>&1; then
    latest=$(ls -t "$BACKUP_DIR"/*.dump.gz | head -1)
    age=$(( ($(date +%s) - $(stat -c %Y "$latest")) / 3600 ))
    if [ "$age" -gt 48 ]; then
        fail "Latest backup is ${age}h old: $(basename "$latest")"
    elif [ "$age" -gt 24 ]; then
        warn "Latest backup is ${age}h old: $(basename "$latest")"
    else
        ok "Latest backup is ${age}h old: $(basename "$latest")"
    fi
else
    warn "No backups found in $BACKUP_DIR"
fi
