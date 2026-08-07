import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LogOut, Home, Users, GraduationCap, Briefcase } from 'lucide-react';

const MainLayout: React.FC = () => {
  const { logout, user } = useAuth();

  return (
    <div className="flex h-screen bg-secondary">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-border flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-border">
          <h1 className="text-xl font-bold text-primary">Agency Portal</h1>
        </div>
        
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          <Link to="/dashboard" className="flex items-center px-3 py-2 text-sm font-medium rounded-md bg-accent text-accent-foreground">
            <Home className="mr-3 h-5 w-5" />
            Dashboard
          </Link>
          <Link to="/profile" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:bg-accent hover:text-accent-foreground">
            <Briefcase className="mr-3 h-5 w-5" />
            Agency Profile
          </Link>
          <Link to="/scholarships" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:bg-accent hover:text-accent-foreground">
            <GraduationCap className="mr-3 h-5 w-5" />
            Scholarships
          </Link>
          <Link to="/leads" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:bg-accent hover:text-accent-foreground">
            <Users className="mr-3 h-5 w-5" />
            Leads
          </Link>
        </nav>

        <div className="p-4 border-t border-border">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-foreground truncate px-2">{user?.sub}</span>
            <button 
              onClick={logout}
              className="p-2 text-muted-foreground hover:text-destructive transition-colors rounded-md hover:bg-accent"
              title="Logout"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="h-16 bg-card border-b border-border flex items-center px-8 shadow-sm">
          <h2 className="text-lg font-medium text-foreground">Welcome back, Agency!</h2>
        </div>
        <div className="flex-1 overflow-y-auto bg-background p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default MainLayout;
