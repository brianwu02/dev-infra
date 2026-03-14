---
name: verification-loop
description: Run after completing changes to verify build, types, and tests pass before committing.
user-invokable: true
---

# Verification Loop

Run this after completing a feature, fixing a bug, or before committing.

## When to Run

- After completing a feature or significant code change
- Before creating a commit or PR
- After refactoring
- When you want to confirm nothing is broken

## Phase 1: Frontend TypeCheck

```bash
cd frontend && npx tsc --noEmit
```

Must pass with zero errors. The frontend is strict TypeScript.

## Phase 2: Frontend Unit Tests

```bash
cd frontend && npx vitest run
```

Check for failures and regressions.

## Phase 3: Backend Tests

```bash
cd backend && python -m pytest tests/ -v
```

Runs all backend tests.

## Phase 4: E2E Tests (if UI changed)

```bash
cd frontend && npx playwright test
```

Only run if you modified frontend components.

## Phase 5: Diff Review

```bash
git diff --stat
```

Review each changed file for:
- Unintended changes or debug code left behind
- Missing `response_model=` on new endpoints
- Bare `fetch()` calls in frontend
- SQL in router files
- Unused imports or variables

## Quick One-Liner (Phases 1-3)

```bash
(cd frontend && npx tsc --noEmit) && \
  (cd frontend && npx vitest run) && \
  (cd backend && python -m pytest tests/ -v) && \
  echo "ALL CHECKS PASSED" || echo "VERIFICATION FAILED"
```

## Output Format

```
VERIFICATION REPORT
==================

TypeCheck:      [PASS/FAIL] (X errors)
Frontend Tests: [PASS/FAIL] (X/Y passed)
Backend Tests:  [PASS/FAIL] (X/Y passed)
E2E:            [SKIP/PASS/FAIL]
Diff:           [X files changed]

Overall:        [READY/NOT READY] to commit

Issues to Fix:
1. ...
```

## What to Do on Failure

| Phase | Fix |
|-------|-----|
| TypeCheck | Fix type errors — no `any` without justification |
| Frontend Tests | Fix failing test or update if behavior changed intentionally |
| Backend Tests | Fix test or update fixtures |
| E2E | Update screenshots if intentional, fix if not |
