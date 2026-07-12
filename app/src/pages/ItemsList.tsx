import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { itemsAPI, categoriesAPI } from '../services/api';
import type { ItemResponse, CategoryResponse } from '../types';


export default function ItemsList() {
  const [items, setItems] = useState<ItemResponse[]>([]);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterCat, setFilterCat] = useState('');

  const load = async () => {
    try {
      const [itRes, catRes] = await Promise.all([
        itemsAPI.list(),
        categoriesAPI.list(),
      ]);
      setItems(itRes.data);
      setCategories(catRes.data);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleDeactivate = async (id: string) => {
    if (!confirm('Desativar este item?')) return;
    await itemsAPI.delete(id);
    load();
  };

  const filtered = filterCat
    ? items.filter((i) => i.category_id === filterCat)
    : items;

  const getCatName = (id: string) =>
    categories.find((c) => c.id === id)?.name || '—';

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Catálogo de Itens</h2>
        <Link
          to="/items/new"
          className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 transition"
        >
          + Novo Item
        </Link>
      </div>

      {/* Filter */}
      <select
        className="w-full border rounded-lg px-3 py-2 text-sm"
        value={filterCat}
        onChange={(e) => setFilterCat(e.target.value)}
      >
        <option value="">Todas as categorias</option>
        {categories.map((c) => (
          <option key={c.id} value={c.id}>{c.name}</option>
        ))}
      </select>

      {loading ? (
        <p className="text-gray-400">Carregando...</p>
      ) : filtered.length === 0 ? (
        <p className="text-gray-400 text-center py-8">Nenhum item encontrado</p>
      ) : (
        <div className="space-y-2">
          {filtered.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-lg shadow-sm border p-4 flex items-center justify-between"
            >
              <div>
                <p className="font-medium text-gray-800">{item.name}</p>
                <p className="text-sm text-gray-500">
                  {getCatName(item.category_id)} · {item.default_unit}
                  {item.min_stock > 0 && ` · Min: ${item.min_stock}`}
                  {item.max_stock > 0 && ` · Max: ${item.max_stock}`}
                </p>
              </div>
              <div className="flex gap-2">
                <Link
                  to={`/items/${item.id}/edit`}
                  className="text-sm text-blue-600 hover:underline"
                >
                  Editar
                </Link>
                <button
                  onClick={() => handleDeactivate(item.id)}
                  className="text-sm text-red-600 hover:underline"
                >
                  Desativar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
