# 🟢 FASE 2 — Backend Features

**Status:** ✅ Concluída em 12/07/2026

---

## Etapas Executadas

| Etapa | Descrição | Status |
|-------|-----------|--------|
| 2.1 | Itens (catálogo) CRUD | ✅ |
| 2.2 | Lojas CRUD | ✅ |
| 2.3 | Inventário (♥) | ✅ |
| 2.4 | Lista + Checklist | ✅ |
| 2.5 | Checkout + Movimentos + Estoque | ✅ |
| 2.6 | Upload + OCR | ✅ |

---

## Etapa 2.1 — Itens (Catálogo) CRUD

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/items` | Criar item (auto-cria registro de estoque) |
| GET | `/api/v1/items` | Listar itens ativos do usuário |
| PUT | `/api/v1/items/{id}` | Atualizar item |
| DELETE | `/api/v1/items/{id}` | Desativar item (soft delete) |

### Regras
- `default_unit` validado pelo enum `Unit` (kg, g, l, ml, un, pct, cx, dz)
- Ao criar, já cria um registro `StockModel` com quantidade 0
- Soft delete: marca `active = False`
- `joinedload(ItemModel.category)` para evitar lazy-load N+1

### Arquivos
- `api/src/application/dtos/item_dtos.py`
- `api/src/application/use_cases/item/create_item.py`
- `api/src/application/use_cases/item/list_items.py`
- `api/src/application/use_cases/item/update_item.py`
- `api/src/application/use_cases/item/deactivate_item.py`
- `api/src/presentation/schemas/item_schemas.py`
- `api/src/presentation/api/routers/item_router.py`

---

## Etapa 2.2 — Lojas CRUD

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/stores` | Criar loja |
| GET | `/api/v1/stores` | Listar lojas do usuário |
| PUT | `/api/v1/stores/{id}` | Atualizar nome |
| DELETE | `/api/v1/stores/{id}` | Excluir loja |

### Arquivos
- `api/src/application/dtos/store_dtos.py`
- `api/src/application/use_cases/store/create_store.py`
- `api/src/application/use_cases/store/list_stores.py`
- `api/src/application/use_cases/store/update_store.py`
- `api/src/application/use_cases/store/delete_store.py`
- `api/src/presentation/schemas/store_schemas.py`
- `api/src/presentation/api/routers/store_router.py`

---

## Etapa 2.3 — Inventário (♥)

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/inventory` | Declarar posse de item |
| GET | `/api/v1/inventory?list_id=` | Listar declarações de uma lista |

### Regras
- `need = max(0, max_stock - declared_quantity)`
- Se `declared_quantity = 1` e `max_stock = 5`, então `need = 4`
- Calculado automaticamente pelo domínio

### Exemplo
```json
POST /api/v1/inventory
{
  "shopping_list_id": "...",
  "pre_registered_item_id": "...",
  "declared_quantity": 1
}
// Response: {"item_name": "Arroz", "declared_quantity": 1, "calculated_need": 4}
```

### Arquivos
- `api/src/application/dtos/inventory_dtos.py`
- `api/src/application/use_cases/inventory/declare_inventory.py`
- `api/src/application/use_cases/inventory/list_inventory.py`
- `api/src/presentation/schemas/inventory_schemas.py`
- `api/src/presentation/api/routers/inventory_router.py`

---

## Etapa 2.4 — Lista + Checklist

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/lists` | Criar lista |
| GET | `/api/v1/lists` | Listar listas do usuário |
| GET | `/api/v1/lists/{id}` | Obter lista com itens |
| POST | `/api/v1/lists/{id}/items` | Adicionar item (pré-cadastrado ou custom) |
| PATCH | `/api/v1/lists/items/{id}/toggle` | Marcar/desmarcar item |
| POST | `/api/v1/lists/{id}/complete` | Finalizar lista |
| POST | `/api/v1/lists/{id}/cancel` | Cancelar lista |

### Regras
- Lista começa como `in_progress`
- Só pode modificar itens se lista estiver `in_progress` ou `pending`
- Complete/Cancel só funcionam uma vez (status vira `completed`/`cancelled`)
- Itens podem ser de catálogo (`pre_registered_item_id`) ou avulsos (`custom_name`)

### Arquivos
- `api/src/application/dtos/shopping_list_dtos.py`
- `api/src/application/use_cases/shopping_list/create_list.py`
- `api/src/application/use_cases/shopping_list/list_lists.py`
- `api/src/application/use_cases/shopping_list/get_list.py`
- `api/src/application/use_cases/shopping_list/add_list_item.py`
- `api/src/application/use_cases/shopping_list/toggle_item.py`
- `api/src/application/use_cases/shopping_list/complete_list.py`
- `api/src/application/use_cases/shopping_list/cancel_list.py`
- `api/src/presentation/schemas/shopping_list_schemas.py`
- `api/src/presentation/api/routers/shopping_list_router.py`

---

## Etapa 2.5 — Checkout + Movimentos + Estoque

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/lists/{id}/checkout` | Processar checkout da lista |

### Fluxo do Checkout
1. Recebe lista de itens comprados com preços
2. Para cada item **checked** na lista, cria um `Movement`
3. Atualiza `Stock` do item (quantidade + preço + loja)
4. Marca a lista como `completed`

### Movement (Movimento Financeiro)
- Código sequencial por usuário: `MOV-001`, `MOV-002`...
- Armazena snapshot do nome da loja no momento da compra
- Quantidade, unidade, preço em centavos
- Imutável após criado (ledger entry)

### Stock (Estoque)
- 1 registro por item (unique `pre_registered_item_id`)
- Atualizado automaticamente no checkout
- Armazena `last_price_cents` e `last_store_id`

### Arquivos
- `api/src/application/dtos/checkout_dtos.py`
- `api/src/application/use_cases/shopping_list/checkout_list.py`
- `api/src/presentation/schemas/checkout_schemas.py`

---

## Etapa 2.6 — Upload + OCR

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/ocr` | Upload de imagem + OCR |

### Funcionamento
1. Upload de imagem (JPEG, PNG, WebP, TIFF) via `multipart/form-data`
2. Salva em `./uploads/` com nome UUID
3. Executa Tesseract OCR com idioma português (`por`)
4. Retorna texto bruto e linhas extraídas

### Stack
- **Pillow** — abertura da imagem
- **pytesseract** 0.3.13 — binding para Tesseract
- **Tesseract OCR** instalado no container (Dockerfile)
- Idiomas: por (português) configurado

### Exemplo
```bash
curl -X POST http://localhost:8000/api/v1/ocr \
  -H "Authorization: Bearer {token}" \
  -F "file=@/tmp/test_receipt.png"
```

```json
{
  "filename": "ab5f859a-0bf7-455b-90b7-7225e56b1aff.png",
  "raw_text": "Arroz R$22.90\nFeijao R$8,50\n",
  "items": [
    {"text": "Arroz R$22.90", "confidence": 0.0},
    {"text": "Feijao R$8,50", "confidence": 0.0}
  ]
}
```

### Arquivos
- `api/src/presentation/schemas/ocr_schemas.py`
- `api/src/presentation/api/routers/ocr_router.py`

---

## Migrations Adicionais

| Migration | Descrição |
|-----------|-----------|
| `0ff37c5aee19` | Adiciona `server_default` ao `stock.updated_at` + `stock.created_at` |
| `0baf0d5ae42a` | Adiciona `created_at`/`updated_at` a `shopping_lists` |

---

## Testes de Verificação

### Itens
```bash
curl -X POST http://localhost:8000/api/v1/items \
  -H "Authorization: Bearer {token}" \
  -d '{"name":"Arroz","category_id":"...","default_unit":"kg","max_stock":5}'
# ✅ 201 - item criado + estoque zerado
```

### Lojas
```bash
curl -X POST http://localhost:8000/api/v1/stores \
  -H "Authorization: Bearer {token}" \
  -d '{"name":"Supermercado X"}'
# ✅ 201
```

### Inventário
```bash
curl -X POST http://localhost:8000/api/v1/inventory \
  -H "Authorization: Bearer {token}" \
  -d '{"shopping_list_id":"...","pre_registered_item_id":"...","declared_quantity":1}'
# ✅ 201 - need calculado automaticamente
```

### Lista + Checkout
```bash
# Criar lista
curl -X POST http://localhost:8000/api/v1/lists \
  -H "Authorization: Bearer {token}" \
  -d '{"name":"Compras"}'

# Adicionar item
curl -X POST http://localhost:8000/api/v1/lists/{list_id}/items \
  -H "Authorization: Bearer {token}" \
  -d '{"pre_registered_item_id":"...","estimated_quantity":2}'

# Marcar item
curl -X PATCH http://localhost:8000/api/v1/lists/items/{item_id}/toggle \
  -H "Authorization: Bearer {token}"

# Checkout
curl -X POST http://localhost:8000/api/v1/lists/{list_id}/checkout \
  -H "Authorization: Bearer {token}" \
  -d '{"items":[{"shopping_list_item_id":"...","price_cents":2290}]}'
# ✅ 200 - movimentos criados + estoque atualizado
```

### OCR
```bash
curl -X POST http://localhost:8000/api/v1/ocr \
  -H "Authorization: Bearer {token}" \
  -F "file=@/tmp/test_receipt.png"
# ✅ 200 - texto extraído
```
