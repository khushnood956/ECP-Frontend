import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
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

apiClient.interceptors.response.use((response) => {
  return response;
}, async (error) => {
  const originalRequest = error.config;

  if (error.response?.status === 401 && !originalRequest._retry) {
    if (originalRequest.url?.includes('/auth/refresh') || originalRequest.url?.includes('/auth/login')) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise(function(resolve, reject) {
        failedQueue.push({ resolve, reject });
      }).then(token => {
        originalRequest.headers.Authorization = 'Bearer ' + token;
        return apiClient(originalRequest);
      }).catch(err => {
        return Promise.reject(err);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      isRefreshing = false;
      localStorage.removeItem('access_token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    try {
      const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {
        refresh_token: refreshToken
      });

      const { access_token, refresh_token } = refreshResponse.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      originalRequest.headers.Authorization = `Bearer ${access_token}`;

      processQueue(null, access_token);
      isRefreshing = false;
      return apiClient(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      isRefreshing = false;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
      return Promise.reject(refreshError);
    }
  }

  return Promise.reject(error);
});
