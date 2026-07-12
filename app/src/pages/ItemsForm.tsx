import { FormEvent, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { itemsAPI, categoriesAPI } from '../services/api';
import type { CategoryResponse } from '../types';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

export default function ItemsForm() {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();

  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [name, setName] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [defaultUnit, setDefaultUnit] = useState('un');
  const [defaultQuantity, setDefaultQuantity] = useState('1');
  const [minStock, setMinStock] = useState('0');
  const [maxStock, setMaxStock] = useState('0');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    (async () => {
      const { data } = await categoriesAPI.list();
      setCategories(data);
      if (data.length > 0 && !categoryId) setCategoryId(data[0].id);
    })();
    if (isEdit) {
      (async () => {
        const { data } = await itemsAPI.list();
        const item = data.find((i: { id: string }) => i.id === id);
        if (item) {
          setName(item.name);
          setCategoryId(item.category_id);
          setDefaultUnit(item.default_unit);
          setDefaultQuantity(String(item.default_quantity));
          setMinStock(String(item.min_stock));
          setMaxStock(String(item.max_stock));
        }
      })();
    }
  }, [id]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        name,
        category_id: categoryId,
        default_unit: defaultUnit,
        default_quantity: parseFloat(defaultQuantity) || 1,
        min_stock: parseFloat(minStock) || 0,
        max_stock: parseFloat(maxStock) || 0,
      };
      if (isEdit) {
        await itemsAPI.update(id!, payload);
      } else {
        await itemsAPI.create(payload);
      }
      navigate('/items');
    } catch {
      alert('Erro ao salvar item');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto">
      <h2 className="text-xl font-bold text-gray-800 mb-4">
        {isEdit ? 'Editar Item' : 'Novo Item'}
      </h2>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6 space-y-4">
        <Input label="Nome" value={name} onChange={(e) => setName(e.target.value)} required />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
          <select
            className="w-full border rounded-lg px-3 py-2"
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            required
          >
            <option value="">Selecione...</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Unidade Padrão</label>
          <select
            className="w-full border rounded-lg px-3 py-2"
            value={defaultUnit}
            onChange={(e) => setDefaultUnit(e.target.value)}
          >
            {['un', 'kg', 'g', 'l', 'ml', 'pct', 'cx', 'dz'].map((u) => (
              <option key={u} value={u}>{u}</option>
            ))}
          </select>
        </div>

        <Input
          label="Qtd. Padrão"
          type="number"
          step="0.01"
          value={defaultQuantity}
          onChange={(e) => setDefaultQuantity(e.target.value)}
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Estoque Mínimo"
            type="number"
            step="0.01"
            value={minStock}
            onChange={(e) => setMinStock(e.target.value)}
          />
          <Input
            label="Estoque Máximo"
            type="number"
            step="0.01"
            value={maxStock}
            onChange={(e) => setMaxStock(e.target.value)}
          />
        </div>

        <div className="flex gap-3">
          <Button type="submit" isLoading={saving}>
            {isEdit ? 'Salvar' : 'Criar'}
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/items')}
          >
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  );
}
