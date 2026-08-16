import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'var(--primary-green)' }}>
        Loading...
      </div>
    );
  }

  if (isAuthenticated) {
    const role = user?.role?.toLowerCase();
    if (role === 'agency') {
      return <Navigate to="/agency/dashboard" replace />;
    } else if (role === 'admin') {
      return <Navigate to="/admin/dashboard" replace />;
    }
    return <Navigate to="/" replace />;
  }

  return children;
};

export default PublicRoute;
