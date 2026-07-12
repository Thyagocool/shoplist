import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { listsAPI, itemsAPI, categoriesAPI } from '../services/api';
import type { ShoppingListResponse, ItemResponse, CategoryResponse } from '../types';
import Button from '../components/ui/Button';

export default function ListDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [list, setList] = useState<ShoppingListResponse | null>(null);
  const [catalogItems, setCatalogItems] = useState<ItemResponse[]>([]);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [showAdd, setShowAdd] = useState(false);
  const [selectedItemId, setSelectedItemId] = useState('');
  const [customName, setCustomName] = useState('');
  const [quantity, setQuantity] = useState('1');
  const [unit, setUnit] = useState('un');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [addingAll, setAddingAll] = useState(false);

  const load = async () => {
    if (!id) return;
    try {
      const [listRes, itemsRes, catRes] = await Promise.all([
        listsAPI.get(id),
        itemsAPI.list(),
        categoriesAPI.list(),
      ]);
      setList(listRes.data);
      setCatalogItems(itemsRes.data);
      setCategories(catRes.data);
    } catch {
      navigate('/lists');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const handleToggle = async (itemId: string) => {
    await listsAPI.toggleItem(itemId);
    load();
  };

  const handleRemove = async (itemId: string) => {
    if (!confirm('Remover este item da lista?')) return;
    try {
      await listsAPI.removeItem(itemId);
      load();
    } catch {
      alert('Erro ao remover item');
    }
  };

  const handleAddItem = async () => {
    if (!id) return;
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {
        estimated_quantity: parseFloat(quantity) || 1,
        unit,
      };
      if (selectedItemId) {
        payload.pre_registered_item_id = selectedItemId;
      } else {
        payload.custom_name = customName;
      }
      await listsAPI.addItem(id, payload);
      setShowAdd(false);
      setSelectedItemId('');
      setCustomName('');
      load();
    } catch {
      alert('Erro ao adicionar item');
    } finally {
      setSaving(false);
    }
  };

  const handleAddAll = async () => {
    if (!id || !list) return;
    setAddingAll(true);
    try {
      const existingIds = new Set(
        list.items.map((i) => i.pre_registered_item_id).filter(Boolean)
      );
      const toAdd = catalogItems.filter(
        (i) => i.active !== false && !existingIds.has(i.id)
      );

      if (toAdd.length === 0) {
        alert('Todos os itens do catálogo já estão na lista!');
        return;
      }

      for (const item of toAdd) {
        await listsAPI.addItem(id, {
          pre_registered_item_id: item.id,
          estimated_quantity: item.default_quantity || 1,
          unit: item.default_unit || 'un',
        });
      }
      alert(`${toAdd.length} item(ns) adicionado(s)!`);
      load();
    } catch {
      alert('Erro ao adicionar itens');
    } finally {
      setAddingAll(false);
    }
  };

  const handleCheckout = async () => {
    if (!id || !list) return;
    const checkedItems = list.items.filter((i) => i.checked);
    if (checkedItems.length === 0) {
      alert('Marque pelo menos um item antes de finalizar');
      return;
    }
    const payload = {
      items: checkedItems.map((i) => ({
        shopping_list_item_id: i.id,
        price_cents: i.price_cents || 0,
      })),
    };
    try {
      await listsAPI.checkout(id, payload);
      alert('Compra registrada! Movimentos e estoque atualizados.');
      navigate('/lists');
    } catch {
      alert('Erro no checkout');
    }
  };

  if (loading) return <p className="text-gray-400">Carregando...</p>;
  if (!list) return <p className="text-gray-400">Lista não encontrada</p>;

  const isEditable = list.status === 'in_progress' || list.status === 'pending';

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-800">{list.name}</h2>
          <p className="text-sm text-gray-500">
            Status: <span className="font-medium">{list.status === 'in_progress' ? 'Em andamento' : list.status}</span>
            {' · '}
            {list.items.filter((i) => i.checked).length}/{list.items.length} itens
          </p>
        </div>
        <div className="flex gap-2">
          {isEditable && (
            <>
              <button
                onClick={() => setShowAdd(!showAdd)}
                className="bg-primary-600 text-white px-3 py-1.5 rounded text-sm hover:bg-primary-700"
              >
                + Item
              </button>
              <button
                onClick={handleAddAll}
                disabled={addingAll}
                className="bg-blue-600 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                {addingAll ? '...' : '+ Todos'}
              </button>
            </>
          )}
          <button
            onClick={() => navigate('/lists')}
            className="text-sm text-gray-500 hover:underline"
          >
            Voltar
          </button>
        </div>
      </div>

      {/* Add item form */}
      {showAdd && (
        <div className="bg-white rounded-xl shadow-sm p-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Item do Catálogo</label>
            <select
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={selectedItemId}
              onChange={(e) => { setSelectedItemId(e.target.value); setCustomName(''); }}
            >
              <option value="">→ Item avulso (digite abaixo)</option>
              {catalogItems.map((it) => (
                <option key={it.id} value={it.id}>{it.name} ({it.default_unit})</option>
              ))}
            </select>
          </div>
          {!selectedItemId && (
            <input
              className="w-full border rounded-lg px-3 py-2 text-sm"
              placeholder="Nome do item avulso"
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
            />
          )}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Qtd</label>
              <input
                className="w-full border rounded-lg px-3 py-2 text-sm"
                type="number"
                step="0.01"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Un</label>
              <select
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
              >
                {['un', 'kg', 'g', 'l', 'ml', 'pct', 'cx', 'dz'].map((u) => (
                  <option key={u} value={u}>{u}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleAddItem} isLoading={saving}>Adicionar</Button>
            <Button variant="secondary" onClick={() => setShowAdd(false)}>Cancelar</Button>
          </div>
        </div>
      )}

      {/* Items list — grouped by category */}
      {list.items.length === 0 ? (
        <p className="text-gray-400 text-center py-8">Nenhum item na lista</p>
      ) : (
        (() => {
          // Build a map: item.id → category_id
          const itemCatMap = new Map<string, string>();
          catalogItems.forEach((ci) => itemCatMap.set(ci.id, ci.category_id));

          // Build groups: category_id → items[]
          const groups = new Map<string, typeof list.items>();
          const uncategorized: typeof list.items = [];

          list.items.forEach((li) => {
            const catId = li.pre_registered_item_id
              ? itemCatMap.get(li.pre_registered_item_id) || ''
              : '';
            if (catId) {
              const arr = groups.get(catId) || [];
              arr.push(li);
              groups.set(catId, arr);
            } else {
              uncategorized.push(li);
            }
          });

          // Sort groups by category name
          const sortedGroups = [...groups.entries()].sort((a, b) => {
            const nameA = categories.find((c) => c.id === a[0])?.name || '';
            const nameB = categories.find((c) => c.id === b[0])?.name || '';
            return nameA.localeCompare(nameB);
          });

          const renderItem = (item: typeof list.items[0]) => (
            <div
              key={item.id}
              className={`bg-white rounded-lg shadow-sm border p-4 flex items-center gap-3 ${
                item.checked ? 'opacity-60' : ''
              }`}
            >
              <input
                type="checkbox"
                checked={item.checked}
                onChange={() => handleToggle(item.id)}
                disabled={!isEditable}
                className="h-5 w-5 text-primary-600 rounded"
              />
              <div className="flex-1">
                <p className={`font-medium ${item.checked ? 'line-through text-gray-400' : 'text-gray-800'}`}>
                  {item.item_name || item.custom_name}
                </p>
                <p className="text-sm text-gray-500">
                  {item.estimated_quantity} {item.unit}
                  {item.price_cents ? ` · R$ ${(item.price_cents / 100).toFixed(2)}` : ''}
                </p>
              </div>
              <div className="flex items-center gap-1">
                {isEditable && (
                  <>
                    {/* Quantidade editável */}
                    <input
                      type="number"
                      className="w-16 border rounded px-1 py-1 text-sm text-center"
                      value={item.estimated_quantity}
                      onChange={async (e) => {
                        const val = parseFloat(e.target.value);
                        if (!isNaN(val) && val > 0) {
                          await listsAPI.updateItem(item.id, { estimated_quantity: val });
                          load();
                        }
                      }}
                      step="0.01"
                      min="0.01"
                    />

                    {/* Preço */}
                    <input
                      type="number"
                      className="w-20 border rounded px-2 py-1 text-sm text-right"
                      placeholder="Preço"
                      value={item.price_cents ? (item.price_cents / 100).toFixed(2) : ''}
                      onChange={() => {}}
                      onBlur={() => load()}
                      step="0.01"
                      min="0"
                    />

                    {/* Lixeira */}
                    <button
                      onClick={() => handleRemove(item.id)}
                      className="p-1.5 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition"
                      title="Remover da lista"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </>
                )}
              </div>
            </div>
          );

          return (
            <div className="space-y-4">
              {sortedGroups.map(([catId, catItems]) => {
                const catName = categories.find((c) => c.id === catId)?.name || 'Sem categoria';
                const checked = catItems.filter((i) => i.checked).length;
                const isExpanded = expanded.has(catId);
                return (
                  <div key={catId}>
                    <div
                      className="flex items-center justify-between mb-2 cursor-pointer select-none"
                      onClick={() => {
                        const next = new Set(expanded);
                        if (isExpanded) next.delete(catId);
                        else next.add(catId);
                        setExpanded(next);
                      }}
                    >
                      <div className="flex items-center gap-2">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className={`h-3 w-3 text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                          strokeWidth={2}
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                        </svg>
                        <h3 className="text-sm font-bold text-gray-600 uppercase tracking-wider">
                          {catName}
                        </h3>
                      </div>
                      <span className="text-xs text-gray-400">
                        {checked}/{catItems.length}
                      </span>
                    </div>
                    {isExpanded && (
                      <div className="space-y-2">
                        {catItems.map(renderItem)}
                      </div>
                    )}
                  </div>
                );
              })}
              {uncategorized.length > 0 && (
                <div>
                  {(() => {
                    const key = '__uncategorized__';
                    const isExpanded = expanded.has(key);
                    return (
                      <>
                        <div
                          className="flex items-center justify-between mb-2 cursor-pointer select-none"
                          onClick={() => {
                            const next = new Set(expanded);
                            if (isExpanded) next.delete(key);
                            else next.add(key);
                            setExpanded(next);
                          }}
                        >
                          <div className="flex items-center gap-2">
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className={`h-3 w-3 text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                              strokeWidth={2}
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                            </svg>
                            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider">
                              Sem categoria
                            </h3>
                          </div>
                          <span className="text-xs text-gray-400">
                            {uncategorized.filter((i) => i.checked).length}/{uncategorized.length}
                          </span>
                        </div>
                        {isExpanded && (
                          <div className="space-y-2">
                            {uncategorized.map(renderItem)}
                          </div>
                        )}
                      </>
                    );
                  })()}
                </div>
              )}
            </div>
          );
        })()
      )}

      {/* Checkout button */}
      {isEditable && list.items.length > 0 && (
        <Button onClick={handleCheckout}>
          Finalizar Compra (Checkout)
        </Button>
      )}
    </div>
  );
}
