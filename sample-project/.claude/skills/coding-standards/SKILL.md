---
name: coding-standards
description: Baseline code quality enforcer — naming conventions, import hygiene, type safety, and style rules for Python backend and TypeScript frontend.
user-invokable: false
---

# Coding Standards

Baseline quality rules that apply to ALL code changes. Non-negotiable.

## When to Activate

- Every code change — this skill is always relevant
- Especially during code review or refactoring

## Naming Conventions

### Backend (Python)

| What | Style | Example |
|------|-------|---------|
| Functions | `snake_case` | `fetch_all_items()` |
| Variables | `snake_case` | `item_id`, `cache_key` |
| Constants | `UPPER_SNAKE` | `FLUSH_INTERVAL`, `MAX_RETRIES` |
| Classes/Models | `PascalCase` | `ItemDetail(BaseModel)` |
| Files | `snake_case` | `router.py`, `queries.py` |
| Test files | `test_` prefix | `test_queries.py` |
| DB tables | `snake_case` | `users`, `audit_logs` |
| DB columns | `snake_case` | `created_at`, `item_type` |
| Cache keys | colon-separated | `app:item:{id}:detail` |

### Frontend (TypeScript)

| What | Style | Example |
|------|-------|---------|
| Variables/functions | `camelCase` | `itemId`, `fetchItems()` |
| Components | `PascalCase` | `ItemCard` |
| Types/interfaces | `PascalCase` | `ItemFeature`, `FilterState` |
| Constants | `UPPER_SNAKE` | `API_BASE_URL` |
| Files (components) | `PascalCase.tsx` | `ItemCard.tsx` |
| Files (hooks) | `camelCase.tsx` | `useSession.tsx` |
| Files (utilities) | `camelCase.ts` | `endpoints.ts`, `client.ts` |
| Test files | `.test.tsx` suffix | `ItemCard.test.tsx` |

**Rule**: File name MUST match the default export.

## Import Hygiene

### Import Ordering

**Python:**
```python
# 1. Standard library
import json
from datetime import date, datetime

# 2. Third-party
import asyncpg
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# 3. Local
from backend.db import get_pool
from . import queries
```

**TypeScript:**
```typescript
// 1. React/framework
import { useState, useEffect } from 'react'

// 2. Third-party
import { z } from 'zod'

// 3. Local
import { useSession } from '@/hooks/useSession'
import { items } from '@/api/endpoints'

// 4. Relative
import type { FilterState } from './types'
```

## Type Safety

### Frontend (strict TypeScript)
- `strict: true`, `allowJs: false` — no escape hatches
- No `any` without a comment explaining why
- All API types from Zod schemas — never hand-written
- Path alias: `@/*` maps to `src/*`

### Backend (Pydantic)
- Every route handler MUST have `response_model=`
- Use `ConfigDict(from_attributes=True)` for DB-backed models
- Use `str | None = None` not `Optional[str]`

## Architecture Rules (Hard Stops)

1. **No SQL in routers** — all SQL in `queries.py`
2. **No bare `fetch()` in frontend** — use `endpoints.ts` → `client.ts` chain
3. **No Redux** — React Context for global state, `useState` for local
4. **Frontend is 100% TypeScript** — `.tsx` for components, `.ts` for everything else
5. **No `docker run`** — always `docker compose`

## Pre-Commit Checklist

- [ ] No unused imports or variables
- [ ] Naming follows conventions
- [ ] `response_model=` on all new/modified endpoints
- [ ] No bare `fetch()` in frontend
- [ ] No `any` without justification
- [ ] No `console.log` / `print()` left behind
- [ ] SQL only in `queries.py` files
