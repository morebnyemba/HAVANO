import { jwtDecode } from 'jwt-decode';

const API_AUTH_BASE_URL = `${import.meta.env.VITE_API_BASE_URL || 'https://autochats.havano.online'}/crm-api/auth`; // Base for auth endpoints
const ACCESS_TOKEN_KEY = 'accessToken';
const REFRESH_TOKEN_KEY = 'refreshToken';

export const authService = {
  // Token Management
  storeTokens(accessToken, refreshToken) {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    if (refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }
  },
  clearTokens() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
  getAccessToken: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),

  // API Calls
  async login(username, password) {
    try {
      // Use a raw fetch call for login to avoid interceptor complexity on 401s
      const response = await fetch(`${API_AUTH_BASE_URL}/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }
      this.storeTokens(data.access, data.refresh);
      const user = jwtDecode(data.access);
      return { success: true, user };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  async logout(notifyBackend = true) {
    const refreshToken = this.getRefreshToken();
    if (notifyBackend && refreshToken) {
      try {
        await fetch(`${API_AUTH_BASE_URL}/token/blacklist/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh: refreshToken }),
        });
      } catch (error) {
        console.warn("Failed to blacklist token on server.", error);
      }
    }
    this.clearTokens();
  },

  async refreshTokenInternal() {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error("Session expired. Please log in.");
    }

    try {
      const response = await fetch(`${API_AUTH_BASE_URL}/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken }),
      });
      const data = await response.json();
      if (!response.ok) {
        this.logout(false); // Critical: Logout if refresh fails
        throw new Error(data.detail || "Session expired. Please log in again.");
      }
      this.storeTokens(data.access); // Only access token is updated
      return data.access;
    } catch (error) {
      this.logout(false); // Also logout on network errors
      throw error;
    }
  },
};