import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const Settings = () => {
  const { user, updateProfile } = useAuth();
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    notificationsEmail: true,
    notificationsSMS: false
  });
  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await updateProfile({ name: formData.name, email: formData.email });
      setMessage('Settings updated successfully.');
    } catch (err) {
      setMessage('Error updating settings: ' + err.message);
    }
  };

  return (
    <div className="dashboard-content">
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Manage your account preferences.</p>
      </div>
      
      <div className="widgets-grid" style={{ gridTemplateColumns: '1fr' }}>
        <div className="widget" style={{ maxWidth: '600px' }}>
          <div className="widget-header">
            <h3 className="widget-title">Account Settings</h3>
          </div>
          
          {message && <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`}>{message}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input type="text" className="form-input" name="name" value={formData.name} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input type="email" className="form-input" name="email" value={formData.email} onChange={handleChange} />
            </div>
            
            <h4 style={{ margin: '1.5rem 0 1rem', fontSize: '1rem', fontWeight: 600 }}>Notifications</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
                <input type="checkbox" name="notificationsEmail" checked={formData.notificationsEmail} onChange={handleChange} />
                Email Notifications
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
                <input type="checkbox" name="notificationsSMS" checked={formData.notificationsSMS} onChange={handleChange} />
                SMS Notifications
              </label>
            </div>

            <button type="submit" className="btn btn-primary">Save Changes</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Settings;
