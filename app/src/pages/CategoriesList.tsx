import { useEffect, useState } from 'react';
import { categoriesAPI } from '../services/api';
import type { CategoryResponse } from '../types';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';

export default function CategoriesList() {
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);

  const load = async () => {
    try {
      const { data } = await categoriesAPI.list();
      setCategories(data);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleSubmit = async () => {
    if (!name.trim()) return;
    setSaving(true);
    try {
      if (editId) {
        await categoriesAPI.update(editId, name);
      } else {
        await categoriesAPI.create(name);
      }
      setName('');
      setEditId(null);
      setShowForm(false);
      load();
    } catch {
      alert('Erro ao salvar categoria');
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (cat: CategoryResponse) => {
    setName(cat.name);
    setEditId(cat.id);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Excluir esta categoria?')) return;
    try {
      await categoriesAPI.delete(id);
      load();
    } catch {
      alert('Erro ao excluir categoria. Pode haver itens vinculados.');
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Categorias</h2>
        <button
          onClick={() => { setShowForm(true); setEditId(null); setName(''); }}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-primary-700 transition"
        >
          + Nova Categoria
        </button>
      </div>

      {/* Inline form */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-4 space-y-3">
          <Input
            label="Nome da Categoria"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ex: Carnes, Laticínios, Bebidas..."
            autoFocus
          />
          <div className="flex gap-2">
            <Button onClick={handleSubmit} isLoading={saving}>
              {editId ? 'Salvar' : 'Criar'}
            </Button>
            <Button
              variant="secondary"
              onClick={() => { setShowForm(false); setEditId(null); setName(''); }}
            >
              Cancelar
            </Button>
          </div>
        </div>
      )}

      {loading ? (
        <p className="text-gray-400">Carregando...</p>
      ) : categories.length === 0 ? (
        <p className="text-gray-400 text-center py-8">Nenhuma categoria cadastrada</p>
      ) : (
        <div className="space-y-2">
          {categories.map((cat) => (
            <div
              key={cat.id}
              className="bg-white rounded-lg shadow-sm border p-4 flex items-center justify-between"
            >
              <span className="font-medium text-gray-800">{cat.name}</span>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(cat)}
                  className="text-sm text-blue-600 hover:underline"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(cat.id)}
                  className="text-sm text-red-600 hover:underline"
                >
                  Excluir
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
