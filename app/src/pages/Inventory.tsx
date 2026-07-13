import { useCallback, useEffect, useMemo, useState } from 'react';
import { inventoriesAPI, stockAPI } from '../services/api';
import type {
  InventoryItemResponse,
  InventorySummaryResponse,
  StockItemResponse,
} from '../types';
import Button from '../components/ui/Button';
import HeroIcon from '../components/ui/HeroIcon';

// ─── helpers ───────────────────────────────────────────────
function fmtDate(d: string) {
  const dt = new Date(d + 'T00:00:00');
  return dt.toLocaleDateString('pt-BR');
}

function fmtDateTime(d: string) {
  const dt = new Date(d);
  return dt.toLocaleString('pt-BR');
}

// ─── main component ───────────────────────────────────────
export default function Inventory() {
  // List mode
  const [inventories, setInventories] = useState<InventorySummaryResponse[]>([]);
  const [listLoading, setListLoading] = useState(true);
  const [listError, setListError] = useState<string | null>(null);

  // Form mode
  const [editingId, setEditingId] = useState<string | null>(null); // null = list, 'new' = creating, UUID = editing
  const [formDate, setFormDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [formNotes, setFormNotes] = useState('');
  const [formItems, setFormItems] = useState<InventoryItemResponse[]>([]);
  const [formStatus, setFormStatus] = useState<string>('open');
  const [formSaving, setFormSaving] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [catalogItems, setCatalogItems] = useState<StockItemResponse[]>([]);

  // ─── load list ──────────────────────────────────────────
  const loadList = useCallback(async () => {
    setListLoading(true);
    setListError(null);
    try {
      const { data } = await inventoriesAPI.list();
      if (!Array.isArray(data)) throw new Error('Resposta inválida');
      setInventories(data);
    } catch (err: any) {
      setListError(err?.response?.data?.detail || err?.message || 'Erro ao carregar inventários');
    } finally {
      setListLoading(false);
    }
  }, []);

  useEffect(() => {
    loadList();
  }, [loadList]);

  // ─── load catalog (for "Carregar todos") ────────────────
  const loadCatalog = useCallback(async () => {
    try {
      const { data } = await stockAPI.list();
      if (Array.isArray(data)) setCatalogItems(data);
    } catch {
      // ignore — will show empty catalog
    }
  }, []);

  // ─── start new inventory ────────────────────────────────
  const startNew = () => {
    setEditingId('new');
    setFormDate(new Date().toISOString().slice(0, 10));
    setFormNotes('');
    setFormItems([]);
    setFormStatus('open');
    setSearchTerm('');
    setExpanded(new Set());
    loadCatalog();
  };

  // ─── edit existing ──────────────────────────────────────
  const editExisting = async (id: string) => {
    setEditingId(id);
    loadCatalog(); // carrega catálogo para permitir adicionar novos itens
    try {
      const { data } = await inventoriesAPI.get(id);
      setFormDate(data.date);
      setFormNotes(data.notes || '');
      setFormItems(data.items);
      setFormStatus(data.status);
      setSearchTerm('');
      setExpanded(new Set(data.items.map((i: InventoryItemResponse) => i.category_name)));
    } catch {
      alert('Erro ao carregar inventário');
      setEditingId(null);
    }
  };

  // ─── back to list ───────────────────────────────────────
  const backToList = () => {
    setEditingId(null);
    loadList();
  };

  // ─── load all catalog items into form ───────────────────
  const handleLoadAll = () => {
    const newItems: InventoryItemResponse[] = catalogItems.map((c) => ({
      id: crypto.randomUUID(),
      pre_registered_item_id: c.pre_registered_item_id,
      item_name: c.item_name,
      category_name: c.category_name,
      declared_quantity: c.current_quantity,
      previous_quantity: c.current_quantity,
      default_unit: c.default_unit,
    }));
    setFormItems((prev) => {
      // Merge: keep existing, add new ones not already present
      const existingIds = new Set(prev.map((i) => i.pre_registered_item_id));
      const merged = [...prev];
      for (const n of newItems) {
        if (!existingIds.has(n.pre_registered_item_id)) {
          merged.push(n);
          existingIds.add(n.pre_registered_item_id);
        }
      }
      return merged;
    });
    // Expand all categories
    setExpanded(new Set(newItems.map((i) => i.category_name)));
  };

  // ─── add single item via search ─────────────────────────
  const searched = useMemo(() => {
    if (!searchTerm.trim()) return [];
    const q = searchTerm.toLowerCase();
    return catalogItems.filter(
      (c) =>
        c.item_name.toLowerCase().includes(q) &&
        !formItems.some((f) => f.pre_registered_item_id === c.pre_registered_item_id)
    );
  }, [searchTerm, catalogItems, formItems]);

  const addItem = (cat: StockItemResponse) => {
    setFormItems((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        pre_registered_item_id: cat.pre_registered_item_id,
        item_name: cat.item_name,
        category_name: cat.category_name,
        declared_quantity: cat.current_quantity,
        previous_quantity: cat.current_quantity,
        default_unit: cat.default_unit,
      },
    ]);
    setSearchTerm('');
  };

  // ─── remove item from form ──────────────────────────────
  const removeItem = (itemId: string) => {
    setFormItems((prev) => prev.filter((i) => i.id !== itemId));
  };

  // ─── update declared quantity ───────────────────────────
  const updateQty = (itemId: string, qty: number) => {
    setFormItems((prev) =>
      prev.map((i) => (i.id === itemId ? { ...i, declared_quantity: qty } : i))
    );
  };

  // ─── group items by category ────────────────────────────
  const groups = useMemo(() => {
    const map = new Map<string, InventoryItemResponse[]>();
    for (const item of formItems) {
      const key = item.category_name || '__uncategorized__';
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(item);
    }
    return Array.from(map.entries())
      .map(([id, items]) => ({
        id,
        name: id === '__uncategorized__' ? 'Sem categoria' : id,
        items: items.sort((a, b) => a.item_name.localeCompare(b.item_name, 'pt-BR')),
      }))
      .sort((a, b) => a.name.localeCompare(b.name, 'pt-BR'));
  }, [formItems]);

  const toggleCategory = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  // ─── save (draft) ───────────────────────────────────────
  const handleSave = async () => {
    setFormSaving(true);
    try {
      const body = {
        date: formDate || undefined,
        notes: formNotes || null,
        items: formItems.map((i) => ({
          pre_registered_item_id: i.pre_registered_item_id,
          declared_quantity: i.declared_quantity,
        })),
      };

      if (editingId === 'new') {
        const { data } = await inventoriesAPI.create(body);
        setEditingId(data.id);
      } else {
        // Already exists — update items
        await inventoriesAPI.updateItems(editingId!, body.items);
      }
      alert('Rascunho salvo!');
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao salvar');
    } finally {
      setFormSaving(false);
    }
  };

  // ─── complete (finalizar) ───────────────────────────────
  const handleComplete = async () => {
    setFormSaving(true);
    try {
      const body = {
        date: formDate || undefined,
        notes: formNotes || null,
        items: formItems.map((i) => ({
          pre_registered_item_id: i.pre_registered_item_id,
          declared_quantity: i.declared_quantity,
        })),
      };

      if (editingId === 'new') {
        const { data } = await inventoriesAPI.create(body);
        await inventoriesAPI.complete(data.id);
      } else {
        await inventoriesAPI.updateItems(editingId!, body.items);
        await inventoriesAPI.complete(editingId!);
      }
      setFormStatus('completed');
      alert('Inventário finalizado! Estoque atualizado.');
      backToList();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao finalizar');
    } finally {
      setFormSaving(false);
    }
  };

  // ─── cancel inventory ───────────────────────────────────
  const handleCancel = async () => {
    if (!editingId || editingId === 'new') {
      backToList();
      return;
    }
    if (!confirm('Cancelar este inventário?')) return;
    try {
      await inventoriesAPI.cancel(editingId);
      alert('Inventário cancelado.');
      backToList();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao cancelar');
    }
  };

  // ─── Render: List view ──────────────────────────────────
  if (!editingId) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <HeroIcon name="archive-box" className="size-6 text-gray-800" />
            <h2 className="text-xl font-bold text-gray-800">Inventários</h2>
          </div>
          {inventories.length > 0 && <Button onClick={startNew}>Novo Inventário</Button>}
        </div>

        {listLoading && <p className="text-gray-400">Carregando...</p>}

        {listError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
            <p className="text-red-700 mb-2">{listError}</p>
            <button
              onClick={loadList}
              className="bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-600 hover:text-white px-4 py-2 rounded-lg text-sm font-medium transition"
            >
              Tentar novamente
            </button>
          </div>
        )}

        {!listLoading && !listError && inventories.length === 0 && (
          <div className="text-center py-12">
            <HeroIcon name="archive-box" className="size-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 mb-4">Nenhum inventário ainda.</p>
            <Button onClick={startNew}>Criar Primeiro Inventário</Button>
          </div>
        )}

        {!listLoading && !listError && inventories.length > 0 && (
          <div className="space-y-3">
            {inventories.map((inv) => {
              const isOpen = inv.status === 'open';
              const isCompleted = inv.status === 'completed';
              return (
                <button
                  key={inv.id}
                  onClick={() => editExisting(inv.id)}
                  className="w-full bg-white border rounded-lg p-4 text-left hover:shadow-md transition flex items-center justify-between"
                >
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-gray-800">
                        {fmtDate(inv.date)}
                      </span>
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                          isOpen
                            ? 'bg-yellow-100 text-yellow-700'
                            : isCompleted
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-500'
                        }`}
                      >
                        {isOpen ? 'Aberto' : isCompleted ? 'Finalizado' : 'Cancelado'}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">
                      {inv.item_count} item(ns) · {fmtDateTime(inv.created_at)}
                    </p>
                  </div>
                  <HeroIcon name="chevron-right" className="size-5 text-gray-400" />
                </button>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  // ─── Render: Form view ──────────────────────────────────
  const canEdit = formStatus === 'open';

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button onClick={backToList} className="p-1 hover:bg-gray-100 rounded transition">
            <HeroIcon name="arrow-left" className="size-5 text-gray-600" />
          </button>
          <h2 className="text-xl font-bold text-gray-800">
            {editingId === 'new' ? 'Novo Inventário' : 'Editar Inventário'}
          </h2>
          <span
            className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              formStatus === 'open'
                ? 'bg-yellow-100 text-yellow-700'
                : formStatus === 'completed'
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-500'
            }`}
          >
            {formStatus === 'open' ? 'Aberto' : formStatus === 'completed' ? 'Finalizado' : 'Cancelado'}
          </span>
        </div>
      </div>

      {/* Date + Notes */}
      <div className="bg-white border rounded-lg p-4 space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Data do inventário</label>
          <input
            type="date"
            value={formDate}
            onChange={(e) => setFormDate(e.target.value)}
            disabled={!canEdit}
            className="border rounded-lg px-3 py-2 text-sm w-full disabled:bg-gray-50 disabled:text-gray-400"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Observações</label>
          <textarea
            value={formNotes}
            onChange={(e) => setFormNotes(e.target.value)}
            disabled={!canEdit}
            rows={2}
            placeholder="Opicional..."
            className="border rounded-lg px-3 py-2 text-sm w-full resize-none disabled:bg-gray-50 disabled:text-gray-400"
          />
        </div>
      </div>

      {/* Items section */}
      <div className="bg-white border rounded-lg p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-700 text-sm">Itens</h3>
          <span className="text-xs text-gray-400">{formItems.length} item(ns)</span>
        </div>

        {/* Search + Load all */}
        {canEdit && (
          <div className="space-y-2">
            <div className="relative">
              <HeroIcon
                name="magnifying-glass"
                className="size-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
              />
              <input
                type="text"
                placeholder="Buscar item para adicionar..."
                className="w-full border rounded-lg pl-9 pr-4 py-2 text-sm"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            {searchTerm && searched.length > 0 && (
              <div className="border rounded-lg max-h-48 overflow-y-auto">
                {searched.slice(0, 15).map((s) => (
                  <button
                    key={s.pre_registered_item_id}
                    onClick={() => addItem(s)}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-blue-50 transition flex items-center justify-between"
                  >
                    <span>{s.item_name}</span>
                    <span className="text-xs text-gray-400">Saldo: {s.current_quantity}</span>
                  </button>
                ))}
              </div>
            )}
            {catalogItems.length > 0 && (
              <button
                onClick={handleLoadAll}
                className="text-sm text-blue-600 hover:text-blue-800 transition"
              >
                + Carregar todos os itens do catálogo
              </button>
            )}
          </div>
        )}

        {/* Items list */}
        {formItems.length === 0 ? (
          <p className="text-center text-gray-400 py-6 text-sm">
            Nenhum item adicionado.
            {canEdit && ' Use a busca acima ou carregue todos os itens.'}
          </p>
        ) : (
          <div className="space-y-2">
            {/* Expand/collapse all */}
            <div className="flex justify-end">
              <button
                onClick={() => {
                  if (groups.every((g) => expanded.has(g.id))) setExpanded(new Set());
                  else setExpanded(new Set(groups.map((g) => g.id)));
                }}
                className="text-xs text-blue-600 hover:text-blue-800 transition"
              >
                {groups.every((g) => expanded.has(g.id)) ? 'Recolher tudo' : 'Expandir tudo'}
              </button>
            </div>

            {groups.map((group) => {
              const isOpen = expanded.has(group.id);
              return (
                <div key={group.id} className="border rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleCategory(group.id)}
                    className="w-full flex items-center justify-between px-3 py-2 bg-gray-50 hover:bg-gray-100 transition text-left"
                  >
                    <span className="font-semibold text-gray-600 text-xs">{group.name}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400">{group.items.length}</span>
                      <HeroIcon
                        name={isOpen ? 'chevron-down' : 'chevron-right'}
                        className="size-3 text-gray-400"
                      />
                    </div>
                  </button>
                  {isOpen && (
                    <div className="divide-y divide-gray-100">
                      {group.items.map((item) => (
                        <div key={item.id} className="px-3 py-2.5">
                          <div className="flex items-start justify-between">
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-800 truncate">
                                {item.item_name}
                              </p>
                              <p className="text-xs text-gray-400">
                                Saldo anterior: {item.previous_quantity} {item.default_unit}
                              </p>
                            </div>
                            {canEdit && (
                              <button
                                onClick={() => removeItem(item.id)}
                                className="text-gray-300 hover:text-red-500 transition ml-2"
                                title="Remover"
                              >
                                <HeroIcon name="x-mark" className="size-4" />
                              </button>
                            )}
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <label className="text-xs text-gray-500">Declarado:</label>
                            <input
                              type="number"
                              step="0.01"
                              min="0"
                              value={item.declared_quantity || ''}
                              onChange={(e) =>
                                updateQty(item.id, parseFloat(e.target.value) || 0)
                              }
                              disabled={!canEdit}
                              className={`flex-1 border rounded px-2 py-1 text-sm w-24 ${
                                item.declared_quantity !== item.previous_quantity
                                  ? 'border-blue-400 bg-blue-50'
                                  : ''
                              } disabled:bg-gray-50 disabled:text-gray-400`}
                              placeholder="0"
                            />
                            <span className="text-xs text-gray-500">{item.default_unit}</span>
                          </div>
                          {item.declared_quantity !== item.previous_quantity && (
                            <p className="text-xs text-blue-600 mt-0.5">
                              {item.previous_quantity} → {item.declared_quantity}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Actions */}
      {canEdit && (
        <div className="flex gap-2">
          <Button
            onClick={handleSave}
            isLoading={formSaving}
            variant="secondary"
            className="flex-1"
          >
            Salvar Rascunho
          </Button>
          <Button
            onClick={handleComplete}
            isLoading={formSaving}
            disabled={formItems.length === 0}
            className="flex-1"
          >
            Finalizar
          </Button>
          <Button
            onClick={handleCancel}
            variant="danger"
            className="w-auto px-3"
          >
            Cancelar
          </Button>
        </div>
      )}

      {!canEdit && (
        <p className="text-center text-sm text-gray-400">
          Este inventário já foi {formStatus === 'completed' ? 'finalizado' : 'cancelado'}.
        </p>
      )}
    </div>
  );
}
