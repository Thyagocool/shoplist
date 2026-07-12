import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const navItems = [
  { path: '/', label: 'Início', icon: '🏠' },
  { path: '/categories', label: 'Categorias', icon: '🏷️' },
  { path: '/items', label: 'Itens', icon: '📦' },
  { path: '/stores', label: 'Lojas', icon: '🏪' },
  { path: '/lists', label: 'Listas', icon: '📋' },
  { path: '/inventory', label: 'Inventário', icon: '🏠' },
  { path: '/ocr', label: 'OCR', icon: '📸' },
  { path: '/stock', label: 'Estoque', icon: '📊' },
  { path: '/history', label: 'Histórico', icon: '📜' },
  { path: '/profile', label: 'Perfil', icon: '👤' },
];

export default function Layout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Header — fixo no topo */}
      <header className="bg-primary-700 text-white shadow-md flex-shrink-0">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <h1
            className="text-xl font-bold cursor-pointer"
            onClick={() => navigate('/')}
          >
            Shoplist
          </h1>
          {user && (
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/profile')}
                className="text-sm opacity-90 hover:opacity-100"
              >
                {user.name}
              </button>
              <button
                onClick={handleLogout}
                className="text-sm bg-primary-600 hover:bg-primary-500 px-3 py-1 rounded transition"
              >
                Sair
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main — scrolla, ocupa o espaço restante */}
      <main className="flex-1 overflow-y-auto max-w-4xl mx-auto px-4 py-6 w-full min-h-0">
        <Outlet />
      </main>

      {/* Bottom Navigation — fixo embaixo */}
      <nav className="bg-white border-t shadow-lg flex-shrink-0">
        <div className="max-w-4xl mx-auto px-2 py-1 flex overflow-x-auto gap-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path ||
              (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`flex flex-col items-center gap-0.5 px-3 py-2 rounded-lg text-xs whitespace-nowrap transition ${
                  isActive
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-500 hover:text-gray-800 hover:bg-gray-100'
                }`}
              >
                <span className="text-base">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
