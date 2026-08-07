import React from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '../components/shared/ProtectedRoute';
import { RoleGuard } from '../components/shared/RoleGuard';

// Layouts
import MainLayout from '../layouts/MainLayout';
import AuthLayout from '../layouts/AuthLayout';

// Pages
import LoginPage from '../features/auth/LoginPage';
import DashboardPage from '../pages/DashboardPage';
import AgencyProfilePage from '../features/agency/AgencyProfilePage';
import CreateAgencyPage from '../features/agency/CreateAgencyPage';
import EditAgencyPage from '../features/agency/EditAgencyPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    path: '/login',
    element: (
      <AuthLayout>
        <LoginPage />
      </AuthLayout>
    ),
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <RoleGuard allowedRoles={['agency']}>
          <MainLayout />
        </RoleGuard>
      </ProtectedRoute>
    ),
    children: [
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'profile',
        element: <AgencyProfilePage />,
      },
      {
        path: 'profile/create',
        element: <CreateAgencyPage />,
      },
      {
        path: 'profile/edit',
        element: <EditAgencyPage />,
      },
      // ... Add more routes here for phases 3, 4, 5
    ],
  },
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
  }
]);

export const AppRoutes: React.FC = () => {
  return <RouterProvider router={router} />;
};
