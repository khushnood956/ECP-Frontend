/* eslint-disable react/only-export-components */
import React, { createContext, useState, useContext, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('educonsultant_token');
      if (token) {
        try {
          const profile = await api.getCurrentUser(token);
          if (profile) {
            setUser(profile);
          } else {
            localStorage.removeItem('educonsultant_token');
          }
        } catch (error) {
          console.error('Failed to restore session:', error);
          localStorage.removeItem('educonsultant_token');
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const data = await api.login(email, password);
      setUser(data.user);
      localStorage.setItem('educonsultant_token', data.token);
      return { success: true };
    } catch (error) {
      setUser(null);
      localStorage.removeItem('educonsultant_token');
      return { success: false, error: error.message };
    }
  };

  const register = async (userData) => {
    try {
      const data = await api.register(userData);
      setUser(data.user);
      localStorage.setItem('educonsultant_token', data.token);
      return { success: true };
    } catch (error) {
      setUser(null);
      localStorage.removeItem('educonsultant_token');
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('educonsultant_token');
  };

  const updateProfile = async (newData) => {
    const token = localStorage.getItem('educonsultant_token');
    if (!token) return { success: false, error: 'No active session' };
    
    try {
      const data = await api.updateProfile(token, newData);
      setUser(data.user);
      localStorage.setItem('educonsultant_token', data.token);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    register,
    logout,
    updateProfile
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
