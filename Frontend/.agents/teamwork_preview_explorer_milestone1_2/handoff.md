# Handoff Report: Milestone 1 - Authentication & Profile UI Design

## 1. Observation
After checking the project layout and file structures in the frontend codebase, the following was observed:
- `package.json` contains `react-router-dom` v7 (`^7.18.1`), React 19 (`^19.2.7`), and `vite` (`^8.1.1`).
- `src/main.jsx` renders `<App />` inside `<StrictMode>`.
- `src/App.jsx` currently implements static routing to a single `Dashboard` element at `/` using `<BrowserRouter>`:
  ```jsx
  const App = () => {
    return (
      <Router>
        <div className="dashboard-layout">
          <Sidebar />
          <div className="main-content">
            <Topbar />
            <Routes>
              <Route path="/" element={<Dashboard />} />
            </Routes>
          </div>
        </div>
      </Router>
    );
  };
  ```
- The `Sidebar` and `Topbar` components are declared inline inside `src/App.jsx` and display hardcoded guest info (e.g., `"Alex Johnson"`).
- There is no auth logic, mock services, validation functions, or separate page components (e.g. `Login.jsx`, `Register.jsx`, `Profile.jsx`) in the project.
- `src/index.css` provides variables (such as `--primary-green: #2db06f`, `--bg-gray: #f8fafc`, etc.) and basic grid rules, but lacks styles for forms, logins, input validation, and alert components.

---

## 2. Logic Chain
To fulfill Milestone 1, we must transform this structure to support dynamic authentication state, guarded routing, and fully functional page components:
1. **Mock API Wrapper (`src/services/api.js`)**: To prepare for a future FastAPI backend integration, authentication operations must be decoupled from the React state and encapsulated in an API layer. We will implement standard CRUD interfaces for auth (`login`, `register`, `logout`, `updateProfile`) and use `localStorage` to simulate database persistence and session tracking.
2. **Context & Custom Hook (`src/context/AuthContext.jsx`)**: The session state needs to be globally available so that the App can display user details, manage redirects, and guard routes. The `AuthContext` will expose the properties (`user`, `isAuthenticated`, `loading`) and actions (`login`, `register`, `logout`, `updateProfile`) to components via a `useAuth` hook.
3. **Route Guards (`src/components/ProtectedRoute.jsx` & `src/components/PublicRoute.jsx`)**:
   - `ProtectedRoute` protects files/routes like `/profile` and `/` (dashboard) by redirecting unauthenticated users to `/login`.
   - `PublicRoute` restricts authenticated users from visiting `/login` and `/register`, redirecting them to `/` if they are already signed in.
4. **Layout Decomposition (`src/components/DashboardLayout.jsx`)**: The sidebar and topbar should only be shown on protected dashboard-level routes. We will create a `DashboardLayout` container using `react-router-dom`'s `<Outlet />` to render the page content dynamically inside the sidebar/topbar shell.
5. **Component Extraction & Page Implementation (`src/pages/*` and `src/components/*`)**:
   - We will extract `Sidebar` and `Topbar` from `App.jsx` into separate reusable components.
   - We will implement forms with validation in `Login.jsx`, `Register.jsx`, and `Profile.jsx`.
   - We will add standard validations (e.g. valid email patterns, matching passwords, and specific IELTS scores from `0.0` to `9.0` in steps of `0.5`).
   - We will use Base64 reading (`FileReader`) for the avatar picture upload, saving the base64 URL directly to localStorage so changes reflect dynamically in the Topbar.
6. **Styling Integration (`src/index.css`)**: We will append clean CSS classes to `src/index.css` leveraging existing root variables, guaranteeing style uniformity.

---

## 3. Caveats
- **Cleartext Passwords**: Since this is a client-side prototype, passwords will be stored in cleartext inside `localStorage`. In production, passwords will be handled securely by a backend hashing library.
- **LocalStorage Capacity**: Profile images are converted to Base64 and saved to `localStorage` (which has a ~5MB limit). A file size constraint of `<500KB` is implemented on image uploads to avoid running out of storage.
- **Loading Latency**: All mock API calls incorporate a short artificial delay (200ms–500ms) to simulate server latency and allow testing of loading spinners.

---

## 4. Conclusion
Below is the complete implementation design. It outlines the exact files to create and modify, along with their proposed source code.

### 4.1 New Files to Create

#### 1. `src/services/api.js` (Mock Data Layer)
```javascript
const MOCK_USERS_KEY = 'educonsultant_users';
const CURRENT_SESSION_KEY = 'educonsultant_session';

const DEFAULT_USER = {
  name: 'Alex Johnson',
  email: 'alex@example.com',
  password: 'password123',
  degreePreference: 'MSc Computer Science',
  ieltsScore: '7.5',
  profileImg: ''
};

// Seed local storage database if it's currently empty
const getStoredUsers = () => {
  const users = localStorage.getItem(MOCK_USERS_KEY);
  if (!users) {
    localStorage.setItem(MOCK_USERS_KEY, JSON.stringify([DEFAULT_USER]));
    return [DEFAULT_USER];
  }
  return JSON.parse(users);
};

const saveUsers = (users) => {
  localStorage.setItem(MOCK_USERS_KEY, JSON.stringify(users));
};

export const mockApi = {
  getCurrentSession: () => {
    const session = localStorage.getItem(CURRENT_SESSION_KEY);
    return session ? JSON.parse(session) : null;
  },

  login: async (email, password) => {
    // Artificial delay to simulate network call
    await new Promise((resolve) => setTimeout(resolve, 500));
    
    const users = getStoredUsers();
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());
    
    if (!user || user.password !== password) {
      throw new Error('Invalid email or password.');
    }
    
    // Omit password from session
    const { password: _, ...userSession } = user;
    localStorage.setItem(CURRENT_SESSION_KEY, JSON.stringify(userSession));
    return userSession;
  },

  register: async (userData) => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    
    const users = getStoredUsers();
    const emailExists = users.some(u => u.email.toLowerCase() === userData.email.toLowerCase());
    
    if (emailExists) {
      throw new Error('Email is already registered.');
    }
    
    const newUser = {
      name: userData.name,
      email: userData.email,
      password: userData.password,
      degreePreference: userData.degreePreference || '',
      ieltsScore: userData.ieltsScore || '',
      profileImg: userData.profileImg || ''
    };
    
    users.push(newUser);
    saveUsers(users);
    
    const { password: _, ...userSession } = newUser;
    localStorage.setItem(CURRENT_SESSION_KEY, JSON.stringify(userSession));
    return userSession;
  },

  logout: async () => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    localStorage.removeItem(CURRENT_SESSION_KEY);
    return true;
  },

  updateProfile: async (currentEmail, updatedData) => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    
    const users = getStoredUsers();
    const userIndex = users.findIndex(u => u.email.toLowerCase() === currentEmail.toLowerCase());
    
    if (userIndex === -1) {
      throw new Error('User profile not found.');
    }
    
    // Check if updated email collides with another user
    if (updatedData.email && updatedData.email.toLowerCase() !== currentEmail.toLowerCase()) {
      const emailExists = users.some(u => u.email.toLowerCase() === updatedData.email.toLowerCase());
      if (emailExists) {
        throw new Error('New email address is already in use by another account.');
      }
    }
    
    // Update user record
    const updatedUser = {
      ...users[userIndex],
      name: updatedData.name ?? users[userIndex].name,
      email: updatedData.email ?? users[userIndex].email,
      degreePreference: updatedData.degreePreference ?? users[userIndex].degreePreference,
      ieltsScore: updatedData.ieltsScore ?? users[userIndex].ieltsScore,
      profileImg: updatedData.profileImg !== undefined ? updatedData.profileImg : users[userIndex].profileImg
    };
    
    users[userIndex] = updatedUser;
    saveUsers(users);
    
    // Update current session storage
    const { password: _, ...userSession } = updatedUser;
    localStorage.setItem(CURRENT_SESSION_KEY, JSON.stringify(userSession));
    return userSession;
  }
};
```

#### 2. `src/context/AuthContext.jsx` (Global Auth Context)
```jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { mockApi } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const session = mockApi.getCurrentSession();
    if (session) {
      setUser(session);
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const loggedUser = await mockApi.login(email, password);
    setUser(loggedUser);
    return loggedUser;
  };

  const register = async (userData) => {
    const registeredUser = await mockApi.register(userData);
    setUser(registeredUser);
    return registeredUser;
  };

  const logout = async () => {
    await mockApi.logout();
    setUser(null);
  };

  const updateProfile = async (newData) => {
    if (!user) throw new Error('No active user session');
    const updatedUser = await mockApi.updateProfile(user.email, newData);
    setUser(updatedUser);
    return updatedUser;
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

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

#### 3. `src/components/ProtectedRoute.jsx` (Guarded Route for Authed Users)
```jsx
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = () => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div className="loading-spinner">Loading...</div>;
  }
  
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
```

#### 4. `src/components/PublicRoute.jsx` (Guarded Route for Guests Only)
```jsx
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const PublicRoute = () => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div className="loading-spinner">Loading...</div>;
  }
  
  return !isAuthenticated ? <Outlet /> : <Navigate to="/" replace />;
};

export default PublicRoute;
```

#### 5. `src/components/DashboardLayout.jsx` (Dashboard Layout Shell)
```jsx
import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

const DashboardLayout = () => {
  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="main-content">
        <Topbar />
        <div className="dashboard-content">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;
```

#### 6. `src/components/Sidebar.jsx` (Refactored Sidebar)
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

  const handleLogoutClick = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="sidebar">
      <div className="brand">
        <GraduationCap className="brand-icon" size={28} />
        EduConsultant
      </div>
      <ul className="nav-menu">
        <li>
          <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <LayoutDashboard size={20} />
            Dashboard
          </NavLink>
        </li>
        <li>
          <NavLink to="/scholarships" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Search size={20} />
            Scholarships
          </NavLink>
        </li>
        <li>
          <NavLink to="/universities" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Building size={20} />
            Universities
          </NavLink>
        </li>
        <li>
          <NavLink to="/applications" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <FileText size={20} />
            My Applications
          </NavLink>
        </li>
        <li>
          <NavLink to="/profile" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <User size={20} />
            My Profile
          </NavLink>
        </li>
        <li style={{ marginTop: 'auto' }}>
          <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Settings size={20} />
            Settings
          </NavLink>
        </li>
        <li>
          <button onClick={handleLogoutClick} className="nav-item logout-btn" style={{ width: '100%', background: 'none', border: 'none', textAlign: 'left', cursor: 'pointer' }}>
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

#### 7. `src/components/Topbar.jsx` (Refactored Topbar)
```jsx
import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Search, Bell, Mail, User } from 'lucide-react';

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
            <img src={user.profileImg} className="avatar" alt={user.name} />
          ) : (
            <div className="icon-wrapper" style={{ width: '36px', height: '36px' }}>
              <User size={20} />
            </div>
          )}
          <div className="user-info">
            <span className="user-name">{user?.name || 'Guest'}</span>
            <span className="user-role">Student</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Topbar;
```

#### 8. `src/pages/Dashboard.jsx` (Extracted Dashboard Page View)
```jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { User, Search, FileText, CheckCircle, TrendingUp, Clock } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const profileCompletion = user ? 85 : 0;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Welcome back, {user?.name}!</h1>
        <p className="page-subtitle">Track your applications and explore opportunities.</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            Profile Completion
            <div className="icon-wrapper"><User size={18} /></div>
          </div>
          <div className="stat-value">{profileCompletion}%</div>
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
};

export default Dashboard;
```

#### 9. `src/pages/Login.jsx` (Login Screen Component)
```jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { GraduationCap, Mail, Lock, Loader2 } from 'lucide-react';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const errors = {};
    if (!email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errors.email = 'Please enter a valid email address';
    }
    if (!password) {
      errors.password = 'Password is required';
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!validate()) return;
    
    setIsSubmitting(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <div className="brand logo-center">
            <GraduationCap className="brand-icon" size={32} />
            EduConsultant
          </div>
          <h2 className="auth-title">Welcome Back</h2>
          <p className="auth-subtitle">Sign in to manage your scholarship applications</p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <div className="input-with-icon">
              <Mail className="input-icon" size={18} />
              <input
                id="email"
                type="email"
                className={`form-input ${fieldErrors.email ? 'input-error' : ''}`}
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isSubmitting}
              />
            </div>
            {fieldErrors.email && <span className="form-error-text">{fieldErrors.email}</span>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <div className="input-with-icon">
              <Lock className="input-icon" size={18} />
              <input
                id="password"
                type="password"
                className={`form-input ${fieldErrors.password ? 'input-error' : ''}`}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isSubmitting}
              />
            </div>
            {fieldErrors.password && <span className="form-error-text">{fieldErrors.password}</span>}
          </div>

          <button type="submit" className="btn btn-primary w-full" disabled={isSubmitting}>
            {isSubmitting ? (
              <span className="flex-center gap-2">
                <Loader2 className="animate-spin" size={18} /> Signing In...
              </span>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <div className="auth-footer">
          Don't have an account? <Link to="/register" className="auth-link">Register Here</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
```

#### 10. `src/pages/Register.jsx` (Register Screen Component)
```jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { GraduationCap, Mail, Lock, User, FileDigit, Building, Loader2 } from 'lucide-react';

const Register = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [degreePreference, setDegreePreference] = useState('MSc Computer Science');
  const [ieltsScore, setIeltsScore] = useState('');

  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const errors = {};
    if (!name.trim()) {
      errors.name = 'Full name is required';
    }
    if (!email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errors.email = 'Please enter a valid email address';
    }
    if (!password) {
      errors.password = 'Password is required';
    } else if (password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }
    if (password !== confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }
    if (ieltsScore) {
      const score = parseFloat(ieltsScore);
      if (isNaN(score) || score < 0 || score > 9 || (score * 2) % 1 !== 0) {
        errors.ieltsScore = 'IELTS score must be between 0.0 and 9.0 in steps of 0.5';
      }
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await register({
        name,
        email,
        password,
        degreePreference,
        ieltsScore: ieltsScore ? parseFloat(ieltsScore).toFixed(1) : ''
      });
      navigate('/');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card" style={{ maxWidth: '500px' }}>
        <div className="auth-header">
          <div className="brand logo-center">
            <GraduationCap className="brand-icon" size={32} />
            EduConsultant
          </div>
          <h2 className="auth-title">Create Account</h2>
          <p className="auth-subtitle">Join us to start planning your academic journey</p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label" htmlFor="name">Full Name</label>
            <div className="input-with-icon">
              <User className="input-icon" size={18} />
              <input
                id="name"
                type="text"
                className={`form-input ${fieldErrors.name ? 'input-error' : ''}`}
                placeholder="Alex Johnson"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isSubmitting}
              />
            </div>
            {fieldErrors.name && <span className="form-error-text">{fieldErrors.name}</span>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <div className="input-with-icon">
              <Mail className="input-icon" size={18} />
              <input
                id="email"
                type="email"
                className={`form-input ${fieldErrors.email ? 'input-error' : ''}`}
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isSubmitting}
              />
            </div>
            {fieldErrors.email && <span className="form-error-text">{fieldErrors.email}</span>}
          </div>

          <div className="grid-2col">
            <div className="form-group">
              <label className="form-label" htmlFor="password">Password</label>
              <div className="input-with-icon">
                <Lock className="input-icon" size={18} />
                <input
                  id="password"
                  type="password"
                  className={`form-input ${fieldErrors.password ? 'input-error' : ''}`}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isSubmitting}
                />
              </div>
              {fieldErrors.password && <span className="form-error-text">{fieldErrors.password}</span>}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="confirmPassword">Confirm Password</label>
              <div className="input-with-icon">
                <Lock className="input-icon" size={18} />
                <input
                  id="confirmPassword"
                  type="password"
                  className={`form-input ${fieldErrors.confirmPassword ? 'input-error' : ''}`}
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={isSubmitting}
                />
              </div>
              {fieldErrors.confirmPassword && <span className="form-error-text">{fieldErrors.confirmPassword}</span>}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="degreePreference">Degree Preference</label>
            <div className="input-with-icon">
              <Building className="input-icon" size={18} />
              <select
                id="degreePreference"
                className="form-input"
                value={degreePreference}
                onChange={(e) => setDegreePreference(e.target.value)}
                disabled={isSubmitting}
              >
                <option value="BSc Computer Science">BSc Computer Science</option>
                <option value="MSc Computer Science">MSc Computer Science</option>
                <option value="Bachelor of Data Science">Bachelor of Data Science</option>
                <option value="Master of Data Science">Master of Data Science</option>
                <option value="BBA Business Administration">BBA Business Administration</option>
                <option value="MBA Business Administration">MBA Business Administration</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="ieltsScore">IELTS Score (Optional)</label>
            <div className="input-with-icon">
              <FileDigit className="input-icon" size={18} />
              <input
                id="ieltsScore"
                type="number"
                step="0.5"
                min="0"
                max="9"
                className={`form-input ${fieldErrors.ieltsScore ? 'input-error' : ''}`}
                placeholder="7.5"
                value={ieltsScore}
                onChange={(e) => setIeltsScore(e.target.value)}
                disabled={isSubmitting}
              />
            </div>
            {fieldErrors.ieltsScore && <span className="form-error-text">{fieldErrors.ieltsScore}</span>}
          </div>

          <button type="submit" className="btn btn-primary w-full" disabled={isSubmitting}>
            {isSubmitting ? (
              <span className="flex-center gap-2">
                <Loader2 className="animate-spin" size={18} /> Creating Account...
              </span>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login" className="auth-link">Login Here</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
```

#### 11. `src/pages/Profile.jsx` (Profile Manager Component)
```jsx
import React, { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Mail, Building, FileDigit, Upload, Trash2, Loader2, CheckCircle2 } from 'lucide-react';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const fileInputRef = useRef(null);

  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [degreePreference, setDegreePreference] = useState(user?.degreePreference || 'MSc Computer Science');
  const [ieltsScore, setIeltsScore] = useState(user?.ieltsScore || '');
  const [profileImg, setProfileImg] = useState(user?.profileImg || '');

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file (PNG, JPG).');
      return;
    }

    if (file.size > 500 * 1024) {
      setError('Image size should be less than 500KB to fit mock storage.');
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      setProfileImg(reader.result);
      setError('');
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveAvatar = () => {
    setProfileImg('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const validate = () => {
    const errors = {};
    if (!name.trim()) {
      errors.name = 'Full name is required';
    }
    if (!email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errors.email = 'Please enter a valid email address';
    }
    if (ieltsScore) {
      const score = parseFloat(ieltsScore);
      if (isNaN(score) || score < 0 || score > 9 || (score * 2) % 1 !== 0) {
        errors.ieltsScore = 'IELTS score must be between 0.0 and 9.0 in steps of 0.5';
      }
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await updateProfile({
        name,
        email,
        degreePreference,
        ieltsScore: ieltsScore ? parseFloat(ieltsScore).toFixed(1) : '',
        profileImg
      });
      setSuccess('Profile updated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to update profile. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (user) {
      setName(user.name || '');
      setEmail(user.email || '');
      setDegreePreference(user.degreePreference || 'MSc Computer Science');
      setIeltsScore(user.ieltsScore || '');
      setProfileImg(user.profileImg || '');
      setError('');
      setFieldErrors({});
    }
  };

  return (
    <div className="profile-container">
      <div className="page-header">
        <h1 className="page-title">My Profile</h1>
        <p className="page-subtitle">Manage your personal information and application preferences</p>
      </div>

      {success && (
        <div className="alert alert-success flex-center gap-2">
          <CheckCircle2 size={18} /> {success}
        </div>
      )}
      {error && <div className="alert alert-error">{error}</div>}

      <div className="profile-grid">
        <div className="profile-avatar-section">
          <div className="avatar-card">
            <h3>Profile Picture</h3>
            <div className="avatar-preview-container">
              {profileImg ? (
                <img src={profileImg} className="profile-avatar-large" alt={name} />
              ) : (
                <div className="profile-avatar-placeholder">
                  <User size={64} color="var(--text-gray)" />
                </div>
              )}
            </div>
            
            <div className="avatar-actions">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleAvatarChange}
                accept="image/*"
                style={{ display: 'none' }}
              />
              <button
                type="button"
                className="btn btn-secondary flex-center gap-2"
                onClick={() => fileInputRef.current?.click()}
                disabled={isSubmitting}
              >
                <Upload size={16} /> Upload Photo
              </button>
              {profileImg && (
                <button
                  type="button"
                  className="btn btn-danger flex-center gap-2"
                  onClick={handleRemoveAvatar}
                  disabled={isSubmitting}
                >
                  <Trash2 size={16} /> Remove
                </button>
              )}
            </div>
            <p className="avatar-tip">JPG or PNG. Max size 500KB.</p>
          </div>
        </div>

        <div className="profile-form-section">
          <div className="form-card">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label" htmlFor="name">Full Name</label>
                <div className="input-with-icon">
                  <User className="input-icon" size={18} />
                  <input
                    id="name"
                    type="text"
                    className={`form-input ${fieldErrors.name ? 'input-error' : ''}`}
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    disabled={isSubmitting}
                  />
                </div>
                {fieldErrors.name && <span className="form-error-text">{fieldErrors.name}</span>}
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="email">Email Address</label>
                <div className="input-with-icon">
                  <Mail className="input-icon" size={18} />
                  <input
                    id="email"
                    type="email"
                    className={`form-input ${fieldErrors.email ? 'input-error' : ''}`}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={isSubmitting}
                  />
                </div>
                {fieldErrors.email && <span className="form-error-text">{fieldErrors.email}</span>}
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="degreePreference">Degree Preference</label>
                <div className="input-with-icon">
                  <Building className="input-icon" size={18} />
                  <select
                    id="degreePreference"
                    className="form-input"
                    value={degreePreference}
                    onChange={(e) => setDegreePreference(e.target.value)}
                    disabled={isSubmitting}
                  >
                    <option value="BSc Computer Science">BSc Computer Science</option>
                    <option value="MSc Computer Science">MSc Computer Science</option>
                    <option value="Bachelor of Data Science">Bachelor of Data Science</option>
                    <option value="Master of Data Science">Master of Data Science</option>
                    <option value="BBA Business Administration">BBA Business Administration</option>
                    <option value="MBA Business Administration">MBA Business Administration</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="ieltsScore">IELTS Score</label>
                <div className="input-with-icon">
                  <FileDigit className="input-icon" size={18} />
                  <input
                    id="ieltsScore"
                    type="number"
                    step="0.5"
                    min="0"
                    max="9"
                    className={`form-input ${fieldErrors.ieltsScore ? 'input-error' : ''}`}
                    placeholder="Not taken yet"
                    value={ieltsScore}
                    onChange={(e) => setIeltsScore(e.target.value)}
                    disabled={isSubmitting}
                  />
                </div>
                {fieldErrors.ieltsScore && <span className="form-error-text">{fieldErrors.ieltsScore}</span>}
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleCancel}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary flex-center gap-2"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="animate-spin" size={16} /> Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
```

---

### 4.2 Codebase Modifications

#### 1. `src/App.jsx` (Central Routing Framework)
The file should be fully updated to contain only routing declarations, import statements, and layout assignments:
```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from './components/PublicRoute';
import DashboardLayout from './components/DashboardLayout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Guest-only auth paths */}
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Route>

          {/* Secure student application workspace */}
          <Route element={<ProtectedRoute />}>
            <Route element={<DashboardLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/profile" element={<Profile />} />
              
              {/* Placeholders for future milestones */}
              <Route path="/scholarships" element={
                <div>
                  <div className="page-header">
                    <h1 className="page-title">Scholarships Discovery</h1>
                    <p className="page-subtitle">Milestone 2 Discovery UI coming soon...</p>
                  </div>
                </div>
              } />
              <Route path="/universities" element={
                <div>
                  <div className="page-header">
                    <h1 className="page-title">Universities Directory</h1>
                    <p className="page-subtitle">Milestone 2 Discovery UI coming soon...</p>
                  </div>
                </div>
              } />
              <Route path="/applications" element={
                <div>
                  <div className="page-header">
                    <h1 className="page-title">My Applications</h1>
                    <p className="page-subtitle">Milestone 3 Applications tracking coming soon...</p>
                  </div>
                </div>
              } />
              <Route path="/documents" element={
                <div>
                  <div className="page-header">
                    <h1 className="page-title">Document Manager</h1>
                    <p className="page-subtitle">Milestone 3 Document manager coming soon...</p>
                  </div>
                </div>
              } />
              <Route path="/settings" element={
                <div>
                  <div className="page-header">
                    <h1 className="page-title">Settings</h1>
                    <p className="page-subtitle">Portal preferences and configuration.</p>
                  </div>
                </div>
              } />
            </Route>
          </Route>

          {/* Wildcard route to handle invalid requests */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
```

#### 2. `src/index.css` (Appended Styling Rules)
The styling code in **Section 4.1** (from `/* Authentication and Form styles */` to `.loading-spinner`) should be appended to the very bottom of `src/index.css` to enable smooth form elements, layout margins, validation highlights, responsive columns, and spinner animations.

---

## 5. Verification Method

### 5.1 Verification Commands
Verify compile safety and syntax completeness by executing standard build tools:
```powershell
# 1. Lint the application using oxlint to verify no unused variables or syntax violations exist
npm run lint

# 2. Build the project using Vite build system to confirm complete bundle resolution
npm run build
```

### 5.2 Manual Acceptance Test Scenarios
- **Scenario A: Unauthenticated Redirects (Guards test)**
  - Access `http://localhost:5173/` or `/profile` directly.
  - *Expected result*: App automatically routes back to `/login` and hides layout components.
- **Scenario B: Public Route Blocks (Guards test)**
  - Authenticate with `alex@example.com` / `password123`.
  - Navigate explicitly to `http://localhost:5173/login`.
  - *Expected result*: User is redirected back to `/` and is not forced to log in again.
- **Scenario C: Session Persistence**
  - Sign in, modify the profile name in `/profile` to "John Doe" and press "Save Changes".
  - Refresh the browser page (`F5`).
  - *Expected result*: The updated session continues. The name "John Doe" remains visible in Topbar and Profile.
- **Scenario D: Dynamic Profile Picture Propagation**
  - Upload an avatar file (<500KB) in `/profile` and submit changes.
  - *Expected result*: Image immediately propagates to Topbar and updates the Sidebar profile info.
- **Scenario E: Validation Check**
  - Try registering with a password of length 4, or an invalid IELTS score (like 7.2).
  - *Expected result*: Fields display validation error text in red, and the API request is aborted.

### 5.3 Invalidation Conditions
- Auth redirects trigger cyclic routing loops.
- `localStorage` JSON parsing failures when clearing sessions.
- React 19 warnings regarding Context Providers or react-router-dom elements.
