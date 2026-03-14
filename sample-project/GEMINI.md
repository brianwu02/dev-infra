# GEMINI.md — Sample Full-Stack App

## What This Is
A template full-stack web app with a Python backend (FastAPI), TypeScript frontend (React + Vite), and PostgreSQL/TimescaleDB database. Self-hosted on a DooD dev container.

## Environment
- Dev container: `dev-box` (DooD pattern)
- Working dir: `/workspace/myproject/`
- DB: TimescaleDB at `timescaledb:5432/devdb`

## Key Commands
```bash
docker compose up -d                           # Start services
psql -h localhost -p 5432 -U devuser -d devdb  # Database
cd frontend && npx vitest run                  # Frontend tests
cd backend && python -m pytest tests/ -v       # Backend tests
```

## Patterns
- Backend: `domains/{domain}/router.py` + `queries.py` + `schemas.py`
- Frontend: `Component → endpoints.ts → client.ts → fetch()`
- All SQL in `queries.py`, never in routers
- All types from Zod schemas, no bare `fetch()`
- Backend `snake_case`, Frontend `camelCase`/`PascalCase`
