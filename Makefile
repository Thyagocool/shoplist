.PHONY: up down logs api-logs app-logs psql test test-unit test-integration build clean

# ─── Development ────────────────────────────────────────────────
up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

api-logs:
	docker compose logs -f api

app-logs:
	docker compose logs -f app

psql:
	docker compose exec postgres psql -U shoplist -d shoplist

# ─── Testing ────────────────────────────────────────────────────
test:
	docker compose exec api python -m pytest tests/ -v

test-unit:
	docker compose exec api python -m pytest tests/unit/ -v

test-integration:
	docker compose exec api python -m pytest tests/integration/ -v

# ─── Build ──────────────────────────────────────────────────────
build:
	docker compose build --no-cache

rebuild:
	docker compose down -v
	docker compose build --no-cache
	docker compose up -d

# ─── Cleanup ────────────────────────────────────────────────────
clean:
	docker compose down -v
	docker system prune -f

# ─── Migrations ─────────────────────────────────────────────────
migration:
	docker compose exec api alembic revision --autogenerate -m "$(message)"

migrate:
	docker compose exec api alembic upgrade head

# Para servidor remoto (acesso SSH)
remote-migrate:
	@echo "Uso: make remote-migrate SSH_HOST=user@servidor"
	ssh $(SSH_HOST) "cd /path/to/shoplist/api && alembic upgrade head"

remote-import:
	@echo "Uso: make remote-import SSH_HOST=user@servidor DB_URL=postgresql+asyncpg://..."
	scp docs/export_thyagocool.sql $(SSH_HOST):/tmp/
	ssh $(SSH_HOST) "psql '$(DB_URL)' -f /tmp/export_thyagocool.sql && rm /tmp/export_thyagocool.sql"

# ─── Frontend ───────────────────────────────────────────────────
app-build:
	cd app && npm run build

app-install:
	cd app && npm install --legacy-peer-deps
