---
name: docker-patterns
description: Docker and DooD patterns — compose commands, container management, networking, volumes, and troubleshooting.
user-invokable: false
---

# Docker Patterns

## DooD (Docker-outside-of-Docker)

The dev-box container mounts the host's Docker socket. Commands inside dev-box manage **sibling containers** on the host, not nested containers.

```
Host Docker Engine
├── dev-box (you are here, via SSH)
│   └── /var/run/docker.sock → host socket
├── timescaledb (sibling)
├── frontend (sibling)
└── backend (sibling)
```

### Key Implications
- `docker ps` inside dev-box shows **all host containers**
- `docker compose up` starts containers on the **host**, not inside dev-box
- Volume paths in compose files are **host paths**, not dev-box paths
- Network `host` mode shares the host's network stack

## Common Commands

```bash
# Start all services
docker compose up -d

# Rebuild and restart one service
docker compose build backend && docker compose up -d backend

# View logs
docker compose logs -f backend
docker compose logs --tail 50 frontend

# Shell into a running container
docker exec -it timescaledb psql -U devuser -d devdb

# Restart without recreating (preserves data)
docker restart timescaledb

# Check resource usage
docker stats --no-stream
```

## Networking

```bash
# List networks
docker network ls

# Inspect a network (see connected containers)
docker network inspect myproject_default

# Containers on the same compose network can reach each other by service name
# e.g., backend can connect to "timescaledb:5432"
```

## Volumes

```bash
# Named volumes (managed by Docker, portable)
docker volume ls
docker volume inspect myproject_timescaledb-data

# Bind mounts (host dir → container dir)
# Defined in docker-compose.yml volumes section
```

### When to Use What
- **Named volumes**: Database data, tool configs, caches (portable, Docker-managed)
- **Bind mounts**: Source code, project files (need host access)

## Troubleshooting

| Issue | Command |
|-------|---------|
| Container keeps restarting | `docker logs --tail 100 container_name` |
| Port already in use | `lsof -i :PORT` or `docker ps --filter publish=PORT` |
| Out of disk space | `docker system df` then `docker system prune` |
| Container can't reach another | Check they're on the same network: `docker network inspect` |
| Data lost after recreate | Use named volumes, not anonymous. NEVER `docker rm` + `docker run` for DBs |

## Important: Container Lifecycle

```bash
# SAFE: restart preserves data and config
docker restart mycontainer

# DANGEROUS: recreate may reinitialize data volumes
docker compose down && docker compose up -d

# VERY DANGEROUS: removes container AND anonymous volumes
docker rm -v mycontainer
```

For databases, always prefer `docker restart` over `docker rm` + `docker run`.
