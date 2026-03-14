# woozy-dev-infra

Reproducible dev environment: DooD (Docker-outside-of-Docker) dev container with monitoring, database, and AI CLI tools. One command to install on any Ubuntu/Debian host.

## Quick Start

```bash
git clone <repo-url> woozy-dev-infra
cd woozy-dev-infra
sudo ./install.sh
```

Then SSH in:
```bash
ssh -p 2222 root@<host-ip>
```

## What You Get

| Service | Port | Purpose |
|---------|------|---------|
| dev-box | 2222 (SSH) | Ubuntu dev container — zsh, tmux, Node, Python, Java, Claude CLI, Gemini CLI |
| TimescaleDB | 5432 | PostgreSQL + TimescaleDB |
| Homepage | 3000 | Dashboard |
| Netdata | 19999 | System monitoring |
| Dozzle | 9999 | Container log viewer |
| Uptime Kuma | 3001 | Uptime monitoring |
| Watchtower | — | Image update monitor (no auto-pull) |

## Makefile

```bash
make up              # Start all services
make down            # Stop all services
make up-devbox       # Start dev-box only
make up-monitoring   # Start monitoring stack only
make up-database     # Start TimescaleDB only
make ps              # Container status
make logs            # Recent logs from all containers
make logs-devbox     # Follow dev-box logs
make health          # Full health check
make backup-db       # Manual database backup
```

## Configuration

Copy `.env.example` to `.env` and edit (or let `install.sh` generate it):

- `PROJECTS_DIR` — host directory mounted as `/workspace` in dev-box
- `BACKUP_DIR` — where database backups land
- `DB_USER` / `DB_PASSWORD` / `DB_NAME` — TimescaleDB credentials
- `TZ` — timezone

See [GUIDE.md](GUIDE.md) for the full workflow documentation.
