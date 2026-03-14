---
name: add-endpoint
description: Full-stack checklist for adding a new API endpoint — Pydantic schema through Zod contract tests.
user-invokable: true
argument-hint: "GET|POST|PUT|DELETE /path"
---

# Add a New Endpoint

Full-stack checklist for adding `$ARGUMENTS`:

## Backend (Python/FastAPI)

### Step 1: Pydantic Response Model

Add to `backend/domains/{domain}/schemas.py`:

```python
class MyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    created_at: datetime | None = None
```

### Step 2: Query Function

Add to `backend/domains/{domain}/queries.py`:

```python
async def fetch_my_data(pool: asyncpg.Pool, param: int):
    rows = await pool.fetch("SELECT id, name, created_at FROM table WHERE id = $1", param)
    return [row_to_my_data(r) for r in rows]
```

- Use `$N` parameterized placeholders (never string interpolation)
- Name functions `fetch_*`, converters `row_to_*`

### Step 3: Route Handler

Add to `backend/domains/{domain}/router.py`:

```python
@router.get("/path", response_model=MyResponse)
async def get_my_data(param: int, pool: asyncpg.Pool = Depends(get_pool)):
    return await queries.fetch_my_data(pool, param)
```

- MUST have `response_model=`
- Add `@cached("app:domain:key", ttl=600)` if data is expensive

## Frontend (TypeScript/React)

### Step 4: Zod Schema

Add to `frontend/src/api/schemas/{domain}.schema.ts`:

```typescript
import { z } from 'zod'

export const MyResponseSchema = z.object({
  id: z.number(),
  name: z.string(),
  createdAt: z.string().nullable(),
})
```

### Step 5: Export Type

Add to `frontend/src/api/types.ts`:

```typescript
import { MyResponseSchema } from './schemas/{domain}.schema'
export type MyResponse = z.infer<typeof MyResponseSchema>
```

### Step 6: Endpoint Function

Add to `frontend/src/api/endpoints.ts`:

```typescript
async myEndpoint(param: number): Promise<MyResponse> {
  return get(`/path?param=${param}`)
},
```

No bare `fetch()` — all access through `endpoints.ts` → `client.ts`.

### Step 7: Contract Test

Add to `frontend/src/api/__tests__/contracts.test.ts`:

```typescript
it('GET /path matches MyResponseSchema', async () => {
  const data = await domain.myEndpoint(1)
  expect(() => MyResponseSchema.parse(data)).not.toThrow()
})
```

## Verify

```bash
# Backend
docker compose restart backend && curl -sf http://localhost:8000/path

# Frontend
cd frontend && npx tsc --noEmit && npx vitest run
```
