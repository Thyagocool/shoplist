# 🟢 FASE 3 — Frontend Core

**Status:** ✅ Concluída em 12/07/2026

---

## Etapas Executadas

| Etapa | Descrição | Status |
|-------|-----------|--------|
| 3.1 | Setup frontend (Vite, PWA, Router) — pré-existente | ✅ |
| 3.2 | API services + Auth store | ✅ |
| 3.3 | Telas Login + Cadastro | ✅ |

---

## Etapa 3.1 — Setup

Pré-existente da FASE 0. Stack:

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| React | 18.3 | UI |
| Vite | 6.4 | Build/Dev |
| TypeScript | 5.5 | Tipagem |
| Tailwind CSS | 3.4 | Estilização |
| React Router | 6.26 | Roteamento SPA |
| Zustand | 5.0 | Gerenciamento de estado |
| Axios | 1.7 | HTTP client |
| vite-plugin-pwa | 0.20 | PWA + Service Worker |
| idb | 8.0 | IndexedDB (offline) |

---

## Etapa 3.2 — API Services + Auth Store

### Arquitetura

```
app/src/
├── types/index.ts          → Interfaces TypeScript (backend mirror)
├── services/api.ts         → Axios instance + módulos de API
└── store/authStore.ts      → Zustand store de autenticação
```

### Tipos Compartilhados (`types/index.ts`)

Reflete todos os schemas do backend:

- `LoginRequest`, `RegisterRequest`, `TokenResponse`, `AuthResponse`, `UserResponse`
- `CategoryResponse`, `ItemResponse`, `StoreResponse`
- `InventoryResponse`
- `ListItemResponse`, `ShoppingListResponse`, `MovementResponse`, `CheckoutResponse`

### API Service (`services/api.ts`)

**Axios instance** configurada com:

- `baseURL: '/api/v1'` — usa proxy do Vite
- **Request interceptor:** anexa `Bearer {token}` do localStorage
- **Response interceptor:** auto-refresh em 401
  - Fila de requisições concorrentes durante refresh
  - Se refresh falhar, redireciona para `/login`

**Módulos exportados:**

| Módulo | Funções |
|--------|---------|
| `authAPI` | register, login, refresh, me |
| `categoriesAPI` | list, create, update, delete |
| `itemsAPI` | list, create, update, delete |
| `storesAPI` | list, create, update, delete |
| `inventoryAPI` | list, declare |
| `listsAPI` | list, get, create, addItem, toggleItem, complete, cancel, checkout |
| `ocrAPI` | upload |

### Auth Store (`store/authStore.ts`)

**Estado:**
- `user`, `isAuthenticated`, `isLoading`, `error`

**Ações:**
- `login(email, password)` — login + salva tokens + carrega user
- `register(name, email, password)` — cadastro + login automático
- `logout()` — limpa tokens + estado
- `loadUser()` — carrega user do `/me` (usado no refresh)
- `clearError()` — limpa mensagem de erro

**Persistência:** tokens no `localStorage`, `isAuthenticated` inicializado de `localStorage.getItem('access_token')`

---

## Etapa 3.3 — Telas Login + Cadastro

### Componentes UI

| Componente | Arquivo | Funcionalidades |
|------------|---------|-----------------|
| `Input` | `components/ui/Input.tsx` | Label, input, erro, focus ring |
| `Button` | `components/ui/Button.tsx` | Variantes (primary/secondary/danger), loading spinner |

### Layout

| Componente | Arquivo | Funcionalidades |
|------------|---------|-----------------|
| `ProtectedRoute` | `components/layout/ProtectedRoute.tsx` | Redireciona para `/login` se não autenticado |
| `Layout` | `components/layout/Layout.tsx` | Header vermelho com nome do usuário + botão Sair |

### Páginas

#### Login (`pages/Login.tsx`)
- Formulário: email + senha
- Validação de campos obrigatórios
- Exibe erro da API (ex: "Credenciais inválidas")
- Loading spinner durante requisição
- Link para cadastro
- Redireciona para `/` após sucesso

#### Register (`pages/Register.tsx`)
- Formulário: nome + email + senha (min 6 caracteres)
- Mesmo padrão de loading/erro do login
- Cadastra + loga automaticamente
- Redireciona para `/` após sucesso

#### Dashboard (`pages/Dashboard.tsx`)
- Saudação personalizada (`Olá, {nome}!`)
- **Stats:** cards com contagem de itens, lojas e listas
- **Listas Ativas:** cards clicáveis com progresso (checked/total)
- **Atalhos:** botões "Nova Lista" e "Catálogo"
- Carrega dados de `itemsAPI`, `storesAPI`, `listsAPI` em paralelo

### Roteamento (`App.tsx`)

```
/login          → Login (público, redireciona se logado)
/register       → Register (público, redireciona se logado)
/               → Dashboard (protegido)
/*              → Redirect para /
```

---

## Testes de Verificação

```bash
# Frontend servindo
curl -s http://localhost:5173 | head -5
# ✅ HTML com React + Vite

# Proxy para API
curl -s -X POST http://localhost:5173/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"thyago@email.com","password":"123456"}'
# ✅ 200 + tokens

# Build
cd app && npm run build
# ✅ 95 modules transformed, PWA gerado
```
