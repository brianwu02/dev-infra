---
name: deploy
description: Deploy the application to staging or production. Covers build, compose, health checks, and verification.
user-invokable: true
argument-hint: "staging|production"
---

# Deploy

## Staging Deploy

```bash
# Build and start staging
docker compose -f docker-compose.staging.yml -p myproject-staging build
docker compose -f docker-compose.staging.yml -p myproject-staging up -d
```

### Verify
```bash
# Backend health
curl -sf http://localhost:8001/health

# Frontend
curl -sf http://localhost:5174 -o /dev/null && echo "Frontend OK"

# Logs
docker compose -f docker-compose.staging.yml -p myproject-staging logs -f
```

### Stop
```bash
docker compose -f docker-compose.staging.yml -p myproject-staging down
```

## Production Deploy

```bash
ssh prod-server 'cd ~/myproject && ./deploy.sh'
```

### Verification Checklist
1. Backend health: `curl -sf https://myapp.example.com/api/health`
2. Frontend loads: visit `https://myapp.example.com`
3. No errors in logs: `docker compose logs --tail 50`

### Rollback
```bash
ssh prod-server 'cd ~/myproject && ./deploy.sh --rollback'
```

## Port Allocation

| Service | Dev | Staging |
|---------|-----|---------|
| Frontend | 5173 | 5174 |
| Backend | 8000 | 8001 |
| Database | 5432 | (shared) |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Container won't start | Check logs: `docker compose logs backend` |
| 502 Bad Gateway | Proxy can't reach backend — verify container and port |
| Old frontend build | Rebuild: `docker compose build --no-cache frontend` |
| DB connection refused | Check database container is running |
