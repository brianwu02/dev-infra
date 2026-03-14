# dev-infra

Reproducible dev environment: a Docker-outside-of-Docker (DooD) dev container with database, caching, object storage, email catching, reverse proxy, and monitoring. One command to install on any Ubuntu/Debian host.

## Quick Start

**Prerequisites:** A running Ubuntu/Debian machine with root access. This guide does not cover provisioning or setting up the host itself — just what runs on top of it.

```bash
# 1. Generate an SSH key if you don't have one
[ -f ~/.ssh/id_ed25519 ] || ssh-keygen -t ed25519

# 2. Copy your key to the host
ssh-copy-id root@<host-ip>

# 3. Install on the host
ssh root@<host-ip>
git clone https://github.com/brianwu02/dev-infra.git
cd dev-infra
sudo ./install.sh

# 4. SSH into the dev-box
ssh -p 2222 root@<host-ip>
```

> **Note:** The dev-box only accepts SSH key auth (no passwords). The installer copies keys from the host's `~/.ssh/authorized_keys` into the dev-box automatically. If you can SSH into the host, you can SSH into the dev-box.
>
> If `ssh-copy-id` fails (host has password auth disabled), manually append your key:
> ```bash
> cat ~/.ssh/id_ed25519.pub | ssh root@<host-ip> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
> ```

## Try It

The included example app proves the full stack works end-to-end — a FastAPI server with an HTML page that increments a hit counter stored in TimescaleDB.

```bash
# 1. Start the infrastructure (DB must be healthy first)
make up-database

# 2. Build and start the example app
make up-example

# 3. Open in your browser
open http://localhost:8000
```

You'll see a counter with **Hit** and **Reset** buttons. Every click writes to TimescaleDB — the count persists across container restarts.

There's also a JSON API if you prefer curl:

```bash
curl http://localhost:8000/api              # read counter
curl -X POST http://localhost:8000/api/hit   # increment
curl -X POST http://localhost:8000/api/reset # reset to zero
```

When you're done: `make down-example`

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

Services are also available via `*.localhost`:

| Route | Service |
|-------|---------|
| `hello.localhost` | Example app |
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

## Makefile

| Command | Description |
|---------|-------------|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make up-devbox` | Start dev-box only |
| `make up-database` | Start TimescaleDB + Redis |
| `make up-monitoring` | Start homepage, watchtower, dozzle, uptime-kuma |
| `make up-services` | Start traefik, minio, mailpit, adminer |
| `make up-example` | Build & start the example hello world app |
| `make down-example` | Stop the example app |
| `make ps` | Show container status |
| `make logs` | Recent logs from all containers |
| `make health` | Run full health check |
| `make backup-db` | Manual database backup |

---

## Usage

### Mac Client Setup

#### SSH aliases (~/.zshrc on Mac)

```bash
# Add these to your Mac's ~/.zshrc
HOST_IP="192.168.1.200"  # Change to your host IP

alias t1="ssh -t -p 2222 root@$HOST_IP 'tmux new-session -As s1'"
alias t2="ssh -t -p 2222 root@$HOST_IP 'tmux new-session -As s2'"
alias t3="ssh -t -p 2222 root@$HOST_IP 'tmux new-session -As s3'"
alias t4="ssh -t -p 2222 root@$HOST_IP 'tmux new-session -As s4'"
alias t5="ssh -t -p 2222 root@$HOST_IP 'tmux new-session -As s5'"
```

#### iTerm2 multi-pane workflow

1. Open iTerm2
2. `⌘+D` to split vertically, `⌘+Shift+D` to split horizontally
3. Run `t1` in the first pane, `t2` in the second, etc.
4. `⌘+Option+←/→` to switch between panes
5. `⌘+Shift+Enter` to zoom/unzoom a pane
6. Disconnecting and re-running `t1`/`t2`/etc. reattaches to existing tmux sessions

### Git Worktree Workflow

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

### AI CLI Tools

#### Claude Code

```bash
claude                    # Interactive mode
claude "explain this code" < file.py   # Pipe input
claude --help             # Full options
```

#### Gemini CLI

```bash
gemini                    # Interactive mode
gemini --help             # Full options
```

Both are pre-installed in the dev-box. First run will prompt for API key configuration.

### VS Code Tunnel

Run inside dev-box to get VS Code access from any browser:

```bash
code tunnel
```

Follow the auth prompts. Then connect via `vscode.dev` or the VS Code desktop app using the Remote Tunnels extension.

### Database

```bash
# From inside dev-box or host
psql -h localhost -p 5432 -U devuser -d devdb

# Or use the Adminer GUI
open http://localhost:8081
```

Credentials are in `.env`. TimescaleDB extensions are available for time-series workloads.

### Redis

```bash
redis-cli -h localhost -p 6379
```

Pre-configured with 128MB max memory and LRU eviction. Ready for caching, job queues (Celery/BullMQ), sessions, and rate limiting.

### Object Storage (MinIO)

S3-compatible API on port 9000, web console on port 9001. Use the same `boto3` / `@aws-sdk/client-s3` code you'd use with AWS S3.

```bash
# Console
open http://localhost:9001  # login: minioadmin / minioadmin

# Example: Python
import boto3
s3 = boto3.client('s3', endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin', aws_secret_access_key='minioadmin')
```

### Email (Mailpit)

SMTP server on port 1025, web UI on port 8025. Point your app's email config at `localhost:1025` and all outgoing mail lands in the Mailpit inbox.

```bash
# Web UI
open http://localhost:8025

# Example: Python
import smtplib
with smtplib.SMTP('localhost', 1025) as smtp:
    smtp.sendmail('test@app.dev', 'user@example.com', 'Subject: Test\n\nHello')
```

### Backups

- **Automatic**: cron runs `backup-db.sh` daily at 3 AM
- **Manual**: `make backup-db`
- **Location**: `$BACKUP_DIR` (default `/home/docker/backups`)
- **Retention**: 7 days (older backups auto-deleted)
- **Format**: `pg_dump -Fc` + gzip (restore with `pg_restore`)

---

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
