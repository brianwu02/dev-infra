---
name: project-structure
description: Full project file tree with descriptions of each directory and key file.
user-invokable: false
---

# Project Structure

```
myproject/
├── CLAUDE.md                    # AI assistant context (this project)
├── GEMINI.md                    # Gemini CLI context
├── docker-compose.yml           # All services (backend, frontend, db, redis)
├── .env                         # Environment variables (not committed)
├── .env.example                 # Template for .env
│
├── backend/
│   ├── main.py                  # FastAPI app, router registration
│   ├── db.py                    # asyncpg pool, get_pool dependency
│   ├── cache.py                 # Redis @cached decorator
│   ├── schemas.py               # Shared Pydantic models
│   ├── domains/
│   │   ├── items/
│   │   │   ├── router.py        # Route handlers
│   │   │   ├── queries.py       # SQL queries (fetch_*, row_to_*)
│   │   │   └── schemas.py       # Domain-specific Pydantic models
│   │   └── users/
│   │       ├── router.py
│   │       ├── queries.py
│   │       └── schemas.py
│   ├── migrations/              # Sequential SQL migrations (001-NNN)
│   │   ├── 001_initial.sql
│   │   └── ...
│   └── tests/
│       ├── test_items.py
│       └── test_users.py
│
├── frontend/
│   ├── tsconfig.json            # strict: true, paths: @/*
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.tsx             # Router setup, providers
│   │   ├── App.tsx              # Root component
│   │   ├── api/
│   │   │   ├── client.ts        # Base fetch wrapper
│   │   │   ├── endpoints.ts     # Typed endpoint functions
│   │   │   ├── types.ts         # Zod-inferred types
│   │   │   ├── schemas/         # Zod schemas per domain
│   │   │   └── __tests__/       # Contract tests
│   │   ├── components/          # React components (PascalCase dirs)
│   │   ├── hooks/               # Custom hooks (camelCase files)
│   │   ├── pages/               # Route pages (lazy-loaded)
│   │   ├── utils/               # Pure utility functions
│   │   └── styles/
│   │       └── app.css          # Tailwind @theme tokens
│   └── e2e/                     # Playwright tests
│
└── .claude/
    ├── settings.json            # Read-only permissions
    └── skills/                  # AI skill definitions
```

## Key Conventions

- **Backend three-file pattern**: Every domain has `router.py`, `queries.py`, `schemas.py`
- **Frontend API chain**: `Component → endpoints.ts → client.ts → fetch()`
- **Migrations**: Sequential numbering, wrapped in BEGIN/COMMIT
- **Tests**: Co-located with source (backend) or in `__tests__/` dirs (frontend)
