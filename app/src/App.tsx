import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/layout/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import CategoriesList from './pages/CategoriesList';
import ItemsList from './pages/ItemsList';
import StoresList from './pages/StoresList';
import Lists from './pages/Lists';
import ListForm from './pages/ListForm';
import ListDetail from './pages/ListDetail';
import Inventory from './pages/Inventory';
import OCR from './pages/OCR';
import Stock from './pages/Stock';
import History from './pages/History';
import Profile from './pages/Profile';

export default function App() {
  const loadUser = useAuthStore((s) => s.loadUser);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => {
    if (isAuthenticated) {
      loadUser();
    }
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/" replace /> : <Login />}
        />
        <Route
          path="/register"
          element={isAuthenticated ? <Navigate to="/" replace /> : <Register />}
        />

        {/* Protected */}
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/categories" element={<CategoriesList />} />
            <Route path="/items" element={<ItemsList />} />
            <Route path="/stores" element={<StoresList />} />
            <Route path="/lists" element={<Lists />} />
            <Route path="/lists/new" element={<ListForm />} />
            <Route path="/lists/:id" element={<ListDetail />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/ocr" element={<OCR />} />
            <Route path="/stock" element={<Stock />} />
            <Route path="/history" element={<History />} />
            <Route path="/profile" element={<Profile />} />
          </Route>
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
