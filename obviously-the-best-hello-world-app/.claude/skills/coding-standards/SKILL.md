---
name: coding-standards
description: Baseline code quality enforcer — naming conventions, import hygiene, type safety, and style rules for a FastAPI + asyncpg + PostgreSQL Python backend.
---

# Coding Standards

Baseline quality rules that apply to ALL code changes. These are non-negotiable.

## When to Activate

- Every code change — this skill is always relevant
- Especially during code review or refactoring

## Naming Conventions

| What | Style | Example |
|------|-------|---------|
| Functions | `snake_case` | `fetch_all_items()` |
| Variables | `snake_case` | `item_id`, `pool` |
| Constants | `UPPER_SNAKE` | `MAX_RETRIES`, `DB_URL` |
| Classes/Models | `PascalCase` | `ItemResponse(BaseModel)` |
| Files | `snake_case` | `router.py`, `queries.py` |
| Test files | `test_` prefix | `test_queries.py` |
| DB tables | `snake_case` | `hello_counter`, `events` |
| DB columns | `snake_case` | `created_at`, `hit_count` |

## Import Ordering

```python
# 1. Standard library
import os
from datetime import date, datetime

# 2. Third-party
import asyncpg
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# 3. Local
from app.db import get_pool
from . import queries
```

- No unused imports — remove them immediately
- No wildcard imports (`from module import *`)

## Type Safety

### Pydantic Models
- Every route handler MUST have `response_model=`
- Use `ConfigDict(from_attributes=True)` for DB-backed models
- Use `str | None = None` not `Optional[str]`

```python
# WRONG — no response_model
@router.get("/items")
async def list_items(pool=Depends(get_pool)):
    return await queries.fetch_all(pool)

# CORRECT
@router.get("/items", response_model=list[ItemResponse])
async def list_items(pool: asyncpg.Pool = Depends(get_pool)):
    return await queries.fetch_all(pool)
```

### Type Hints
- All function signatures must have type hints
- Use `asyncpg.Pool` for pool parameters, `asyncpg.Record` for rows

## Code Style

### Simplicity
- Keep functions short and focused
- Prefer simple conditionals over clever abstractions
- Three similar lines > premature abstraction
- Extract only when logic is genuinely reused

### No Dead Code
- Remove unused functions, variables, imports
- Don't comment out code "for later" — git has history
- Don't leave `print()` debug statements

## Architecture Rules

1. **No SQL in routers** — all SQL belongs in `queries.py` or a dedicated query module
2. **No business logic in route handlers** — handlers wire together dependencies and return results
3. **Always use `docker compose`** — we run inside a dev container (DooD pattern)
4. **Parameterized queries only** — use `$1, $2, ...` placeholders, never string interpolation

## Pre-Commit Checklist

Before committing any change, verify:
- [ ] No unused imports or variables
- [ ] Naming follows conventions above
- [ ] `response_model=` on all new/modified endpoints
- [ ] No `print()` debug statements left behind
- [ ] SQL only in query modules, not routers
- [ ] All queries use `$N` parameterized placeholders
