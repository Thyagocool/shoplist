import { useEffect, useState } from 'react';
import { itemsAPI, categoriesAPI } from '../services/api';
import type { ItemResponse, CategoryResponse } from '../types';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';

const UNITS = ['un', 'kg', 'g', 'l', 'ml', 'pct', 'cx', 'dz'];

interface FormState {
  name: string;
  unit: string;
  quantity: string;
  minStock: string;
  maxStock: string;
}

const emptyForm = (unit = 'un'): FormState => ({
  name: '',
  unit,
  quantity: '1',
  minStock: '0',
  maxStock: '0',
});

export default function ItemsList() {
  const [items, setItems] = useState<ItemResponse[]>([]);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCat, setSelectedCat] = useState('');

  // Form state (create / edit)
  const [form, setForm] = useState<FormState>(emptyForm());
  const [editId, setEditId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

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

  const resetForm = () => {
    setForm(emptyForm());
    setEditId(null);
  };

  const handleSubmit = async () => {
    if (!form.name.trim() || !selectedCat) return;
    setSaving(true);
    try {
      const payload = {
        name: form.name,
        category_id: selectedCat,
        unit: form.unit,
        default_quantity: parseFloat(form.quantity) || 1,
        min_stock: parseFloat(form.minStock) || 0,
        max_stock: parseFloat(form.maxStock) || 0,
      };
      if (editId) {
        await itemsAPI.update(editId, payload);
      } else {
        await itemsAPI.create(payload);
      }
      resetForm();
      load();
    } catch {
      alert('Erro ao salvar item');
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (item: ItemResponse) => {
    setForm({
      name: item.name,
      unit: item.default_unit,
      quantity: String(item.default_quantity),
      minStock: String(item.min_stock),
      maxStock: String(item.max_stock),
    });
    setEditId(item.id);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Desativar este item?')) return;
    await itemsAPI.delete(id);
    if (editId === id) resetForm();
    load();
  };

  const filtered = items.filter((i) => i.category_id === selectedCat);

  const getCatName = (id: string) =>
    categories.find((c) => c.id === id)?.name || '—';

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-800">Catálogo de Itens</h2>

      {/* Seletor de Categoria */}
      <select
        className="w-full border rounded-lg px-3 py-2 text-sm"
        value={selectedCat}
        onChange={(e) => { setSelectedCat(e.target.value); resetForm(); }}
      >
        <option value="">Selecione uma categoria...</option>
        {categories.map((c) => (
          <option key={c.id} value={c.id}>
            {c.name} ({items.filter((i) => i.category_id === c.id).length})
          </option>
        ))}
      </select>

      {!selectedCat ? (
        <p className="text-gray-400 text-center py-8">
          Selecione uma categoria acima para gerenciar os itens
        </p>
      ) : (
        <>
          {/* Formulário inline — Novo / Editar */}
          <div className="bg-white rounded-xl shadow-sm border p-4 space-y-3">
            <h3 className="font-semibold text-gray-700 text-sm">
              {editId ? 'Editar Item' : 'Novo Item'} — {getCatName(selectedCat)}
            </h3>

            <Input
              label="Nome"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Ex: Arroz, Feijão..."
              autoFocus
            />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Unidade</label>
                <select
                  className="w-full border rounded-lg px-3 py-2"
                  value={form.unit}
                  onChange={(e) => setForm({ ...form, unit: e.target.value })}
                >
                  {UNITS.map((u) => (
                    <option key={u} value={u}>{u}</option>
                  ))}
                </select>
              </div>
              <Input
                label="Qtd. Padrão"
                type="number"
                step="0.01"
                value={form.quantity}
                onChange={(e) => setForm({ ...form, quantity: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Estoque Mínimo"
                type="number"
                step="0.01"
                value={form.minStock}
                onChange={(e) => setForm({ ...form, minStock: e.target.value })}
              />
              <Input
                label="Estoque Máximo"
                type="number"
                step="0.01"
                value={form.maxStock}
                onChange={(e) => setForm({ ...form, maxStock: e.target.value })}
              />
            </div>

            <div className="flex gap-2 pt-1">
              <Button onClick={handleSubmit} isLoading={saving}>
                {editId ? 'Salvar' : 'Adicionar'}
              </Button>
              {editId && (
                <Button variant="secondary" onClick={resetForm}>
                  Cancelar
                </Button>
              )}
            </div>
          </div>

          {/* Lista de Itens da Categoria */}
          {loading ? (
            <p className="text-gray-400">Carregando...</p>
          ) : filtered.length === 0 ? (
            <p className="text-gray-400 text-center py-4">
              Nenhum item nesta categoria ainda. Adicione acima!
            </p>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-gray-500 font-medium">
                {filtered.length} item(ns) em {getCatName(selectedCat)}
              </p>
              {filtered.map((item) => (
                <div
                  key={item.id}
                  className={`bg-white rounded-lg shadow-sm border p-4 flex items-center justify-between ${
                    editId === item.id ? 'ring-2 ring-primary-400' : ''
                  }`}
                >
                  <div>
                    <p className="font-medium text-gray-800">{item.name}</p>
                    <p className="text-sm text-gray-500">
                      {item.default_unit}
                      {item.default_quantity > 0 && ` · Qtd: ${item.default_quantity}`}
                      {item.min_stock > 0 && ` · Min: ${item.min_stock}`}
                      {item.max_stock > 0 && ` · Max: ${item.max_stock}`}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(item)}
                      className="border border-blue-200 text-blue-600 bg-blue-50 hover:bg-blue-600 hover:text-white hover:border-blue-600 active:bg-blue-700 active:text-white px-2 py-0.5 rounded text-xs font-medium transition"
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="border border-red-200 text-red-600 bg-red-50 hover:bg-red-600 hover:text-white hover:border-red-600 active:bg-red-700 active:text-white px-2 py-0.5 rounded text-xs font-medium transition"
                    >
                      Desativar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
