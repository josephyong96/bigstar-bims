import axios from "axios";
import { useAuthStore } from "../stores/authStore";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Auth
export const login = (username: string, password: string) =>
  api.post("/auth/login", { username, password });

export const getMe = () => api.get("/auth/me");

// Items
export const getItems = (params?: Record<string, unknown>) =>
  api.get("/items", { params });
export const getItem = (id: number) => api.get(`/items/${id}`);
export const createItem = (data: unknown) => api.post("/items", data);
export const updateItem = (id: number, data: unknown) =>
  api.put(`/items/${id}`, data);
export const deleteItem = (id: number) => api.delete(`/items/${id}`);

// Projects
export const getProjects = (params?: Record<string, unknown>) =>
  api.get("/projects", { params });
export const getProject = (id: number) => api.get(`/projects/${id}`);
export const createProject = (data: unknown) => api.post("/projects", data);
export const updateProject = (id: number, data: unknown) =>
  api.put(`/projects/${id}`, data);
export const deleteProject = (id: number) => api.delete(`/projects/${id}`);

// Purchase Orders
export const getPurchaseOrders = (params?: Record<string, unknown>) =>
  api.get("/purchase-orders", { params });
export const getPurchaseOrder = (id: number) => api.get(`/purchase-orders/${id}`);
export const createPurchaseOrder = (data: unknown) =>
  api.post("/purchase-orders", data);
export const updatePurchaseOrder = (id: number, data: unknown) =>
  api.put(`/purchase-orders/${id}`, data);
export const deletePurchaseOrder = (id: number) =>
  api.delete(`/purchase-orders/${id}`);

// Delivery Orders
export const getDeliveryOrders = (params?: Record<string, unknown>) =>
  api.get("/delivery-orders", { params });
export const getDeliveryOrder = (id: number) => api.get(`/delivery-orders/${id}`);
export const createDeliveryOrder = (data: unknown) =>
  api.post("/delivery-orders", data);
export const updateDeliveryOrder = (id: number, data: unknown) =>
  api.put(`/delivery-orders/${id}`, data);
export const deleteDeliveryOrder = (id: number) =>
  api.delete(`/delivery-orders/${id}`);

// Repairs
export const getRepairs = (params?: Record<string, unknown>) =>
  api.get("/repairs", { params });
export const getRepair = (id: number) => api.get(`/repairs/${id}`);
export const createRepair = (data: unknown) => api.post("/repairs", data);
export const updateRepair = (id: number, data: unknown) =>
  api.put(`/repairs/${id}`, data);
export const deleteRepair = (id: number) => api.delete(`/repairs/${id}`);

// Stock Movements
export const getStockMovements = (params?: Record<string, unknown>) =>
  api.get("/stock-movements", { params });
export const createStockMovement = (data: unknown) =>
  api.post("/stock-movements", data);

// Batch Numbers
export const getBatchNumbers = (params?: Record<string, unknown>) =>
  api.get("/batch-numbers", { params });
export const getBatchNumber = (id: number) => api.get(`/batch-numbers/${id}`);

// Serial Numbers
export const getSerialNumbers = (params?: Record<string, unknown>) =>
  api.get("/serial-numbers", { params });
export const getSerialNumber = (id: number) => api.get(`/serial-numbers/${id}`);

// Locations
export const getLocations = (params?: Record<string, unknown>) =>
  api.get("/locations", { params });
export const createLocation = (data: unknown) => api.post("/locations", data);
export const updateLocation = (id: number, data: unknown) =>
  api.put(`/locations/${id}`, data);
export const deleteLocation = (id: number) => api.delete(`/locations/${id}`);

// Users
export const getUsers = (params?: Record<string, unknown>) =>
  api.get("/users", { params });
export const createUser = (data: unknown) => api.post("/users", data);
export const updateUser = (id: number, data: unknown) =>
  api.put(`/users/${id}`, data);
export const deleteUser = (id: number) => api.delete(`/users/${id}`);

// Dashboard
export const getDashboardStats = () => api.get("/dashboard/stats");
export const getDashboardActivities = () => api.get("/dashboard/activities");
export const getDashboardAlerts = () => api.get("/dashboard/alerts");
