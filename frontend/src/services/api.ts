import axios, { AxiosError } from 'axios'
import { useAuthStore } from '../stores/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config
    if (!originalRequest) return Promise.reject(error)

    if (error.response?.status === 401) {
      const refreshToken = useAuthStore.getState().refreshToken
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          })
          const { access_token } = response.data
          useAuthStore.getState().setTokens(access_token, refreshToken)
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch {
          useAuthStore.getState().logout()
          window.location.href = '/login'
        }
      } else {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Items API
export const itemsApi = {
  list: (params?: Record<string, unknown>) => api.get('/items', { params }),
  get: (id: string) => api.get(`/items/${id}`),
  create: (data: unknown) => api.post('/items', data),
  update: (id: string, data: unknown) => api.put(`/items/${id}`, data),
  delete: (id: string) => api.delete(`/items/${id}`),
  getStockSummary: (id: string) => api.get(`/items/${id}/stock-summary`),
}

// Stock API
export const stockApi = {
  list: (params?: Record<string, unknown>) => api.get('/stock', { params }),
  stockIn: (data: unknown) => api.post('/stock/in', data),
  stockOut: (data: unknown) => api.post('/stock/out', data),
  transfer: (data: unknown) => api.post('/stock/transfer', data),
  movements: (params?: Record<string, unknown>) => api.get('/stock/movements', { params }),
  adjust: (data: unknown) => api.post('/stock/adjust', data),
}

// Purchase Orders API
export const poApi = {
  list: (params?: Record<string, unknown>) => api.get('/purchase-orders', { params }),
  get: (id: string) => api.get(`/purchase-orders/${id}`),
  create: (data: unknown) => api.post('/purchase-orders', data),
  update: (id: string, data: unknown) => api.put(`/purchase-orders/${id}`, data),
  receive: (id: string, data: unknown) => api.post(`/purchase-orders/${id}/receive`, data),
  getPdf: (id: string) => api.get(`/purchase-orders/${id}/pdf`, { responseType: 'blob' }),
}

// Delivery Orders API
export const doApi = {
  list: (params?: Record<string, unknown>) => api.get('/delivery-orders', { params }),
  get: (id: string) => api.get(`/delivery-orders/${id}`),
  create: (data: unknown) => api.post('/delivery-orders', data),
  update: (id: string, data: unknown) => api.put(`/delivery-orders/${id}`, data),
  updateStatus: (id: string, data: unknown) => api.patch(`/delivery-orders/${id}/status`, data),
}

// Repair Tickets API
export const repairApi = {
  list: (params?: Record<string, unknown>) => api.get('/repair-tickets', { params }),
  get: (id: string) => api.get(`/repair-tickets/${id}`),
  create: (data: unknown) => api.post('/repair-tickets', data),
  update: (id: string, data: unknown) => api.put(`/repair-tickets/${id}`, data),
  updateStatus: (id: string, data: unknown) => api.patch(`/repair-tickets/${id}/status`, data),
  assign: (id: string, data: unknown) => api.patch(`/repair-tickets/${id}/assign`, data),
}

// Projects API
export const projectApi = {
  list: (params?: Record<string, unknown>) => api.get('/projects', { params }),
  get: (id: string) => api.get(`/projects/${id}`),
  create: (data: unknown) => api.post('/projects', data),
  update: (id: string, data: unknown) => api.put(`/projects/${id}`, data),
  delete: (id: string) => api.delete(`/projects/${id}`),
  getStock: (id: string) => api.get(`/projects/${id}/stock`),
}

// Serial Numbers API
export const serialApi = {
  list: (params?: Record<string, unknown>) => api.get('/serials', { params }),
  get: (id: string) => api.get(`/serials/${id}`),
  create: (data: unknown[]) => api.post('/serials', data),
  update: (id: string, data: unknown) => api.put(`/serials/${id}`, data),
  bulkUpdate: (data: unknown) => api.post('/serials/bulk-update', data),
}

// Batch Numbers API
export const batchApi = {
  list: (params?: Record<string, unknown>) => api.get('/batches', { params }),
  get: (id: string) => api.get(`/batches/${id}`),
  create: (data: unknown) => api.post('/batches', data),
  update: (id: string, data: unknown) => api.put(`/batches/${id}`, data),
  delete: (id: string) => api.delete(`/batches/${id}`),
}

// Locations API
export const locationApi = {
  list: (params?: Record<string, unknown>) => api.get('/locations', { params }),
  get: (id: string) => api.get(`/locations/${id}`),
  create: (data: unknown) => api.post('/locations', data),
  update: (id: string, data: unknown) => api.put(`/locations/${id}`, data),
  delete: (id: string) => api.delete(`/locations/${id}`),
}

// Users API
export const usersApi = {
  list: (params?: Record<string, unknown>) => api.get('/users', { params }),
  get: (id: string) => api.get(`/users/${id}`),
  create: (data: unknown) => api.post('/users', data),
  update: (id: string, data: unknown) => api.put(`/users/${id}`, data),
  delete: (id: string) => api.delete(`/users/${id}`),
}

// Reports API
export const reportsApi = {
  dashboard: () => api.get('/reports/dashboard'),
  inventorySummary: (params?: Record<string, unknown>) => api.get('/reports/inventory-summary', { params }),
  stockMovements: (params?: Record<string, unknown>) => api.get('/reports/stock-movements', { params }),
  poSummary: () => api.get('/reports/purchase-order-summary'),
  repairSummary: () => api.get('/reports/repair-summary'),
  lowStock: () => api.get('/reports/low-stock'),
}

// Auth API
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
  me: () => api.get('/auth/me'),
}
