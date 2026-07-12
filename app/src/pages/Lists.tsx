import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { listsAPI } from '../services/api';
import type { ShoppingListResponse } from '../types';

export default function Lists() {
  const [lists, setLists] = useState<ShoppingListResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const { data } = await listsAPI.list();
        setLists(data);
      } catch {
        // silent
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleComplete = async (id: string) => {
    await listsAPI.complete(id);
    const { data } = await listsAPI.list();
    setLists(data);
  };

  const handleCancel = async (id: string) => {
    if (!confirm('Cancelar esta lista?')) return;
    await listsAPI.cancel(id);
    const { data } = await listsAPI.list();
    setLists(data);
  };

  const active = lists.filter((l) => l.status === 'in_progress' || l.status === 'pending');
  const completed = lists.filter((l) => l.status === 'completed' || l.status === 'cancelled');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Listas de Compras</h2>
        <button
          onClick={() => navigate('/lists/new')}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition"
        >
          + Nova Lista
        </button>
      </div>

      {loading ? (
        <p className="text-gray-400">Carregando...</p>
      ) : (
        <>
          {/* Active */}
          <section>
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Ativas</h3>
            {active.length === 0 ? (
              <p className="text-gray-400 text-sm">Nenhuma lista ativa</p>
            ) : (
              <div className="space-y-2">
                {active.map((list) => (
                  <div
                    key={list.id}
                    className="bg-white rounded-lg shadow-sm border p-4"
                  >
                    <Link
                      to={`/lists/${list.id}`}
                      className="font-medium text-gray-800 hover:text-primary-700"
                    >
                      {list.name}
                    </Link>
                    <p className="text-xs text-gray-400 mt-1">
                      {list.items?.length || 0} itens ·{' '}
                      {list.items?.filter((i) => i.checked).length || 0} marcados
                      {list.items?.some((i) => i.price_cents) && (
                        <>
                          {' · '}
                          <span className="text-primary-600 font-medium">
                            R$ {(
                              (list.items?.reduce((acc, i) => acc + (i.price_cents || 0), 0) || 0) /
                              100
                            ).toFixed(2)}
                          </span>
                        </>
                      )}
                    </p>
                    <div className="flex gap-2 mt-2">
                      <button
                        onClick={() => handleComplete(list.id)}
                        className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded"
                      >
                        Finalizar
                      </button>
                      <button
                        onClick={() => handleCancel(list.id)}
                        className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Completed */}
          <section>
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Finalizadas</h3>
            {completed.length === 0 ? (
              <p className="text-gray-400 text-sm">Nenhuma lista finalizada</p>
            ) : (
              <div className="space-y-2">
                {completed.map((list) => (
                  <div
                    key={list.id}
                    className="bg-white rounded-lg shadow-sm border p-4 opacity-70"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-800">{list.name}</span>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        list.status === 'completed' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-500'
                      }`}>
                        {list.status === 'completed' ? 'OK' : 'Cancelado'}
                      </span>
                    </div>
                    {list.completed_at && (
                      <p className="text-xs text-gray-400 mt-1">
                        {new Date(list.completed_at).toLocaleDateString('pt-BR')}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
