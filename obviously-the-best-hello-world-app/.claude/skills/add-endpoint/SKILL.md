---
name: add-endpoint
description: Step-by-step checklist for adding a new API endpoint to a FastAPI + asyncpg app. Covers schema, query, route, and verification.
user-invokable: true
argument-hint: "GET|POST|PUT|DELETE /path"
---

# Add a New API Endpoint

Checklist for adding `$ARGUMENTS` to the app.

## Step 1: Pydantic Response Model

Define the response shape in your schemas module (or `main.py` for small apps):

```python
from pydantic import BaseModel, ConfigDict

class MyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    created_at: datetime
```

## Step 2: Query Function

Write the SQL query in a dedicated query module (or inline for small apps):

```python
async def fetch_my_data(pool: asyncpg.Pool, param: int) -> list[asyncpg.Record]:
    return await pool.fetch(
        "SELECT id, name, created_at FROM my_table WHERE category = $1 ORDER BY created_at DESC",
        param
    )
```

Rules:
- Use `$N` parameterized placeholders (NEVER string interpolation)
- Name functions: `fetch_*` for reads, `insert_*` / `update_*` / `delete_*` for writes
- Return `asyncpg.Record` objects — let Pydantic handle serialization

## Step 3: Route Handler

```python
@app.get("/api/my-endpoint", response_model=list[MyResponse])
async def get_my_data(category: int):
    rows = await fetch_my_data(pool, category)
    return [dict(r) for r in rows]
```

Rules:
- MUST have `response_model=`
- Keep handler thin — it wires dependencies together, doesn't contain logic
- Use proper HTTP methods: GET for reads, POST for creates, PUT/PATCH for updates, DELETE for deletes
- Use path params for resource identity (`/items/{id}`), query params for filtering (`/items?status=active`)

## Step 4: Write Tests

```python
@pytest.mark.asyncio
async def test_get_my_data_returns_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/my-endpoint?category=1")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

@pytest.mark.asyncio
async def test_get_my_data_validates_params():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/my-endpoint?category=invalid")
        assert resp.status_code == 422
```

## Step 5: Migration (if new table needed)

If the endpoint requires a new table, use the `/add-migration` skill first.

## Step 6: Verify

```bash
# Check it compiles
python -m py_compile main.py

# Run tests
python -m pytest tests/ -v

# Smoke test (with services running)
docker compose up -d
curl -s http://localhost:8000/api/my-endpoint?category=1 | jq .

# Check OpenAPI docs
# Visit http://localhost:8000/docs
```
