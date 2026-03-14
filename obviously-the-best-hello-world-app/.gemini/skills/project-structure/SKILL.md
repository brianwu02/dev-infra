---
name: project-structure
description: Project file tree and layout conventions. Use when navigating the codebase, finding where files belong, or understanding the project layout.
user-invokable: false
---

# Project Structure

```
obviously-the-best-hello-world-app/
├── CLAUDE.md                    <- project instructions (Claude Code)
├── GEMINI.md                    <- project instructions (Gemini)
├── main.py                      <- FastAPI app (single file for now)
├── requirements.txt             <- Python dependencies
├── Dockerfile                   <- Container build
├── .claude/
│   ├── settings.json            <- Claude Code permissions
│   └── skills/                  <- Claude Code skills
│       ├── coding-standards/
│       ├── verification-loop/
│       ├── tdd-workflow/
│       ├── add-endpoint/
│       ├── add-migration/
│       ├── db-schema/
│       ├── project-structure/
│       └── docker-patterns/
└── .gemini/
    ├── settings.json            <- Gemini permissions
    └── skills/                  <- Gemini skills (mirrors .claude)
```

## Growing the Project

As the app grows beyond a single `main.py`, adopt this structure:

```
app/
├── main.py                      <- FastAPI app setup, lifespan, router registration
├── db.py                        <- asyncpg pool lifecycle + dependency injection
├── schemas.py                   <- Shared Pydantic models
├── domains/
│   └── {domain}/
│       ├── router.py            <- Route handlers (thin — wire deps, return results)
│       ├── queries.py           <- SQL queries (all DB access here)
│       └── schemas.py           <- Domain-specific Pydantic models
├── migrations/
│   ├── 001_initial.sql
│   └── 002_add_events.sql
└── tests/
    ├── conftest.py              <- Shared fixtures (mock pool, test client)
    ├── test_endpoints.py        <- API integration tests
    └── test_queries.py          <- Query unit tests
```

### Key Conventions

- **Three-file pattern per domain**: `router.py` + `queries.py` + `schemas.py`
- **No SQL in routers** — all SQL lives in `queries.py`
- **No HTTP logic in queries** — queries return data, routers handle HTTP
- **Every route handler has `response_model=`**
- **Migrations are sequential**: `001_`, `002_`, etc.
- **Tests mirror source structure**: `test_endpoints.py` tests routes, `test_queries.py` tests queries
