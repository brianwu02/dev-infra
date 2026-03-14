# GEMINI.md — obviously-the-best-hello-world-app

## What This Is
A minimal FastAPI app with a hit counter stored in PostgreSQL. Serves as a starter template for FastAPI + asyncpg + PostgreSQL projects and a proof-of-life service in the dev-infra stack.

## Architecture
- **Runtime**: Python 3.12, FastAPI, asyncpg, uvicorn
- **Database**: PostgreSQL (Postgres + PostgreSQL extension)
- **Container**: Single Dockerfile, runs via `docker compose` from the parent `woozy-dev-infra` project
- **Dev environment**: Runs inside `dev-box` container using DooD (Docker-outside-of-Docker) — the Docker socket is mounted from the host

## App Layout
Single-file app (`main.py`) with 3 API endpoints:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | HTML page with counter UI |
| GET | `/api` | Returns current hit count as JSON |
| POST | `/api/hit` | Increments counter, returns new count |
| POST | `/api/reset` | Resets counter to 0 |

All state is in the `hello_counter` table (single row, auto-created on startup).

## Database
- **Host**: `postgres` (Docker service name)
- **Port**: 5432
- **DB**: `devdb`
- **User**: `devuser` / `changeme`
- **Connection**: asyncpg pool (min=1, max=3), initialized in FastAPI lifespan

## Quick Commands
```bash
# Start
docker compose up -d hello-world postgres

# Logs
docker compose logs -f hello-world

# Test endpoints
curl -s http://localhost:8000/api | jq .
curl -s -X POST http://localhost:8000/api/hit | jq .
curl -s -X POST http://localhost:8000/api/reset | jq .

# Rebuild after changes
docker compose up -d --build hello-world

# Connect to DB
psql postgresql://devuser:changeme@localhost:5432/devdb
```

## Conventions
- **No SQL in route handlers** — keep queries in dedicated functions (or inline for trivial single-file apps)
- **`response_model=` on all endpoints** as the app grows
- **Parameterized queries** — use `$1, $2, ...` placeholders, never string interpolation
- **`docker compose` only** — no bare `docker run` for app services
- See `coding-standards` skill for full naming/style rules

## Skills
The `.gemini/skills/` directory contains reusable development skills:

| Skill | Description |
|-------|-------------|
| `coding-standards` | Naming, imports, type safety, style rules |
| `verification-loop` | Post-change quality gate |
| `tdd-workflow` | Test-driven development process |
| `add-endpoint` | Checklist for new API endpoints |
| `add-migration` | Create DB migrations |
| `db-schema` | Database schema reference |
| `project-structure` | File tree and layout conventions |
| `docker-patterns` | DooD, compose, container lifecycle |
