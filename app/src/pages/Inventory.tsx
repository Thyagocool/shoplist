import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { itemsAPI, listsAPI, inventoryAPI } from '../services/api';
import type { ItemResponse } from '../types';
import Button from '../components/ui/Button';

export default function Inventory() {
  const [items, setItems] = useState<ItemResponse[]>([]);
  const [declarations, setDeclarations] = useState<Record<string, number>>({});
  const [, setListId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const [itemsRes] = await Promise.all([itemsAPI.list()]);
        setItems(itemsRes.data);
        const init: Record<string, number> = {};
        itemsRes.data.forEach((i: ItemResponse) => { init[i.id] = 0; });
        setDeclarations(init);
      } catch {
        // silent
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleDeclare = (itemId: string, value: number) => {
    setDeclarations((prev) => ({ ...prev, [itemId]: value }));
  };

  const handleSubmit = async () => {
    setSaving(true);
    try {
      // Create a list first
      const listRes = await listsAPI.create('Inventário ' + new Date().toLocaleDateString('pt-BR'));
      const newListId = listRes.data.id;
      setListId(newListId);

      // Declare each item
      for (const item of items) {
        const declared = declarations[item.id] || 0;
        if (declared > 0 || item.max_stock > 0) {
          await inventoryAPI.declare({
            shopping_list_id: newListId,
            pre_registered_item_id: item.id,
            declared_quantity: declared,
          });
        }
      }

      navigate(`/lists/${newListId}`);
    } catch {
      alert('Erro ao processar inventário');
    } finally {
      setSaving(false);
    }
  };

  const calcNeed = (item: ItemResponse, declared: number) => {
    return Math.max(0, item.max_stock - declared);
  };

  if (loading) return <p className="text-gray-400">Carregando...</p>;

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-800">Inventário 🏠</h2>
        <p className="text-sm text-gray-500">
          Informe quanto você tem em casa de cada item. A lista será gerada com o que falta.
        </p>
      </div>

      {items.length === 0 ? (
        <p className="text-gray-400 text-center py-8">
          Nenhum item no catálogo.{' '}
          <button onClick={() => navigate('/items/new')} className="text-primary-600 hover:underline">
            Cadastre itens primeiro
          </button>
        </p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => {
            const declared = declarations[item.id] || 0;
            const need = calcNeed(item, declared);
            return (
              <div key={item.id} className="bg-white rounded-lg shadow-sm border p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <p className="font-medium text-gray-800">{item.name}</p>
                    <p className="text-xs text-gray-500">
                      Max: {item.max_stock} {item.default_unit}
                      {item.min_stock > 0 && ` · Min: ${item.min_stock}`}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold">
                      Precisa: <span className={need > 0 ? 'text-orange-600' : 'text-primary-600'}>{need}</span>
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <label className="text-sm text-gray-600">Eu tenho:</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    className="flex-1 border rounded-lg px-3 py-1.5 text-sm"
                    value={declared || ''}
                    onChange={(e) => handleDeclare(item.id, parseFloat(e.target.value) || 0)}
                    placeholder="0"
                  />
                  <span className="text-sm text-gray-500">{item.default_unit}</span>
                </div>
                {need > 0 && (
                  <p className="text-xs text-orange-600 mt-1">
                    → Adicionar {need} {item.default_unit} à lista
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {items.length > 0 && (
        <Button onClick={handleSubmit} isLoading={saving}>
          Gerar Lista a partir do Inventário
        </Button>
      )}
    </div>
  );
}
