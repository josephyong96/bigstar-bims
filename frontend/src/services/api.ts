import axios, { AxiosError } from "axios";
import { useAuthStore } from "@/stores/authStore";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().clearAuth();
      window.location.href = "/login";
    }
    const message =
      (error.response?.data as any)?.detail || error.message || "Request failed";
    return Promise.reject(new Error(message));
  }
);

export const api = {
  get: async <T = any>(url: string, params?: any): Promise<T> => {
    const response = await apiClient.get(url, { params });
    return response.data;
  },

  post: async <T = any>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.post(url, data);
    return response.data;
  },

  put: async <T = any>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.put(url, data);
    return response.data;
  },

  patch: async <T = any>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.patch(url, data);
    return response.data;
  },

  delete: async <T = any>(url: string): Promise<T> => {
    const response = await apiClient.delete(url);
    return response.data;
  },
};
