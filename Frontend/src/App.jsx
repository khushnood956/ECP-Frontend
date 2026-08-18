import React from 'react';
import { createBrowserRouter, RouterProvider, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
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

// Agency Portal Pages
import AgencyDashboard from './pages/agency/AgencyDashboard';
import AgencyProfilePage from './pages/agency/AgencyProfilePage';
import CreateAgencyPage from './pages/agency/CreateAgencyPage';
import EditAgencyPage from './pages/agency/EditAgencyPage';
import LeadsPage from './pages/agency/LeadsPage';
import LeadDetailsPage from './pages/agency/LeadDetailsPage';
import ScholarshipsListPage from './pages/agency/ScholarshipsListPage';
import ScholarshipDetailsPage from './pages/agency/ScholarshipDetailsPage';
import CreateScholarshipPage from './pages/agency/CreateScholarshipPage';
import EditScholarshipPage from './pages/agency/EditScholarshipPage';
import AdminDashboard from './pages/admin/AdminDashboard';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RoleGuard } from './components/shared/RoleGuard';

const queryClient = new QueryClient();

const RootDashboard = () => {
  const { user } = useAuth();
  const role = user?.role?.toLowerCase();
  if (role === 'agency') {
    return <Navigate to="/agency/dashboard" replace />;
  }
  if (role === 'admin') {
    return <Navigate to="/admin/dashboard" replace />;
  }
  return <Dashboard />;
};

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
        element: <RootDashboard />
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
      },
      // Agency Portal Routes protected by RoleGuard
      {
        path: '/agency/dashboard',
        element: (
          <RoleGuard allowedRoles={['agency']}>
            <AgencyDashboard />
          </RoleGuard>
        )
      },
      {
        path: '/agency/profile',
        element: (
          <RoleGuard allowedRoles={['agency']}>
            <AgencyProfilePage />
          </RoleGuard>
        )
      },
      {
        path: '/agency/profile/create',
        element: (
          <RoleGuard allowedRoles={['agency']}>
            <CreateAgencyPage />
          </RoleGuard>
        )
      },
      {
        path: '/agency/profile/edit',
        element: (
          <RoleGuard allowedRoles={['agency']}>
            <EditAgencyPage />
          </RoleGuard>
        )
      },
      {
        path: '/agency/leads',
        element: (
          <RoleGuard allowedRoles={['agency']}>
            <LeadsPage />
          </RoleGuard>
        )
      },
      {
        path: '/agency/leads/:id',
        element: (
          <RoleGuard allowedRoles={['agency']}>
            <LeadDetailsPage />
          </RoleGuard>
        )
      },
      {
        path: '/agency/scholarships',
        element: (
          <RoleGuard allowedRoles={['agency']}>
            <ScholarshipsListPage />
          </RoleGuard>
        )
      },
      {
        path: '/agency/scholarships/new',
        element: (
          <RoleGuard allowedRoles={['agency']}>
            <CreateScholarshipPage />
          </RoleGuard>
        )
      },
      {
        path: '/agency/scholarships/:id',
        element: (
          <RoleGuard allowedRoles={['agency']}>
            <ScholarshipDetailsPage />
          </RoleGuard>
        )
      },
      {
        path: '/agency/scholarships/:id/edit',
        element: (
          <RoleGuard allowedRoles={['agency']}>
            <EditScholarshipPage />
          </RoleGuard>
        )
      },
      {
        path: '/admin/dashboard',
        element: (
          <RoleGuard allowedRoles={['admin']}>
            <AdminDashboard />
          </RoleGuard>
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
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppProvider>
          <RouterProvider router={router} />
        </AppProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;

