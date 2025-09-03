import axios from 'axios';
import { toast } from 'sonner';

// Use environment variables for the API base URL, with a sensible fallback for local development.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add the JWT token to every outgoing request.
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken'); // Assumes token is stored in localStorage
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor to handle common API errors and provide user feedback.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.response?.data?.error || error.message || 'An unknown error occurred.';
    
    // Avoid showing toasts for certain errors, like 401 which should trigger a redirect.
    if (error.response?.status !== 401) {
      toast.error(`API Error: ${message}`);
    }
    
    // Handle token expiry and refresh logic here if needed.
    if (error.response?.status === 401) {
        // e.g., redirect to login page
        // window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

// --- API Service Definitions ---

// --- Flows API ---
export const flowsApi = {
  list: () => apiClient.get('/crm-api/flows/flows/'),
  get: (id) => apiClient.get(`/crm-api/flows/flows/${id}/`),
  create: (data) => apiClient.post('/crm-api/flows/flows/', data),
  update: (id, data) => apiClient.put(`/crm-api/flows/flows/${id}/`, data),
  delete: (id) => apiClient.delete(`/crm-api/flows/flows/${id}/`),
};

// --- Flow Steps API ---
export const flowStepsApi = {
  list: (flowId) => apiClient.get(`/crm-api/flows/flows/${flowId}/steps/`),
  get: (flowId, stepId) => apiClient.get(`/crm-api/flows/flows/${flowId}/steps/${stepId}/`),
  create: (flowId, data) => apiClient.post(`/crm-api/flows/flows/${flowId}/steps/`, data),
  update: (flowId, stepId, data) => apiClient.put(`/crm-api/flows/flows/${flowId}/steps/${stepId}/`, data),
  delete: (flowId, stepId) => apiClient.delete(`/crm-api/flows/flows/${flowId}/steps/${stepId}/`),
};

// --- Flow Transitions API ---
export const flowTransitionsApi = {
    list: (flowId, stepId) => apiClient.get(`/crm-api/flows/flows/${flowId}/steps/${stepId}/transitions/`),
    create: (flowId, stepId, data) => apiClient.post(`/crm-api/flows/flows/${flowId}/steps/${stepId}/transitions/`, data),
    update: (flowId, stepId, transitionId, data) => apiClient.put(`/crm-api/flows/flows/${flowId}/steps/${stepId}/transitions/${transitionId}/`, data),
    delete: (flowId, stepId, transitionId) => apiClient.delete(`/crm-api/flows/flows/${flowId}/steps/${stepId}/transitions/${transitionId}/`),
};

// --- Media Assets API ---
export const mediaAssetsApi = {
  list: (params) => apiClient.get('/crm-api/media/assets/', { params }),
  get: (id) => apiClient.get(`/crm-api/media/assets/${id}/`),
  create: (formData) => apiClient.post('/crm-api/media/assets/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  update: (id, formData) => apiClient.patch(`/crm-api/media/assets/${id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  delete: (id) => apiClient.delete(`/crm-api/media/assets/${id}/`),
  manualSync: (id) => apiClient.post(`/crm-api/media/assets/${id}/sync-with-whatsapp/`),
};

export default apiClient;