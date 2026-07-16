import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  GraduationCap, LayoutDashboard, Search, FileText, 
  Building, User, Settings, LogOut
} from 'lucide-react';

const Sidebar = ({ isOpen, onClose }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/scholarships', label: 'Scholarships', icon: Search },
    { path: '/universities', label: 'Universities', icon: Building },
    { path: '/applications', label: 'My Applications', icon: FileText },
    { path: '/documents', label: 'Documents', icon: FileText },
    { path: '/profile', label: 'My Profile', icon: User },
  ];

  return (
    <div className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="brand" style={{ cursor: 'pointer' }} onClick={() => { navigate('/'); onClose?.(); }}>
        <GraduationCap className="brand-icon" size={28} />
        EduConsultant
      </div>
      <ul className="nav-menu">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <li key={item.path}>
              <NavLink 
                to={item.path} 
                className={({ isActive }) => `nav-link nav-item ${isActive ? 'active' : ''}`}
                style={{ textDecoration: 'none' }}
                onClick={() => onClose?.()}
              >
                <Icon size={20} />
                {item.label}
              </NavLink>
            </li>
          );
        })}
        <li style={{ marginTop: 'auto' }}>
          <NavLink 
            to="/settings" 
            className={({ isActive }) => `nav-link nav-item ${isActive ? 'active' : ''}`}
            style={{ textDecoration: 'none' }}
            onClick={() => onClose?.()}
          >
            <Settings size={20} />
            Settings
          </NavLink>
        </li>
        <li>
          <button onClick={handleLogout} className="nav-item nav-link" style={{ background: 'none', border: 'none', width: '100%', textAlign: 'left', cursor: 'pointer' }}>
            <LogOut size={20} />
            Logout
          </button>
        </li>
      </ul>
    </div>
  );
};

export default Sidebar;
