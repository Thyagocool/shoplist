import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { listsAPI, itemsAPI } from '../services/api';
import type { ShoppingListResponse, ItemResponse } from '../types';
import Button from '../components/ui/Button';

export default function ListDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [list, setList] = useState<ShoppingListResponse | null>(null);
  const [items, setItems] = useState<ItemResponse[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [selectedItemId, setSelectedItemId] = useState('');
  const [customName, setCustomName] = useState('');
  const [quantity, setQuantity] = useState('1');
  const [unit, setUnit] = useState('un');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    if (!id) return;
    try {
      const [listRes, itemsRes] = await Promise.all([
        listsAPI.get(id),
        itemsAPI.list(),
      ]);
      setList(listRes.data);
      setItems(itemsRes.data);
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
            <button
              onClick={() => setShowAdd(!showAdd)}
              className="bg-green-600 text-white px-3 py-1.5 rounded text-sm hover:bg-green-700"
            >
              + Item
            </button>
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
              {items.map((it) => (
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

      {/* Items list */}
      <div className="space-y-2">
        {list.items.length === 0 ? (
          <p className="text-gray-400 text-center py-8">Nenhum item na lista</p>
        ) : (
          list.items.map((item) => (
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
                className="h-5 w-5 text-green-600 rounded"
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
              {isEditable && (
                <input
                  type="number"
                  className="w-20 border rounded px-2 py-1 text-sm text-right"
                  placeholder="Preço"
                  value={item.price_cents ? (item.price_cents / 100).toFixed(2) : ''}
                  onChange={() => {
                    // Optimistic: just reload. In production would have a dedicated endpoint
                  }}
                  onBlur={() => load()}
                  step="0.01"
                  min="0"
                />
              )}
            </div>
          ))
        )}
      </div>

      {/* Checkout button */}
      {isEditable && list.items.length > 0 && (
        <Button onClick={handleCheckout}>
          Finalizar Compra (Checkout)
        </Button>
      )}
    </div>
  );
}
