---
name: docker-patterns
description: Docker patterns for this project — DooD (Docker-outside-of-Docker), compose conventions, container lifecycle, and dev-box workflow.
user-invokable: false
---

# Docker Patterns

## DooD (Docker-outside-of-Docker)

This project runs inside a `dev-box` container that has the Docker socket mounted from the host. This means:

- `docker` and `docker compose` commands inside the dev container control **host Docker**
- Containers started from dev-box are siblings, not children
- Volume mounts use **host paths**, not dev-box paths

```yaml
# dev-box mounts the host Docker socket
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

### Implications
- Always use `docker compose` to manage services (never `docker run` for app services)
- Container names and networks are on the host Docker daemon
- Logs, inspect, stats all work normally from inside dev-box

## Compose Conventions

### Service Definition
```yaml
services:
  hello-world:
    build: ./obviously-the-best-hello-world-app
    ports:
      - "8000:8000"
    environment:
      DB_HOST: postgres
      DB_PORT: "5432"
      DB_NAME: devdb
      DB_USER: devuser
      DB_PASSWORD: changeme
    depends_on:
      postgres:
        condition: service_healthy
    mem_limit: 256m
    restart: unless-stopped
```

### Health Checks
Always add health checks so `depends_on` with `condition: service_healthy` works:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U devuser -d devdb"]
  interval: 5s
  timeout: 3s
  retries: 5
```

### Memory Limits
Set `mem_limit` on every container to prevent runaway memory:
```yaml
mem_limit: 256m    # App containers
mem_limit: 512m    # Database containers
```

Use `docker stats` to monitor actual usage and adjust.

## Container Lifecycle

### Starting Services
```bash
docker compose up -d                    # All services
docker compose up -d hello-world        # Single service
docker compose up -d --build hello-world  # Rebuild and start
```

### Viewing Logs
```bash
docker compose logs -f hello-world      # Follow logs
docker compose logs --tail=50 hello-world  # Last 50 lines
```

### Restarting
```bash
docker compose restart hello-world      # Restart without rebuild
docker compose up -d --build hello-world  # Rebuild + restart
```

### Database Containers
IMPORTANT: For database containers, prefer `docker restart` over `docker rm` + `docker run`. Recreating a database container can reinitialize the data directory and destroy data.

## Networking

### Container-to-Container Communication
Containers on the same compose network can reach each other by service name:
```python
# From hello-world container, reach the DB:
DB_HOST = "postgres"  # Service name, not localhost
DB_PORT = "5432"         # Internal port, not host-mapped port
```

### Host Access
Services are exposed on host ports via `ports:` mapping:
```
http://localhost:8000  -> hello-world container
localhost:5432        -> postgres container
```

## Development Workflow

1. Edit code in dev-box (mounted workspace)
2. Rebuild: `docker compose up -d --build hello-world`
3. Check logs: `docker compose logs -f hello-world`
4. Test: `curl http://localhost:8000/api`
5. Iterate

For hot-reload during development, mount the source code:
```yaml
volumes:
  - ./obviously-the-best-hello-world-app:/app
command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```
