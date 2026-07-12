# 🟡 FASE 1 — Backend Core

**Status:** ✅ Concluída em 12/07/2026

---

## Etapas Executadas

| Etapa | Descrição | Status |
|-------|-----------|--------|
| 1.1 | Entidades de Domínio + Value Objects + Interfaces | ✅ |
| 1.2 | SQLAlchemy Models + Repositórios + Migrations | ✅ |
| 1.3 | Autenticação (register, login, JWT, middleware) | ✅ |
| 1.4 | Categorias CRUD | ✅ |

---

## Etapa 1.1 — Domínio Puro

### Value Objects (`api/src/domain/value_objects/`)

| Arquivo | Descrição |
|---------|-----------|
| `email.py` | `Email` — validação de email com regex, frozen dataclass |
| `price.py` | `Price` — preço em centavos (int), parse de string `R$ 12,90` |
| `unit.py` | `Unit` — enum padronizado: kg, g, l, ml, un, pct, cx, dz |

### Entidades (`api/src/domain/entities/`)

| Arquivo | Entidade | Métodos principais |
|---------|----------|-------------------|
| `user.py` | `User` | `create()` |
| `category.py` | `Category` | `create()` |
| `pre_registered_item.py` | `PreRegisteredItem` | `create()`, `deactivate()` |
| `store.py` | `Store` | `create()` |
| `shopping_list.py` | `ShoppingList` | `create()`, `complete()`, `cancel()` |
| `shopping_list_item.py` | `ShoppingListItem` | `from_pre_registered()`, `create_custom()`, `toggle_check()` |
| `movement.py` | `Movement` | `create()` |
| `stock.py` | `Stock` | `create()`, `add_purchase()`, `is_below_minimum()` |
| `inventory.py` | `InventoryDeclaration` | `declare()` — calcula `need = max_stock - declared` |

### Interfaces (`api/src/domain/interfaces/`)

| Arquivo | Descrição |
|---------|-----------|
| `repository.py` | `Repository[T]` — genérico com save, find_by_id, find_all, delete |
| `unit_of_work.py` | `UnitOfWork` — commit/rollback atômico |
| `auth_service.py` | `AuthService` — hash/verify password, JWT tokens |

---

## Etapa 1.2 — Infraestrutura de Banco

### SQLAlchemy Models (`api/src/infrastructure/database/models/`)

9 models espelhando as entidades + `base.py` com `UUIDMixin` e `TimestampMixin`.

| Modelo | Tabela | Destaques |
|--------|--------|-----------|
| `UserModel` | `users` | email único indexado |
| `CategoryModel` | `categories` | FK → users |
| `ItemModel` | `pre_registered_items` | unit como string, active bool, min/max stock |
| `StoreModel` | `stores` | FK → users |
| `ShoppingListModel` | `shopping_lists` | status enum (string), completed_at nullable |
| `ShoppingListItemModel` | `shopping_list_items` | FK → list, item, store; checked bool |
| `MovementModel` | `movements` | sequential_code, price_cents, store_name_snapshot |
| `StockModel` | `stock` | unique por item, last_price, last_store |
| `InventoryModel` | `inventory_declarations` | declared_quantity, calculated_need |

### Repositórios (`api/src/infrastructure/database/repositories/`)

| Repositório | Métodos extras |
|-------------|----------------|
| `BaseRepository[T]` | save, find_by_id, find_all, delete (genérico) |
| `UserRepository` | find_by_email |
| `CategoryRepository` | find_by_user_id, count_items |
| `ItemRepository` | find_active_by_user_id, find_by_category |
| `StoreRepository` | find_by_user_id, find_by_name |
| `ShoppingListRepository` | find_by_user_id, find_with_items, find_in_progress |
| `MovementRepository` | find_by_user_id (com filtros), get_next_sequential_code |
| `StockRepository` | find_by_item_id, find_by_user_id, find_alerts |
| `InventoryRepository` | find_by_list_id |

### Unit of Work (`api/src/infrastructure/database/unit_of_work.py`)
`SQLAlchemyUnitOfWork` — implementa `__aenter__`/`__aexit__` com commit automático.

### Migrations
Migration inicial gerada via Alembic: `ace5ef00cc7c_create_all_tables.py`
Cria todas as 9 tabelas + `alembic_version`.

---

## Etapa 1.3 — Autenticação

### Infraestrutura (`api/src/infrastructure/auth/`)

| Arquivo | Descrição |
|---------|-----------|
| `password_service.py` | bcrypt hash (cost 12) + verify |
| `jwt_service.py` | create_access_token (15min), create_refresh_token (7d), decode |

### Use Cases (`api/src/application/use_cases/auth/`)

| Use Case | Descrição |
|----------|-----------|
| `RegisterUserUseCase` | Valida email, verifica duplicidade, hasheia senha, cria user + tokens |
| `LoginUserUseCase` | Busca por email, verifica senha, retorna tokens |
| `RefreshTokenUseCase` | Valida refresh token, gera novo access token |

### Presentation (`api/src/presentation/`)

| Arquivo | Descrição |
|---------|-----------|
| `schemas/auth_schemas.py` | RegisterRequest, LoginRequest, TokenResponse, UserResponse |
| `api/middleware/auth_middleware.py` | `get_current_user_id()` — extrai user_id do JWT |
| `api/errors/handlers.py` | Error handlers para ValueError (400) e Exception (500) |
| `api/routers/auth_router.py` | Rotas: POST /register, POST /login, POST /refresh, GET /me |

### Testes

```bash
# Registrar
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Thyago","email":"thyago@email.com","password":"123456"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"thyago@email.com","password":"123456"}' | jq .tokens.access_token

# Me (com token)
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {token}"
```

---

## Etapa 1.4 — Categorias CRUD

### Use Cases (`api/src/application/use_cases/category/`)

| Use Case | Regras |
|----------|--------|
| `CreateCategoryUseCase` | Cria entidade + persiste |
| `ListCategoriesUseCase` | Lista por user_id, ordenado por nome |
| `UpdateCategoryUseCase` | Busca por id, atualiza nome |
| `DeleteCategoryUseCase` | Só deleta se não houver itens vinculados |

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/categories` | Criar categoria |
| GET | `/api/v1/categories` | Listar categorias do usuário |
| PUT | `/api/v1/categories/{id}` | Atualizar nome |
| DELETE | `/api/v1/categories/{id}` | Remover (se sem itens) |

---

## Arquivos Criados/Alterados (FASE 1)

```
api/src/
├── domain/
│   ├── entities/
│   │   ├── __init__.py              (atualizado)
│   │   ├── category.py              🆕
│   │   ├── inventory.py             🆕
│   │   ├── movement.py              🆕
│   │   ├── pre_registered_item.py   🆕
│   │   ├── shopping_list.py         🆕
│   │   ├── shopping_list_item.py    🆕
│   │   ├── stock.py                 🆕
│   │   ├── store.py                 🆕
│   │   └── user.py                  🆕
│   ├── value_objects/
│   │   ├── __init__.py              (atualizado)
│   │   ├── email.py                 🆕
│   │   ├── price.py                 🆕
│   │   └── unit.py                  🆕
│   └── interfaces/
│       ├── auth_service.py          🆕
│       ├── repository.py            🆕
│       └── unit_of_work.py          🆕
├── application/
│   ├── dtos/
│   │   ├── auth_dtos.py             🆕
│   │   └── category_dtos.py         🆕
│   └── use_cases/
│       ├── auth/
│       │   ├── register_user.py     🆕
│       │   ├── login_user.py        🆕
│       │   └── refresh_token.py     🆕
│       └── category/
│           ├── create_category.py   🆕
│           ├── list_categories.py   🆕
│           ├── update_category.py   🆕
│           └── delete_category.py   🆕
├── infrastructure/
│   ├── auth/
│   │   ├── jwt_service.py           🆕
│   │   └── password_service.py      🆕
│   └── database/
│       ├── models/
│       │   ├── __init__.py          (criado)
│       │   ├── category_model.py    🆕
│       │   ├── inventory_model.py   🆕
│       │   ├── item_model.py        🆕
│       │   ├── list_item_model.py   🆕
│       │   ├── list_model.py        🆕
│       │   ├── movement_model.py    🆕
│       │   ├── stock_model.py       🆕
│       │   ├── store_model.py       🆕
│       │   └── user_model.py        🆕
│       ├── repositories/
│       │   ├── __init__.py          (criado)
│       │   ├── base_repository.py   🆕
│       │   ├── category_repository.py 🆕
│       │   ├── inventory_repository.py 🆕
│       │   ├── item_repository.py   🆕
│       │   ├── list_repository.py   🆕
│       │   ├── movement_repository.py 🆕
│       │   ├── stock_repository.py  🆕
│       │   ├── store_repository.py  🆕
│       │   └── user_repository.py   🆕
│       ├── migrations/versions/
│       │   └── ace5ef00cc7c_create_all_tables.py 🆕
│       └── unit_of_work.py          🆕
└── presentation/
    ├── api/
    │   ├── errors/
    │   │   └── handlers.py          🆕
    │   ├── middleware/
    │   │   └── auth_middleware.py   🆕
    │   └── routers/
    │       ├── auth_router.py       🆕
    │       └── category_router.py   🆕
    └── schemas/
        ├── auth_schemas.py          🆕
        └── category_schemas.py      🆕
api/main.py                          (atualizado)
```

---

## Verificações Realizadas

| Check | Status |
|-------|--------|
| `alembic upgrade head` (10 tabelas criadas) | ✅ |
| `POST /api/v1/auth/register` | ✅ 201 + tokens |
| `POST /api/v1/auth/login` | ✅ 200 + tokens |
| `GET /api/v1/auth/me` | ✅ 200 + user data |
| `POST /api/v1/categories` | ✅ 201 |
| `GET /api/v1/categories` | ✅ 200 + lista |
| `PUT /api/v1/categories/{id}` | ✅ |
| `DELETE /api/v1/categories/{id}` | ✅ |
| Isolamento por usuário (outro user não vê categorias) | ✅ |
