# Handoff Report — Milestone 1: Authentication & Profile UI

## 1. Observation
After a thorough analysis of the repository, the following items were observed:
- **Repository Structure**:
  - The project is a React 19 + Vite application.
  - The `package.json` specifies `"react": "^19.2.7"`, `"react-dom": "^19.2.7"`, and `"react-router-dom": "^7.18.1"`.
  - The lint script uses `oxlint`: `"lint": "oxlint"` (line 9).
- **Existing Authentication State**:
  - There are no folders/files in `src/context/`, `src/components/`, or `src/pages/` at present.
  - `src/App.jsx` currently contains inline static components for `Sidebar`, `Topbar`, `Dashboard`, and `App` (with a single route `/` for `<Dashboard />` wrapped in `<Router>`).
  - `Topbar` has hardcoded user details:
    ```jsx
    68:           <span className="user-name">Alex Johnson</span>
    69:           <span className="user-role">Student</span>
    ```
  - `src/index.css` contains baseline styling rules for the layout and widgets but lacks styling for forms, login cards, alerts, and inputs.

---

## 2. Logic Chain
To implement Milestone 1 according to the design criteria in `PROJECT.md` and `SCOPE.md`, the following steps must be followed:
1. **Mock Service (`src/services/api.js`)**:
   - Needs to simulate a real REST API backend using asynchronous delays and `localStorage` to store user data.
   - Provides methods: `login`, `register`, `updateProfile`, `getCurrentUser`.
2. **State Management (`src/context/AuthContext.jsx`)**:
   - `AuthContext` must keep track of `user`, `isAuthenticated`, and `loading` states.
   - `loading` state is crucial to prevent redirect flashing when the page refreshes and checks `localStorage` for a session token.
3. **Route Guards (`src/components/ProtectedRoute.jsx` and `src/components/PublicRoute.jsx`)**:
   - `ProtectedRoute` will prevent unauthenticated access, redirecting users to `/login`.
   - `PublicRoute` will prevent authenticated users from viewing login/register forms, redirecting them to the dashboard `/`.
4. **Layout Separation**:
   - Extraction of `Sidebar` and `Topbar` from `src/App.jsx` into separate components allows clean composition.
   - A wrapper component `Layout.jsx` will house the dashboard page container and `<Outlet />`, binding `Sidebar` and `Topbar` to it.
5. **UI Pages**:
   - `Login.jsx` & `Register.jsx`: Include standard state management, form inputs matching scope parameters, field-level validations, and error alert views.
   - `Profile.jsx`: Allows view and modification of academic info (Degree Preference, IELTS Band Score, Name, and Email) and profile image preview using a URL text input (perfect for mockups like Dicebear avatar URLs).
   - `Dashboard.jsx`: Extracted from `App.jsx` cleanly.

---

## 3. Caveats
- **Mock State Persistence**: The database is simulated via `localStorage` (key `educonsultant_users`). While this persists credentials across sessions, deleting browser cache will reset it to the default seeded user (`alex@example.com` / `password123`).
- **No Real Token Decryption**: Mock tokens are simple base64-encoded strings of user emails (`mock-jwt-token-YmxhaEBlbWFpbC5jb20=`). In production, this must be swapped for real JWT handling.
- **Routing Module**: Uses client-side memory routing and path matching via `react-router-dom` v7. The entrypoint `src/main.jsx` wraps `<App />` in `<StrictMode>`, so rendering checks will execute twice during local development.

---

## 4. Conclusion & Implementation Plan
Below is the precise, file-by-file specification of the files to create and edit.

### A. New File: `src/services/api.js`
This file simulates API response latency and manages the local storage mock database.

```javascript
const USERS_KEY = 'educonsultant_users';
const CURRENT_USER_KEY = 'educonsultant_current_user';
const TOKEN_KEY = 'educonsultant_token';

// Helper for realistic network delay
const delay = (ms = 600) => new Promise(resolve => setTimeout(resolve, ms));

const getStoredUsers = () => {
  const users = localStorage.getItem(USERS_KEY);
  if (!users) {
    // Seed default user
    const defaultUsers = [
      {
        name: 'Alex Johnson',
        email: 'alex@example.com',
        password: 'password123',
        profileImg: 'https://api.dicebear.com/7.x/adventurer/svg?seed=Alex',
        degreePreference: 'Master of Computer Science',
        ieltsScore: '7.5'
      }
    ];
    localStorage.setItem(USERS_KEY, JSON.stringify(defaultUsers));
    return defaultUsers;
  }
  return JSON.parse(users);
};

export const api = {
  login: async (email, password) => {
    await delay();
    const users = getStoredUsers();
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());
    
    if (!user) {
      throw new Error('User not found. Please register first.');
    }
    if (user.password !== password) {
      throw new Error('Invalid credentials. Please try again.');
    }
    
    // Success - omit password from returned user details
    const { password: _, ...userProfile } = user;
    const token = `mock-jwt-token-${btoa(email)}`;
    
    return { user: userProfile, token };
  },

  register: async (userData) => {
    await delay();
    const users = getStoredUsers();
    
    if (users.some(u => u.email.toLowerCase() === userData.email.toLowerCase())) {
      throw new Error('An account with this email already exists.');
    }

    const newUser = {
      name: userData.name,
      email: userData.email,
      password: userData.password,
      profileImg: userData.profileImg || `https://api.dicebear.com/7.x/adventurer/svg?seed=${encodeURIComponent(userData.name)}`,
      degreePreference: userData.degreePreference || 'Master of Science',
      ieltsScore: userData.ieltsScore || '7.0'
    };

    users.push(newUser);
    localStorage.setItem(USERS_KEY, JSON.stringify(users));

    const { password: _, ...userProfile } = newUser;
    const token = `mock-jwt-token-${btoa(newUser.email)}`;

    return { user: userProfile, token };
  },

  updateProfile: async (token, profileData) => {
    await delay();
    if (!token) throw new Error('Unauthorized');
    
    // Decode email from mock token
    const emailBase64 = token.replace('mock-jwt-token-', '');
    let email;
    try {
      email = atob(emailBase64);
    } catch (e) {
      throw new Error('Invalid session token');
    }

    const users = getStoredUsers();
    const userIndex = users.findIndex(u => u.email.toLowerCase() === email.toLowerCase());

    if (userIndex === -1) {
      throw new Error('User not found.');
    }

    const originalEmail = users[userIndex].email;
    const newEmail = profileData.email || originalEmail;

    if (newEmail.toLowerCase() !== originalEmail.toLowerCase()) {
      if (users.some((u, idx) => idx !== userIndex && u.email.toLowerCase() === newEmail.toLowerCase())) {
        throw new Error('The email address is already in use by another user.');
      }
    }

    users[userIndex] = {
      ...users[userIndex],
      name: profileData.name || users[userIndex].name,
      email: newEmail,
      degreePreference: profileData.degreePreference || users[userIndex].degreePreference,
      ieltsScore: profileData.ieltsScore || users[userIndex].ieltsScore,
      profileImg: profileData.profileImg || users[userIndex].profileImg
    };

    localStorage.setItem(USERS_KEY, JSON.stringify(users));

    // If email updated, generate a new token
    const newToken = newEmail.toLowerCase() !== originalEmail.toLowerCase() 
      ? `mock-jwt-token-${btoa(newEmail)}` 
      : token;

    const { password: _, ...userProfile } = users[userIndex];
    return { user: userProfile, token: newToken };
  },

  getCurrentUser: async (token) => {
    await delay(200); // Shorter delay for initial session check
    if (!token) return null;

    const emailBase64 = token.replace('mock-jwt-token-', '');
    let email;
    try {
      email = atob(emailBase64);
    } catch (e) {
      return null;
    }

    const users = getStoredUsers();
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());
    if (!user) return null;

    const { password: _, ...userProfile } = user;
    return userProfile;
  }
};
```

### B. New File: `src/context/AuthContext.jsx`
Provides authentication context, credentials methods, and states to the rest of the application.

```jsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('educonsultant_token');
      if (token) {
        try {
          const profile = await api.getCurrentUser(token);
          if (profile) {
            setUser(profile);
          } else {
            localStorage.removeItem('educonsultant_token');
          }
        } catch (error) {
          console.error('Failed to restore session:', error);
          localStorage.removeItem('educonsultant_token');
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const data = await api.login(email, password);
      setUser(data.user);
      localStorage.setItem('educonsultant_token', data.token);
      return { success: true };
    } catch (error) {
      setUser(null);
      localStorage.removeItem('educonsultant_token');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    try {
      const data = await api.register(userData);
      setUser(data.user);
      localStorage.setItem('educonsultant_token', data.token);
      return { success: true };
    } catch (error) {
      setUser(null);
      localStorage.removeItem('educonsultant_token');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('educonsultant_token');
  };

  const updateProfile = async (newData) => {
    const token = localStorage.getItem('educonsultant_token');
    if (!token) return { success: false, error: 'No active session' };
    
    setLoading(true);
    try {
      const data = await api.updateProfile(token, newData);
      setUser(data.user);
      localStorage.setItem('educonsultant_token', data.token);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    register,
    logout,
    updateProfile
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### C. New File: `src/components/ProtectedRoute.jsx`
Intercepts unauthenticated access to secure routes and redirects to `/login`.

```jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'var(--primary-green)' }}>
        Loading session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

### D. New File: `src/components/PublicRoute.jsx`
Redirects authenticated users away from public auth pages (like `/login`, `/register`) to the dashboard root `/`.

```jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'var(--primary-green)' }}>
        Loading...
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default PublicRoute;
```

### E. New File: `src/components/Sidebar.jsx`
Extracted sidebar navigation layout with context integration.

```jsx
import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  GraduationCap, LayoutDashboard, Search, FileText, 
  Building, User, Settings, LogOut
} from 'lucide-react';

const Sidebar = () => {
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
    { path: '/profile', label: 'My Profile', icon: User },
  ];

  return (
    <div className="sidebar">
      <div className="brand" style={{ cursor: 'pointer' }} onClick={() => navigate('/')}>
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
```

### F. New File: `src/components/Topbar.jsx`
Extracted top action bar with stateful user info display.

```jsx
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
```

### G. New File: `src/components/Layout.jsx`
Encapsulates protected pages inside sidebar/topbar framing.

```jsx
import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

const Layout = () => {
  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="main-content">
        <Topbar />
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;
```

### H. New File: `src/pages/Dashboard.jsx`
Extracted from `src/App.jsx` completely.

```jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { 
  User, Search, FileText, CheckCircle, Clock, TrendingUp
} from 'lucide-react';

const Dashboard = () => (
  <div className="dashboard-content">
    <div className="page-header">
      <h1 className="page-title">Student Dashboard</h1>
      <p className="page-subtitle">Track your applications and explore opportunities.</p>
    </div>

    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-header">
          Profile Completion
          <div className="icon-wrapper"><User size={18} /></div>
        </div>
        <div className="stat-value">85%</div>
        <div className="stat-trend positive">
          <TrendingUp size={14} /> +15% since last login
        </div>
      </div>
      <div className="stat-card">
        <div className="stat-header">
          Saved Scholarships
          <div className="icon-wrapper"><Search size={18} /></div>
        </div>
        <div className="stat-value">12</div>
        <div className="stat-trend">2 deadlines approaching</div>
      </div>
      <div className="stat-card">
        <div className="stat-header">
          Active Applications
          <div className="icon-wrapper"><FileText size={18} /></div>
        </div>
        <div className="stat-value">3</div>
        <div className="stat-trend positive">1 under review</div>
      </div>
      <div className="stat-card">
        <div className="stat-header">
          Documents Verified
          <div className="icon-wrapper"><CheckCircle size={18} /></div>
        </div>
        <div className="stat-value">4/5</div>
        <div className="stat-trend">Pending IELTS score</div>
      </div>
    </div>

    <div className="widgets-grid">
      <div className="widget">
        <div className="widget-header">
          <h3 className="widget-title">Recent Applications</h3>
          <Link to="/applications" style={{ color: 'var(--primary-green)', textDecoration: 'none', fontSize: '0.875rem' }}>View All →</Link>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ color: 'var(--text-gray)', fontSize: '0.875rem', borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ paddingBottom: '1rem' }}>University</th>
              <th style={{ paddingBottom: '1rem' }}>Program</th>
              <th style={{ paddingBottom: '1rem' }}>Intake</th>
              <th style={{ paddingBottom: '1rem' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ padding: '1rem 0' }}>University of Toronto</td>
              <td style={{ padding: '1rem 0' }}>MSc Computer Science</td>
              <td style={{ padding: '1rem 0' }}>Fall 2026</td>
              <td style={{ padding: '1rem 0' }}><span style={{ color: 'var(--primary-green)', background: 'var(--primary-green-light)', padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem' }}>Submitted</span></td>
            </tr>
            <tr>
              <td style={{ padding: '1rem 0' }}>University of Melbourne</td>
              <td style={{ padding: '1rem 0' }}>Master of Data Science</td>
              <td style={{ padding: '1rem 0' }}>Spring 2027</td>
              <td style={{ padding: '1rem 0' }}><span style={{ color: '#eab308', background: '#fef9c3', padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem' }}>In Review</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="widget">
        <div className="widget-header">
          <h3 className="widget-title">Tasks & Deadlines</h3>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <div style={{ color: 'var(--text-gray)' }}><Clock size={20} /></div>
            <div>
              <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>Upload IELTS Certificate</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-gray)' }}>Due in 2 days</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <div style={{ color: 'var(--text-gray)' }}><Clock size={20} /></div>
            <div>
              <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>Review Scholarship Essay</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-gray)' }}>Due in 5 days</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default Dashboard;
```

### I. New File: `src/pages/Login.jsx`
The standard, styled authentication portal screen.

```jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { GraduationCap } from 'lucide-react';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors = {};
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters long';
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
    if (apiError) {
      setApiError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    const result = await login(formData.email, formData.password);
    setIsSubmitting(false);

    if (result.success) {
      navigate('/');
    } else {
      setApiError(result.error || 'Login failed. Please check your credentials.');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-brand">
          <GraduationCap className="brand-icon" size={32} />
          <span>EduConsultant</span>
        </div>
        <h2 className="auth-title">Welcome back</h2>
        <p className="auth-subtitle">Sign in to your student account</p>

        {apiError && <div className="alert alert-error">{apiError}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="alex@example.com"
              className={`form-input ${errors.email ? 'input-error' : ''}`}
              disabled={isSubmitting}
            />
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              className={`form-input ${errors.password ? 'input-error' : ''}`}
              disabled={isSubmitting}
            />
            {errors.password && <span className="field-error">{errors.password}</span>}
          </div>

          <button type="submit" className="btn btn-primary btn-block" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="auth-footer">
          Don't have an account? <Link to="/register" className="auth-link">Register here</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
```

### J. New File: `src/pages/Register.jsx`
Forms for name, email, credentials, and preference setups to build a robust profile state.

```jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { GraduationCap } from 'lucide-react';

const Register = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    degreePreference: 'Master of Computer Science',
    ieltsScore: '7.0'
  });

  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

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
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
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
    if (apiError) {
      setApiError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    const { confirmPassword: _, ...registerData } = formData;
    const result = await register(registerData);
    setIsSubmitting(false);

    if (result.success) {
      navigate('/');
    } else {
      setApiError(result.error || 'Registration failed. Please try again.');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-brand">
          <GraduationCap className="brand-icon" size={32} />
          <span>EduConsultant</span>
        </div>
        <h2 className="auth-title">Create your account</h2>
        <p className="auth-subtitle">Join the student portal dashboard</p>

        {apiError && <div className="alert alert-error">{apiError}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label" htmlFor="name">Full Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Alex Johnson"
              className={`form-input ${errors.name ? 'input-error' : ''}`}
              disabled={isSubmitting}
            />
            {errors.name && <span className="field-error">{errors.name}</span>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="alex@example.com"
              className={`form-input ${errors.email ? 'input-error' : ''}`}
              disabled={isSubmitting}
            />
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label className="form-label" htmlFor="degreePreference">Degree Preference</label>
              <select
                id="degreePreference"
                name="degreePreference"
                value={formData.degreePreference}
                onChange={handleChange}
                className="form-input"
                disabled={isSubmitting}
              >
                <option value="Bachelor of Computer Science">Bachelor of CS</option>
                <option value="Master of Computer Science">Master of CS</option>
                <option value="Master of Data Science">Master of Data Science</option>
                <option value="MBA">MBA</option>
                <option value="PhD in Engineering">PhD in Engineering</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="ieltsScore">IELTS Score</label>
              <select
                id="ieltsScore"
                name="ieltsScore"
                value={formData.ieltsScore}
                onChange={handleChange}
                className="form-input"
                disabled={isSubmitting}
              >
                <option value="6.0">6.0</option>
                <option value="6.5">6.5</option>
                <option value="7.0">7.0</option>
                <option value="7.5">7.5</option>
                <option value="8.0">8.0</option>
                <option value="8.5">8.5</option>
                <option value="9.0">9.0</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              className={`form-input ${errors.password ? 'input-error' : ''}`}
              disabled={isSubmitting}
            />
            {errors.password && <span className="field-error">{errors.password}</span>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="••••••••"
              className={`form-input ${errors.confirmPassword ? 'input-error' : ''}`}
              disabled={isSubmitting}
            />
            {errors.confirmPassword && <span className="field-error">{errors.confirmPassword}</span>}
          </div>

          <button type="submit" className="btn btn-primary btn-block" disabled={isSubmitting}>
            {isSubmitting ? 'Creating account...' : 'Register'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login" className="auth-link">Login here</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
```

### K. New File: `src/pages/Profile.jsx`
Features dual-panel interface supporting profile detail adjustments and dynamic preview changes.

```jsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
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
        <div className={`alert ${message.type === 'success' ? 'alert-success' : 'alert-error'}`} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
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
                {errors.name && <span className="field-error">{errors.name}</span>}
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
                {errors.email && <span className="field-error">{errors.email}</span>}
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
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Award size={16} /> IELTS Band Score
                </label>
                <select
                  name="ieltsScore"
                  value={formData.ieltsScore}
                  onChange={handleChange}
                  className="form-input"
                  disabled={isSaving}
                >
                  <option value="6.0">6.0</option>
                  <option value="6.5">6.5</option>
                  <option value="7.0">7.0</option>
                  <option value="7.5">7.5</option>
                  <option value="8.0">8.0</option>
                  <option value="8.5">8.5</option>
                  <option value="9.0">9.0</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
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
```

### L. File Modification: `src/App.jsx`
Rewrites the routing infrastructure and sets up the global `AuthProvider`.

```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from './components/PublicRoute';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route 
            path="/login" 
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            } 
          />
          <Route 
            path="/register" 
            element={
              <PublicRoute>
                <Register />
              </PublicRoute>
            } 
          />

          {/* Protected Routes inside Layout */}
          <Route 
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<Dashboard />} />
            <Route path="/profile" element={<Profile />} />
            
            {/* Placeholders for subsequent milestones */}
            <Route path="/scholarships" element={
              <div className="dashboard-content">
                <div className="page-header">
                  <h1 className="page-title">Scholarships</h1>
                  <p className="page-subtitle">Coming soon in Milestone 2.</p>
                </div>
              </div>
            } />
            <Route path="/universities" element={
              <div className="dashboard-content">
                <div className="page-header">
                  <h1 className="page-title">Universities</h1>
                  <p className="page-subtitle">Coming soon in Milestone 2.</p>
                </div>
              </div>
            } />
            <Route path="/applications" element={
              <div className="dashboard-content">
                <div className="page-header">
                  <h1 className="page-title">Applications</h1>
                  <p className="page-subtitle">Coming soon in Milestone 3.</p>
                </div>
              </div>
            } />
            <Route path="/settings" element={
              <div className="dashboard-content">
                <div className="page-header">
                  <h1 className="page-title">Settings</h1>
                  <p className="page-subtitle">Coming soon.</p>
                </div>
              </div>
            } />
          </Route>

          {/* Catch-all Redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
```

### M. File Modification: `src/index.css`
Append these rules to the bottom of the file to support the authentication styling theme and overrides.

```css

/* --- Milestone 1 Styling Enhancements --- */

/* Auth Layout styling */
.auth-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: var(--bg-gray);
  padding: 2rem;
}

.auth-card {
  background-color: var(--bg-white);
  padding: 2.5rem;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  width: 100%;
  max-width: 440px;
  text-align: center;
}

.auth-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 700;
  font-size: 1.5rem;
  color: var(--text-dark);
  margin-bottom: 1.5rem;
}

.auth-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-dark);
  margin-bottom: 0.5rem;
}

.auth-subtitle {
  color: var(--text-gray);
  font-size: 0.875rem;
  margin-bottom: 2rem;
}

/* Auth & General Forms */
.auth-form {
  text-align: left;
  width: 100%;
}

.form-group {
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 0.25rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-dark);
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background-color: var(--bg-white);
  font-family: inherit;
  font-size: 0.875rem;
  color: var(--text-dark);
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  border-color: var(--primary-green);
  box-shadow: 0 0 0 3px var(--primary-green-light);
}

.form-input.input-error {
  border-color: #ef4444;
}

.form-input.input-error:focus {
  box-shadow: 0 0 0 3px #fee2e2;
}

.field-error {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.375rem;
  font-weight: 500;
}

/* Button UI Components */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background-color: var(--primary-green);
  color: white;
}

.btn-primary:hover {
  background-color: #248f5a;
}

.btn-primary:disabled {
  background-color: #a7f3d0;
  cursor: not-allowed;
}

.btn-block {
  width: 100%;
}

/* Alert Notification UI Components */
.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
  text-align: left;
  border: 1px solid transparent;
}

.alert-error {
  background-color: #fef2f2;
  color: #b91c1c;
  border-color: #fca5a5;
}

.alert-success {
  background-color: var(--primary-green-light);
  color: #15803d;
  border-color: #a7f3d0;
}

.auth-footer {
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: var(--text-gray);
}

.auth-link {
  color: var(--primary-green);
  text-decoration: none;
  font-weight: 600;
}

.auth-link:hover {
  text-decoration: underline;
}

/* NavLink Reset */
.nav-link {
  text-decoration: none;
  display: flex;
  align-items: center;
  width: 100%;
}
```

---

## 5. Verification Method

### A. Static Analysis
Run the project's linter and bundler commands to ensure there are no compilation errors, missing imports, or type discrepancies:
1. `npm run lint`: Verifies syntax clean compilation using oxlint.
2. `npm run build`: Bundles the application using Vite to verify that standard asset linking works without issues.

### B. Dynamic Functional Flow
1. **Redirection (Guards)**:
   - Access the root page `/` or `/profile` directly without a session. The system must redirect instantly to `/login`.
   - Access `/login` or `/register` when logged in. The system must redirect instantly to `/`.
2. **Registration Check**:
   - Navigate to `/register`.
   - Submit invalid details (e.g. passwords that do not match, or leaving fields blank) to verify field validation error messages display.
   - Fill in details for a new user (e.g. `test@example.com` / `password123`). Submit and verify redirection to `/` happens and the Topbar displays the new user's name and role.
3. **Login Check**:
   - Log out. Navigate to `/login`.
   - Try logging in with the seeded user: `alex@example.com` and password `password123`. Verify it authenticates instantly and logs you into the dashboard.
4. **Profile Modification Check**:
   - Navigate to `/profile`.
   - Change the Name, Degree Preference, and IELTS score.
   - Input a custom image URL (or change the dicebear seed URL parameter) and verify that the avatar preview image updates in real-time.
   - Click "Save Changes". Verify the success alert displays.
   - Refresh the page and confirm that the modified profile info is retrieved correctly from `localStorage`.
