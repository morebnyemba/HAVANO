// Filename: src/context/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import apiClient from '../lib/api'; // Import the configured client

// const AUTH_API_URL = `${API_BASE_URL}/crm-api/auth`; // No longer needed

const ACCESS_TOKEN_KEY = 'accessToken';
const REFRESH_TOKEN_KEY = 'refreshToken';
const USER_DATA_KEY = 'user';

const AuthContext = createContext(null);

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [authState, setAuthState] = useState(() => {
    const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    let user = null;
    try {
        user = JSON.parse(localStorage.getItem(USER_DATA_KEY));
    } catch {
        console.warn("Could not parse user data from localStorage");
    }
    return {
      accessToken: accessToken || null,
      refreshToken: refreshToken || null,
      isAuthenticated: !!accessToken,
      user: user || null,
      isLoading: true, // Start with loading true until we check token
    };
  });

  const setAuthData = useCallback((data) => {
    const newAccessToken = data?.access || null;
    const newRefreshToken = data?.refresh || null;
    // Preserve existing user data if new data doesn't explicitly provide it
    const newUser = data?.user !== undefined ? data.user : authState.user;

    setAuthState({
      accessToken: newAccessToken,
      refreshToken: newRefreshToken,
      isAuthenticated: !!newAccessToken,
      user: newUser,
      isLoading: false,
    });

    if (newAccessToken) localStorage.setItem(ACCESS_TOKEN_KEY, newAccessToken);
    else localStorage.removeItem(ACCESS_TOKEN_KEY);

    if (newRefreshToken) localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);
    else localStorage.removeItem(REFRESH_TOKEN_KEY);
    
    if (newUser) localStorage.setItem(USER_DATA_KEY, JSON.stringify(newUser));
    else localStorage.removeItem(USER_DATA_KEY);
  }, [authState.user]); // Include authState.user to correctly use its value in closure

  const logoutUser = useCallback(async (informBackend = true) => {
    const currentRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    
    // Clear local state and storage immediately
    setAuthData({ access: null, refresh: null, user: null });

    if (informBackend && currentRefreshToken) {
      try {
        // Use the configured apiClient to blacklist the token
        await apiClient.post('/crm-api/auth/token/blacklist/', {
          refresh: currentRefreshToken,
        });
        toast.info("You have been logged out.");
      } catch (error) {
        // The interceptor in apiClient will handle general error toasts.
        // We might not need specific handling here unless it's a special case.
        console.warn("Failed to blacklist token on server:", error.response?.data || error.message);
      }
    }
    // Navigation will be handled by ProtectedRoute or the calling component.
  }, [setAuthData]);

  // This effect runs once on mount to set the initial auth state.
  useEffect(() => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (token) {
      // Here you could add a check to /token/verify/ if you want to be sure.
      // For now, we'll trust the token if it exists. The interceptor will refresh it if it's expired.
      setAuthState(prev => ({ ...prev, isLoading: false }));
    } else {
      setAuthState(prev => ({ ...prev, isLoading: false }));
    }
  }, []); // Run only once

  const loginUser = async (username, password) => {
    setAuthState(prev => ({ ...prev, isLoading: true }));
    try {
      // The apiClient will throw on non-2xx responses, and the interceptor will toast.
      const response = await apiClient.post('/crm-api/auth/token/', { username, password });
      const userData = response.data.user || { username }; // Adjust based on actual response
      setAuthData({ ...response.data, user: userData });
      toast.success("Login successful!");
      return { success: true, user: userData }; // Return success for LoginPage to handle navigation
    } catch (error) {
      // The interceptor already showed a toast. We just need to handle UI state.
      setAuthState(prev => ({ ...prev, isAuthenticated: false, user: null, isLoading: false }));
      return { success: false, error: error.message };
    }
  };

  const value = {
    accessToken: authState.accessToken,
    user: authState.user,
    isAuthenticated: authState.isAuthenticated,
    isLoadingAuth: authState.isLoading, // Use this in ProtectedRoute
    login: loginUser,
    logout: logoutUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};