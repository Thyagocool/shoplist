import { FormEvent, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listsAPI, categoriesAPI, itemsAPI, stockAPI, storesAPI } from '../services/api';
import type { CategoryResponse, ItemResponse, StockItemResponse, StoreResponse } from '../types';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

interface ItemWithStock extends ItemResponse {
  current_quantity: number;
}

export default function ListForm() {
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [stores, setStores] = useState<StoreResponse[]>([]);
  const [storeId, setStoreId] = useState('');
  const [items, setItems] = useState<ItemWithStock[]>([]);
  const [includeItems, setIncludeItems] = useState(false);
  const [onlyMinStock, setOnlyMinStock] = useState(false);
  const [filterCat, setFilterCat] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      const [catRes, storeRes, itRes, stockRes] = await Promise.all([
        categoriesAPI.list(),
        storesAPI.list(),
        itemsAPI.list(),
        stockAPI.list().catch(() => ({ data: [] })),
      ]);
      setCategories(catRes.data);
      setStores(storeRes.data);

      const catalogItems: ItemResponse[] = itRes.data;
      const stockItems: StockItemResponse[] = stockRes.data || [];

      const stockMap = new Map<string, number>();
      stockItems.forEach((s) => stockMap.set(s.pre_registered_item_id, s.current_quantity));

      const merged: ItemWithStock[] = catalogItems.map((item) => ({
        ...item,
        current_quantity: stockMap.get(item.id) ?? 0,
      }));

      setItems(merged);
    })();
  }, []);

  const filteredItems = useMemo(() => {
    let result = items.filter((i) => i.active !== false);

    // Category filter
    if (filterCat) {
      result = result.filter((i) => i.category_id === filterCat);
    }

    // Min stock filter
    if (onlyMinStock) {
      result = result.filter((i) => i.min_stock > 0 && i.current_quantity <= i.min_stock);
    }

    return result;
  }, [items, filterCat, onlyMinStock]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try {
      const { data } = await listsAPI.create(name, storeId || undefined);

      // Add items based on selection
      if (includeItems || onlyMinStock) {
        const itemsToAdd = includeItems ? filteredItems : (onlyMinStock ? filteredItems : []);
        for (const item of itemsToAdd) {
          await listsAPI.addItem(data.id, {
            pre_registered_item_id: item.id,
            estimated_quantity: item.default_quantity || 1,
            unit: item.default_unit || 'un',
          });
        }
      }

      navigate(`/lists/${data.id}`);
    } catch {
      alert('Erro ao criar lista');
    } finally {
      setSaving(false);
    }
  };

  const activeCount = items.filter((i) => i.active !== false).length;
  const belowMinCount = items.filter((i) => i.min_stock > 0 && i.current_quantity <= i.min_stock).length;

  return (
    <div className="max-w-lg mx-auto">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Nova Lista de Compras</h2>
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6 space-y-4">
        <Input
          label="Nome da Lista"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Ex: Feira da semana"
          autoFocus
          required
        />

        {/* Loja */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Loja</label>
          <select
            value={storeId}
            onChange={(e) => setStoreId(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Sem loja definida</option>
            {stores.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        {/* Opções de itens */}
        <div className="border rounded-lg p-4 space-y-3 bg-gray-50">
          <p className="text-sm font-semibold text-gray-700">Itens da lista</p>

          {/* Opção 1: catálogo completo */}
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={includeItems}
              onChange={(e) => setIncludeItems(e.target.checked)}
              className="h-5 w-5 text-primary-600 rounded"
            />
            <span className="text-sm text-gray-700">
              Incluir itens do catálogo
            </span>
          </label>

          {includeItems && (
            <select
              className="w-full border rounded-lg px-3 py-2 text-sm"
              value={filterCat}
              onChange={(e) => setFilterCat(e.target.value)}
            >
              <option value="">Todas as categorias ({activeCount} itens)</option>
              {categories.map((c) => {
                const count = items.filter((i) => i.category_id === c.id && i.active !== false).length;
                return (
                  <option key={c.id} value={c.id}>
                    {c.name} ({count} itens)
                  </option>
                );
              })}
            </select>
          )}

          {/* Opção 2: somente estoque mínimo */}
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={onlyMinStock}
              onChange={(e) => setOnlyMinStock(e.target.checked)}
              className="h-5 w-5 text-primary-600 rounded"
            />
            <span className="text-sm text-gray-700">
              Somente itens com estoque mínimo ({belowMinCount} itens)
            </span>
          </label>

          {(includeItems || onlyMinStock) && (
            <p className="text-xs text-gray-500">
              {filteredItems.length} item(ns) serão adicionados à lista
              {onlyMinStock && !includeItems && (
                <span className="text-yellow-600">
                  {' · '}baseado no saldo atual do estoque
                </span>
              )}
            </p>
          )}
        </div>

        <div className="flex gap-2">
          <Button type="submit" isLoading={saving}>
            Criar Lista {(includeItems || onlyMinStock) && filteredItems.length > 0
              ? `(+${filteredItems.length} itens)`
              : ''}
          </Button>
          <Button variant="secondary" onClick={() => navigate('/lists')}>
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  );
}
