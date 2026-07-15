import React from 'react';
import { createBrowserRouter, RouterProvider, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from './components/PublicRoute';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';

const router = createBrowserRouter([
  {
    element: (
      <PublicRoute>
        <Outlet />
      </PublicRoute>
    ),
    children: [
      {
        path: '/login',
        element: <Login />
      },
      {
        path: '/register',
        element: <Register />
      }
    ]
  },
  {
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: '/',
        element: <Dashboard />
      },
      {
        path: '/profile',
        element: <Profile />
      },
      {
        path: '/scholarships',
        element: (
          <div className="dashboard-content">
            <div className="page-header">
              <h1 className="page-title">Scholarships</h1>
              <p className="page-subtitle">Coming soon in Milestone 2.</p>
            </div>
          </div>
        )
      },
      {
        path: '/universities',
        element: (
          <div className="dashboard-content">
            <div className="page-header">
              <h1 className="page-title">Universities</h1>
              <p className="page-subtitle">Coming soon in Milestone 2.</p>
            </div>
          </div>
        )
      },
      {
        path: '/applications',
        element: (
          <div className="dashboard-content">
            <div className="page-header">
              <h1 className="page-title">Applications</h1>
              <p className="page-subtitle">Coming soon in Milestone 3.</p>
            </div>
          </div>
        )
      },
      {
        path: '/settings',
        element: (
          <div className="dashboard-content">
            <div className="page-header">
              <h1 className="page-title">Settings</h1>
              <p className="page-subtitle">Coming soon.</p>
            </div>
          </div>
        )
      }
    ]
  },
  {
    path: '*',
    element: <Navigate to="/" replace />
  }
]);

const App = () => {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  );
};

export default App;

