/* eslint-disable react/only-export-components */
import React, { createContext, useState, useContext, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import { AuthAPI } from '../services/api/auth.api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const decoded = jwtDecode(token);
          setUser({
            sub: decoded.sub,
            role: decoded.role
          });
        } catch (error) {
          console.error('Failed to restore session:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const data = await AuthAPI.login(params);
      
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      
      const decoded = jwtDecode(data.access_token);
      const userProfile = {
        sub: decoded.sub,
        role: decoded.role
      };
      
      setUser(userProfile);
      return { success: true, role: decoded.role };
    } catch (error) {
      setUser(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Login failed. Please check your credentials.' 
      };
    }
  };

  const register = async (userData) => {
    try {
      // Backend /register endpoint takes JSON payload UserCreate: email, password, role
      const payload = {
        email: userData.email,
        password: userData.password,
        role: userData.role || 'student'
      };
      
      const { apiClient } = await import('../services/api/apiClient');
      await apiClient.post('/auth/register', payload);
      
      // Auto login after registration
      return await login(userData.email, userData.password);
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Registration failed.' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    register,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
