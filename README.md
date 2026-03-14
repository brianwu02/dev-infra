# dev-infra

An AI-first development environment for solo developers. Run multiple AI coding agents (Claude, Gemini) in parallel across tmux sessions, with all the infrastructure you need to ship — database, cache, object storage, email, reverse proxy, and monitoring. One `./install.sh` on any Ubuntu/Debian host.

## Prerequisites

- A running **Ubuntu/Debian machine** with root access. This repo does not cover provisioning or setting up the host itself.
- An **SSH key** on your local machine (Mac/Linux).

## 1. Install

```bash
# Generate an SSH key if you don't have one
[ -f ~/.ssh/id_ed25519 ] || ssh-keygen -t ed25519

# Copy your key to the host
ssh-copy-id root@<host-ip>

# Install on the host
ssh root@<host-ip>
git clone https://github.com/brianwu02/dev-infra.git
cd dev-infra
sudo ./install.sh
```

> If `ssh-copy-id` fails (host has password auth disabled), manually append your key:
> ```bash
> cat ~/.ssh/id_ed25519.pub | ssh root@<host-ip> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
> ```

The installer will: install Docker if needed, generate a `.env` with a random DB password, copy your SSH keys into the dev-box, and start all services.

## 2. Connect

The dev-box is your development environment. The host just runs Docker — you don't work on it directly.

### Terminal (SSH)

```bash
ssh -p 2222 root@<host-ip>
```

The dev-box only accepts SSH key auth (no passwords). The installer copies keys from the host's `~/.ssh/authorized_keys` automatically — if you can SSH into the host, you can SSH into the dev-box.

### VS Code

**Option A: Remote SSH** (recommended)

1. Install the [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) extension
2. Add to `~/.ssh/config` on your Mac:
   ```
   Host devbox
     HostName <host-ip>
     Port 2222
     User root
   ```
3. `Cmd+Shift+P` → "Remote-SSH: Connect to Host" → select `devbox`
4. Open `/workspace` as your folder

**Option B: VS Code Tunnel** (works from any browser, no SSH config needed)

```bash
# Inside the dev-box
code tunnel
```

Follow the GitHub auth prompts. Then connect via `vscode.dev` or the VS Code desktop app using the [Remote Tunnels](https://marketplace.visualstudio.com/items?itemName=ms-vscode.remote-server) extension.

### Remote Access (Tailscale)

Want to code from a coffee shop? [Tailscale](https://tailscale.com/) creates a private WireGuard mesh network so your Mac can reach your dev box from anywhere — no port forwarding, no exposing SSH to the internet.

```bash
# On the host
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# On your Mac
brew install tailscale
# Open Tailscale app, sign in with the same account
```

Once both devices are on your tailnet, use the Tailscale IP instead of your LAN IP:

```bash
ssh -p 2222 root@<tailscale-ip>
```

Update your `~/.ssh/config` accordingly:

```
Host devbox
  HostName <tailscale-ip>   # e.g. 100.x.y.z
  Port 2222
  User root
```

All services (Adminer, Mailpit, MinIO console, etc.) are accessible at `http://<tailscale-ip>:<port>` — same as on your home network, but encrypted and works from anywhere. Free for personal use.

## 3. Verify

Once connected to the dev-box, verify the full stack works with the included example app — a FastAPI server with an HTML page that increments a hit counter stored in TimescaleDB.

```bash
# Start TimescaleDB and the example app
cd /workspace/.dev-infra
docker compose up -d timescaledb obviously-the-best-hello-world-app

# Open in your browser (use your host's IP)
# http://<host-ip>:8000
```

You'll see a counter with **Hit** and **Reset** buttons. Every click writes to TimescaleDB — the count persists across container restarts.

There's also a JSON API:

```bash
curl http://localhost:8000/api              # read counter
curl -X POST http://localhost:8000/api/hit   # increment
curl -X POST http://localhost:8000/api/reset # reset to zero
```

When you're done:

```bash
docker compose stop obviously-the-best-hello-world-app
```

## 4. Start Building

All your projects live in `/workspace`. Clone repos here — this is your working directory.

```bash
cd /workspace
git clone <your-repo>
cd your-project
```

> **Path mapping:** `/workspace/myproject` inside the dev-box is actually `/home/docker/projects/myproject` on the host. When mounting volumes in docker commands from inside the dev-box, use host paths. The host filesystem is available at `/host_root/` for reference.

## 5. Workflows

The multi-terminal workflow is inspired by [Boris Cherny's AI terminal setup](https://youtu.be/julbw1JuAz0?si=Evag9oEPUgDUOWiK&t=2017), where he describes running multiple AI agents in parallel across tmux sessions.

### Multi-Terminal (tmux + SSH aliases)

Add to `~/.zshrc` on your Mac:

```bash
HOST_IP="<host-ip>"  # Change to your host IP (or Tailscale IP)

# Each alias SSHs into the dev-box and attaches to a named tmux session.
# If the session doesn't exist, it creates one. If it does, it reattaches.
# This means you can disconnect (close the terminal, lose wifi, etc.)
# and pick up exactly where you left off by running the same alias.
# Run t1-t5 in separate iTerm2 panes for parallel AI agent sessions.
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

### Git Worktrees

The shell includes three helpers for working on multiple branches simultaneously:

```bash
wt myproject task1     # create worktree + branch, cd into it
wtl myproject          # list worktrees
wtr myproject task1    # remove worktree
```

### AI CLI Tools

Both are pre-installed in the dev-box. First run will prompt for API key configuration.

```bash
claude                    # Claude Code interactive mode
claude "explain this" < file.py

gemini                    # Gemini CLI interactive mode
```

---

## Reference

### What's Included

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

### Database (TimescaleDB)

```bash
psql -h localhost -p 5432 -U devuser -d devdb

# Or use the Adminer GUI
open http://<host-ip>:8081
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
open http://<host-ip>:9001  # login: minioadmin / minioadmin

# Example: Python
import boto3
s3 = boto3.client('s3', endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin', aws_secret_access_key='minioadmin')
```

### Email (Mailpit)

SMTP server on port 1025, web UI on port 8025. Point your app's email config at `localhost:1025` and all outgoing mail lands in the Mailpit inbox.

```bash
# Web UI
open http://<host-ip>:8025

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

### Configuration

Copy `.env.example` to `.env` and edit (or let `install.sh` generate it):

- `PROJECTS_DIR` — host directory mounted as `/workspace` in dev-box
- `BACKUP_DIR` — where database backups land
- `DB_USER` / `DB_PASSWORD` / `DB_NAME` — TimescaleDB credentials
- `MINIO_USER` / `MINIO_PASSWORD` — MinIO credentials
- All ports are configurable — see `.env.example` for the full list
- `TZ` — timezone

### Makefile

Run from `/workspace/.dev-infra`:

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
