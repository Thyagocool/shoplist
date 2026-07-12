# 🟢 FASE 0 — Setup do Projeto

**Status:** ✅ Concluída em 12/07/2026

---

## Objetivo

Preparar o ambiente de desenvolvimento completo: estrutura de pastas, Docker,
git, configurações de qualidade de código e esqueleto do backend e frontend.

---

## O que foi criado

### 📁 Estrutura de Diretórios

```
shoplist/
├── .gitignore
├── docker-compose.yml
├── DOCS/
│   ├── PLANO.MD
│   ├── EXECUCAO.MD
│   └── FASE-0-SETUP.md              ← Este arquivo
│
├── api/                              ← Backend FastAPI
│   ├── Dockerfile
│   ├── .env.example
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── config.py                     ← Settings via pydantic-settings
│   ├── main.py                       ← FastAPI app factory + health check
│   ├── data/                         ← Volume Docker para SQLite
│   ├── uploads/                      ← Volume Docker para fotos
│   └── src/
│       ├── domain/
│       │   ├── entities/             ← Entidades puras do domínio
│       │   ├── value_objects/        ← Value Objects (Email, Price, Unit)
│       │   └── interfaces/           ← Protocolos/ABCs (Repository, UnitOfWork)
│       ├── application/
│       │   ├── use_cases/            ← Casos de uso (auth, category, item…)
│       │   └── dtos/                 ← Data Transfer Objects
│       ├── infrastructure/
│       │   ├── database/
│       │   │   ├── models/           ← SQLAlchemy models
│       │   │   ├── repositories/     ← Implementações dos repositórios
│       │   │   └── migrations/       ← Alembic migrations
│       │   ├── auth/                 ← JWT + bcrypt
│       │   ├── storage/              ← Upload de arquivos
│       │   └── ocr/                  ← Tesseract OCR
│       └── presentation/
│           ├── api/
│           │   ├── routers/          ← FastAPI routers (cada recurso)
│           │   ├── middleware/       ← Auth middleware
│           │   └── errors/           ← Error handlers padronizados
│           └── schemas/              ← Pydantic request/response schemas
│   └── tests/
│       ├── unit/                     ← Testes unitários
│       └── integration/              ← Testes de integração
│
├── app/                              ← Frontend React + PWA
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts               ← Vite + PWA plugin + proxy API
│   ├── tsconfig.json
│   ├── tailwind.config.js            ← Tailwind CSS + cores personalizadas
│   ├── postcss.config.js
│   ├── index.html
│   ├── public/
│   │   ├── favicon.ico
│   │   └── icons/
│   │       ├── 192.png               ← PWA icon
│   │       └── 512.png               ← PWA icon
│   └── src/
│       ├── main.tsx                  ← Entry point React
│       ├── App.tsx                   ← Rotas + páginas placeholder
│       ├── index.css                 ← Tailwind + classes customizadas
│       ├── vite-env.d.ts
│       ├── components/
│       │   ├── ui/                   ← Button, Input, Modal, Badge…
│       │   ├── layout/               ← Header, BottomNav
│       │   ├── items/                ← ItemCard, ItemForm
│       │   ├── inventory/            ← InventoryForm, NeedsPreview
│       │   ├── list/                 ← ShoppingListItem, OfflineBanner
│       │   ├── camera/               ← CameraModal, PriceSuggestion
│       │   ├── stock/                ← StockCard, StockAlert
│       │   └── store/                ← StoreForm, StoreAutocomplete
│       ├── pages/                    ← Login, Register, Dashboard, Catalog…
│       ├── services/                 ← API clients (auth, item, list…)
│       ├── store/                    ← Zustand stores
│       ├── hooks/                    ← useCamera, useOffline, useAuth…
│       ├── types/                    ← TypeScript interfaces
│       └── utils/                    ← Formatadores, validadores
│
└── .git                              ← Git init com primeiro commit
```

### 🐳 Docker Compose

**`docker-compose.yml`** define dois serviços:

| Serviço | Porta | Proposito |
|---------|-------|-----------|
| `api`   | 8000  | FastAPI com hot reload, SQLite, Tesseract |
| `app`   | 5173  | Vite dev server com HMR, proxy `/api` → api |

Volumes nomeados para persistência: `api-data`, `api-uploads`.

### ⚙️ Backend — Configurações

- **`config.py`**: `pydantic-settings` lê de `.env` com fallback para defaults
- **`main.py`**: App factory com CORS, health check, static files
- **`pyproject.toml`**: Configurações do black, isort, mypy, ruff, pytest
- **`requirements.txt`**: FastAPI, SQLAlchemy async, Alembic, JWT, bcrypt, Pillow, pytesseract…

### 🎨 Frontend — Configurações

- **`vite.config.ts`**: React + PWA plugin + proxy para API + runtime caching
- **`tailwind.config.js`**: Cores primárias verde (`primary-50` a `primary-900`)
- **`index.css`**: Componentes Tailwind customizados (`.btn-primary`, `.input-field`, `.card`)
- **`App.tsx`**: Rotas iniciais com HomePage, LoginPage e RegisterPage (placeholders)

### 🖼️ PWA Icons

Ícones PNG sólidos (verde `#16a34a`) gerados via script Python para 192x192 e 512x512.

### 🧪 Testes

- `api/tests/unit/` — testes de entidades e value objects
- `api/tests/integration/` — testes de use cases e endpoints

---

## Verificações Realizadas

| Check | Status |
|-------|--------|
| `docker compose build api` | ✅ Build sem erros |
| `docker compose build app` | ✅ Build sem erros |
| `curl localhost:8000/health` | ✅ `{"status":"ok","version":"0.1.0"}` |
| `curl localhost:8000/docs` | ✅ Swagger UI disponível (200) |
| `curl localhost:5173` | ✅ Frontend servindo (200) |
| `git log --oneline` | ✅ 2 commits: inicialização + fix Dockerfile |

---

## Commits

```
ceae426 fix: ajusta Dockerfile do frontend para npm install com legacy-peer-deps
fa2be14 feat: inicializa projeto shoplist com estrutura backend/frontend
```

---

## Próxima Fase

**FASE 1 — Backend Core:** Entidades de domínio + value objects + interfaces.
