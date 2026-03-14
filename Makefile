COMPOSE = docker compose
DIR     = $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: up down ps logs health backup-db up-devbox up-monitoring up-database \
        down-devbox down-monitoring down-database \
        logs-devbox logs-timescaledb logs-homepage logs-netdata logs-dozzle logs-uptime-kuma logs-watchtower

# ---------- All services ----------

up:
	$(COMPOSE) -f $(DIR)/docker-compose.yml up -d

down:
	$(COMPOSE) -f $(DIR)/docker-compose.yml down

# ---------- Selective startup ----------

up-devbox:
	$(COMPOSE) -f $(DIR)/docker-compose.yml up -d dev-box

up-database:
	$(COMPOSE) -f $(DIR)/docker-compose.yml up -d timescaledb

up-monitoring:
	$(COMPOSE) -f $(DIR)/docker-compose.yml up -d homepage netdata watchtower dozzle uptime-kuma

down-devbox:
	$(COMPOSE) -f $(DIR)/docker-compose.yml stop dev-box

down-database:
	$(COMPOSE) -f $(DIR)/docker-compose.yml stop timescaledb

down-monitoring:
	$(COMPOSE) -f $(DIR)/docker-compose.yml stop homepage netdata watchtower dozzle uptime-kuma

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

logs-homepage:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f homepage

logs-netdata:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f netdata

logs-dozzle:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f dozzle

logs-uptime-kuma:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f uptime-kuma

logs-watchtower:
	$(COMPOSE) -f $(DIR)/docker-compose.yml logs --tail 50 -f watchtower

# ---------- Health check ----------

health:
	$(DIR)/scripts/health-check.sh

# ---------- Database backups ----------

backup-db:
	$(DIR)/scripts/backup-db.sh
