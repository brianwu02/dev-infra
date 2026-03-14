---
name: verification-loop
description: Run after completing changes to verify the app builds, tests pass, and the diff is clean before committing.
user-invokable: true
---

# Verification Loop

Run this after completing a feature, fixing a bug, or before committing. Catches broken code before it lands.

## When to Run

- After completing a feature or significant code change
- Before creating a commit or PR
- After refactoring
- When you want to confirm nothing is broken

## Phase 1: Lint / Type Check

```bash
cd /workspace/woozy-dev-infra/obviously-the-best-hello-world-app
python -m py_compile main.py
```

If the project grows to use mypy or ruff:
```bash
ruff check .
mypy --strict .
```

## Phase 2: Unit Tests

```bash
cd /workspace/woozy-dev-infra/obviously-the-best-hello-world-app
python -m pytest tests/ -v
```

Check for failures and regressions. All tests must pass.

## Phase 3: Container Build

```bash
docker compose build hello-world
```

Ensures the Dockerfile is valid and dependencies install correctly.

## Phase 4: Smoke Test

```bash
# Start the service
docker compose up -d hello-world

# Test endpoints
curl -s http://localhost:8000/api | jq .
curl -s -X POST http://localhost:8000/api/hit | jq .
curl -s -X POST http://localhost:8000/api/reset | jq .
```

Verify all endpoints return valid JSON with the expected `hits` field.

## Phase 5: Diff Review

```bash
git diff --stat
```

Review each changed file for:
- Unintended changes or debug code left behind
- Missing `response_model=` on new endpoints
- SQL in router files (should be in query modules)
- Unused imports or variables
- Hardcoded secrets or credentials

## Output Format

After running all phases, produce:

```
VERIFICATION REPORT
==================

Compile:    [PASS/FAIL]
Tests:      [PASS/FAIL] (X/Y passed)
Build:      [PASS/FAIL]
Smoke:      [PASS/FAIL]
Diff:       [X files changed]

Overall:    [READY/NOT READY] to commit

Issues to Fix:
1. ...
```

## What to Do on Failure

| Phase | Fix |
|-------|-----|
| Compile | Fix syntax or type errors |
| Tests | Fix failing test or update test if behavior changed intentionally |
| Build | Fix Dockerfile or requirements |
| Smoke | Check container logs: `docker compose logs hello-world` |
