# CLAUDE.md — Sample Full-Stack App

## What This Is
A template full-stack web app with a Python backend (FastAPI), TypeScript frontend (React + Vite), and PostgreSQL/TimescaleDB database. Self-hosted on a DooD dev container.

## Environment & Architecture
- **Dev container**: `dev-box` (ubuntu:22.04) with Docker socket mounted (DooD pattern)
- **Working dir**: `/workspace/myproject/`
- **Host filesystem**: `/host_root/`
- **DB**: TimescaleDB at `timescaledb:5432/devdb`
- **Architecture**: Services run via Docker Compose. No cloud — fully self-hosted.

## Tech Stack
| Layer | Stack |
|-------|-------|
| Backend | FastAPI, asyncpg, uvicorn, Pydantic |
| Frontend | TypeScript + React 18, Vite, Zod, TailwindCSS |
| Database | TimescaleDB (PostgreSQL 15 + time-series extensions) |
| Testing | Vitest (frontend), pytest (backend), Playwright (E2E) |

## Quick Reference Commands
```bash
# Start all services
docker compose up -d

# Database
psql -h localhost -p 5432 -U devuser -d devdb

# Run migrations
psql -h localhost -p 5432 -U devuser -d devdb -f backend/migrations/NNN_name.sql

# Tests
cd frontend && npx vitest run              # Frontend unit tests
cd backend && python -m pytest tests/ -v   # Backend tests
cd frontend && npx playwright test         # E2E tests
```

## Architectural Patterns (MUST FOLLOW)
- **Always use `docker compose`**: We run inside `dev-box` (DooD). Manage services via compose commands.
- **Backend three-file pattern**: `domains/{domain}/router.py` + `queries.py` + `schemas.py`. Never put SQL in routers. Every route handler MUST have `response_model=`.
- **Frontend API chain**: `Component → endpoints.ts → client.ts → fetch()`. No bare `fetch()` calls. All types from Zod schemas.
- **Frontend state**: React Context for global, `useState` for local. No Redux.
- **Code Quality**: Backend `snake_case`, Frontend `camelCase`/`PascalCase`. Frontend is strict TypeScript.

## Reference Skills (auto-loaded when relevant)
- `coding-standards` — Naming conventions, import hygiene, type safety
- `verification-loop` — Post-change quality gate (typecheck, tests, diff review)
- `tdd-workflow` — Test-driven development with 80%+ coverage
- `docker-patterns` — DooD, compose, container management
- `postgres-patterns` — SQL, migrations, TimescaleDB

## Workflow
- **Parallel Work**: Use git worktrees (`wt myproject task1`) for parallel branches.
- **Before committing**: Run `/verification-loop` to check types, tests, and lint.
