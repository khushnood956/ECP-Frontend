import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface RoleGuardProps {
  allowedRoles: string[];
  children: React.ReactNode;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({ allowedRoles, children }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user || !allowedRoles.includes(user.role)) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground p-4">
        <h1 className="text-4xl font-bold text-destructive mb-4">403</h1>
        <h2 className="text-2xl font-semibold mb-2">Unauthorized</h2>
        <p className="text-muted-foreground text-center max-w-md">
          You do not have the required permissions to access this page. Please contact your administrator if you believe this is a mistake.
        </p>
      </div>
    );
  }

  return <>{children}</>;
};
