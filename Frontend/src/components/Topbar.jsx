import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useAppContext } from '../context/AppContext';
import { Bell, Mail, Search, User, Menu } from 'lucide-react';

const Topbar = ({ toggleSidebar }) => {
  const { user } = useAuth();
  const { searchQuery, setSearchQuery, notifications, markNotificationRead } = useAppContext();
  const [showNotifications, setShowNotifications] = useState(false);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="topbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button className="icon-btn mobile-menu-btn" onClick={toggleSidebar}>
          <Menu size={24} />
        </button>
        <div className="search-bar">
          <Search size={18} color="var(--text-gray)" />
          <input 
            type="text" 
            className="search-input" 
            placeholder="Search..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>
      <div className="topbar-actions">
        <div style={{ position: 'relative' }}>
          <button className="icon-btn" onClick={() => setShowNotifications(!showNotifications)}>
            <Bell size={20} />
            {unreadCount > 0 && <span className="badge"></span>}
          </button>
          
          {showNotifications && (
            <div className="dropdown-menu notifications-dropdown">
              <h4 style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border-color)', margin: 0 }}>Notifications</h4>
              <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {notifications.map(n => (
                  <div key={n.id} style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border-color)', background: n.read ? 'transparent' : 'var(--bg-gray)' }}>
                    <h5 style={{ fontSize: '0.875rem', margin: '0 0 0.25rem' }}>{n.title}</h5>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', margin: '0 0 0.25rem' }}>{n.message}</p>
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-gray)' }}>{n.time}</span>
                    {!n.read && (
                      <button onClick={() => markNotificationRead(n.id)} style={{ background: 'none', border: 'none', color: 'var(--primary-green)', fontSize: '0.75rem', display: 'block', marginTop: '0.25rem', cursor: 'pointer' }}>Mark as read</button>
                    )}
                  </div>
                ))}
                {notifications.length === 0 && <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-gray)' }}>No notifications.</div>}
              </div>
            </div>
          )}
        </div>
        <button className="icon-btn hide-mobile">
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
          <div className="user-info hide-mobile">
            <span className="user-name">{user?.name || 'Guest User'}</span>
            <span className="user-role">Student</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Topbar;
