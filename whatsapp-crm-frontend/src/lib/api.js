// Filename: src/lib/api.js
import axios from 'axios';
import { toast } from 'sonner';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

const refreshToken = async () => {
  try {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) throw new Error("Session expired. Please log in again.");

    const response = await axios.post(`${API_BASE_URL}/crm-api/auth/token/refresh/`, {
      refresh: refreshToken,
    });

    const { access, refresh: newRefreshToken } = response.data;
    localStorage.setItem('accessToken', access);
    if (newRefreshToken) {
      localStorage.setItem('refreshToken', newRefreshToken);
    }
    return access;
  } catch (err) {
    // On failure, clear tokens and redirect to login
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    // A simple reload will do, and the ProtectedRoute component will handle the redirect.
    window.location.href = '/login';
    return Promise.reject(err);
  }
};

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise(function(resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token;
          return apiClient(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newAccessToken = await refreshToken();
        apiClient.defaults.headers.common['Authorization'] = 'Bearer ' + newAccessToken;
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        processQueue(null, newAccessToken);
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        toast.error(refreshError.message || "Your session has expired. Please log in again.");
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    const message =
      error.response?.data?.detail ||
      (typeof error.response?.data === 'object' && error.response?.data !== null
        ? Object.entries(error.response.data)
            .map(([k, v]) => `${k.replace(/_/g, ' ')}: ${Array.isArray(v) ? v.join(', ') : v}`)
            .join('; ')
        : error.message) ||
      'An unknown error occurred.';

    if (error.response?.status !== 401) {
      toast.error(`API Error: ${message}`);
    }

    return Promise.reject(error);
  }
);

// --- API Service Definitions ---

// --- Dashboard Stats API ---
export const dashboardApi = {
  getSummary: () => apiClient.get('/crm-api/stats/summary/'),
};

// --- Contacts API ---
export const contactsApi = {
  list: (params) => apiClient.get('/crm-api/conversations/contacts/', { params }),
  retrieve: (id) => apiClient.get(`/crm-api/conversations/contacts/${id}/`),
  patch: (id, data) => apiClient.patch(`/crm-api/conversations/contacts/${id}/`, data),
  listMessages: (contactId) => apiClient.get(`/crm-api/conversations/contacts/${contactId}/messages/`),
};

// --- Customer Profile API ---
export const profilesApi = {
  patch: (id, data) => apiClient.patch(`/crm-api/customer-data/profiles/${id}/`, data),
};

// --- Flows API (Expanded) ---
export const flowsApi = {
  list: () => apiClient.get('/crm-api/flows/flows/'),
  retrieve: (id) => apiClient.get(`/crm-api/flows/flows/${id}/`),
  create: (data) => apiClient.post('/crm-api/flows/flows/', data),
  update: (id, data) => apiClient.put(`/crm-api/flows/flows/${id}/`, data),
  patch: (id, data) => apiClient.patch(`/crm-api/flows/flows/${id}/`, data),
  delete: (id) => apiClient.delete(`/crm-api/flows/flows/${id}/`),

  // Steps
  listSteps: (flowId) => apiClient.get(`/crm-api/flows/flows/${flowId}/steps/`),
  createStep: (flowId, data) => apiClient.post(`/crm-api/flows/flows/${flowId}/steps/`, data),
  patchStep: (flowId, stepId, data) => apiClient.patch(`/crm-api/flows/flows/${flowId}/steps/${stepId}/`, data),
  deleteStep: (flowId, stepId) => apiClient.delete(`/crm-api/flows/flows/${flowId}/steps/${stepId}/`),

  // Transitions
  listTransitions: (flowId, stepId) => apiClient.get(`/crm-api/flows/flows/${flowId}/steps/${stepId}/transitions/`),
  createTransition: (flowId, stepId, data) => apiClient.post(`/crm-api/flows/flows/${flowId}/steps/${stepId}/transitions/`, data),
  updateTransition: (flowId, stepId, transitionId, data) => apiClient.put(`/crm-api/flows/flows/${flowId}/steps/${stepId}/transitions/${transitionId}/`, data),
  deleteTransition: (flowId, stepId, transitionId) => apiClient.delete(`/crm-api/flows/flows/${flowId}/steps/${stepId}/transitions/${transitionId}/`),
};

// --- Meta API Configs (Expanded) ---
export const metaApi = {
  getConfigs: () => apiClient.get('/crm-api/meta/api/configs/'),
  createConfig: (data) => apiClient.post('/crm-api/meta/api/configs/', data),
  updateConfig: (id, data) => apiClient.put(`/crm-api/meta/api/configs/${id}/`, data),
};

// --- Media Assets API ---
export const mediaAssetsApi = {
  list: (params) => apiClient.get('/media/media-assets/', { params }),
};

// --- Analytics API ---
export const analyticsApi = {
  getReports: (params) => apiClient.get('/crm-api/analytics/reports/', { params }),
};

// --- Saved Data API ---
export const savedDataApi = {
  list: () => apiClient.get('/crm-api/saved-data/'), // Assuming this endpoint
};

export default apiClient;