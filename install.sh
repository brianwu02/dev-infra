#!/usr/bin/env bash
# install.sh — One-command installer for the dev-infra environment
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[dev-infra]${NC} $*"; }
warn() { echo -e "${YELLOW}[dev-infra]${NC} $*"; }
err()  { echo -e "${RED}[dev-infra]${NC} $*" >&2; exit 1; }

# --- Require root ---
[ "$(id -u)" -eq 0 ] || err "Please run as root: sudo ./install.sh"

# --- Detect OS ---
if [ -f /etc/os-release ]; then
    . /etc/os-release
    case "$ID" in
        ubuntu|debian) log "Detected $PRETTY_NAME" ;;
        *) warn "Untested OS: $PRETTY_NAME — proceeding anyway" ;;
    esac
else
    warn "Cannot detect OS — proceeding anyway"
fi

# --- Install Docker if missing ---
if ! command -v docker &>/dev/null; then
    log "Installing Docker..."
    curl -fsSL https://get.docker.com | bash
    systemctl enable --now docker
    log "Docker installed"
else
    log "Docker already installed: $(docker --version)"
fi

# --- Ensure Compose plugin ---
if ! docker compose version &>/dev/null; then
    log "Installing Docker Compose plugin..."
    apt-get update && apt-get install -y docker-compose-plugin
fi
log "Docker Compose: $(docker compose version --short)"

# --- Directories ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECTS_DIR="${PROJECTS_DIR:-/home/docker/projects}"
BACKUP_DIR="${BACKUP_DIR:-/home/docker/backups}"
INSTALL_DIR="$PROJECTS_DIR/.dev-infra"

mkdir -p "$PROJECTS_DIR" "$BACKUP_DIR"
log "Projects dir: $PROJECTS_DIR"
log "Backup dir:   $BACKUP_DIR"

# --- Copy repo into place ---
if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    log "Copying files to $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
    cp -a "$SCRIPT_DIR"/* "$INSTALL_DIR"/
    cp -a "$SCRIPT_DIR"/.env.example "$INSTALL_DIR"/ 2>/dev/null || true
fi

# --- Generate .env ---
ENV_FILE="$INSTALL_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    DB_PASSWORD=$(openssl rand -base64 18 | tr -d '/+=')
    log "Generating .env with random DB password..."
    sed "s/DB_PASSWORD=CHANGEME/DB_PASSWORD=$DB_PASSWORD/" \
        "$INSTALL_DIR/.env.example" > "$ENV_FILE"
    sed -i "s|PROJECTS_DIR=.*|PROJECTS_DIR=$PROJECTS_DIR|" "$ENV_FILE"
    sed -i "s|BACKUP_DIR=.*|BACKUP_DIR=$BACKUP_DIR|" "$ENV_FILE"
    log "Generated $ENV_FILE"
else
    log ".env already exists, skipping"
fi

# --- SSH key ---
SSH_KEY=""
if [ -f /root/.ssh/authorized_keys ] && [ -s /root/.ssh/authorized_keys ]; then
    SSH_KEY=$(head -1 /root/.ssh/authorized_keys)
    log "Found SSH key from host authorized_keys"
fi

if [ -z "$SSH_KEY" ]; then
    echo ""
    warn "No SSH key found. Paste your public key (or press Enter to skip):"
    read -r SSH_KEY
fi

if [ -n "$SSH_KEY" ]; then
    mkdir -p /root/.ssh
    echo "$SSH_KEY" >> /root/.ssh/authorized_keys
    sort -u -o /root/.ssh/authorized_keys /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
    log "SSH key configured"
fi

# --- Make scripts executable ---
chmod +x "$INSTALL_DIR/init_devbox.sh"
chmod +x "$INSTALL_DIR/scripts/"*.sh

# --- Install backup cron ---
CRON_CMD="0 3 * * * cd $INSTALL_DIR && /usr/bin/bash scripts/backup-db.sh >> /var/log/dev-infra-backup.log 2>&1"
if ! crontab -l 2>/dev/null | grep -qF "dev-infra-backup"; then
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    log "Installed backup cron (3 AM daily)"
else
    log "Backup cron already installed"
fi

# --- Start everything ---
log "Starting all services..."
cd "$INSTALL_DIR"
docker compose --env-file "$ENV_FILE" up -d

# --- Wait for healthy containers ---
log "Waiting for containers to be ready..."
TIMEOUT=120
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if docker inspect --format='{{.State.Health.Status}}' timescaledb 2>/dev/null | grep -q healthy; then
        break
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
    warn "TimescaleDB did not become healthy within ${TIMEOUT}s — check logs"
else
    log "TimescaleDB is healthy"
fi

# --- Print summary ---
echo ""
echo "========================================"
echo "  dev-infra environment is ready!"
echo "========================================"
echo ""
echo "  SSH into dev-box:    ssh -p 2222 root@localhost"
echo "  Homepage:            http://localhost:3000"
echo "  Netdata:             http://localhost:19999"
echo "  Dozzle:              http://localhost:9999"
echo "  Uptime Kuma:         http://localhost:3001"
echo "  TimescaleDB:         psql -h localhost -p 5432 -U devuser -d devdb"
echo ""
echo "  Makefile commands:   cd $INSTALL_DIR && make help"
echo "  Health check:        make health"
echo ""
log "Done!"
