# 🟢 FASE 1 — Migração para PostgreSQL

**Status:** ✅ Concluída em 12/07/2026

---

## Objetivo

Substituir o SQLite (dev) pelo PostgreSQL 16 como banco de dados principal,
com suporte a async/await, pool de conexões, e migrations via Alembic.

---

## O que foi criado/alterado

### 🐘 Serviço PostgreSQL no Docker

**`docker-compose.yml`** — novo serviço `postgres`:

```yaml
postgres:
  image: postgres:16-alpine
  environment:
    POSTGRES_DB: shoplist
    POSTGRES_USER: shoplist
    POSTGRES_PASSWORD: shoplist123
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U shoplist"]
    interval: 5s
    retries: 5
```

A API agora depende do PostgreSQL com `condition: service_healthy`,
ou seja, só sobe quando o banco estiver pronto.

### 📦 Database Config (infra)

**`api/src/infrastructure/database/config.py`** — novo arquivo com:

| Componente | Descrição |
|-----------|-----------|
| `Base` | Classe declarativa do SQLAlchemy |
| `engine` | `create_async_engine` com `asyncpg`, pool de 5-10 conexões |
| `async_session_factory` | Fábrica de sessões assíncronas |
| `get_session()` | Generator para FastAPI `Depends` (commit/rollback automático) |
| `init_db()` | Cria todas as tabelas (para testes) |
| `drop_db()` | Dropa todas as tabelas (para testes) |

### 🗂️ Base Model

**`api/src/infrastructure/database/models/base.py`** — classes base:

- **`Base`** — `DeclarativeBase` do SQLAlchemy
- **`UUIDMixin`** — coluna `id` UUID PK com `uuid.uuid4`
- **`TimestampMixin`** — colunas `created_at` e `updated_at` com `server_default` e `onupdate`

### 🔄 Alembic Configurado

| Arquivo | Função |
|---------|--------|
| `api/alembic.ini` | Config principal do Alembic |
| `api/src/infrastructure/database/migrations/env.py` | Env assíncrono (roda migrations com async engine) |
| `api/src/infrastructure/database/migrations/script.py.mako` | Template das migrations |

O `env.py` lê a `DATABASE_URL` do `settings` (que vem do `.env`),
suportando troca entre ambientes sem mudar config.

### ⚙️ Configurações Atualizadas

**`api/config.py`**:
```python
# Antes (SQLite)
database_url: str = "sqlite+aiosqlite:///./data/shoplist.db"

# Depois (PostgreSQL)
database_url: str = "postgresql+asyncpg://shoplist:shoplist123@localhost:5432/shoplist"
```

**`api/requirements.txt`** — adicionado:
```
asyncpg>=0.29.0
```

**`api/.env.example`** — URL atualizada para PostgreSQL.

### 🔗 Lifespan da App

**`api/main.py`** — adicionado `lifespan` context manager:
- **Startup:** testa conexão com o banco
- **Shutdown:** fecha o engine (libera pool)

---

## Como Rodar

```bash
# Sobe tudo (postgres + api + app)
docker compose up -d

# A API só sobe depois do postgres ficar healthy
# Verificar logs:
docker compose logs api

# Testar conexão:
docker compose exec api python -c "
import asyncio
from sqlalchemy import text
from src.infrastructure.database.config import engine

async def test():
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT version()'))
        print(f'Conectado: {result.fetchone()[0]}')

asyncio.run(test())
"
```

---

## Arquivos Alterados/Criados

| Arquivo | Ação |
|---------|------|
| `docker-compose.yml` | ✏️ Adicionado serviço postgres + dependência |
| `api/config.py` | ✏️ Default URL alterado para PostgreSQL |
| `api/requirements.txt` | ✏️ Adicionado asyncpg |
| `api/.env.example` | ✏️ URL atualizada |
| `api/main.py` | ✏️ Adicionado lifespan (conexão/desconexão) |
| `api/alembic.ini` | 🆕 Config do Alembic |
| `api/src/infrastructure/database/config.py` | 🆕 Engine, session, init/drop helpers |
| `api/src/infrastructure/database/models/base.py` | 🆕 Base, UUIDMixin, TimestampMixin |
| `api/src/infrastructure/database/migrations/env.py` | 🆕 Env assíncrono do Alembic |
| `api/src/infrastructure/database/migrations/script.py.mako` | 🆕 Template de migrations |
| `api/src/infrastructure/database/migrations/versions/` | 🆕 Pasta para versões |

---

## Verificações Realizadas

| Check | Resultado |
|-------|-----------|
| Build da API | ✅ |
| PostgreSQL 16.3 healthy | ✅ |
| `GET /health` | ✅ `{"status":"ok","version":"0.1.0"}` |
| Conexão assíncrona via asyncpg | ✅ `PostgreSQL 16.13 on x86_64-pc-linux-musl` |
| `docker compose ps` | ✅ 3 containers: postgres, api, app |

---

## Commit

```
d621e5e feat: migra banco de SQLite para PostgreSQL
```
