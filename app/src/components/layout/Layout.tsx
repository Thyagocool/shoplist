import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const navItems = [
  { path: '/', label: 'Início', icon: '🏠' },
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
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-green-700 text-white shadow-md">
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
                className="text-sm bg-green-600 hover:bg-green-500 px-3 py-1 rounded transition"
              >
                Sair
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 max-w-4xl mx-auto px-4 py-6 w-full">
        <Outlet />
      </main>

      {/* Bottom Navigation */}
      <nav className="bg-white border-t shadow-lg">
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
                    ? 'bg-green-100 text-green-700'
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
