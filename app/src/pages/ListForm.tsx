import { FormEvent, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listsAPI, categoriesAPI, itemsAPI } from '../services/api';
import type { CategoryResponse, ItemResponse } from '../types';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

export default function ListForm() {
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [items, setItems] = useState<ItemResponse[]>([]);
  const [includeItems, setIncludeItems] = useState(false);
  const [filterCat, setFilterCat] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      const [catRes, itRes] = await Promise.all([
        categoriesAPI.list(),
        itemsAPI.list(),
      ]);
      setCategories(catRes.data);
      setItems(itRes.data);
    })();
  }, []);

  const filteredItems = filterCat
    ? items.filter((i) => i.category_id === filterCat && i.active !== false)
    : items.filter((i) => i.active !== false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try {
      const { data } = await listsAPI.create(name);

      // Se marcou "Incluir itens", adiciona todos os itens filtrados
      if (includeItems && filteredItems.length > 0) {
        for (const item of filteredItems) {
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

        {/* Incluir itens */}
        <div className="border rounded-lg p-4 space-y-3 bg-gray-50">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={includeItems}
              onChange={(e) => setIncludeItems(e.target.checked)}
              className="h-5 w-5 text-green-600 rounded"
            />
            <span className="text-sm font-medium text-gray-700">
              Incluir itens do catálogo
            </span>
          </label>

          {includeItems && (
            <>
              <select
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={filterCat}
                onChange={(e) => setFilterCat(e.target.value)}
              >
                <option value="">Todas as categorias ({items.filter((i) => i.active !== false).length} itens)</option>
                {categories.map((c) => {
                  const count = items.filter((i) => i.category_id === c.id && i.active !== false).length;
                  return (
                    <option key={c.id} value={c.id}>
                      {c.name} ({count} itens)
                    </option>
                  );
                })}
              </select>

              <p className="text-xs text-gray-500">
                {filteredItems.length} item(ns) serão adicionados à lista
              </p>
            </>
          )}
        </div>

        <div className="flex gap-2">
          <Button type="submit" isLoading={saving}>
            Criar Lista {includeItems && filteredItems.length > 0 ? `(+${filteredItems.length} itens)` : ''}
          </Button>
          <Button variant="secondary" onClick={() => navigate('/lists')}>
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  );
}
