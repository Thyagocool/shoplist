import { useEffect, useState } from 'react';
import { itemsAPI } from '../services/api';
import type { ItemResponse } from '../types';

// Stock info is embedded in the item via min_stock/max_stock
// The backend tracks current stock, but for now we show the planned stock levels

export default function Stock() {
  const [items, setItems] = useState<ItemResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await itemsAPI.list();
        setItems(data);
      } catch {
        // silent
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const belowMin = items.filter(
    (i) => i.min_stock > 0
  );

  if (loading) return <p className="text-gray-400">Carregando...</p>;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800">Estoque 📦</h2>
        <p className="text-sm text-gray-500">Níveis de estoque configurados</p>
      </div>

      {/* Alerts */}
      {belowMin.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-red-600 uppercase mb-2">
            ⚠️ Itens com Estoque Mínimo ({belowMin.length})
          </h3>
          <div className="space-y-2">
            {belowMin.map((item) => (
              <div key={item.id} className="bg-white rounded-lg shadow-sm border-l-4 border-l-red-500 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-800">{item.name}</p>
                    <p className="text-xs text-gray-500">Mín: {item.min_stock} · Máx: {item.max_stock}</p>
                  </div>
                  <span className="text-sm font-semibold text-red-600">
                    {item.min_stock} {item.default_unit}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* All items stock levels */}
      <section>
        <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">
          Todos os Itens
        </h3>
        {items.length === 0 ? (
          <p className="text-gray-400 text-sm">Nenhum item cadastrado</p>
        ) : (
          <div className="space-y-2">
            {items.map((item) => (
              <div key={item.id} className="bg-white rounded-lg shadow-sm border p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-800">{item.name}</p>
                    <p className="text-xs text-gray-500">{item.category_name}</p>
                  </div>
                  <div className="text-right text-sm">
                    <p>
                      Min: <span className="font-medium">{item.min_stock}</span>
                    </p>
                    <p>
                      Max: <span className="font-medium">{item.max_stock}</span>
                    </p>
                  </div>
                </div>
                {item.max_stock > 0 && (
                  <div className="mt-2 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-500 h-2 rounded-full"
                      style={{ width: `${Math.min(100, (item.min_stock / item.max_stock) * 100)}%` }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
