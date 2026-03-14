---
name: tdd-workflow
description: Test-driven development workflow for FastAPI + asyncpg apps. Write tests first, then implement, then refactor.
---

# Test-Driven Development Workflow

This skill ensures all code development follows TDD principles.

## When to Activate

- Writing new features or functionality
- Fixing bugs
- Refactoring existing code
- Adding API endpoints

## Core Principles

### 1. Tests BEFORE Code
ALWAYS write tests first, then implement code to make tests pass.

### 2. Red-Green-Refactor
1. **Red**: Write a failing test that defines desired behavior
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Clean up while keeping tests green

### 3. Test Types for FastAPI + asyncpg

#### Unit Tests
- Pure functions, helpers, data transformations
- Query builder logic (if applicable)
- Pydantic model validation

#### Integration Tests
- API endpoint tests using `httpx.AsyncClient` + FastAPI `TestClient`
- Database operations against a test database
- Connection pool behavior

## TDD Workflow Steps

### Step 1: Define the Behavior
```
As a [role], I want to [action], so that [benefit]

Example:
As an API consumer, I want to POST /api/events to record events,
so that I can track usage over time.
```

### Step 2: Write Failing Tests

```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_create_event_returns_201():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/events", json={"name": "page_view"})
        assert resp.status_code == 201
        assert "id" in resp.json()

@pytest.mark.asyncio
async def test_create_event_validates_input():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/events", json={})
        assert resp.status_code == 422
```

### Step 3: Run Tests (They Should Fail)
```bash
python -m pytest tests/ -v
```

### Step 4: Implement Minimal Code
Write just enough code to make tests pass. No more.

### Step 5: Run Tests Again (They Should Pass)
```bash
python -m pytest tests/ -v
```

### Step 6: Refactor
Improve code quality while keeping tests green:
- Remove duplication
- Improve naming
- Extract helpers

## Testing Patterns for asyncpg

### Mocking the Connection Pool
```python
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_pool():
    pool = AsyncMock(spec=asyncpg.Pool)
    pool.fetchrow.return_value = {"id": 1, "hits": 42}
    pool.fetch.return_value = [{"id": 1, "hits": 42}]
    return pool
```

### Testing with a Real DB (Integration)
```python
@pytest.fixture
async def test_pool():
    pool = await asyncpg.create_pool(os.environ["TEST_DATABASE_URL"])
    await pool.execute("DELETE FROM hello_counter")
    yield pool
    await pool.close()
```

### Testing FastAPI Endpoints
```python
from fastapi.testclient import TestClient

def test_read_hits():
    with TestClient(app) as client:
        resp = client.get("/api")
        assert resp.status_code == 200
        assert "hits" in resp.json()
```

## File Organization

```
project/
├── main.py
├── queries.py
├── schemas.py
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_endpoints.py    # API integration tests
│   ├── test_queries.py      # DB query unit tests
│   └── test_schemas.py      # Pydantic validation tests
```

## Best Practices

1. **One assert per test** — focus on single behavior
2. **Descriptive test names** — `test_hit_increments_counter`, not `test_1`
3. **Arrange-Act-Assert** — clear test structure
4. **Isolate tests** — each test sets up its own data
5. **Mock external deps** — DB, HTTP, filesystem
6. **Test error paths** — not just happy paths
7. **Keep tests fast** — mock the pool for unit tests, real DB for integration only
