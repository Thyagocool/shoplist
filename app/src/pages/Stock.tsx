import { useEffect, useMemo, useState } from 'react';
import { itemsAPI } from '../services/api';
import HeroIcon from '../components/ui/HeroIcon';
import type { ItemResponse } from '../types';

interface CategoryGroup {
  id: string;
  name: string;
  items: ItemResponse[];
  totalMin: number;
  totalMax: number;
  pct: number; // 0–100
}

export default function Stock() {
  const [items, setItems] = useState<ItemResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [alertsOpen, setAlertsOpen] = useState(true);

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

  const groups = useMemo<CategoryGroup[]>(() => {
    const map = new Map<string, ItemResponse[]>();
    for (const item of items) {
      const key = item.category_id || '__uncategorized__';
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(item);
    }

    return Array.from(map.entries())
      .map(([id, catItems]) => {
        const totalMin = catItems.reduce((s, i) => s + (i.min_stock || 0), 0);
        const totalMax = catItems.reduce((s, i) => s + (i.max_stock || 0), 0);
        const pct = totalMax > 0 ? Math.round((totalMin / totalMax) * 100) : 0;
        const name =
          id === '__uncategorized__'
            ? 'Sem categoria'
            : catItems[0]?.category_name || 'Sem categoria';
        return { id, name, items: catItems, totalMin, totalMax, pct };
      })
      .sort((a, b) => b.pct - a.pct); // mais crítico primeiro
  }, [items]);

  const belowMin = items.filter((i) => i.min_stock > 0);

  if (loading) return <p className="text-gray-400">Carregando...</p>;

  const pctColor = (pct: number) => {
    if (pct <= 25) return 'bg-red-500';
    if (pct <= 50) return 'bg-orange-400';
    if (pct <= 75) return 'bg-yellow-400';
    return 'bg-green-500';
  };

  const pctBgColor = (pct: number) => {
    if (pct <= 25) return 'bg-red-100';
    if (pct <= 50) return 'bg-orange-100';
    if (pct <= 75) return 'bg-yellow-100';
    return 'bg-green-100';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <HeroIcon name="archive-box" className="size-6 text-gray-800" />
          <h2 className="text-xl font-bold text-gray-800">Estoque</h2>
        </div>
        <p className="text-sm text-gray-500">
          {items.length} itens em {groups.length} categorias
        </p>
      </div>

      {/* Alerts — itens abaixo do mínimo */}
      {belowMin.length > 0 && (
        <section>
          <div
            className="flex items-center justify-between cursor-pointer select-none mb-2"
            onClick={() => setAlertsOpen(!alertsOpen)}
          >
            <h3 className="text-sm font-semibold text-red-600 uppercase flex items-center gap-1">
              <HeroIcon name="exclamation-triangle" className="size-4" />
              Atenção ({belowMin.length})
            </h3>
            <HeroIcon
              name="chevron-down"
              className={`size-4 text-red-400 transition-transform ${alertsOpen ? '' : '-rotate-90'}`}
            />
          </div>
          {alertsOpen && (
            <div className="space-y-1.5">
              {belowMin.map((item) => (
                <div
                  key={item.id}
                  className="bg-red-50 border border-red-200 rounded-lg px-4 py-2 flex items-center justify-between"
                >
                  <div>
                    <p className="text-sm font-medium text-red-800">{item.name}</p>
                    <p className="text-xs text-red-500">{item.category_name}</p>
                  </div>
                  <span className="text-xs font-semibold text-red-600 bg-red-100 px-2 py-0.5 rounded">
                    Min: {item.min_stock} {item.default_unit}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Categorias */}
      {groups.length === 0 ? (
        <p className="text-gray-400 text-sm">Nenhum item cadastrado</p>
      ) : (
        <div className="space-y-4">
          {/* Expandir / Recolher tudo */}
          {groups.length > 1 && (
            <button
              onClick={() =>
                setExpanded(
                  expanded.size === groups.length ? new Set() : new Set(groups.map((g) => g.id))
                )
              }
              className="text-xs px-3 py-1 rounded-full border border-gray-200 bg-white text-gray-500 hover:bg-gray-100 active:bg-gray-200 transition"
            >
              {expanded.size === groups.length ? (
                <span className="inline-flex items-center gap-1">
                  <HeroIcon name="chevron-up" className="size-4" />
                  Recolher tudo
                </span>
              ) : (
                <span className="inline-flex items-center gap-1">
                  <HeroIcon name="chevron-down" className="size-4" />
                  Expandir tudo
                </span>
              )}
            </button>
          )}

          {groups.map((group) => {
            const isExpanded = expanded.has(group.id);
            const hasStock = group.items.some((i) => i.max_stock > 0);
            return (
              <div key={group.id} className="bg-white rounded-xl shadow-sm border overflow-hidden">
                {/* Cabeçalho da categoria — clicável */}
                <div
                  className="px-4 py-3 border-b border-gray-100 cursor-pointer select-none"
                  onClick={() => {
                    const next = new Set(expanded);
                    if (isExpanded) next.delete(group.id);
                    else next.add(group.id);
                    setExpanded(next);
                  }}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-2">
                      <HeroIcon
                        name="chevron-right"
                        className={`size-3 text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                      />
                      <h3 className="font-semibold text-gray-800">{group.name}</h3>
                    </div>
                    <span className="text-xs text-gray-500">
                      {group.items.length} itens
                    </span>
                  </div>
                  {hasStock && (
                    <div className="flex items-center gap-3">
                      <div className={`flex-1 h-2.5 rounded-full ${pctBgColor(group.pct)}`}>
                        <div
                          className={`h-2.5 rounded-full transition-all ${pctColor(group.pct)}`}
                          style={{ width: `${Math.min(100, group.pct)}%` }}
                        />
                      </div>
                      <span className={`text-xs font-semibold ${pctColor(group.pct).replace('bg-', 'text-')}`}>
                        {group.pct}%
                      </span>
                    </div>
                  )}
                  {!hasStock && (
                    <p className="text-xs text-gray-400">Nenhum item com estoque configurado</p>
                  )}
                </div>

                {/* Itens da categoria — expansível */}
                {isExpanded && (
                  <div className="divide-y divide-gray-50">
                    {group.items.map((item) => {
                      const itemPct =
                        item.max_stock > 0
                          ? Math.round((item.min_stock / item.max_stock) * 100)
                          : 0;
                      const hasItemStock = item.max_stock > 0;
                      return (
                        <div key={item.id} className="px-4 py-2.5 flex items-center justify-between">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-800 truncate">
                              {item.name}
                            </p>
                            {hasItemStock && (
                              <div className="flex items-center gap-2 mt-1">
                                <div className="flex-1 max-w-[120px] bg-gray-100 rounded-full h-1.5">
                                  <div
                                    className={`h-1.5 rounded-full ${pctColor(itemPct)}`}
                                    style={{ width: `${Math.min(100, itemPct)}%` }}
                                  />
                                </div>
                                <span className="text-xs text-gray-400">
                                  {item.min_stock}–{item.max_stock} {item.default_unit}
                                </span>
                              </div>
                            )}
                            {!hasItemStock && (
                              <p className="text-xs text-gray-400">Sem estoque configurado</p>
                            )}
                          </div>
                          {hasItemStock && (
                            <span className={`text-xs font-medium ml-3 ${pctColor(itemPct).replace('bg-', 'text-')}`}>
                              {itemPct}%
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
                {!isExpanded && (
                  <div className="px-4 py-2 text-xs text-gray-400">
                    Clique para ver {group.items.length} item(ns)
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
