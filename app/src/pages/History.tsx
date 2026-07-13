import { useEffect, useState } from 'react';
import { listsAPI } from '../services/api';
import HeroIcon from '../components/ui/HeroIcon';
import type { ShoppingListResponse } from '../types';

export default function History() {
  const [lists, setLists] = useState<ShoppingListResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await listsAPI.list();
        setLists(data.filter((l: ShoppingListResponse) => l.status === 'completed'));
      } catch {
        // silent
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const totalSpent = (list: ShoppingListResponse) => {
    if (!list.items) return 0;
    return list.items.reduce((acc, i) => acc + (i.price_cents || 0), 0);
  };

  if (loading) return <p className="text-gray-400">Carregando...</p>;

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center gap-2">
          <HeroIcon name="clock" className="size-6 text-gray-800" />
          <h2 className="text-xl font-bold text-gray-800">Histórico de Compras</h2>
        </div>
        <p className="text-sm text-gray-500">Compras finalizadas</p>
      </div>

      {lists.length === 0 ? (
        <p className="text-gray-400 text-center py-8">Nenhuma compra finalizada ainda</p>
      ) : (
        <div className="space-y-3">
          {lists.map((list) => {
            const spent = totalSpent(list);
            const checked = list.items?.filter((i) => i.checked).length || 0;

            return (
              <div key={list.id} className="bg-white rounded-lg shadow-sm border p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-800">{list.name}</p>
                    <p className="text-xs text-gray-500">
                      {list.completed_at
                        ? new Date(list.completed_at).toLocaleDateString('pt-BR')
                        : '—'}
                      {' · '}
                      {checked}/{list.items?.length || 0} itens
                    </p>
                  </div>
                  {spent > 0 && (
                    <p className="text-lg font-bold text-primary-700">
                      R$ {(spent / 100).toFixed(2)}
                    </p>
                  )}
                </div>

                {list.items && list.items.length > 0 && (
                  <div className="mt-2 pt-2 border-t space-y-1">
                    {list.items.slice(0, 5).map((item) => (
                      <div key={item.id} className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">
                          {item.item_name || item.custom_name}
                        </span>
                        <span className="text-gray-500">
                          {item.estimated_quantity} {item.unit}
                          {item.price_cents ? ` · R$ ${(item.price_cents / 100).toFixed(2)}` : ''}
                        </span>
                      </div>
                    ))}
                    {list.items.length > 5 && (
                      <p className="text-xs text-gray-400">...e mais {list.items.length - 5} itens</p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
