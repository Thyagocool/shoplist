import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listsAPI } from '../services/api';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

export default function ListForm() {
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try {
      const { data } = await listsAPI.create(name);
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
        <div className="flex gap-2">
          <Button type="submit" isLoading={saving}>Criar Lista</Button>
          <Button variant="secondary" onClick={() => navigate('/lists')}>Cancelar</Button>
        </div>
      </form>
    </div>
  );
}
