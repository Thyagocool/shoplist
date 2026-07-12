import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { itemsAPI, storesAPI, listsAPI } from '../services/api';
import type { ShoppingListResponse } from '../types';

export default function Dashboard() {
  const user = useAuthStore((s) => s.user);
  const [lists, setLists] = useState<ShoppingListResponse[]>([]);
  const [stats, setStats] = useState({ items: 0, stores: 0, lists: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [itemsRes, storesRes, listsRes] = await Promise.all([
          itemsAPI.list(),
          storesAPI.list(),
          listsAPI.list(),
        ]);
        setStats({
          items: itemsRes.data.length,
          stores: storesRes.data.length,
          lists: listsRes.data.length,
        });
        setLists(listsRes.data.slice(0, 5));
      } catch {
        // silently fail for dashboard
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const activeLists = lists.filter((l) => l.status === 'in_progress' || l.status === 'pending');

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800">
          Olá, {user?.name || 'usuário'}! 👋
        </h2>
        <p className="text-gray-500">Bem-vindo ao Shoplist</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow-sm p-4 text-center">
          <p className="text-2xl font-bold text-primary-700">{stats.items}</p>
          <p className="text-sm text-gray-500">Itens</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 text-center">
          <p className="text-2xl font-bold text-blue-700">{stats.stores}</p>
          <p className="text-sm text-gray-500">Lojas</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 text-center">
          <p className="text-2xl font-bold text-purple-700">{stats.lists}</p>
          <p className="text-sm text-gray-500">Listas</p>
        </div>
      </div>

      {/* Active lists */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Listas Ativas</h3>
          <Link
            to="/lists"
            className="text-sm text-primary-600 hover:underline"
          >
            Ver todas
          </Link>
        </div>

        {loading ? (
          <p className="text-gray-400 text-sm">Carregando...</p>
        ) : activeLists.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <p className="text-lg mb-2">Nenhuma lista ativa</p>
            <Link
              to="/lists/new"
              className="text-primary-600 hover:underline text-sm"
            >
              Criar nova lista
            </Link>
          </div>
        ) : (
          <div className="space-y-2">
            {activeLists.map((list) => (
              <Link
                key={list.id}
                to={`/lists/${list.id}`}
                className="block p-3 rounded-lg hover:bg-gray-50 transition border border-gray-100"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-800">{list.name}</span>
                  <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded">
                    {list.items?.filter((i) => i.checked).length || 0}/{list.items?.length || 0}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 gap-4">
        <Link
          to="/lists/new"
          className="bg-primary-600 text-white rounded-xl p-4 text-center hover:bg-primary-700 transition shadow-sm"
        >
          <p className="text-lg font-bold">+</p>
          <p className="text-sm">Nova Lista</p>
        </Link>
        <Link
          to="/items"
          className="bg-blue-600 text-white rounded-xl p-4 text-center hover:bg-blue-700 transition shadow-sm"
        >
          <p className="text-lg font-bold">📦</p>
          <p className="text-sm">Catálogo</p>
        </Link>
      </div>
    </div>
  );
}
