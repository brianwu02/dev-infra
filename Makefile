COMPOSE = docker compose
DIR     = $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: up down ps logs health backup-db \
        up-devbox up-monitoring up-database up-services up-example down-example \
        down-devbox down-monitoring down-database down-services \
        logs-devbox logs-timescaledb logs-homepage logs-dozzle logs-uptime-kuma logs-watchtower \
        logs-traefik logs-redis logs-minio logs-mailpit logs-adminer logs-hello

# ---------- All services ----------

up:
	$(COMPOSE) -f $(DIR)/docker-compose.yml up -d

down:
	$(COMPOSE) -f $(DIR)/docker-compose.yml down

# ---------- Selective startup ----------

up-devbox:
	$(COMPOSE) -f $(DIR)/docker-compose.yml up -d dev-box

up-database:
	$(COMPOSE) -f $(DIR)/docker-compose.yml up -d timescaledb redis

up-monitoring:
	$(COMPOSE) -f $(DIR)/docker-compose.yml up -d homepage watchtower dozzle uptime-kuma

up-services:
	$(COMPOSE) -f $(DIR)/docker-compose.yml up -d traefik minio mailpit adminer

down-devbox:
	$(COMPOSE) -f $(DIR)/docker-compose.yml stop dev-box

down-database:
	$(COMPOSE) -f $(DIR)/docker-compose.yml stop timescaledb redis

down-monitoring:
	$(COMPOSE) -f $(DIR)/docker-compose.yml stop homepage watchtower dozzle uptime-kuma

down-services:
	$(COMPOSE) -f $(DIR)/docker-compose.yml stop traefik minio mailpit adminer

# ---------- Example app ----------

up-example:
	$(COMPOSE) -f $(DIR)/docker-compose.yml up -d --build obviously-the-best-hello-world-app

down-example:
	$(COMPOSE) -f $(DIR)/docker-compose.yml stop obviously-the-best-hello-world-app

# ---------- Status ----------

ps:
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | sort

# ---------- Logs ----------

logs:
	@docker ps --format '{{.Names}}' | xargs docker logs --tail 20 --timestamps 2>&1 | head -200

logs-devbox:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f dev-box

logs-timescaledb:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f timescaledb

logs-redis:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f redis

logs-homepage:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f homepage

logs-dozzle:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f dozzle

logs-uptime-kuma:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f uptime-kuma

logs-watchtower:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f watchtower

logs-traefik:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f traefik

logs-minio:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f minio

logs-mailpit:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f mailpit

logs-adminer:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f adminer

logs-hello:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f obviously-the-best-hello-world-app

# ---------- Health check ----------

health:
	$(DIR)/scripts/health-check.sh

# ---------- Database backups ----------

backup-db:
	$(DIR)/scripts/backup-db.sh
