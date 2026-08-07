import React from 'react';
import { Outlet } from 'react-router-dom';

const AuthLayout: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-secondary">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-foreground">
          Agency Portal
        </h2>
        <p className="mt-2 text-center text-sm text-muted-foreground">
          Sign in to your account
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-card py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-border">
          {children || <Outlet />}
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
