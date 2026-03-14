# dev-infra

Reproducible dev environment: DooD (Docker-outside-of-Docker) dev container with database, caching, object storage, email catching, reverse proxy, and monitoring. One command to install on any Ubuntu/Debian host.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Mac (Client)                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │ iTerm2 split panes                               │   │
│  │  t1 ──┐  t2 ──┐  t3 ──┐  t4 ──┐  t5 ──┐       │   │
│  │       │       │       │       │       │        │   │
│  └───────┼───────┼───────┼───────┼───────┼────────┘   │
│          │ SSH   │ SSH   │ SSH   │ SSH   │ SSH        │
└──────────┼───────┼───────┼───────┼───────┼────────────┘
           ▼       ▼       ▼       ▼       ▼
┌──────────────────────────────────────────────────────────┐
│  Host (Ubuntu/Debian)          docker.sock               │
│  ┌─────────────────────────────────┬────────────────┐    │
│  │ dev-box (host network, :2222)   │ Docker Engine   │    │
│  │  tmux sessions (s1–s5)          │                 │    │
│  │  zsh + oh-my-zsh                │  ┌───────────┐  │    │
│  │  claude / gemini CLI            │  │timescaledb │  │    │
│  │  git worktrees                  │  │  :5432     │  │    │
│  │  VS Code tunnel                 │  ├───────────┤  │    │
│  │                                 │  │  redis    │  │    │
│  │  docker CLI ─────────────────►  │  │  :6379    │  │    │
│  │         (DooD via socket)       │  ├───────────┤  │    │
│  │                                 │  │  minio    │  │    │
│  │                                 │  │  :9000/01 │  │    │
│  │                                 │  ├───────────┤  │    │
│  │                                 │  │ traefik   │  │    │
│  │                                 │  │  :80/8080 │  │    │
│  │                                 │  ├───────────┤  │    │
│  │                                 │  │ mailpit   │  │    │
│  │                                 │  │  :8025    │  │    │
│  │                                 │  ├───────────┤  │    │
│  │                                 │  │ homepage  │  │    │
│  │                                 │  │  :3000    │  │    │
│  │                                 │  ├───────────┤  │    │
│  │                                 │  │ dozzle    │  │    │
│  │                                 │  │  :9999    │  │    │
│  │                                 │  ├───────────┤  │    │
│  │                                 │  │uptime-kuma│  │    │
│  │                                 │  │  :3001    │  │    │
│  └─────────────────────────────────┴───────────────┘  │    │
└──────────────────────────────────────────────────────────┘
```

### Why DooD (Docker-outside-of-Docker)?

The dev-box container runs Docker commands by mounting the host's `/var/run/docker.sock`. This means containers launched from inside dev-box are **siblings** on the host, not nested children.

| | DooD (this setup) | DinD (docker-in-docker) |
|-|---|---|
| **Performance** | Native — no nested overhead | Extra layer of virtualization |
| **Port access** | `localhost` just works — dev-box uses host networking | Containers live in a nested network, need extra port mapping |
| **Volume mounts** | Paths must be host paths (not dev-box paths) | Paths are relative to the inner daemon |
| **Image cache** | Shared with host — pull once, use everywhere | Separate cache per DinD instance |
| **Security** | Socket access = root on host (fine for a personal dev box) | More isolated but slower and more complex |
| **Compose/Swarm** | Full access to host Docker engine | Needs privileged mode, still can't manage host containers |

**TL;DR**: DooD is simpler and faster for a single-dev setup where you trust the environment. DinD is better when you need full isolation (CI runners, multi-tenant). Since this is your personal dev box, DooD is the right call.

One gotcha: when you `docker run -v /some/path:/data` from inside dev-box, `/some/path` must exist **on the host**, not inside the container. The host filesystem is mounted at `/host_root/` for reference.

## Quick Start

```bash
# On the host
git clone https://github.com/brianwu02/dev-infra.git
cd dev-infra
sudo ./install.sh

# From your Mac
ssh -p 2222 root@<host-ip>
```

## What You Get

| Service | Port | Purpose |
|---------|------|---------|
| dev-box | 2222 (SSH) | Ubuntu dev container — zsh, tmux, Node, Python, Java, Claude CLI, Gemini CLI |
| Traefik | 80 / 8080 | Reverse proxy + dashboard (`*.localhost` routing) |
| TimescaleDB | 5432 | PostgreSQL + TimescaleDB |
| Redis | 6379 | Cache, queues, rate limiting |
| MinIO | 9000 / 9001 | S3-compatible object storage + console |
| Mailpit | 8025 / 1025 | Email catcher (SMTP on 1025, web UI on 8025) |
| Adminer | 8081 | Database GUI (pre-configured for TimescaleDB) |
| Homepage | 3000 | Dashboard |
| Dozzle | 9999 | Container log viewer |
| Uptime Kuma | 3001 | Uptime monitoring |
| Watchtower | — | Auto-pulls image updates daily at 4 AM |

### Traefik Routes

When accessing from the host machine, services are also available via `*.localhost`:

| Route | Service |
|-------|---------|
| `home.localhost` | Homepage |
| `logs.localhost` | Dozzle |
| `status.localhost` | Uptime Kuma |
| `db.localhost` | Adminer |
| `mail.localhost` | Mailpit |
| `minio.localhost` | MinIO Console |

## Configuration

Copy `.env.example` to `.env` and edit (or let `install.sh` generate it):

- `PROJECTS_DIR` — host directory mounted as `/workspace` in dev-box
- `BACKUP_DIR` — where database backups land
- `DB_USER` / `DB_PASSWORD` / `DB_NAME` — TimescaleDB credentials
- `MINIO_USER` / `MINIO_PASSWORD` — MinIO credentials
- All ports are configurable — see `.env.example` for the full list
- `TZ` — timezone

## Mac Client Setup

### SSH aliases (~/.zshrc on Mac)

```bash
# Add these to your Mac's ~/.zshrc
HOST_IP="192.168.1.200"  # Change to your host IP

alias t1="ssh -t -p 2222 root@$HOST_IP 'tmux new-session -As s1'"
alias t2="ssh -t -p 2222 root@$HOST_IP 'tmux new-session -As s2'"
alias t3="ssh -t -p 2222 root@$HOST_IP 'tmux new-session -As s3'"
alias t4="ssh -t -p 2222 root@$HOST_IP 'tmux new-session -As s4'"
alias t5="ssh -t -p 2222 root@$HOST_IP 'tmux new-session -As s5'"
```

### iTerm2 multi-pane workflow

1. Open iTerm2
2. `⌘+D` to split vertically, `⌘+Shift+D` to split horizontally
3. Run `t1` in the first pane, `t2` in the second, etc.
4. `⌘+Option+←/→` to switch between panes
5. `⌘+Shift+Enter` to zoom/unzoom a pane
6. Disconnecting and re-running `t1`/`t2`/etc. reattaches to existing tmux sessions

## Git Worktree Workflow

The shell includes three helpers for working with git worktrees:

```bash
# Create a worktree for a task (creates branch "task1" if needed)
wt myproject task1
# → creates /workspace/myproject-task1 and cd's into it

# List worktrees for a project
wtl myproject

# Remove a worktree when done
wtr myproject task1
```

This lets you work on multiple branches simultaneously in different tmux sessions without stashing.

## AI CLI Tools

### Claude Code

```bash
claude                    # Interactive mode
claude "explain this code" < file.py   # Pipe input
claude --help             # Full options
```

### Gemini CLI

```bash
gemini                    # Interactive mode
gemini --help             # Full options
```

Both are pre-installed in the dev-box. First run will prompt for API key configuration.

## VS Code Tunnel

Run inside dev-box to get VS Code access from any browser:

```bash
code tunnel
```

Follow the auth prompts. Then connect via `vscode.dev` or the VS Code desktop app using the Remote Tunnels extension.

## Database

```bash
# From inside dev-box or host
psql -h localhost -p 5432 -U devuser -d devdb

# Or use the Adminer GUI
open http://localhost:8081
```

Credentials are in `.env`. TimescaleDB extensions are available for time-series workloads.

## Redis

```bash
redis-cli -h localhost -p 6379
```

Pre-configured with 128MB max memory and LRU eviction. Ready for caching, job queues (Celery/BullMQ), sessions, and rate limiting.

## Object Storage (MinIO)

S3-compatible API on port 9000, web console on port 9001. Use the same `boto3` / `@aws-sdk/client-s3` code you'd use with AWS S3.

```bash
# Console
open http://localhost:9001  # login: minioadmin / minioadmin

# Example: Python
import boto3
s3 = boto3.client('s3', endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin', aws_secret_access_key='minioadmin')
```

## Email (Mailpit)

SMTP server on port 1025, web UI on port 8025. Point your app's email config at `localhost:1025` and all outgoing mail lands in the Mailpit inbox.

```bash
# Web UI
open http://localhost:8025

# Example: Python
import smtplib
with smtplib.SMTP('localhost', 1025) as smtp:
    smtp.sendmail('test@app.dev', 'user@example.com', 'Subject: Test\n\nHello')
```

## Makefile

| Command | Description |
|---------|-------------|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make up-devbox` | Start dev-box only |
| `make up-database` | Start TimescaleDB + Redis |
| `make up-monitoring` | Start homepage, watchtower, dozzle, uptime-kuma |
| `make up-services` | Start traefik, minio, mailpit, adminer |
| `make ps` | Show container status |
| `make logs` | Recent logs from all containers |
| `make health` | Run full health check |
| `make backup-db` | Manual database backup |

## Backups

- **Automatic**: cron runs `backup-db.sh` daily at 3 AM
- **Manual**: `make backup-db`
- **Location**: `$BACKUP_DIR` (default `/home/docker/backups`)
- **Retention**: 7 days (older backups auto-deleted)
- **Format**: `pg_dump -Fc` + gzip (restore with `pg_restore`)
