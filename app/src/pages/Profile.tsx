import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import Button from '../components/ui/Button';

export default function Profile() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="max-w-lg mx-auto space-y-4">
      <h2 className="text-xl font-bold text-gray-800">Meu Perfil</h2>

      <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-2xl font-bold text-primary-700">
              {user?.name?.charAt(0).toUpperCase() || '?'}
            </span>
          </div>
          <div>
            <p className="text-lg font-semibold text-gray-800">{user?.name}</p>
            <p className="text-sm text-gray-500">{user?.email}</p>
          </div>
        </div>

        <div className="border-t pt-4 space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Nome</span>
            <span className="font-medium">{user?.name}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Email</span>
            <span className="font-medium">{user?.email}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Membro desde</span>
            <span className="font-medium">—</span>
          </div>
        </div>

        <div className="border-t pt-4">
          <Button variant="danger" onClick={handleLogout}>
            Sair da Conta
          </Button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="font-semibold text-gray-800 mb-2">Sobre</h3>
        <p className="text-sm text-gray-500">
          Shoplist v0.1.0
        </p>
        <p className="text-sm text-gray-500 mt-1">
          Sua lista de compras inteligente com inventário, OCR e controle de estoque.
        </p>
      </div>
    </div>
  );
}
