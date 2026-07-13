import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { redirectToLogin } from '../lib/authRedirect';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor — attach JWT
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — auto-refresh on 401
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: unknown) => void;
  reject: (reason: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        redirectToLogin();
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post(`${API_BASE}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        const newToken = data.access_token;
        localStorage.setItem('access_token', newToken);
        processQueue(null, newToken);
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
        }
        return api(originalRequest);
      } catch {
        processQueue(error, null);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        redirectToLogin();
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;

// --- Auth ---
export const authAPI = {
  register: (data: { name: string; email: string; password: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  refresh: (refresh_token: string) =>
    api.post('/auth/refresh', { refresh_token }),
  me: () => api.get('/auth/me'),
};

// --- Categories ---
export const categoriesAPI = {
  list: () => api.get('/categories'),
  create: (name: string) => api.post('/categories', { name }),
  update: (id: string, name: string) => api.put(`/categories/${id}`, { name }),
  delete: (id: string) => api.delete(`/categories/${id}`),
};

// --- Items ---
export const itemsAPI = {
  list: () => api.get('/items'),
  create: (data: Record<string, unknown>) => api.post('/items', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/items/${id}`, data),
  delete: (id: string) => api.delete(`/items/${id}`),
};

// --- Stores ---
export const storesAPI = {
  list: () => api.get('/stores'),
  create: (name: string) => api.post('/stores', { name }),
  update: (id: string, name: string) => api.put(`/stores/${id}`, { name }),
  delete: (id: string) => api.delete(`/stores/${id}`),
};

// --- Inventory ---
export const inventoryAPI = {
  list: (listId: string) => api.get('/inventory', { params: { list_id: listId } }),
  declare: (data: {
    shopping_list_id: string;
    pre_registered_item_id: string;
    declared_quantity: number;
  }) => api.post('/inventory', data),
};

// --- Shopping Lists ---
export const listsAPI = {
  list: () => api.get('/lists'),
  get: (id: string) => api.get(`/lists/${id}`),
  create: (name: string, store_id?: string) =>
    api.post('/lists', { name, store_id }),
  addItem: (
    listId: string,
    data: {
      pre_registered_item_id?: string;
      custom_name?: string;
      estimated_quantity?: number;
      unit?: string;
    }
  ) => api.post(`/lists/${listId}/items`, data),
  toggleItem: (itemId: string) =>
    api.patch(`/lists/items/${itemId}/toggle`),
  complete: (id: string) => api.post(`/lists/${id}/complete`),
  cancel: (id: string) => api.post(`/lists/${id}/cancel`),
  updateItem: (itemId: string, data: { unit?: string; estimated_quantity?: number; price_cents?: number }) =>
    api.patch(`/lists/items/${itemId}`, data),
  removeItem: (itemId: string) => api.delete(`/lists/items/${itemId}`),
  checkout: (
    id: string,
    data: { items: Array<{ shopping_list_item_id: string; price_cents: number }> }
  ) => api.post(`/lists/${id}/checkout`, data),
};

// --- OCR ---
export const ocrAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/ocr', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};
