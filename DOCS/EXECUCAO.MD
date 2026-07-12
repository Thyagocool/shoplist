# 🏗️ Shoplist — Plano de Execução

> Passo a passo para implementar o projeto, do zero ao deploy.
> Cada etapa tem: **objetivo**, **arquivos envolvidos**, **o que implementar**
> e **como verificar**.

---

## 📊 Progresso Atual

| Fase | Status |
|------|--------|
| 🟢 **FASE 0** — Setup do Projeto | ✅ **Concluída** |
| 🟢 **FASE 0.5** — Banco de Dados (PostgreSQL) | ✅ **Concluída** |
| 🟢 **FASE 1** — Backend Core (entidades, auth, CRUDs) | ✅ **Concluída** |
| 🟢 **FASE 2** — Backend Features (itens, lojas, inventário, lista, checkout, OCR) | ✅ **Concluída** |
| 🟢 **FASE 3** — Frontend Core (Login, Cadastro, Dashboard) | ✅ **Concluída** |
| ⬜ FASE 4 — Frontend Features | ❌ Pendente |
| ⬜ FASE 5 — Finalização | ❌ Pendente |

**Progresso:** 7 de 24 etapas concluídas ✅ (~29%)

---

## 📐 Convenções e Metodologia

### Git Workflow
```
main           → produção (protegida)
  ├ develop    → integração
     ├ feat/backend-xxx   → branches de features do backend
     └ feat/frontend-xxx  → branches de features do frontend
```

- Commits pequenos e descritivos em português:
  `feat: adiciona entidade User com value object Email`
  `fix: validação de email duplicado no registro`

### TDD / Testes
- Use Cases testados com pytest + mock de repositórios
- Entidades testadas unitariamente (regras de negócio)
- Endpoints testados via TestClient (httpx)
- Frontend: testes de componente com Vitest + Testing Library

### Padrão de Código
- Black + isort para formatação
- Ruff para lint
- mypy strict mode no backend
- ESLint + Prettier no frontend

---

## 🗺️ Fases e Etapas

```
FASE 0: Setup              (1 etapa)
FASE 1: Backend Core        (etapas 2-5)
FASE 2: Backend Features    (etapas 6-12)
FASE 3: Frontend Core       (etapas 13-15)
FASE 4: Frontend Features   (etapas 16-20)
FASE 5: Finalização         (etapas 21-22)
```

---

## 🟢 FASE 0 — Setup do Projeto

### Etapa 0.1 — Inicialização

**Objetivo:** Preparar o ambiente, containers, git e estrutura de pastas.

**Arquivos a criar:**

```
shoplist/
├── .gitignore
├── docker-compose.yml
├── api/
│   ├── Dockerfile
│   ├── .env.example
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── main.py                  ← app factory + uvicorn
│   ├── config.py                ← settings via pydantic-settings
│   └── src/
│       ├── __init__.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── entities/
│       │   │   └── __init__.py
│       │   ├── value_objects/
│       │   │   └── __init__.py
│       │   └── interfaces/
│       │       └── __init__.py
│       ├── application/
│       │   ├── __init__.py
│       │   ├── use_cases/
│       │   │   └── __init__.py
│       │   └── dtos/
│       │       └── __init__.py
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── database/
│       │   │   ├── __init__.py
│       │   │   ├── models/
│       │   │   │   └── __init__.py
│       │   │   └── repositories/
│       │   │       └── __init__.py
│       │   ├── auth/
│       │   │   └── __init__.py
│       │   └── ocr/
│       │       └── __init__.py
│       └── presentation/
│           ├── __init__.py
│           ├── api/
│           │   ├── __init__.py
│           │   ├── routers/
│           │   │   └── __init__.py
│           │   ├── middleware/
│           │   │   └── __init__.py
│           │   └── errors/
│           │       └── __init__.py
│           └── schemas/
│               └── __init__.py
├── app/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── components/
│       │   └── ui/
│       ├── pages/
│       ├── services/
│       ├── store/
│       ├── hooks/
│       ├── types/
│       └── utils/
└── DOCS/
    ├── PLANO.MD
    └── EXECUCAO.MD
```

**`docker-compose.yml` — conteúdo mínimo:**
```yaml
version: '3.9'
services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    volumes:
      - ./api:/app
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/shoplist.db
      - JWT_SECRET=change-me
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  app:
    build: ./app
    ports:
      - "5173:5173"
    volumes:
      - ./app:/app
    depends_on:
      - api
    command: npm run dev
```

**`api/.env.example`:**
```
DATABASE_URL=sqlite+aiosqlite:///./data/shoplist.db
JWT_SECRET=super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
UPLOAD_DIR=./uploads
```

**Verificação:**
```bash
docker compose up -d
curl http://localhost:8000/docs    # Deve abrir Swagger
docker compose down
```

---

## 🟡 FASE 1 — Backend Core (Domínio + Infra Base)

### Etapa 1.1 — Entidades de Domínio + Value Objects

**Objetivo:** Implementar as entidades PURAS do domínio (sem dependência externa) e os value objects.

**Arquivos:** `api/src/domain/entities/*.py` e `api/src/domain/value_objects/*.py`

**O que implementar:**

#### `value_objects/email.py`
```python
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', self.value):
            raise ValueError(f"Email inválido: {self.value}")
```

#### `value_objects/price.py`
```python
@dataclass(frozen=True)
class Price:
    cents: int  # Preço em centavos

    @classmethod
    def from_float(cls, value: float) -> 'Price':
        return cls(cents=int(round(value * 100)))

    @classmethod
    def from_str_br(cls, value: str) -> 'Price':
        # "R$ 12,90" ou "12.90" ou "12,90"
        cleaned = value.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        return cls.from_float(float(cleaned))

    def to_float(self) -> float:
        return round(self.cents / 100, 2)

    def __str__(self) -> str:
        return f"R$ {self.to_float():.2f}".replace('.', ',')
```

#### `value_objects/unit.py`
```python
class Unit(str, Enum):
    KG = "kg"
    G = "g"
    L = "l"
    ML = "ml"
    UN = "un"
    PCT = "pct"
    CX = "cx"
    DZ = "dz"
```

#### Entidades:

**`entities/user.py`**
```python
@dataclass
class User:
    id: UUID
    name: str
    email: Email
    password_hash: str
    created_at: datetime
    updated_at: datetime
```

**`entities/category.py`** — id, name, user_id, created_at

**`entities/pre_registered_item.py`**
```python
@dataclass
class PreRegisteredItem:
    id: UUID
    name: str
    category_id: UUID
    default_unit: Unit
    default_quantity: Decimal
    min_stock: Decimal
    max_stock: Decimal
    user_id: UUID
    active: bool
    created_at: datetime
    updated_at: datetime
```

**`entities/store.py`** — id, name, user_id, created_at

**`entities/shopping_list.py`** — id, name, status (enum: pending/in_progress/completed/cancelled), user_id, created_at, completed_at

**`entities/shopping_list_item.py`** — id, shopping_list_id, pre_registered_item_id?, custom_name?, estimated_quantity, unit, checked, user_id, created_at

**`entities/movement.py`**
```python
@dataclass
class Movement:
    id: UUID
    sequential_code: str
    shopping_list_item_id: UUID | None
    pre_registered_item_id: UUID | None
    custom_name: str | None
    quantity: Decimal
    unit: Unit
    price_cents: int  # usa Price value object
    store_id: UUID | None
    store_name_snapshot: str | None
    photo_url: str | None
    notes: str | None
    user_id: UUID
    purchased_at: datetime
    created_at: datetime
```

**`entities/stock.py`** — id, pre_registered_item_id, current_quantity, last_price_cents?, last_store_id?, user_id, updated_at

**`entities/inventory.py`** — id, shopping_list_id, pre_registered_item_id, declared_quantity, calculated_need, user_id, created_at

#### `interfaces/repository.py` — Protocol/ABC genérico
```python
class Repository[T](ABC):
    @abstractmethod
    async def save(self, entity: T) -> T: ...
    @abstractmethod
    async def find_by_id(self, id: UUID) -> T | None: ...
    @abstractmethod
    async def delete(self, id: UUID) -> None: ...
```

#### `interfaces/unit_of_work.py`
```python
class UnitOfWork(ABC):
    @abstractmethod
    async def commit(self): ...
    @abstractmethod
    async def rollback(self): ...
    @abstractmethod
    async def __aenter__(self): ...
    @abstractmethod
    async def __aexit__(self, *args): ...
```

**Verificação:**
```bash
cd api && python -c "
from src.domain.value_objects.price import Price
p = Price.from_str_br('R$ 12,90')
assert p.cents == 1290
print(f'Price OK: {p}')
"
```

---

### Etapa 1.2 — Infraestrutura de Banco de Dados

**Objetivo:** SQLAlchemy models, engine, sessão, Alembic, repositórios.

**Arquivos:**
- `api/src/infrastructure/database/config.py` — engine + session factory
- `api/src/infrastructure/database/models/base.py` — Base declarativa
- `api/src/infrastructure/database/models/*.py` — Cada model
- `api/src/infrastructure/database/repositories/base_repository.py`
- `api/src/infrastructure/database/repositories/*.py`
- `api/src/infrastructure/database/unit_of_work.py`
- `api/alembic.ini` + `api/alembic/` + migrations

**O que implementar:**

1. **Base declarativa** com `id = UUID` padrão, `created_at`, `updated_at`
2. **SQLAlchemy models** espelhando as entidades (UserModel, CategoryModel, ItemModel, etc.)
3. **Config**: ler `DATABASE_URL` do env, criar engine async com `aiosqlite` (dev) / `asyncpg` (prod)
4. **BaseRepository[T, TModel]** genérico com CRUD básico
5. **Repositórios específicos** (Ex: `UserRepository.find_by_email()`)
6. **UnitOfWork** com session scope
7. **Alembic** configurado para gerar migrations automaticamente

**Modelos — regras importantes:**
- `users.email` → unique index
- `stock.pre_registered_item_id` → unique (1:1 com item)
- `movements.store_id` → FK para stores
- `pre_registered_items.active` → default True
- `default_unit` → VARCHAR(20) mapeando Unit enum

**Verificação:**
```bash
cd api && alembic upgrade head
# Deve criar todas as tabelas sem erro
python -c "
from src.infrastructure.database.config import get_session
import asyncio; asyncio.run(get_session())
print('DB conectado com sucesso')
"
```

---

### Etapa 1.3 — Autenticação (Auth)

**Objetivo:** Registro, login, JWT, refresh token, middleware.

**Arquivos:**
- `api/src/domain/interfaces/auth_service.py`
- `api/src/infrastructure/auth/jwt_service.py`
- `api/src/infrastructure/auth/password_service.py`
- `api/src/application/use_cases/auth/register_user.py`
- `api/src/application/use_cases/auth/login_user.py`
- `api/src/application/use_cases/auth/refresh_token.py`
- `api/src/application/dtos/auth_dtos.py`
- `api/src/presentation/schemas/auth_schemas.py`
- `api/src/presentation/api/routers/auth_router.py`
- `api/src/presentation/api/middleware/auth_middleware.py`
- `api/src/presentation/api/errors/handlers.py`

**O que implementar:**

1. **PasswordService** — hash com bcrypt, verify
2. **JWTService** — create_access_token (15min), create_refresh_token (7d), decode/verify
3. **Use Case RegisterUser:**
   - Validar email único
   - Hash da senha
   - Salvar User + criar Stock para cada item pré-cadastrado? (não, stock só quando tiver item)
   - Retornar tokens
4. **Use Case LoginUser:**
   - Buscar por email, verificar senha, gerar tokens
5. **Use Case RefreshToken:**
   - Validar refresh token, gerar novo access token
6. **AuthMiddleware** — extrai Bearer token, decodifica, injeta `user_id` no request state
7. **Error handlers** — 401, 403, 404, 422, 500 padronizados

**DTOS/Schemas:**
```python
# auth_schemas.py
class RegisterRequest(BaseModel):
    name: str = Field(max_length=120)
    email: str = Field(max_length=255)
    password: str = Field(min_length=6)

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

**Verificação:**
```bash
# Registrar
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Thyago","email":"thyago@email.com","password":"123456"}'
# → 201 + tokens

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"thyago@email.com","password":"123456"}'
# → 200 + tokens

# Me (com token)
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {access_token}"
# → 200 + dados do user
```

---

### Etapa 1.4 — Categorias CRUD

**Objetivo:** CRUD completo de categorias.

**Arquivos:**
- `api/src/application/use_cases/category/*.py`
- `api/src/application/dtos/category_dtos.py`
- `api/src/presentation/schemas/category_schemas.py`
- `api/src/presentation/api/routers/category_router.py`

**O que implementar:**
- CreateCategory (name, user_id)
- ListCategories (user_id)
- UpdateCategory (id, name)
- DeleteCategory (id) — só se não tiver itens vinculados

**Padrão dos Use Cases:**
```python
@dataclass
class CreateCategoryRequest:
    name: str
    user_id: UUID

class CreateCategoryUseCase:
    def __init__(self, repo: CategoryRepository, uow: UnitOfWork):
        ...

    async def execute(self, request: CreateCategoryRequest) -> CategoryDTO:
        category = Category(id=uuid4(), name=request.name, user_id=request.user_id, ...)
        await self.repo.save(category)
        await self.uow.commit()
        return CategoryDTO.from_entity(category)
```

**Verificação:**
```bash
# Criar
curl -X POST http://localhost:8000/api/v1/categories \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Carnes"}'
# Listar
curl http://localhost:8000/api/v1/categories \
  -H "Authorization: Bearer {token}"
```

---

## 🟠 FASE 2 — Backend Features

### Etapa 2.1 — Itens Pré-Cadastrados (Catálogo)

**Objetivo:** CRUD do catálogo pessoal com min/max stock e soft delete.

**Arquivos:**
- `api/src/application/use_cases/item/*.py` (create, list, update, deactivate)
- `api/src/application/dtos/item_dtos.py`
- `api/src/presentation/schemas/item_schemas.py`
- `api/src/presentation/api/routers/item_router.py`

**Regras:**
- Ao criar item, criar registro em `stock` com `current_quantity = 0`
- Soft delete: `active = False`, não deleta fisicamente
- Listagem filtra `active=True` por padrão
- Filtro por `category_id` opcional

**DTO de criação:**
```python
class CreateItemRequest(BaseModel):
    name: str = Field(max_length=120)
    category_id: UUID
    default_unit: Unit
    default_quantity: Decimal = Field(default=1, ge=0)
    min_stock: Decimal = Field(default=0, ge=0)
    max_stock: Decimal = Field(default=0, ge=0)
```

**Verificação:**
```bash
# Criar item
curl -X POST http://localhost:8000/api/v1/items \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Peito de Frango","category_id":"...","default_unit":"kg","max_stock":5}'
# Listar
curl http://localhost:8000/api/v1/items \
  -H "Authorization: Bearer {token}"
```

---

### Etapa 2.2 — Lojas CRUD

**Objetivo:** CRUD simples de lojas.

**Arquivos:**
- `api/src/application/use_cases/store/*.py`
- `api/src/application/dtos/store_dtos.py`
- `api/src/presentation/schemas/store_schemas.py`
- `api/src/presentation/api/routers/store_router.py`

**Implementação:** idêntico ao pattern de categorias, mais simples ainda (só name + user_id).

**Verificação:**
```bash
curl -X POST http://localhost:8000/api/v1/stores \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Supermercado X"}'
```

---

### Etapa 2.3 — Inventário (♥ coração do sistema)

**Objetivo:** O usuário declara o estoque atual → sistema calcula necessidades → gera lista.

**Arquivos:**
- `api/src/application/use_cases/inventory/preview_inventory.py`
- `api/src/application/use_cases/inventory/declare_inventory.py`
- `api/src/application/use_cases/inventory/generate_list_from_inventory.py`
- `api/src/application/dtos/inventory_dtos.py`
- `api/src/presentation/schemas/inventory_schemas.py`
- `api/src/presentation/api/routers/inventory_router.py`

**Fluxo dos use cases:**

#### `preview_inventory`
```python
# GET /api/v1/inventory/preview
# Para cada item ativo do catálogo, retorna:
#   {item_id, item_name, category, unit,
#    suggested_quantity (do stock automático),
#    min_stock, max_stock}
# O frontend usa isso para pré-preecher o formulário
```

#### `declare_inventory`
```python
# POST /api/v1/inventory/declare
# Body: {declarations: [{item_id, declared_quantity}]}
# Calcula para cada item: need = max(max_stock - declared_quantity, 0)
# Retorna: [{item_id, declared_quantity, need, will_be_added: need > 0}]
```

#### `generate_list_from_inventory`
```python
# POST /api/v1/inventory/generate-list
# Body: {declarations: [{item_id, declared_quantity}]}  # mesma estrutura
# 1. Salva cada declaration na tabela `inventory` com calculated_need
# 2. Cria `shopping_list` com status 'in_progress'
# 3. Para cada item com need > 0, cria `shopping_list_item`
# 4. Retorna a shopping_list completa com os itens
```

**Verificação:**
```bash
# Preview
curl http://localhost:8000/api/v1/inventory/preview \
  -H "Authorization: Bearer {token}"

# Declarar + calcular
curl -X POST http://localhost:8000/api/v1/inventory/declare \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"declarations":[{"item_id":"...","declared_quantity":2}]}'

# Gerar lista
curl -X POST http://localhost:8000/api/v1/inventory/generate-list \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"declarations":[{"item_id":"...","declared_quantity":2}]}'
```

---

### Etapa 2.4 — Lista de Compras + Checklist

**Objetivo:** Gerenciar os itens da lista, marcar como comprado.

**Arquivos:**
- `api/src/application/use_cases/shopping_list/*.py`
- `api/src/application/dtos/list_dtos.py`
- `api/src/presentation/schemas/list_schemas.py`
- `api/src/presentation/api/routers/list_router.py`

**Use cases:**
- `GetList` — retorna lista + itens com status
- `AddItemToList` — adiciona item avulso
- `UpdateListItem` — altera quantidade, marca/desmarca checked
- `RemoveItemFromList` — remove item da lista
- `UpdateListStatus` — renomear, mudar status

**Regras:**
- Itens com `pre_registered_item_id` podem ser "recarregados" com os defaults do catálogo
- Itens avulsos têm `custom_name` e `pre_registered_item_id = None`

**Verificação:**
```bash
# Ver lista (criada pelo inventário)
curl http://localhost:8000/api/v1/lists/{list_id} \
  -H "Authorization: Bearer {token}"

# Marcar item como comprado
curl -X PATCH http://localhost:8000/api/v1/lists/{list_id}/items/{item_id} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"checked":true}'

# Adicionar item avulso
curl -X POST http://localhost:8000/api/v1/lists/{list_id}/items \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"custom_name":"Pão de queijo","estimated_quantity":1,"unit":"pct"}'
```

---

### Etapa 2.5 — Checkout + Movimentações + Estoque

**Objetivo:** Finalizar compra (parcial ou total), criar movimentações, atualizar estoque.

**Arquivos:**
- `api/src/application/use_cases/movement/*.py`
- `api/src/application/use_cases/stock/*.py`
- `api/src/presentation/schemas/movement_schemas.py`
- `api/src/presentation/schemas/stock_schemas.py`
- `api/src/presentation/api/routers/movement_router.py`
- `api/src/presentation/api/routers/stock_router.py`

**Use cases:**

#### `checkout_list` (checkout parcial)
```python
# POST /api/v1/lists/{list_id}/checkout
# Pega TODOS os itens com checked=True da lista
# Para cada um, cria Movement:
#   - quantity, unit, price_cents, store_id, photo_url, notes
#   - pre_registered_item_id (se tiver), custom_name (se avulso)
#   - store_name_snapshot (copia o nome da store no momento)
#   - sequential_code = gera próximo código do user
# Atualiza Stock:
#   - stock.current_quantity += movement.quantity
#   - stock.last_price_cents = movement.price_cents
#   - stock.last_store_id = movement.store_id
# Marca os itens como "finalizados" (ou os remove)
# Se a lista não tiver mais itens pendentes, status = 'completed'
```

#### `close_list` (fechamento forçado)
```python
# POST /api/v1/lists/{list_id}/close
# Para itens NÃO comprados, cria movimentações com quantity = 0 (registro)
# Para itens comprados, fluxo normal do checkout
# Status da lista → 'completed'
```

#### `list_movements`
```python
# GET /api/v1/movements?from_date=&to_date=&item_id=&store_id=
# Filtros: data, item, loja
# Retorna lista paginada de movimentações
```

#### `register_movement` (manual)
```python
# POST /api/v1/movements
# Para registrar uma compra avulsa (sem lista vinculada)
# Cria movement + atualiza stock
```

#### `get_stock`
```python
# GET /api/v1/stock
# Retorna todos os itens com estoque, último preço, última loja
```

#### `get_alerts`
```python
# GET /api/v1/stock/alerts
# Retorna só os itens com current_quantity < min_stock
```

**Verificação:**
```bash
# Checkout parcial
curl -X POST http://localhost:8000/api/v1/lists/{list_id}/checkout \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{}'

# Ver estoque
curl http://localhost:8000/api/v1/stock \
  -H "Authorization: Bearer {token}"

# Ver alertas
curl http://localhost:8000/api/v1/stock/alerts \
  -H "Authorization: Bearer {token}"

# Histórico
curl http://localhost:8000/api/v1/movements \
  -H "Authorization: Bearer {token}"
```

---

### Etapa 2.6 — Upload de Foto + OCR

**Objetivo:** Upload de imagem, OCR para sugerir preço.

**Arquivos:**
- `api/src/infrastructure/storage/local_storage.py`
- `api/src/infrastructure/ocr/tesseract_service.py`
- `api/src/presentation/api/routers/upload_router.py`

**O que implementar:**

#### Upload
```python
# POST /api/v1/upload/photo
# Recebe multipart/form-data com field "file"
# Salva em UPLOAD_DIR com nome UUID + extensão
# Retorna {"url": "/uploads/uuid.jpg"}
```

#### OCR
```python
# POST /api/v1/ocr/price
# Recebe multipart/form-data com field "file" (ou JSON com "photo_url")
# 1. Abre imagem com Pillow
# 2. Tesseract OCR extrai texto
# 3. Regex busca padrões de preço:
#    - R$ 12,90 → 1290
#    - 12,90 → 1290
#    - R$10.99 → 1099
# 4. Retorna {"suggested_price_cents": 1290, "confidence": 0.85}
#    OU {"suggested_price_cents": null, "error": "Preço não encontrado"}
```

**Verificação:**
```bash
# Upload
curl -X POST http://localhost:8000/api/v1/upload/photo \
  -H "Authorization: Bearer {token}" \
  -F "file=@/tmp/foto-cupom.jpg"

# OCR
curl -X POST http://localhost:8000/api/v1/ocr/price \
  -H "Authorization: Bearer {token}" \
  -F "file=@/tmp/foto-preco.jpg"
# → {"suggested_price_cents": 1290, "confidence": 0.92}
```

---

## 🔵 FASE 3 — Frontend Core

### Etapa 3.1 — Setup Vite + PWA + Tailwind + Router

**Objetivo:** Base do frontend funcionando com PWA.

**`app/package.json`:**
```json
{
  "name": "shoplist",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.26.0",
    "zustand": "^5.0.0",
    "axios": "^1.7.0",
    "idb": "^8.0.0",
    "react-media-capture": "^1.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^6.0.0",
    "vite-plugin-pwa": "^0.20.0",
    "typescript": "^5.5.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

**`app/vite.config.ts`:**
```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'icons/*.png'],
      manifest: {
        name: 'Shoplist',
        short_name: 'Shoplist',
        description: 'Sua lista de compras inteligente',
        theme_color: '#16a34a',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          { src: 'icons/192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icons/512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
    }),
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': 'http://api:8000',
      '/uploads': 'http://api:8000',
    },
  },
})
```

**`app/src/main.tsx`:**
```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
```

**`app/src/App.tsx`:**
```tsx
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import CatalogPage from './pages/CatalogPage'
import InventoryPage from './pages/InventoryPage'
import ListDetailPage from './pages/ListDetailPage'
import StockPage from './pages/StockPage'
import StoresPage from './pages/StoresPage'
import HistoryPage from './pages/HistoryPage'
import ProfilePage from './pages/ProfilePage'
import Layout from './components/layout/Layout'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore(s => s.accessToken)
  return token ? <>{children}</> : <Navigate to="/login" />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/catalog" element={<CatalogPage />} />
        <Route path="/inventory" element={<InventoryPage />} />
        <Route path="/lists/:id" element={<ListDetailPage />} />
        <Route path="/stock" element={<StockPage />} />
        <Route path="/stores" element={<StoresPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Route>
    </Routes>
  )
}
```

**Layout com BottomNav:**
```tsx
// components/layout/Layout.tsx
import { Outlet } from 'react-router-dom'
import BottomNav from './BottomNav'
import OfflineBanner from '../list/OfflineBanner'

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50 pb-16">
      <OfflineBanner />
      <main className="max-w-lg mx-auto p-4">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  )
}
```

**Verificação:**
```bash
cd app && npm install && npm run dev
# Abrir http://localhost:5173 → deve ver a página (mesmo que vazia)
```

---

### Etapa 3.2 — Serviços API + Auth Store

**Objetivo:** Camada de comunicação com o backend + gerenciamento de autenticação.

**`app/src/services/api.ts`:**
```ts
import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const api = axios.create({
  baseURL: '/api/v1',
})

api.interceptors.request.use(config => {
  const token = useAuthStore.getState().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  async error => {
    if (error.response?.status === 401) {
      const refresh = useAuthStore.getState().refreshToken
      if (refresh) {
        try {
          const { data } = await axios.post('/api/v1/auth/refresh', { refresh_token: refresh })
          useAuthStore.getState().setTokens(data.access_token, data.refresh_token)
          error.config.headers.Authorization = `Bearer ${data.access_token}`
          return axios(error.config)
        } catch {
          useAuthStore.getState().logout()
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api
```

**`app/src/store/authStore.ts`:**
```ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  user: { id: string; name: string; email: string } | null
  accessToken: string | null
  refreshToken: string | null
  setTokens: (access: string, refresh: string) => void
  setUser: (user: AuthState['user']) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    set => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setTokens: (access, refresh) => set({ accessToken: access, refreshToken: refresh }),
      setUser: user => set({ user }),
      logout: () => set({ user: null, accessToken: null, refreshToken: null }),
    }),
    { name: 'auth-storage' }
  )
)
```

**Services:**
Criar `auth.service.ts`, `category.service.ts`, `item.service.ts`, `store.service.ts`, `inventory.service.ts`, `list.service.ts`, `movement.service.ts`, `stock.service.ts`, `upload.service.ts` — cada um com funções que chamam a API.

**Verificação:**
```ts
// Testar no console do navegador
import api from './services/api'
const res = await api.get('/auth/me')
console.log(res.data)
```

---

### Etapa 3.3 — Telas de Login + Cadastro

**Objetivo:** Tela de login e cadastro funcionando.

**`app/src/pages/LoginPage.tsx`:**
```tsx
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { login } from '../services/auth.service'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const setTokens = useAuthStore(s => s.setTokens)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const data = await login(email, password)
      setTokens(data.access_token, data.refresh_token)
      navigate('/')
    } catch (err) {
      setError('Email ou senha inválidos')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-bold text-center">Shoplist</h1>
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <input type="email" placeholder="Email" value={email}
          onChange={e => setEmail(e.target.value)} required
          className="w-full border rounded-lg p-3" />
        <input type="password" placeholder="Senha" value={password}
          onChange={e => setPassword(e.target.value)} required
          className="w-full border rounded-lg p-3" />
        <button type="submit" className="w-full bg-green-600 text-white rounded-lg p-3 font-semibold">
          Entrar
        </button>
        <p className="text-center text-sm">
          Não tem conta? <Link to="/register" className="text-green-600">Cadastre-se</Link>
        </p>
      </form>
    </div>
  )
}
```

**Verificação:**
- Abrir o app no navegador
- Ver tela de login
- Clicar em "Cadastre-se" → ir para registro
- Fazer cadastro → ser redirecionado ao dashboard
- Fazer logout → voltar ao login

---

## 🟣 FASE 4 — Frontend Features

### Etapa 4.1 — Dashboard + Catálogo + Lojas

**Objetivo:** Dashboard com resumo, CRUD de categorias/itens/lojas.

**DashboardPage.tsx:**
```tsx
// Cards com:
// - "Nova Lista" → vai pra InventoryPage
// - "Estoque" → vai pra StockPage
// - "Últimas Compras" → preview do histórico
// - Alertas de estoque baixo
// - Lista em andamento (se existir)
```

**CatalogPage.tsx:**
```tsx
// Tabs: Categorias | Itens | Lojas
// Categorias: lista + botão adicionar + modal/form
// Itens: lista agrupada por categoria + form com:
//   nome, categoria, unidade, qtd padrão, estoque min/max
// Lojas: lista simples + form
```

**Componentes:**
- `ItemCard.tsx` — card do item com nome, categoria, badge de unidade
- `ItemForm.tsx` — formulário com campos e validação
- `StoreForm.tsx` — formulário de loja
- `StoreAutocomplete.tsx` — input com sugestões

**Verificação:**
- Navegar no catálogo
- Criar categoria "Carnes"
- Criar item "Peito de Frango" (kg, min:1, max:5)
- Criar loja "Supermercado X"
- Ver itens listados no dashboard

---

### Etapa 4.2 — Inventário (Tela Principal)

**Objetivo:** Tela de inventário onde o usuário declara o estoque atual e gera a lista.

**InventoryPage.tsx — Fluxo:**

```
1. Ao entrar, chama GET /inventory/preview
   → Mostra lista de itens do catálogo com:
      [Nome Item] [un] [Estoque Atual (input)] [Mín] [Máx] [Necessidade]
   → Input já vem preenchido com o suggested_quantity

2. Usuário ajusta cada quantidade

3. Clica em "Calcular Necessidades"
   → Chama POST /inventory/declare
   → Mostra NeedsPreview:
      "Você precisa comprar:"
      - 4kg de Peito de Frango 🟢
      - 2kg de Arroz 🟢
      - (os itens sem necessidade somem)

4. Clica em "Gerar Lista de Compras"
   → Chama POST /inventory/generate-list
   → Redireciona para /lists/{id} (ListDetailPage)
```

**Componente `InventoryForm.tsx`:**
```tsx
// Recebe a lista de itens do preview
// Cada linha: nome, input numérico, badge min/max
// Botão "Calcular Necessidades" no final
```

**Componente `NeedsPreview.tsx`:**
```tsx
// Mostra os itens que precisam ser comprados
// Cada item: nome, quantidade necessária, unidade
// Botão "Confirmar e Gerar Lista"
```

**Verificação:**
```bash
# Fluxo completo:
# 1. Preview carrega itens
# 2. Digita estoque atual
# 3. Calcula necessidades
# 4. Gera lista
# 5. Redireciona pra lista
```

---

### Etapa 4.3 — Lista de Compras + Checklist Offline

**Objetivo:** Tela da lista funcionando offline.

**ListDetailPage.tsx:**
```tsx
// Header: nome da lista, status
// Lista de itens agrupados (checked / unchecked)
// Cada item:
//   [checkbox] Nome — Qtd necessária
//   Se checked: input preço, autocomplete loja, botão foto
// OfflineBanner no topo se estiver sem internet
// Botão "Finalizar Itens Marcados" (checkout parcial)
// Botão "Fechar Lista" (forçar fim)
```

**Componente `ShoppingListItem.tsx`:**
```tsx
// Props: item, onToggle, onPriceChange, onStoreChange, onPhoto
// Estados: normal, checked, saving, syncing
```

**Offline-first com IndexedDB (via `idb`):**
```ts
// hooks/useOffline.ts
// - Detecta navigator.onLine
// - Quando marca item como comprado offline:
//   1. Salva no IndexedDB (idb)
//   2. Mostra badge "pendente de sincronização"
// - Quando volta online:
//   1. Pega itens pendentes do IndexedDB
//   2. Envia para API
//   3. Remove do IndexedDB
```

**Verificação:**
```bash
# 1. Abrir lista no navegador
# 2. Desligar internet (DevTools → Network → Offline)
# 3. Marcar itens como comprado
# 4. Ligar internet → itens sincronizarem
# 5. Clicar em "Finalizar Itens Marcados"
# 6. Ver movimentações no histórico
```

---

### Etapa 4.4 — Câmera + OCR + Preço

**Objetivo:** Tirar foto e extrair preço.

**Componente `CameraModal.tsx`:**
```tsx
// Abre um modal fullscreen com a câmera
// Usa react-media-capture ou navigator.mediaDevices
// Botão para tirar foto
// Preview da foto
// Botão "Usar Foto" → faz upload + OCR
```

**Componente `PriceSuggestion.tsx`:**
```tsx
// Recebe o preço sugerido do OCR
// Mostra: "Preço sugerido: R$ 12,90"
// Botões: "Confirmar" | "Editar" | "Tentar Novamente"
// Input manual sempre visível
```

**Fluxo:**
```
1. Usuário clica no ícone de câmera no item da lista
2. Abre CameraModal → tira foto
3. Upload da foto → POST /upload/photo → recebe URL
4. OCR → POST /ocr/price → recebe sugestão
5. PriceSuggestion → usuário confirma ou edita
6. Preço salvo no item (e depois enviado no checkout)
```

**Verificação:**
- Clicar no ícone de câmera
- Tirar foto de um preço (ou usar imagem de teste)
- Ver sugestão de preço aparecer
- Confirmar e ver preço no item

---

### Etapa 4.5 — Estoque + Alertas + Histórico

**Objetivo:** Visualizar estoque, alertas e histórico de compras.

**StockPage.tsx:**
```tsx
// Lista de todos os itens com estoque
// Cada card:
//   [Nome] — Qtd atual [un]
//   Min: X | Max: Y
//   Última compra: R$ 22,90 no Super X
//   Badge: ✅ OK | ⚠️ Abaixo do mínimo | 🔴 Crítico
// Botão "Ajustar Estoque" (manual)
```

**StockAlert.tsx:**
```tsx
// Banner/destacado no dashboard
// "3 itens estão com estoque baixo"
// Lista: Nome — atual X (mín Y)
// Botão "Gerar Lista" → vai pro inventário
```

**HistoryPage.tsx:**
```tsx
// Filtros: mês, item, loja
// Lista de movimentações:
//   [Data] [Item] [Qtd] [Preço] [Loja] [Foto?]
// Agrupado por mês
// Total gasto no mês
```

**Verificação:**
- Ver estoque dos itens (atualizado após checkout)
- Ver alerta de estoque baixo no dashboard
- Ver histórico com movimentações
- Filtrar por mês

---

### Etapa 4.6 — Perfil + Ajustes

**Objetivo:** Tela de perfil e configurações.

**ProfilePage.tsx:**
```tsx
// Nome e email do usuário
// Botão "Editar Perfil"
// Botão "Sair" (logout)
// Versão do app
```

---

## 🔴 FASE 5 — Finalização

### Etapa 5.1 — Testes

**Backend:**
- `api/tests/unit/` — testes de entidades, value objects
- `api/tests/integration/` — testes de use cases (com DB de teste SQLite)
- `api/tests/conftest.py` — fixtures: test DB, client autenticado

**Frontend:**
- `app/src/**/*.test.tsx` — testes de componentes com Vitest
- Testes de store (Zustand)

**Verificação:**
```bash
cd api && pytest --cov=src --cov-report=term-missing
cd app && npm run test -- --coverage
```

---

### Etapa 5.2 — Docker + Deploy

**Objetivo:** Publicar no servidor.

**`api/Dockerfile`:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`app/Dockerfile` (multi-stage):**
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**`docker-compose.yml` (produção):**
```yaml
services:
  api:
    build: ./api
    env_file: .env.prod
    volumes:
      - data:/app/data
      - uploads:/app/uploads
    restart: unless-stopped

  app:
    build: ./app
    ports:
      - "80:80"
    depends_on:
      - api
    restart: unless-stopped

volumes:
  data:
  uploads:
```

**Verificação:**
```bash
# Build e deploy
docker compose -f docker-compose.prod.yml up -d --build
# Acessar http://{servidor}
```

---

## 📊 Resumo das Etapas

| # | Etapa | Depends On | Esforço | Status |
|---|-------|-----------|---------|--------|
| 0.1 | Setup do projeto | — | 1h | ✅ |
| 0.2 | Migração SQLite → PostgreSQL | 0.1 | 1h | ✅ |
| 1.1 | Entidades + Value Objects + Interfaces | 0.2 | 2h | ✅ |
| 1.2 | Infra banco (models, migrations, repos) | 1.1 | 2h | ✅ |
| 1.3 | Autenticação | 1.2 | 3h | ✅ |
| 1.4 | Categorias CRUD | 1.3 | 1h | ✅ |
| 2.1 | Itens (catálogo) | 1.4 | 2h | ✅ |
| 2.2 | Lojas CRUD | 1.3 | 1h | ✅ |
| 2.3 | Inventário (♥) | 2.1, 2.2 | 3h | ✅ |
| 2.4 | Lista + Checklist | 2.3 | 2h | ✅ |
| 2.5 | Checkout + Movimentos + Estoque | 2.4 | 3h | ✅ |
| 2.6 | Upload + OCR | 2.5 | 2h | ✅ |
| 3.1 | Setup frontend (Vite, PWA, Router) | 0.2 | 1h | ✅ |
| 3.2 | API services + Auth store | 3.1 | 1h | ✅ |
| 3.3 | Telas Login + Cadastro | 3.2 | 2h | ✅ |
| 4.1 | Dashboard + Catálogo + Lojas | 3.3, 1.4, 2.1, 2.2 | 4h | ❌ |
| 4.2 | Inventário (tela) | 4.1, 2.3 | 3h | ❌ |
| 4.3 | Lista + Checklist Offline | 4.1, 2.4 | 4h | ❌ |
| 4.4 | Câmera + OCR | 4.3, 2.6 | 3h | ❌ |
| 4.5 | Estoque + Alertas + Histórico | 4.1, 2.5 | 2h | ❌ |
| 4.6 | Perfil | 3.3 | 1h | ❌ |
| 5.1 | Testes | todas | 4h | ❌ |
| 5.2 | Docker + Deploy | 5.1 | 2h | ❌ |
| | **Total** | | **~49h** | |

---

## 🚦 Ritmo de Desenvolvimento Sugerido

```
Semana 1  → Etapas 0.1 até 1.4 (Setup + Core do Backend)
Semana 2  → Etapas 2.1 até 2.3 (Features do Backend)
Semana 3  → Etapas 2.4 até 2.6 + 3.1 (Backend final + Setup Frontend)
Semana 4  → Etapas 3.2 até 4.2 (Frontend: Auth + Catálogo + Inventário)
Semana 5  → Etapas 4.3 até 4.6 (Frontend: Lista + OCR + Estoque + Perfil)
Semana 6  → Etapas 5.1 e 5.2 (Testes + Deploy)
```

---

> **Progresso:** 15 de 24 etapas concluídas ✅ (~63%)
>
> **Próximo passo:** **FASE 4 — Frontend Features** (Dashboard completo, catálogo, lojas, inventário, lista, OCR).
> Base do frontend pronta com auth, API services e layout.
