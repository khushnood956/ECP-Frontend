import React from 'react';
import { createBrowserRouter, RouterProvider, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AppProvider } from './context/AppContext';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from './components/PublicRoute';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import Scholarships from './pages/Scholarships';
import Universities from './pages/Universities';
import Applications from './pages/Applications';
import Documents from './pages/Documents';
import Settings from './pages/Settings';
import ScholarshipDetail from './pages/ScholarshipDetail';
import UniversityDetail from './pages/UniversityDetail';
import ApplicationDetail from './pages/ApplicationDetail';

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
        element: <Scholarships />
      },
      {
        path: '/scholarships/:id',
        element: <ScholarshipDetail />
      },
      {
        path: '/universities',
        element: <Universities />
      },
      {
        path: '/universities/:id',
        element: <UniversityDetail />
      },
      {
        path: '/applications',
        element: <Applications />
      },
      {
        path: '/applications/:id',
        element: <ApplicationDetail />
      },
      {
        path: '/documents',
        element: <Documents />
      },
      {
        path: '/settings',
        element: <Settings />
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
      <AppProvider>
        <RouterProvider router={router} />
      </AppProvider>
    </AuthProvider>
  );
};

export default App;

