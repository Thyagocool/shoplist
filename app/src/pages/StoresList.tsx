import { useEffect, useState } from 'react';
import { storesAPI } from '../services/api';
import type { StoreResponse } from '../types';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';

export default function StoresList() {
  const [stores, setStores] = useState<StoreResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);

  const load = async () => {
    try {
      const { data } = await storesAPI.list();
      setStores(data);
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
        await storesAPI.update(editId, name);
      } else {
        await storesAPI.create(name);
      }
      setName('');
      setEditId(null);
      setShowForm(false);
      load();
    } catch {
      alert('Erro ao salvar loja');
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (s: StoreResponse) => {
    setName(s.name);
    setEditId(s.id);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Excluir esta loja?')) return;
    await storesAPI.delete(id);
    load();
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Lojas</h2>
        <button
          onClick={() => { setShowForm(true); setEditId(null); setName(''); }}
          className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 transition"
        >
          + Nova Loja
        </button>
      </div>

      {/* Inline form */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-4 space-y-3">
          <Input
            label="Nome da Loja"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ex: Supermercado Centro"
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
      ) : stores.length === 0 ? (
        <p className="text-gray-400 text-center py-8">Nenhuma loja cadastrada</p>
      ) : (
        <div className="space-y-2">
          {stores.map((store) => (
            <div
              key={store.id}
              className="bg-white rounded-lg shadow-sm border p-4 flex items-center justify-between"
            >
              <span className="font-medium text-gray-800">{store.name}</span>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(store)}
                  className="text-sm text-blue-600 hover:underline"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(store.id)}
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
