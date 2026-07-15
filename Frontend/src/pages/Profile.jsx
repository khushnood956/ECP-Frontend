import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useBlocker } from 'react-router-dom';
import { User, Mail, GraduationCap, Award, ShieldAlert, Check } from 'lucide-react';

const Profile = () => {
  const { user, updateProfile } = useAuth();

  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    degreePreference: user?.degreePreference || '',
    ieltsScore: user?.ieltsScore || '',
    profileImg: user?.profileImg || ''
  });

  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState({ text: '', type: '' });
  const [isSaving, setIsSaving] = useState(false);

  const isDirty = 
    formData.name !== (user?.name || '') ||
    formData.email !== (user?.email || '') ||
    formData.degreePreference !== (user?.degreePreference || '') ||
    formData.ieltsScore !== (user?.ieltsScore || '') ||
    formData.profileImg !== (user?.profileImg || '');

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        email: user.email || '',
        degreePreference: user.degreePreference || '',
        ieltsScore: user.ieltsScore || '',
        profileImg: user.profileImg || ''
      });
    }
  }, [user]);

  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
        return '';
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isDirty]);

  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) => {
      return isDirty && currentLocation.pathname !== nextLocation.pathname;
    }
  );

  useEffect(() => {
    if (blocker.state === 'blocked') {
      const confirmProceed = window.confirm('You have unsaved changes. Are you sure you want to leave?');
      if (confirmProceed) {
        blocker.proceed();
      } else {
        blocker.reset();
      }
    }
  }, [blocker, isDirty]);

  const handleCancel = () => {
    if (user) {
      setFormData({
        name: user.name || '',
        email: user.email || '',
        degreePreference: user.degreePreference || '',
        ieltsScore: user.ieltsScore || '',
        profileImg: user.profileImg || ''
      });
    }
    setErrors({});
    setMessage({ text: '', type: '' });
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.name.trim()) {
      newErrors.name = 'Full name is required';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.ieltsScore || formData.ieltsScore.toString().trim() === '') {
      newErrors.ieltsScore = 'IELTS Score is required';
    } else {
      const score = parseFloat(formData.ieltsScore);
      if (isNaN(score)) {
        newErrors.ieltsScore = 'IELTS Score must be a valid number';
      } else if (score > 9.0) {
        newErrors.ieltsScore = 'IELTS Score must be less than or equal to 9.0';
      } else if (score < 0) {
        newErrors.ieltsScore = 'IELTS Score must be greater than or equal to 0';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
    if (message.text) {
      setMessage({ text: '', type: '' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSaving(true);
    const result = await updateProfile(formData);
    setIsSaving(false);

    if (result.success) {
      setMessage({ text: 'Profile updated successfully!', type: 'success' });
    } else {
      setMessage({ text: result.error || 'Failed to update profile.', type: 'error' });
    }
  };

  return (
    <div className="dashboard-content">
      <div className="page-header">
        <h1 className="page-title">My Profile</h1>
        <p className="page-subtitle">Update your personal details and academic preferences.</p>
      </div>

      {message.text && (
        <div className={`alert ${message.type === 'success' ? 'alert-success success-message toast-success' : 'alert-error'}`} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
          {message.type === 'success' ? <Check size={18} /> : <ShieldAlert size={18} />}
          <span>{message.text}</span>
        </div>
      )}

      <div className="profile-layout" style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        {/* Left Column: Avatar Preview */}
        <div className="widget" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '2rem', height: 'fit-content' }}>
          <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
            {formData.profileImg ? (
              <img 
                src={formData.profileImg} 
                alt="Profile Preview" 
                style={{ width: '120px', height: '120px', borderRadius: '50%', objectFit: 'cover', border: '3px solid var(--primary-green-light)' }} 
                onError={(e) => {
                  e.target.src = 'https://api.dicebear.com/7.x/adventurer/svg?seed=placeholder';
                }}
              />
            ) : (
              <div style={{ width: '120px', height: '120px', borderRadius: '50%', backgroundColor: 'var(--primary-green-light)', display: 'flex', justifyContent: 'center', alignItems: 'center', color: 'var(--primary-green)' }}>
                <User size={60} />
              </div>
            )}
          </div>
          
          <h3 className="widget-title" style={{ marginBottom: '0.25rem' }}>{formData.name || 'Your Name'}</h3>
          <span style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '1.5rem' }}>{formData.email || 'your.email@example.com'}</span>
          
          <div className="form-group" style={{ width: '100%' }}>
            <label className="form-label">Avatar URL</label>
            <input 
              type="text" 
              name="profileImg" 
              value={formData.profileImg} 
              onChange={handleChange}
              placeholder="https://api.dicebear.com/... or any URL"
              className="form-input"
              disabled={isSaving}
              style={{ fontSize: '0.8rem' }}
            />
            <span style={{ fontSize: '0.7rem', color: 'var(--text-gray)', marginTop: '0.25rem', display: 'block' }}>
              We recommend using a Dicebear adventurer seed (e.g., https://api.dicebear.com/7.x/adventurer/svg?seed=YourName).
            </span>
          </div>
        </div>

        {/* Right Column: Profile Edit Form */}
        <div className="widget" style={{ padding: '2rem' }}>
          <h3 className="widget-title" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
            Account Settings & Academic Profile
          </h3>

          <form onSubmit={handleSubmit} className="auth-form" style={{ maxWidth: '100%' }}>
            <div className="form-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
              <div className="form-group">
                <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <User size={16} /> Full Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className={`form-input ${errors.name ? 'input-error' : ''}`}
                  disabled={isSaving}
                />
                {errors.name && <span className="field-error error-message">{errors.name}</span>}
              </div>

              <div className="form-group">
                <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Mail size={16} /> Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={`form-input ${errors.email ? 'input-error' : ''}`}
                  disabled={isSaving}
                />
                {errors.email && <span className="field-error error-message">{errors.email}</span>}
              </div>
            </div>

            <div className="form-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
              <div className="form-group">
                <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <GraduationCap size={16} /> Degree Preference
                </label>
                <select
                  name="degreePreference"
                  value={formData.degreePreference}
                  onChange={handleChange}
                  className="form-input"
                  disabled={isSaving}
                >
                  <option value="Bachelor of Computer Science">Bachelor of CS</option>
                  <option value="Master of Computer Science">Master of CS</option>
                  <option value="Master of Data Science">Master of Data Science</option>
                  <option value="MBA">MBA</option>
                  <option value="PhD in Engineering">PhD in Engineering</option>
                  <option value="Masters">Masters</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Award size={16} /> IELTS Band Score
                </label>
                <input
                  type="text"
                  name="ieltsScore"
                  value={formData.ieltsScore}
                  onChange={handleChange}
                  className={`form-input ${errors.ieltsScore ? 'input-error' : ''}`}
                  disabled={isSaving}
                />
                {errors.ieltsScore && <span className="field-error error-message">{errors.ieltsScore}</span>}
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
              <button 
                type="button" 
                onClick={handleCancel} 
                className="btn" 
                disabled={isSaving} 
                style={{ backgroundColor: '#f1f5f9', color: '#475569' }}
              >
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={isSaving} style={{ minWidth: '150px' }}>
                {isSaving ? 'Saving Changes...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile;
