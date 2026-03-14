# woozy-dev-infra — Full Workflow Guide

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
│  │                                 │  │ homepage  │  │    │
│  │  docker CLI ─────────────────►  │  │  :3000    │  │    │
│  │         (DooD via socket)       │  ├───────────┤  │    │
│  │                                 │  │ netdata   │  │    │
│  │                                 │  │  :19999   │  │    │
│  │                                 │  ├───────────┤  │    │
│  │                                 │  │ dozzle    │  │    │
│  │                                 │  │  :9999    │  │    │
│  │                                 │  ├───────────┤  │    │
│  │                                 │  │uptime-kuma│  │    │
│  │                                 │  │  :3001    │  │    │
│  │                                 │  ├───────────┤  │    │
│  │                                 │  │watchtower │  │    │
│  └─────────────────────────────────┴───────────────┘  │    │
└──────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# On the host
git clone <repo-url> woozy-dev-infra
cd woozy-dev-infra
sudo ./install.sh

# From your Mac
ssh -p 2222 root@<host-ip>
```

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

## Monitoring Endpoints

| Service | URL | Notes |
|---------|-----|-------|
| Homepage | http://HOST:3000 | Dashboard — configure widgets in the homepage volume |
| Netdata | http://HOST:19999 | Real-time system metrics |
| Dozzle | http://HOST:9999 | Container log viewer |
| Uptime Kuma | http://HOST:3001 | Needs initial setup via web UI on first visit |

## Database

```bash
# From inside dev-box
psql -h localhost -p 5432 -U devuser -d devdb

# From host
psql -h localhost -p 5432 -U devuser -d devdb
```

Credentials are in `.env`. TimescaleDB extensions are available for time-series workloads.

## Makefile Reference

| Command | Description |
|---------|-------------|
| `make up` | Start all 7 services |
| `make down` | Stop all services |
| `make up-devbox` | Start dev-box only |
| `make up-database` | Start TimescaleDB only |
| `make up-monitoring` | Start homepage, netdata, watchtower, dozzle, uptime-kuma |
| `make ps` | Show container status |
| `make logs` | Recent logs from all containers |
| `make logs-devbox` | Follow dev-box logs |
| `make logs-timescaledb` | Follow TimescaleDB logs |
| `make health` | Run full health check |
| `make backup-db` | Manual database backup |

## Backups

- **Automatic**: cron runs `backup-db.sh` daily at 3 AM
- **Manual**: `make backup-db`
- **Location**: `$BACKUP_DIR` (default `/home/docker/backups`)
- **Retention**: 7 days (older backups auto-deleted)
- **Format**: `pg_dump -Fc` + gzip (restore with `pg_restore`)
