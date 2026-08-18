/* eslint-disable react/only-export-components */
import React, { createContext, useState, useContext, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import { AuthAPI } from '../services/api/auth.api';
import { apiClient } from '../services/api/apiClient';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const DEGREE_UI_TO_BACKEND = {
    'Bachelor of Computer Science': 'bachelor',
    'Master of Computer Science': 'master',
    'Master of Data Science': 'master',
    'MBA': 'master',
    'PhD in Engineering': 'phd',
    'Masters': 'master'
  };

  const DEGREE_BACKEND_TO_UI = {
    'bachelor': 'Bachelor of Computer Science',
    'master': 'Master of Computer Science',
    'phd': 'PhD in Engineering',
    'high_school': 'Bachelor of Computer Science',
    'postdoc': 'PhD in Engineering',
    'other': 'Bachelor of Computer Science'
  };

  const loadProfileDetails = async (role) => {
    if (role === 'student') {
      try {
        const res = await apiClient.get('/student-profiles');
        const profiles = res.data.data;
        if (profiles && profiles.length > 0) {
          const p = profiles[0];
          const name = `${p.first_name || ''} ${p.last_name || ''}`.trim() || 'Student';
          const degreePref = DEGREE_BACKEND_TO_UI[p.preferred_degree] || 'Bachelor of Computer Science';
          
          return {
            profileId: p.id,
            name,
            firstName: p.first_name,
            lastName: p.last_name,
            degreePreference: degreePref,
            ieltsScore: p.cgpa_or_percentage ? p.cgpa_or_percentage.toString() : '7.0',
            profileImg: p.profile_picture_url || ''
          };
        }
      } catch (err) {
        console.error('Failed to load profile details:', err);
      }
    } else if (role === 'agency') {
      try {
        const res = await apiClient.get('/agencies/me');
        const agency = res.data.data;
        return {
          profileId: agency.id,
          name: agency.name || 'Agency',
          profileImg: agency.logo_url || ''
        };
      } catch (err) {
        console.error('Failed to load agency profile details:', err);
      }
    }
    return {};
  };

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const decoded = jwtDecode(token);
        const currentTime = Date.now() / 1000;
        
        if (decoded.exp > currentTime) {
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          const profile = await loadProfileDetails(decoded.role);
          setUser({
            sub: decoded.sub,
            role: decoded.role,
            ...profile
          });
          setLoading(false);
        } else if (refreshToken) {
          try {
            const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
            const { default: axios } = await import('axios');
            const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
              refresh_token: refreshToken
            });
            const { access_token, refresh_token } = response.data;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            
            apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
            const newDecoded = jwtDecode(access_token);
            const profile = await loadProfileDetails(newDecoded.role);
            setUser({
              sub: newDecoded.sub,
              role: newDecoded.role,
              ...profile
            });
          } catch (refreshErr) {
            console.error('Failed to refresh token on startup:', refreshErr);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setUser(null);
          }
          setLoading(false);
        } else {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          setUser(null);
          setLoading(false);
        }
      } catch (error) {
        console.error('Failed to restore session:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
        setLoading(false);
      }
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
      
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      const decoded = jwtDecode(data.access_token);
      const profile = await loadProfileDetails(decoded.role);
      const userProfile = {
        sub: decoded.sub,
        role: decoded.role,
        ...profile
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
      const nameParts = (userData.name || '').trim().split(/\s+/);
      const firstName = nameParts[0] || 'New';
      const lastName = nameParts.slice(1).join(' ') || 'Student';

      const payload = {
        email: userData.email,
        password: userData.password,
        role: userData.role || 'student',
        first_name: firstName,
        last_name: lastName
      };
      
      await apiClient.post('/auth/register', payload);
      return await login(userData.email, userData.password);
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Registration failed.' 
      };
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const isStudent = user.role === 'student';
      
      if (isStudent) {
        const nameToUse = profileData.name !== undefined ? profileData.name : user.name;
        const nameParts = (nameToUse || '').trim().split(/\s+/);
        const firstName = nameParts[0] || 'Student';
        const lastName = nameParts.slice(1).join(' ') || 'User';

        const degreePrefToUse = profileData.degreePreference !== undefined ? profileData.degreePreference : user.degreePreference;
        const preferredDegree = DEGREE_UI_TO_BACKEND[degreePrefToUse] || 'bachelor';

        const ieltsScoreToUse = profileData.ieltsScore !== undefined ? profileData.ieltsScore : user.ieltsScore;
        const profileImgToUse = profileData.profileImg !== undefined ? profileData.profileImg : user.profileImg;

        const payload = {
          first_name: firstName,
          last_name: lastName,
          preferred_degree: preferredDegree,
          cgpa_or_percentage: parseFloat(ieltsScoreToUse) || 7.0,
          profile_picture_url: profileImgToUse || ''
        };

        if (user.profileId) {
          await apiClient.patch(`/student-profiles/${user.profileId}`, payload);
        } else {
          const res = await apiClient.post('/student-profiles', payload);
          setUser(prev => ({ ...prev, profileId: res.data.data.id }));
        }

        const emailToUse = profileData.email !== undefined ? profileData.email : (user.sub || user.email);

        setUser(prev => ({
          ...prev,
          name: nameToUse,
          sub: emailToUse,
          firstName,
          lastName,
          degreePreference: degreePrefToUse,
          ieltsScore: ieltsScoreToUse,
          profileImg: profileImgToUse
        }));
      }

      return { success: true };
    } catch (error) {
      console.error('Failed to update profile:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Failed to update profile.'
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
    updateProfile,
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
