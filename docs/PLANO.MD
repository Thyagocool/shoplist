# 🛒 Shoplist — Plano de Desenvolvimento

> Sistema de lista de compras mensais para casa, com controle de estoque,
> captura de preços por foto e gerenciamento por usuário.
>
> **Stack:** Python / FastAPI (backend) · React + PWA (frontend)

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Regras de Negócio](#2-regras-de-negócio)
3. [Arquitetura do Backend](#3-arquitetura-do-backend)
4. [Arquitetura do Frontend](#4-arquitetura-do-frontend)
5. [Modelagem do Banco de Dados](#5-modelagem-do-banco-de-dados)
6. [API — Endpoints](#6-api--endpoints)
7. [Autenticação](#7-autenticação)
8. [OCR — Captura de Preço por Foto](#8-ocr--captura-de-preço-por-foto)
9. [Fluxo Principal](#9-fluxo-principal)
10. [Estrutura de Diretórios](#10-estrutura-de-diretórios)
11. [Tecnologias e Dependências](#11-tecnologias-e-dependências)
12. [MVP vs Futuro](#12-mvp-vs-futuro)
13. [Próximos Passos](#13-próximos-passos)

---

## 1. Visão Geral

### 1.1 Problema
Organizar as compras do mês sem esquecer itens, controlar o que está em casa
(estoque), saber onde comprou cada coisa e por quanto, e evitar compras
desnecessárias.

### 1.2 Solução
Um PWA ( Progressive Web App ) que funciona como um app nativo no celular,
com:

- **Catálogo pessoal** de itens pré-cadastrados com estoque mínimo/máximo
- **Inventário manual** antes de cada compra: você digita o que tem em casa
- **Lista de necessidades** gerada automaticamente (só o que falta)
- **Captura de preço por foto** (OCR) na hora da compra
- **Controle de estoque** com último preço e local de compra
- **Lojas cadastradas** com autocomplete
- **Histórico de movimentações** com preço, quantidade, local e foto
- **Funciona offline** na hora da compra (checklist)
- **Login** com dados isolados por usuário

---

## 2. Regras de Negócio

### RN01 — Catálogo Pessoal
Cada usuário possui seu próprio catálogo de itens. Um item pertence a
exatamente um usuário.

### RN02 — Inventário (base da lista)
Antes de gerar a lista de compras, o usuário faz um **inventário manual**:
percorre a despensa e digita o estoque atual de cada item. O sistema calcula
a necessidade como `max_stock - estoque_atual`. Se o resultado for positivo,
o item entra na lista com essa quantidade.

### RN03 — Geração de Lista
A lista de compras é gerada **a partir do inventário**, não do catálogo bruto.
Itens com estoque acima do máximo ou zerados na necessidade **não** aparecem.
Ainda assim, o usuário pode adicionar itens avulsos manualmente.

### RN04 — Movimentação
Cada vez que o usuário compra um item, é registrada uma **movimentação**
com:
- ID único (UUID)
- Quantidade comprada
- Preço unitário ou total
- Local da compra (supermercado / loja) — referenciando tabela `stores`
- Data/hora
- Foto do cupom/produto (opcional)
- Notas

### RN05 — Estoque Automático + Última Compra
O estoque é atualizado **automaticamente** com base nas movimentações
(compra = entrada). Cada item de estoque guarda também o `last_price_cents`
e `last_store_id` para consulta rápida. O usuário define estoque **mínimo**
e **máximo** para cada item no catálogo.

### RN06 — Inventário vs Estoque Automático
O estoque automático (atualizado via movimentações) serve como referência,
mas **não é a fonte oficial** para gerar listas. A fonte oficial é o
inventário manual que o usuário faz antes de cada lista. Isso evita
divergências (ex: comeu algo sem registrar, deu um tanto pra alguém).

### RN07 — Unidade Padronizada
Toda quantidade usa uma unidade de um **enum fixo**: `kg`, `g`, `l`, `ml`,
`un`, `pct`, `cx`, `dz`. Não é permitido texto livre. Frontend usa dropdown,
backend valida contra o enum.

### RN08 — Lojas Cadastradas
O local da compra é referenciado por FK para a tabela `stores`, não texto
livre. O frontend oferece autocomplete com as lojas já usadas e permite
cadastrar nova na hora.

### RN09 — Isolamento por Usuário
Nenhum dado de um usuário é visível para outro. O filtro é feito pelo
`user_id` autenticado via JWT.

### RN10 — Checklist
Durante a compra, o usuário marca itens como "comprado". Pode finalizar
**parcialmente**: só os itens marcados viram movimentação; a lista continua
aberta pros pendentes. Fecha de vez quando todos estiverem comprados ou
quando o usuário solicitar.

### RN11 — Offline-first (checklist)
A tela de lista de compras + checklist deve funcionar **sem internet**.
Os dados são armazenados em cache local (Service Worker + IndexedDB).
Quando a conexão voltar, as alterações são sincronizadas com o backend.

### RN12 — Soft Delete de Itens
Um item desativado do catálogo **permanece** nas listas abertas (para não
quebrar o planejamento), mas não aparece em listas novas nem no inventário.

---

## 3. Arquitetura do Backend

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  (FastAPI routers, middlewares, Pydantic request/response)   │
└───────────────────┬─────────────────────────────────────────┘
                    │  chama use cases
┌───────────────────▼─────────────────────────────────────────┐
│                    Application Layer                         │
│  (Use Cases / Interactors, DTOs, ports/interfaces)          │
└───────────────────┬─────────────────────────────────────────┘
                    │  executa regras de negócio
┌───────────────────▼─────────────────────────────────────────┐
│                     Domain Layer                             │
│  (Entities, Value Objects, Domain Services, Repository       │
│   interfaces — sem dependência externa)                      │
└───────────────────┬─────────────────────────────────────────┘
                    │  persiste / consulta
┌───────────────────▼─────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  (SQLAlchemy models, repository implementations, JWT,        │
│   file storage, OCR service, migrations)                    │
└─────────────────────────────────────────────────────────────┘
```

### 3.1 Princípios

| Princípio | Aplicação |
|-----------|-----------|
| **DRY** | Repositórios genéricos (BaseRepository), handlers de erro centralizados, schemas reutilizáveis |
| **SOLID** | SRP (cada use case faz uma coisa), OCP (novos comportamentos via herança/implementação), LSP, ISP (interfaces pequenas), DIP (domínio não depende de infra) |
| **Clean Code** | Nomes significativos, funções pequenas, coesão, tratamento de erros consistente |
| **Clean Architecture** | Dependências apontam para dentro (domínio no centro, infra nas bordas) |
| **OO** | Entidades ricas com comportamento, não anêmicas; uso de composição |

---

## 4. Arquitetura do Frontend

```
┌────────────────────────────────────────────┐
│               PWA Shell                     │
│  (manifest.json, service worker, offline)  │
├────────────────────────────────────────────┤
│              Pages / Routes                │
│  Login / Cadastro / Home / Lista /         │
│  Inventário / Estoque / Histórico /        │
│  Lojas / Perfil                            │
├────────────────────────────────────────────┤
│            Components (reutilizáveis)       │
│  Header, BottomNav, ItemCard, CameraModal, │
│  PriceInput, StockBadge, LoadingState,     │
│  InventoryForm, StoreAutocomplete          │
├────────────────────────────────────────────┤
│           State Management (Zustand)        │
│  authStore / listStore / stockStore /      │
│  inventoryStore / storeStore               │
├────────────────────────────────────────────┤
│          Services / API Layer               │
│  Axios client, interceptors, auth refresh  │
├────────────────────────────────────────────┤
│            Hooks customizados               │
│  useCamera, useOCR, useGeolocation,        │
│  useDebounce, usePWA                       │
└────────────────────────────────────────────┘
```

- **Vite** como bundler (rápido, suporte nativo a PWA)
- **React Router v6** para navegação
- **Zustand** para estado global (leve, tipado, sem boilerplate)
- **Tailwind CSS** para estilização mobile-first
- **vite-plugin-pwa** para gerar service worker + manifest

---

## 5. Modelagem do Banco de Dados

### 5.1 Diagrama Conceitual

```
┌──────────┐       ┌──────────────────┐       ┌───────────────┐
│   User   │1────N│ PreRegisteredItem │       │   Store       │
└──────────┘       └──────────────────┘       └───────────────┘
     │                   │                           │
     │                   │                           │N
     │                   │                           │
     │                   ▼                           ▼
     │          ┌──────────────────┐       ┌────────────────────┐
     │          │     Stock        │       │   Movement         │
     │          │ (last_price,     │       │  (cada compra)     │
     │          │  last_store_id)  │       └────────────────────┘
     │          └──────────────────┘                ▲
     │                                               │
     │       ┌──────────────────┐                    │
     │       │  ShoppingList    │────────────────────┘
     │       └──────────────────┘        │N
     │               │1                  │
     │               │                   │
     │               ▼                   │
     │       ┌────────────────────┐      │
     │       │  ShoppingListItem  │──────┘
     │       └────────────────────┘
     │
     │       ┌──────────────────┐
     └──────│    Inventory     │
              └──────────────────┘
```

### 5.2 Tabelas Detalhadas

#### `users`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | |
| name | VARCHAR(120) | Nome do usuário |
| email | VARCHAR(255) UNIQUE | Login |
| password_hash | VARCHAR(255) | bcrypt |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

#### `categories`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | |
| name | VARCHAR(80) | Ex: "Carnes", "Higiene" |
| user_id | UUID FK → users | |
| created_at | TIMESTAMP | |

#### `pre_registered_items`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | |
| name | VARCHAR(120) | Ex: "Arroz Branco Tio João" |
| category_id | UUID FK → categories | |
| default_unit | VARCHAR(20) | "kg", "un", "pct", "l" |
| default_quantity | DECIMAL(10,2) | Quantidade padrão ao incluir na lista |
| min_stock | DECIMAL(10,2) | Estoque mínimo desejado |
| max_stock | DECIMAL(10,2) | Estoque máximo desejado |
| user_id | UUID FK → users | |
| active | BOOLEAN | Para desativar sem deletar |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

#### `shopping_lists`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | |
| name | VARCHAR(120) | Ex: "Compras Julho/2026" |
| status | ENUM('pending','in_progress','completed','cancelled') | |
| user_id | UUID FK → users | |
| created_at | TIMESTAMP | |
| completed_at | TIMESTAMP NULL | |

#### `shopping_list_items`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | |
| shopping_list_id | UUID FK → shopping_lists | |
| pre_registered_item_id | UUID FK → pre_registered_items NULL | NULL se for item avulso |
| custom_name | VARCHAR(120) NULL | Nome digitado na hora se avulso |
| estimated_quantity | DECIMAL(10,2) | Quantidade planejada |
| unit | VARCHAR(20) | |
| checked | BOOLEAN | Marcado como comprado |
| user_id | UUID FK → users | |
| created_at | TIMESTAMP | |

#### `stores`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | |
| name | VARCHAR(120) | Ex: "Supermercado X", "Açougue Y" |
| user_id | UUID FK → users | |
| created_at | TIMESTAMP | |

#### `movements`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | |
| sequential_code | VARCHAR(20) | Código amigável tipo `MOV-001` (auto-increment por usuário) |
| shopping_list_item_id | UUID FK → shopping_list_items NULL | |
| pre_registered_item_id | UUID FK → pre_registered_items NULL | |
| custom_name | VARCHAR(120) NULL | Se for item sem pré-cadastro |
| quantity | DECIMAL(10,2) | Quantidade comprada |
| unit | VARCHAR(20) | Enum fixo: kg, g, l, ml, un, pct, cx, dz |
| price_cents | INTEGER | Preço em centavos (evitar float) |
| store_id | UUID FK → stores NULL | Local da compra (FK, não texto livre) |
| store_name_snapshot | VARCHAR(120) NULL | Nome da loja no momento da compra (congelado) |
| photo_url | TEXT NULL | URL da foto do cupom/produto |
| notes | TEXT NULL | Observações |
| user_id | UUID FK → users | |
| purchased_at | TIMESTAMP | Data/hora da compra |
| created_at | TIMESTAMP | |

> **Nota:** `store_name_snapshot` congela o nome da loja no momento da compra,
> para que o histórico não mude se o usuário renomear a loja depois.

#### `stock`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | |
| pre_registered_item_id | UUID FK → pre_registered_items UNIQUE | |
| current_quantity | DECIMAL(10,2) | Quantidade atual em casa |
| last_price_cents | INTEGER NULL | Último preço pago |
| last_store_id | UUID FK → stores NULL | Onde comprou da última vez |
| user_id | UUID FK → users | |
| updated_at | TIMESTAMP | |

#### `inventory`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | |
| shopping_list_id | UUID FK → shopping_lists | Vinculado à lista que será gerada |
| pre_registered_item_id | UUID FK → pre_registered_items | |
| declared_quantity | DECIMAL(10,2) | Quantidade que o usuário DIGITOU que tem em casa |
| calculated_need | DECIMAL(10,2) | `max_stock - declared_quantity` (se > 0, vira item na lista) |
| user_id | UUID FK → users | |
| created_at | TIMESTAMP | |

### 5.3 Observações sobre o Modelo

- `pre_registered_items` é o **catálogo pessoal** do usuário.
- `stores` é uma tabela separada com autocomplete. Na `movement`, o nome
  da loja é congelado via `store_name_snapshot` pra não quebrar histórico.
- `inventory` é o coração do fluxo: o usuário declara o que tem em casa,
  o sistema calcula a necessidade e gera a lista. O estoque automático
  (`stock`) serve como referência, mas não substitui o inventário manual.
- Cada `movement` representa uma **compra real** de um item. É a tabela de
  movimentação financeira/estoque.
- `stock` é atualizado via **evento** sempre que um movement é criado:
  `stock.current_quantity += movement.quantity`;
  `stock.last_price_cents = movement.price_cents`;
  `stock.last_store_id = movement.store_id`.
- Preço em centavos (`price_cents`) evita problemas de ponto flutuante.
- Unidade de medida é um **enum fixo**: `kg`, `g`, `l`, `ml`, `un`, `pct`,
  `cx`, `dz`. Nada de texto livre — frontend usa dropdown, backend valida.

---

## 6. API — Endpoints

### 6.1 Autenticação

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/auth/register` | Cadastro (name, email, password) |
| POST | `/api/v1/auth/login` | Login → retorna access + refresh token |
| POST | `/api/v1/auth/refresh` | Renova access token |
| GET | `/api/v1/auth/me` | Dados do usuário logado |

### 6.2 Categorias

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/categories` | Listar categorias do usuário |
| POST | `/api/v1/categories` | Criar categoria |
| PUT | `/api/v1/categories/{id}` | Atualizar |
| DELETE | `/api/v1/categories/{id}` | Remover (se sem itens) |

### 6.3 Itens Pré-Cadastrados (Catálogo)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/items` | Listar todos (com filtro por categoria, active) |
| POST | `/api/v1/items` | Criar item |
| PUT | `/api/v1/items/{id}` | Atualizar (incluindo min/max stock) |
| DELETE | `/api/v1/items/{id}` | Desativar (soft delete) |

### 6.4 Lojas

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/stores` | Listar lojas do usuário |
| POST | `/api/v1/stores` | Cadastrar loja |
| PUT | `/api/v1/stores/{id}` | Atualizar |
| DELETE | `/api/v1/stores/{id}` | Remover |

### 6.5 Inventário (antes de criar a lista)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/inventory/preview` | Lista os itens do catálogo com estoque atual (preenchido automaticamente como sugestão) |
| POST | `/api/v1/inventory/declare` | Envia o inventário: `[{item_id, declared_quantity}]` → retorna cálculo de necessidades |
| POST | `/api/v1/inventory/generate-list` | Confirma o inventário e **gera a lista de compras** com os itens necessários |

### 6.6 Listas de Compras

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/lists` | Listar listas do usuário |
| GET | `/api/v1/lists/{id}` | Detalhes + itens da lista |
| PATCH | `/api/v1/lists/{id}` | Renomear, atualizar status |
| POST | `/api/v1/lists/{id}/checkout` | **Checkout parcial:** finaliza só os itens marcados |
| POST | `/api/v1/lists/{id}/close` | Força fechamento da lista (mesmo com pendentes) |
| DELETE | `/api/v1/lists/{id}` | Remover lista |

### 6.7 Itens da Lista

| Método | Rota | Descrição |
|--------|------|-----------|
| PATCH | `/api/v1/lists/{list_id}/items/{item_id}` | Marcar/desmarcar checked, alterar qtd |
| POST | `/api/v1/lists/{list_id}/items` | Adicionar item avulso à lista |
| DELETE | `/api/v1/lists/{list_id}/items/{item_id}` | Remover item da lista |

### 6.8 Movimentações (Compras)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/movements` | Histórico de compras (filtro por data, item, loja) |
| POST | `/api/v1/movements` | Registrar uma compra manual |
| GET | `/api/v1/movements/{id}` | Detalhes de uma movimentação |
| DELETE | `/api/v1/movements/{id}` | Estornar (remove e ajusta estoque) |

### 6.9 Estoque

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/stock` | Estoque atual do usuário (com last_price e last_store) |
| GET | `/api/v1/stock/alerts` | Itens abaixo do mínimo |
| PATCH | `/api/v1/stock/{item_id}` | Ajuste manual de estoque |

### 6.10 Upload + OCR

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/upload/photo` | Faz upload da foto → retorna URL |
| POST | `/api/v1/ocr/price` | Envia foto → retorna preço **sugerido** (usuário confirma) |

---

## 7. Autenticação

### 7.1 Fluxo

```
Usuário → [POST /auth/login] → Backend valida credenciais
                              → Gera Access Token (JWT, 15min)
                              → Gera Refresh Token (JWT, 7 dias)
                              → Retorna ambos

Frontend armazena no httpOnly cookie (refresh) e memória (access)
Ou, para PWA: localStorage com interceptors renovando automaticamente
```

### 7.2 Segurança

- Senhas hash com **bcrypt** (cost = 12)
- JWT com **HS256** e secret por env var
- Refresh token rotation
- Middleware `AuthMiddleware` valida token em todas as rotas protegidas
- `user_id` extraído do token é injetado no request → usado em todos os
  repositórios como filtro obrigatório

---

## 8. OCR — Captura de Preço por Foto

### 8.1 Estratégia MVP

> ⚠️ **OCR é um helper, não a fonte principal.** O usuário sempre pode
> digitar o preço manualmente. O OCR serve para agilizar, mas nunca é
> obrigatório.

- O usuário tira uma foto do produto ou cupom fiscal
- A imagem é enviada para o backend
- Usamos **Tesseract OCR** (pytesseract) para extrair texto da imagem
- Um algoritmo simples procura por padrões de preço (`R$ 12,90`, `12,90`, `R$ 10.99`)
- O preço é **sugerido** ao usuário, que pode confirmar ou editar
- Dois fluxos sempre disponíveis: **manual** (digita o preço) e **OCR** (foto → sugestão)

### 8.2 Fluxo

```
[Camera] → [Preview] → [Confirma] → POST /upload/photo
                                    → POST /ocr/price
                                    → Retorna preço sugerido
                                    → Usuário confirma OU edita
                                    → POST /movements (com price)

        ─ ou ─

[Digita preço manualmente] → POST /movements (com price)
```

### 8.3 Evolução Futura

- Substituir Tesseract por API de IA (Google Vision, AWS Textract)
- Reconhecimento específico de cupom fiscal brasileiro (SAT, NFC-e)

---

## 9. Fluxo Principal

### 9.1 Primeiro Acesso

```
1. Usuário acessa o PWA → tela de login
2. Clica em "Cadastrar" → preenche nome, email, senha
3. É redirecionado ao Dashboard (vazio)
4. Clica em "Configurar Catálogo" → adiciona categorias e itens
   Ex: Categoria "Carnes" → Item "Peito de Frango" (kg, min:1, max:5)
5. Cadastra algumas lojas que frequenta (opcional, pode fazer depois)
6. Pronto! Pode gerar a primeira lista
```

### 9.2 Preparando a Compra do Mês (com Inventário)

```
1. No Dashboard, clica em "Nova Lista"
2. Sistema pergunta: "Vamos fazer o inventário?"
   → Abre a tela de inventário com todos os itens ativos do catálogo
   → Cada item já vem com o estoque atual sugerido (puxado do stock automático)
3. Usuário percorre a despensa e ajusta as quantidades:
   - Arroz: tem 2kg em casa → digita 2
   - Feijão: acabou → digita 0
   - Creme dental: tem 1 → digita 1
4. Clica em "Calcular Necessidades"
   → Sistema calcula: necessidade = max_stock - declared_quantity
   → Mostra preview: "Você precisa comprar: 3kg de Arroz, 2kg de Feijão..."
   → Itens com necessidade = 0 são ocultados (mas podem ser reinseridos)
5. Confirma → sistema gera a lista de compras
```

### 9.3 No Mercado (Checklist + Preço)

```
1. Abre a lista no celular (funciona OFFLINE 📡)
2. Cada item mostra: nome, qtd necessária, checkbox, campo de preço, loja
3. Conforme pega os produtos:
   - Marca "Arroz" como comprado ✓
   - Digita o preço R$ 22,90 (ou tira foto → OCR sugere → confirma)
   - Seleciona a loja "Supermercado X" (autocomplete)
   - Opcional: tira foto do cupom/produto
4. A cada item marcado, o frontend salva no cache local
5. Ao final, clica em "Finalizar Itens Marcados" (checkout parcial)
   → Cria movimentações SÓ dos itens marcados
   → Lista continua aberta com os pendentes
```

### 9.4 Finalização e Estoque

```
1. Quando voltar ao mercado pra pegar o resto (ou desistir):
   - Clica em "Fechar Lista" → força o fechamento
   - Itens não comprados viram movimentações com quantity = 0 (apenas registro)
2. Sistema automaticamente:
   - Cria as movimentações
   - Atualiza stock.current_quantity (+= quantity comprada)
   - Atualiza stock.last_price_cents e stock.last_store_id
3. Lista vai pra "Histórico" com status "completed"
```

### 9.5 Consulta e Planejamento

```
1. Abre "Estoque" → vê todos os itens com quantidade atual, último preço e loja
   → Arroz: 3kg (mín 2kg, máx 5kg) ✅ — última compra: R$ 22,90 no Super X
   → Feijão: 0.5kg (mín 1kg) ⚠️ — última compra: R$ 8,50 no Super Y
2. Abre "Histórico" → filtro por mês, item ou loja
   → Vê evolução de preços do arroz nos últimos meses
3. Decide fazer nova lista → fluxo do inventário novamente
   → Inventário já sugere os valores atuais do estoque
   → Só ajusta o que mudou desde a última compra
```

---

## 10. Estrutura de Diretórios

```
shoplist/
├── DOCS/
│   └── PLANO.MD                    ← Este arquivo
│
├── api/                            ← Backend FastAPI
│   ├── src/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   ├── category.py
│   │   │   │   ├── pre_registered_item.py
│   │   │   │   ├── shopping_list.py
│   │   │   │   ├── shopping_list_item.py
│   │   │   │   ├── movement.py
│   │   │   │   ├── stock.py
│   │   │   │   ├── store.py
│   │   │   │   └── inventory.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── email.py
│   │   │   │   ├── price.py
│   │   │   │   └── unit.py  ← Enum: kg, g, l, ml, un, pct, cx, dz
│   │   │   └── interfaces/
│   │   │       ├── __init__.py
│   │   │       ├── repository.py
│   │   │       ├── auth_service.py
│   │   │       └── unit_of_work.py
│   │   │
│   │   ├── application/
│   │   │   ├── use_cases/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth/
│   │   │   │   │   ├── register_user.py
│   │   │   │   │   ├── login_user.py
│   │   │   │   │   └── refresh_token.py
│   │   │   │   ├── category/
│   │   │   │   │   ├── create_category.py
│   │   │   │   │   ├── list_categories.py
│   │   │   │   │   ├── update_category.py
│   │   │   │   │   └── delete_category.py
│   │   │   │   ├── item/
│   │   │   │   │   ├── create_item.py
│   │   │   │   │   ├── list_items.py
│   │   │   │   │   ├── update_item.py
│   │   │   │   │   └── deactivate_item.py
│   │   │   │   ├── shopping_list/
│   │   │   │   │   ├── create_list.py
│   │   │   │   │   ├── get_list.py
│   │   │   │   │   ├── update_list_status.py
│   │   │   │   │   ├── add_item_to_list.py
│   │   │   │   │   └── remove_item_from_list.py
│   │   │   │   ├── store/
│   │   │   │   │   ├── create_store.py
│   │   │   │   │   ├── list_stores.py
│   │   │   │   │   ├── update_store.py
│   │   │   │   │   └── delete_store.py
│   │   │   │   ├── inventory/
│   │   │   │   │   ├── preview_inventory.py
│   │   │   │   │   ├── declare_inventory.py
│   │   │   │   │   └── generate_list_from_inventory.py
│   │   │   │   ├── movement/
│   │   │   │   │   ├── register_movement.py
│   │   │   │   │   ├── checkout_list.py
│   │   │   │   │   └── list_movements.py
│   │   │   │   └── stock/
│   │   │   │       ├── get_stock.py
│   │   │   │       ├── get_alerts.py
│   │   │   │       └── adjust_stock.py
│   │   │   └── dtos/
│   │   │       ├── __init__.py
│   │   │       ├── auth_dtos.py
│   │   │       ├── category_dtos.py
│   │   │       ├── item_dtos.py
│   │   │       ├── store_dtos.py
│   │   │       ├── inventory_dtos.py
│   │   │       ├── list_dtos.py
│   │   │       ├── movement_dtos.py
│   │   │       └── stock_dtos.py
│   │   │
│   │   ├── infrastructure/
│   │   │   ├── database/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py
│   │   │   │   ├── models/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── base.py
│   │   │   │   │   ├── user_model.py
│   │   │   │   │   ├── category_model.py
│   │   │   │   │   ├── item_model.py
│   │   │   │   │   ├── list_model.py
│   │   │   │   │   ├── list_item_model.py
│   │   │   │   │   ├── movement_model.py
│   │   │   │   │   ├── stock_model.py
│   │   │   │   │   ├── store_model.py
│   │   │   │   │   └── inventory_model.py
│   │   │   │   ├── repositories/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── base_repository.py
│   │   │   │   │   ├── user_repository.py
│   │   │   │   │   ├── category_repository.py
│   │   │   │   │   ├── item_repository.py
│   │   │   │   │   ├── store_repository.py
│   │   │   │   │   ├── inventory_repository.py
│   │   │   │   │   ├── list_repository.py
│   │   │   │   │   ├── movement_repository.py
│   │   │   │   │   └── stock_repository.py
│   │   │   │   ├── migrations/        ← Alembic
│   │   │   │   └── unit_of_work.py
│   │   │   ├── auth/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── jwt_service.py
│   │   │   │   └── password_service.py
│   │   │   ├── storage/
│   │   │   │   ├── __init__.py
│   │   │   │   └── local_storage.py
│   │   │   └── ocr/
│   │   │       ├── __init__.py
│   │   │       └── tesseract_service.py
│   │   │
│   │   └── presentation/
│   │       ├── __init__.py
│   │       ├── api/
│   │       │   ├── __init__.py
│   │       │   ├── app.py              ← FastAPI app factory
│   │       │   ├── routers/
│   │       │   │   ├── __init__.py
│   │       │   │   ├── auth_router.py
│   │       │   │   ├── category_router.py
│   │   │   │   ├── item_router.py
│   │   │   │   ├── store_router.py
│   │   │   │   ├── inventory_router.py
│   │   │   │   ├── list_router.py
│   │   │   │   ├── movement_router.py
│   │   │   │   ├── stock_router.py
│   │   │   │   └── upload_router.py
│   │       │   ├── middleware/
│   │       │   │   ├── __init__.py
│   │       │   │   └── auth_middleware.py
│   │       │   └── errors/
│   │       │       ├── __init__.py
│   │       │       └── handlers.py
│   │       └── schemas/
│   │           ├── __init__.py
│   │           ├── auth_schemas.py
│   │           ├── category_schemas.py
│   │           ├── item_schemas.py
│   │           ├── store_schemas.py
│   │           ├── inventory_schemas.py
│   │           ├── list_schemas.py
│   │           ├── movement_schemas.py
│   │           └── stock_schemas.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   │
│   ├── alembic.ini
│   ├── config.py
│   ├── main.py                       ← Entrypoint: uvicorn
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── app/                              ← Frontend React + PWA
│   ├── public/
│   │   ├── manifest.json
│   │   ├── icons/                    ← Ícones do PWA (192x192, 512x512)
│   │   ├── favicon.ico
│   │   └── service-worker.js
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                   ← Componentes atômicos
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Badge.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── LoadingSpinner.tsx
│   │   │   │   └── EmptyState.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── BottomNav.tsx
│   │   │   │   └── PageContainer.tsx
│   │   │   ├── items/
│   │   │   │   ├── ItemCard.tsx
│   │   │   │   ├── ItemForm.tsx
│   │   │   │   └── ItemList.tsx
│   │   │   ├── inventory/
│   │   │   │   ├── InventoryForm.tsx      ← Lista de itens pra declarar estoque
│   │   │   │   ├── InventoryRow.tsx       ← Linha com nome + input de qtd
│   │   │   │   └── NeedsPreview.tsx       ← Preview do cálculo de necessidade
│   │   │   ├── list/
│   │   │   │   ├── ShoppingListItem.tsx
│   │   │   │   ├── ListHeader.tsx
│   │   │   │   ├── CheckoutButton.tsx
│   │   │   │   └── OfflineBanner.tsx      ← Mostra status offline/online
│   │   │   ├── camera/
│   │   │   │   ├── CameraModal.tsx
│   │   │   │   ├── PhotoPreview.tsx
│   │   │   │   └── PriceSuggestion.tsx
│   │   │   ├── stock/
│   │   │   │   ├── StockCard.tsx
│   │   │   │   └── StockAlert.tsx
│   │   │   └── store/
│   │   │       ├── StoreForm.tsx
│   │   │       └── StoreAutocomplete.tsx
│   │   │
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── CatalogPage.tsx
│   │   │   ├── InventoryPage.tsx          ← Inventário pré-lista
│   │   │   ├── ListDetailPage.tsx
│   │   │   ├── StockPage.tsx
│   │   │   ├── StoresPage.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   └── ProfilePage.tsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts                ← Axios instance + interceptors
│   │   │   ├── auth.service.ts
│   │   │   ├── category.service.ts
│   │   │   ├── item.service.ts
│   │   │   ├── store.service.ts
│   │   │   ├── inventory.service.ts
│   │   │   ├── list.service.ts
│   │   │   ├── movement.service.ts
│   │   │   ├── stock.service.ts
│   │   │   └── upload.service.ts
│   │   │
│   │   ├── store/
│   │   │   ├── authStore.ts
│   │   │   ├── listStore.ts
│   │   │   ├── inventoryStore.ts
│   │   │   ├── stockStore.ts
│   │   │   └── storeStore.ts
│   │   │
│   │   ├── hooks/
│   │   │   ├── useCamera.ts
│   │   │   ├── useOCR.ts
│   │   │   ├── useAuth.ts
│   │   │   ├── usePWA.ts
│   │   │   ├── useOffline.ts           ← Detecta status + sincroniza
│   │   │   └── useStoreAutocomplete.ts
│   │   │
│   │   ├── types/
│   │   │   ├── user.ts
│   │   │   ├── item.ts
│   │   │   ├── store.ts
│   │   │   ├── inventory.ts
│   │   │   ├── list.ts
│   │   │   ├── movement.ts
│   │   │   └── stock.ts
│   │   │
│   │   ├── utils/
│   │   │   ├── format.ts
│   │   │   ├── storage.ts
│   │   │   └── validators.ts
│   │   │
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── index.css
│   │   └── vite-env.d.ts
│   │
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 11. Tecnologias e Dependências

### 11.1 Backend (`api/`)

| Pacote | Versão (aprox.) | Motivo |
|--------|----------------|--------|
| Python | 3.12+ | Tipagem moderna, performance |
| FastAPI | 0.115+ | Performance async, OpenAPI automático |
| uvicorn | 0.30+ | ASGI server |
| SQLAlchemy | 2.0+ | ORM maduro, assíncrono |
| Alembic | 1.13+ | Migrations |
| Pydantic | 2.0+ | Validação de schemas |
| PyJWT | 2.9+ | JWT tokens |
| bcrypt | 4.1+ | Hash de senha |
| python-multipart | 0.0.9+ | Upload de fotos |
| aiofiles | 24.1+ | IO assíncrono de arquivos |
| Pillow | 10+ | Processamento de imagem |
| pytesseract | 0.3.10+ | OCR |
| python-dotenv | 1.0+ | Env vars |
| pytest | 8+ | Testes |
| httpx | 0.27+ | Testes async com TestClient |

### 11.2 Frontend (`app/`)

| Pacote | Versão (aprox.) | Motivo |
|--------|----------------|--------|
| React | 18+ | UI |
| TypeScript | 5+ | Tipagem |
| Vite | 6+ | Bundler rápido |
| vite-plugin-pwa | 0.20+ | PWA service worker |
| React Router | 6+ | Rotas |
| Zustand | 5+ | Estado global |
| Axios | 1.7+ | HTTP client |
| Tailwind CSS | 3+ | Estilização utility-first |
| react-media-capture | — | Captura de câmera |
| idb | 8+ | IndexedDB wrapper para cache offline |
| workbox-window | 7+ | Gerenciamento do service worker |

### 11.3 Infra

| Ferramenta | Uso |
|------------|-----|
| Docker / docker-compose | Containerização |
| SQLite (dev) / PostgreSQL (prod) | Banco de dados |
| Servidor cloud (próprio) | Deploy |

---

## 12. MVP vs Futuro

### ✅ MVP (Fase 1)
- [x] Autenticação (cadastro, login, JWT, refresh token)
- [x] CRUD de categorias
- [x] CRUD de itens pré-cadastrados (catálogo com min/max stock)
- [x] CRUD de lojas (stores)
- [x] **Inventário manual** antes de gerar a lista (declara estoque atual)
- [x] **Cálculo de necessidades** baseado em `max_stock - declared_quantity`
- [x] Geração de lista de compras a partir do inventário
- [x] Adição de itens avulsos na lista
- [x] Checklist na lista (marcar como comprado) — **offline-first**
- [x] Finalização **parcial** (checkout só dos marcados)
- [x] Criação de movimentações com preço, loja (FK), foto
- [x] Histórico de movimentações com busca/filtro
- [x] Estoque automático (atualizado no checkout: qtd, último preço, última loja)
- [x] Alerta de estoque baixo (estoque < mínimo)
- [x] Upload de foto + OCR básico como **helper** (não obrigatório)
- [x] Enum de unidades padronizado (kg, g, l, ml, un, pct, cx, dz)
- [x] Soft delete de itens (não somem de listas abertas)
- [x] PWA funcional (installable, offline, service worker)
- [x] Isolamento de dados por usuário

### 🔮 Futuro (Pós-MVP)
- [ ] Compartilhamento de lista com outros usuários (ex: cônjuges)
- [ ] Escaneamento de código de barras + auto-preenchimento
- [ ] Reconhecimento de cupom fiscal completo (SAT/NFC-e)
- [ ] Gráficos de gastos por mês/categoria
- [ ] Previsão de gastos baseada no histórico
- [ ] Sincronia offline completa (IndexedDB + conflict resolution)
- [ ] Push notifications (estoque baixo, lembretes de compra)
- [ ] Tema escuro
- [ ] Importação/exportação de dados

---

## 13. Próximos Passos

A ordem de implementação sugerida é:

| # | Etapa | Duração (estimada) |
|---|-------|--------------------|
| 1 | Setup do projeto (git, docker-compose, estrutura de pastas, env) | ~1h |
| 2 | Backend: domain entities + interfaces + value objects (unit enum) | ~2h |
| 3 | Backend: infra banco (SQLAlchemy models, migrations - todas as tabelas) | ~3h |
| 4 | Backend: auth (register, login, JWT, refresh, middleware) | ~3h |
| 5 | Backend: CRUD categorias + itens (catálogo) | ~3h |
| 6 | Backend: CRUD lojas (stores) | ~1h |
| 7 | Backend: inventário (declarar, calcular necessidades, gerar lista) | ~3h |
| 8 | Backend: lista de compras + itens + checklist | ~2h |
| 9 | Backend: checkout parcial + movimentações + atualização de estoque | ~3h |
| 10 | Backend: OCR + upload de foto | ~2h |
| 11 | Frontend: setup Vite + PWA + Tailwind + Router + Axios | ~1h |
| 12 | Frontend: tela de login + cadastro | ~2h |
| 13 | Frontend: catálogo (categorias + itens + lojas) | ~3h |
| 14 | Frontend: inventário + cálculo de necessidades | ~3h |
| 15 | Frontend: lista de compras + checklist offline-first | ~4h |
| 16 | Frontend: câmera + OCR + preço | ~3h |
| 17 | Frontend: estoque + alertas + histórico | ~2h |
| 18 | Testes e ajustes finos | ~4h |
| 19 | Deploy no servidor | ~2h |
| | **Total estimado** | **~44h** |

---

> Plano criado em: 12/07/2026
>
> Revisado e aprovado por: _______________
