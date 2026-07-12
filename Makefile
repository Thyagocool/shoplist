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

# ─── Frontend ───────────────────────────────────────────────────
app-build:
	cd app && npm run build

app-install:
	cd app && npm install --legacy-peer-deps
