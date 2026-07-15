import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Bell, Mail, Search, User } from 'lucide-react';

const Topbar = () => {
  const { user } = useAuth();

  return (
    <div className="topbar">
      <div className="search-bar">
        <Search size={18} color="var(--text-gray)" />
        <input type="text" className="search-input" placeholder="Search scholarships, universities..." />
      </div>
      <div className="topbar-actions">
        <button className="icon-btn">
          <Bell size={20} />
          <span className="badge"></span>
        </button>
        <button className="icon-btn">
          <Mail size={20} />
        </button>
        <div className="user-profile">
          {user?.profileImg ? (
            <img src={user.profileImg} alt={user.name} className="avatar" />
          ) : (
            <div className="icon-wrapper" style={{ width: '36px', height: '36px' }}>
              <User size={20} />
            </div>
          )}
          <div className="user-info">
            <span className="user-name">{user?.name || 'Guest User'}</span>
            <span className="user-role">Student</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Topbar;
