---
name: tdd-workflow
description: Enforces test-driven development — write tests first, then code, with 80%+ coverage.
user-invokable: false
---

# Test-Driven Development Workflow

## When to Activate

- Writing new features
- Fixing bugs
- Refactoring existing code
- Adding API endpoints or components

## Core Principles

1. **Tests BEFORE Code** — always write tests first
2. **80%+ coverage** minimum (unit + integration + E2E)
3. **All edge cases covered** — error scenarios, boundary conditions

## Test Types

### Unit Tests (Vitest / pytest)
- Individual functions, components, utilities
- Fast (<50ms each), isolated, no external deps

### Integration Tests
- API endpoints, database operations
- Service interactions

### E2E Tests (Playwright)
- Critical user flows
- Full browser automation

## TDD Workflow

### Step 1: Write User Journey
```
As a [role], I want to [action], so that [benefit]
```

### Step 2: Generate Test Cases
```typescript
describe('Feature', () => {
  it('handles the happy path', async () => { /* ... */ })
  it('handles empty input', async () => { /* ... */ })
  it('handles errors gracefully', async () => { /* ... */ })
})
```

### Step 3: Run Tests (They Should Fail)
```bash
npx vitest run  # or: python -m pytest tests/ -v
```

### Step 4: Implement Minimal Code
Write just enough to make tests pass.

### Step 5: Run Tests Again (Should Pass)

### Step 6: Refactor
Improve while keeping tests green.

### Step 7: Verify Coverage
```bash
npx vitest run --coverage
# or: python -m pytest tests/ --cov
```

## Testing Patterns

### Component Test (Vitest)
```typescript
import { render, screen, fireEvent } from '@testing-library/react'

describe('Button', () => {
  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

### API Test (pytest)
```python
async def test_list_items(client):
    response = await client.get("/api/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

### E2E Test (Playwright)
```typescript
test('user can search items', async ({ page }) => {
  await page.goto('/')
  await page.fill('input[placeholder="Search"]', 'test')
  await expect(page.locator('[data-testid="result"]')).toHaveCount(5)
})
```

## Common Mistakes to Avoid

- Testing implementation details instead of behavior
- Brittle CSS selectors — use `data-testid` or semantic selectors
- Tests that depend on each other — each test sets up its own data
- Leaving `console.log` / `print()` in tests
