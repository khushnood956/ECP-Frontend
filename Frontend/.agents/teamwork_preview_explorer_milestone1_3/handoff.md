# Handoff Report: Milestone 1 - Authentication & Profile UI Design

## 1. Observation
After searching and analyzing the Frontend codebase, the following was observed:
1. **Dependencies & Routing** (`package.json` line 14-16):
   ```json
   "react": "^19.2.7",
   "react-dom": "^19.2.7",
   "react-router-dom": "^7.18.1"
   ```
   React 19 and React Router v7 are available.
2. **Static Layout Wrapper** (`src/App.jsx` line 177-191):
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
   Currently, the layout wrapper (containing `Sidebar` and `Topbar`) statically wraps all routes. This layout must be decoupled to allow `/login` and `/register` routes to display without the side/top navigations.
3. **Missing Auth State and Contexts**:
   - There are currently no authentication hooks, context providers, or services in `src/context/` or `src/services/`.
   - The user data inside `Topbar` (lines 68-69) and the completion stats inside `Dashboard` (line 89) are hardcoded:
     ```jsx
     <span className="user-name">Alex Johnson</span>
     <span className="user-role">Student</span>
     ```
4. **Branding Variables** (`src/index.css` line 1-14):
   ```css
   :root {
     --primary-green: #2db06f;
     --primary-green-light: #e6f6ef;
     --text-dark: #1e293b;
     --text-gray: #64748b;
     --bg-gray: #f8fafc;
     --bg-white: #ffffff;
     --border-color: #f1f5f9;
     ...
   }
   ```
   The styling relies on variables with green/white premium theme properties. No forms/auth styles exist in the stylesheet.

---

## 2. Logic Chain
Based on the observations:
1. **Decoupling Public/Private Layouts**: Since `/login` and `/register` pages do not feature the Dashboard sidebar and topbar, we must restructure the routing inside `src/App.jsx` using React Router v7 nested routing layouts. A Layout wrapper component with `<Outlet />` will wrap protected dashboard routes.
2. **Auth Management with Persisted Mock State**: For user session persistence across page reloads, a context provider `AuthContext` coupled with `localStorage` is ideal. This is safer, mirrors actual server behavior, and allows testing the profile changes dynamically.
3. **Component Restructuring**:
   - `Sidebar` needs to use `NavLink` to dynamically style the active state and handle the `logout` action.
   - `Topbar` needs to display user details fetched from `useAuth` rather than hardcoded text.
4. **Unified Styling**: To support form elements, validation blocks, inputs, and the profile configuration layout, new CSS styles using existing CSS variables must be appended to `src/index.css`.

---

## 3. Caveats
- **Mock State Reset**: Clearing the browser storage or incognito mode will reset the user database back to the seed account details (`alex@educonsultant.com` / `password123`).
- **File Upload Limitation**: Profile image custom uploads are not implemented via backend multi-part forms. Instead, user profile picture change will select from Unsplash presets or clear it, fitting the prototype scope.

---

## 4. Conclusion
We need to create/modify 8 files to achieve Milestone 1. The details of these proposed changes are provided below:

### 4.1. Create `src/services/api.js` (Mock API Service)
```javascript
const mockDelay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms));

const SEED_USERS = [
  {
    name: "Alex Johnson",
    email: "alex@educonsultant.com",
    password: "password123",
    degreePreference: "Master of Computer Science",
    ieltsScore: "7.5",
    profileImg: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=100"
  }
];

const getUsers = () => {
  const users = localStorage.getItem("mock_users");
  if (!users) {
    localStorage.setItem("mock_users", JSON.stringify(SEED_USERS));
    return SEED_USERS;
  }
  return JSON.parse(users);
};

export const apiLogin = async (email, password) => {
  await mockDelay();
  const users = getUsers();
  const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());
  if (!user || user.password !== password) {
    throw new Error("Invalid email or password");
  }
  const { password: _, ...userWithoutPassword } = user;
  return userWithoutPassword;
};

export const apiRegister = async (userData) => {
  await mockDelay();
  const users = getUsers();
  const exists = users.some(u => u.email.toLowerCase() === userData.email.toLowerCase());
  if (exists) {
    throw new Error("Email already registered");
  }
  const newUser = {
    name: userData.name,
    email: userData.email,
    password: userData.password,
    degreePreference: "",
    ieltsScore: "",
    profileImg: ""
  };
  users.push(newUser);
  localStorage.setItem("mock_users", JSON.stringify(users));
  
  const { password: _, ...userWithoutPassword } = newUser;
  return userWithoutPassword;
};

export const apiUpdateProfile = async (email, updatedData) => {
  await mockDelay();
  const users = getUsers();
  const userIndex = users.findIndex(u => u.email.toLowerCase() === email.toLowerCase());
  if (userIndex === -1) {
    throw new Error("User not found");
  }
  users[userIndex] = {
    ...users[userIndex],
    ...updatedData
  };
  localStorage.setItem("mock_users", JSON.stringify(users));
  const { password: _, ...userWithoutPassword } = users[userIndex];
  return userWithoutPassword;
};
```

### 4.2. Create `src/context/AuthContext.jsx` (Auth Context Provider & useAuth Hook)
```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiLogin, apiRegister, apiUpdateProfile } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedUser = localStorage.getItem("current_user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const userData = await apiLogin(email, password);
      setUser(userData);
      localStorage.setItem("current_user", JSON.stringify(userData));
      return userData;
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    try {
      const newUser = await apiRegister(userData);
      setUser(newUser);
      localStorage.setItem("current_user", JSON.stringify(newUser));
      return newUser;
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("current_user");
  };

  const updateProfile = async (updatedData) => {
    if (!user) throw new Error("Not authenticated");
    setLoading(true);
    try {
      const updatedUser = await apiUpdateProfile(user.email, updatedData);
      setUser(updatedUser);
      localStorage.setItem("current_user", JSON.stringify(updatedUser));
      return updatedUser;
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, loading, login, register, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
```

### 4.3. Create `src/components/RouteGuards.jsx` (Guarded Routes)
```javascript
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return <div className="loading-container"><div className="spinner"></div></div>;
  }
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

export const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return <div className="loading-container"><div className="spinner"></div></div>;
  }
  return isAuthenticated ? <Navigate to="/" replace /> : children;
};
```

### 4.4. Create `src/pages/Login.jsx` (Login Screen)
```javascript
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { GraduationCap, Mail, Lock, AlertCircle } from 'lucide-react';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors = {};
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Invalid email address';
    }
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError('');
    if (!validate()) return;
    setIsSubmitting(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setApiError(err.message || 'Failed to login');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFillDemo = () => {
    setEmail('alex@educonsultant.com');
    setPassword('password123');
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <div className="brand" style={{ justifyContent: 'center', marginBottom: '1rem' }}>
            <GraduationCap className="brand-icon" size={32} />
            EduConsultant
          </div>
          <h2>Welcome Back</h2>
          <p>Login to manage your student application portal</p>
        </div>

        {apiError && (
          <div className="auth-error-box">
            <AlertCircle size={18} />
            <span>{apiError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={18} />
              <input
                type="email"
                className={`form-control ${errors.email ? 'has-error' : ''}`}
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={18} />
              <input
                type="password"
                className={`form-control ${errors.password ? 'has-error' : ''}`}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            {errors.password && <span className="error-message">{errors.password}</span>}
          </div>

          <button type="submit" className="btn-submit" disabled={isSubmitting}>
            {isSubmitting ? 'Logging in...' : 'Sign In'}
          </button>
        </form>

        <button type="button" className="btn-demo" onClick={handleFillDemo}>
          Autofill Demo Account
        </button>

        <div className="auth-footer">
          Don't have an account? <Link to="/register">Register here</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
```

### 4.5. Create `src/pages/Register.jsx` (Registration Screen)
```javascript
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { GraduationCap, User, Mail, Lock, AlertCircle } from 'lucide-react';

const Register = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors = {};
    if (!name.trim()) {
      newErrors.name = 'Full name is required';
    } else if (name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Invalid email address';
    }
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError('');
    if (!validate()) return;
    setIsSubmitting(true);
    try {
      await register({ name, email, password });
      navigate('/');
    } catch (err) {
      setApiError(err.message || 'Failed to register');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <div className="brand" style={{ justifyContent: 'center', marginBottom: '1rem' }}>
            <GraduationCap className="brand-icon" size={32} />
            EduConsultant
          </div>
          <h2>Create Account</h2>
          <p>Get started with your scholarship applications</p>
        </div>

        {apiError && (
          <div className="auth-error-box">
            <AlertCircle size={18} />
            <span>{apiError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <div className="input-wrapper">
              <User className="input-icon" size={18} />
              <input
                type="text"
                className={`form-control ${errors.name ? 'has-error' : ''}`}
                placeholder="Alex Johnson"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            {errors.name && <span className="error-message">{errors.name}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={18} />
              <input
                type="email"
                className={`form-control ${errors.email ? 'has-error' : ''}`}
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={18} />
              <input
                type="password"
                className={`form-control ${errors.password ? 'has-error' : ''}`}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            {errors.password && <span className="error-message">{errors.password}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={18} />
              <input
                type="password"
                className={`form-control ${errors.confirmPassword ? 'has-error' : ''}`}
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
            {errors.confirmPassword && <span className="error-message">{errors.confirmPassword}</span>}
          </div>

          <button type="submit" className="btn-submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Login here</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
```

### 4.6. Create `src/pages/Profile.jsx` (Profile Customizer)
```javascript
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Mail, GraduationCap, Award, Check, AlertCircle } from 'lucide-react';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [degreePreference, setDegreePreference] = useState(user?.degreePreference || '');
  const [ieltsScore, setIeltsScore] = useState(user?.ieltsScore || '');
  const [profileImg, setProfileImg] = useState(user?.profileImg || '');
  
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [apiError, setApiError] = useState('');

  const validate = () => {
    const newErrors = {};
    if (!name.trim()) {
      newErrors.name = 'Full name is required';
    }
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Invalid email address';
    }
    if (ieltsScore) {
      const score = parseFloat(ieltsScore);
      if (isNaN(score) || score < 0 || score > 9 || (score * 10) % 5 !== 0) {
        newErrors.ieltsScore = 'IELTS score must be between 0 and 9 in steps of 0.5';
      }
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccessMsg('');
    setApiError('');
    if (!validate()) return;
    setIsSubmitting(true);
    try {
      await updateProfile({
        name,
        email,
        degreePreference,
        ieltsScore: ieltsScore ? parseFloat(ieltsScore).toString() : '',
        profileImg
      });
      setSuccessMsg('Profile updated successfully!');
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setApiError(err.message || 'Failed to update profile');
    } finally {
      setIsSubmitting(false);
    }
  };

  const AVATAR_PRESETS = [
    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=100',
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=100',
    'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=100',
    'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=100'
  ];

  return (
    <div className="profile-container">
      <div className="page-header">
        <h1 className="page-title">My Profile</h1>
        <p className="page-subtitle">Manage your personal details and academic credentials.</p>
      </div>

      <div className="profile-grid">
        <div className="profile-card">
          <form onSubmit={handleSubmit}>
            {successMsg && (
              <div className="profile-success-box">
                <Check size={18} />
                <span>{successMsg}</span>
              </div>
            )}
            {apiError && (
              <div className="profile-error-box">
                <AlertCircle size={18} />
                <span>{apiError}</span>
              </div>
            )}

            <div className="profile-avatar-section">
              <div className="profile-avatar-large">
                {profileImg ? (
                  <img src={profileImg} alt={name} />
                ) : (
                  <User size={40} />
                )}
              </div>
              <div className="avatar-presets-wrapper">
                <span className="form-label" style={{ marginBottom: '0.5rem' }}>Select Avatar Preset</span>
                <div className="avatar-presets">
                  {AVATAR_PRESETS.map((url, idx) => (
                    <button
                      key={idx}
                      type="button"
                      className={`preset-btn ${profileImg === url ? 'active' : ''}`}
                      onClick={() => setProfileImg(url)}
                    >
                      <img src={url} alt={`Preset ${idx + 1}`} />
                    </button>
                  ))}
                  <button
                    type="button"
                    className={`preset-btn-clear ${!profileImg ? 'active' : ''}`}
                    onClick={() => setProfileImg('')}
                  >
                    Clear
                  </button>
                </div>
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <div className="input-wrapper">
                  <User className="input-icon" size={18} />
                  <input
                    type="text"
                    className={`form-control ${errors.name ? 'has-error' : ''}`}
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>
                {errors.name && <span className="error-message">{errors.name}</span>}
              </div>

              <div className="form-group">
                <label className="form-label">Email Address</label>
                <div className="input-wrapper">
                  <Mail className="input-icon" size={18} />
                  <input
                    type="email"
                    className={`form-control ${errors.email ? 'has-error' : ''}`}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                {errors.email && <span className="error-message">{errors.email}</span>}
              </div>

              <div className="form-group">
                <label className="form-label">Degree Preference</label>
                <div className="input-wrapper">
                  <GraduationCap className="input-icon" size={18} />
                  <select
                    className="form-control"
                    value={degreePreference}
                    onChange={(e) => setDegreePreference(e.target.value)}
                  >
                    <option value="">Select a Preference</option>
                    <option value="Bachelor of Computer Science">Bachelor of Computer Science</option>
                    <option value="Bachelor of Business Administration">Bachelor of Business Administration</option>
                    <option value="Master of Computer Science">Master of Computer Science</option>
                    <option value="Master of Business Administration">Master of Business Administration</option>
                    <option value="Ph.D. in Data Science">Ph.D. in Data Science</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">IELTS Band Score</label>
                <div className="input-wrapper">
                  <Award className="input-icon" size={18} />
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    max="9"
                    className={`form-control ${errors.ieltsScore ? 'has-error' : ''}`}
                    placeholder="e.g. 7.5"
                    value={ieltsScore}
                    onChange={(e) => setIeltsScore(e.target.value)}
                  />
                </div>
                {errors.ieltsScore && <span className="error-message">{errors.ieltsScore}</span>}
              </div>
            </div>

            <button type="submit" className="btn-submit" style={{ marginTop: '1.5rem', width: 'auto', padding: '0.75rem 2rem' }} disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile;
```

### 4.7. Modify `src/App.jsx` (Restructured Routes & Integrated Layout)
```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, NavLink, useLocation, useNavigate, Outlet } from 'react-router-dom';
import { 
  GraduationCap, LayoutDashboard, Search, FileText, 
  Building, Bell, Mail, Settings, User, LogOut,
  TrendingUp, CheckCircle, Clock
} from 'lucide-react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute, PublicRoute } from './components/RouteGuards';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import './index.css';

const Sidebar = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
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
          <div className="nav-item">
            <Settings size={20} />
            Settings
          </div>
        </li>
        <li>
          <button onClick={handleLogout} className="nav-item btn-logout-link" style={{ background: 'none', border: 'none', width: '100%', textAlign: 'left', font: 'inherit', cursor: 'pointer' }}>
            <LogOut size={20} />
            Logout
          </button>
        </li>
      </ul>
    </div>
  );
};

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
          <div className="avatar-wrapper">
            {user?.profileImg ? (
              <img src={user.profileImg} alt={user.name} className="avatar" />
            ) : (
              <div className="icon-wrapper" style={{ width: '36px', height: '36px' }}>
                <User size={20} />
              </div>
            )}
          </div>
          <div className="user-info">
            <span className="user-name">{user?.name || 'Guest User'}</span>
            <span className="user-role">Student</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const PlaceholderPage = ({ title }) => (
  <div className="profile-container">
    <div className="page-header">
      <h1 className="page-title">{title}</h1>
      <p className="page-subtitle">This page is scheduled for a future milestone.</p>
    </div>
    <div className="profile-card">
      <p style={{ color: 'var(--text-gray)' }}>The {title.toLowerCase()} workflow is currently under construction.</p>
    </div>
  </div>
);

const Dashboard = () => {
  const { user } = useAuth();
  const profileCompletePercent = user?.degreePreference && user?.ieltsScore ? 100 : user?.degreePreference || user?.ieltsScore ? 90 : 80;

  return (
    <div className="dashboard-content">
      <div className="page-header">
        <h1 className="page-title">Student Dashboard</h1>
        <p className="page-subtitle">Welcome back, {user?.name || 'Student'}! Track your applications and explore opportunities.</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            Profile Completion
            <div className="icon-wrapper"><User size={18} /></div>
          </div>
          <div className="stat-value">{profileCompletePercent}%</div>
          <div className="stat-trend positive">
            <TrendingUp size={14} /> Profile update synced
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
          <div className="stat-value">{user?.ieltsScore ? '5/5' : '4/5'}</div>
          <div className="stat-trend">{user?.ieltsScore ? 'All verified' : 'Pending IELTS score'}</div>
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
                <div style={{ fontSize: '0.75rem', color: 'var(--text-gray)' }}>{user?.ieltsScore ? 'Completed' : 'Due in 2 days'}</div>
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

const DashboardLayout = () => {
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

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

          <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/scholarships" element={<PlaceholderPage title="Scholarships Discovery" />} />
            <Route path="/universities" element={<PlaceholderPage title="University Directory" />} />
            <Route path="/applications" element={<PlaceholderPage title="My Applications" />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
```

### 4.8. Modify `src/index.css` (Append new CSS blocks)
Appended styles at the end of the file:
```css

/* ==========================================================================
   Milestone 1 Additions: Auth Pages, Forms, and Profile Styling
   ========================================================================= */

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
  border: 1px solid var(--border-color);
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.auth-header {
  text-align: center;
  margin-bottom: 0.5rem;
}

.auth-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-dark);
  margin-bottom: 0.25rem;
}

.auth-header p {
  color: var(--text-gray);
  font-size: 0.875rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-dark);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 0.875rem;
  color: var(--text-gray);
  pointer-events: none;
}

.form-control {
  width: 100%;
  padding: 0.625rem 0.875rem 0.625rem 2.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  background-color: var(--bg-white);
  color: var(--text-dark);
  outline: none;
  transition: all 0.2s ease-in-out;
}

select.form-control {
  padding-left: 2.5rem;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.875rem center;
  background-size: 1rem;
}

.form-control:focus {
  border-color: var(--primary-green);
  box-shadow: 0 0 0 3px var(--primary-green-light);
}

.form-control.has-error {
  border-color: #ef4444;
}

.form-control.has-error:focus {
  box-shadow: 0 0 0 3px #fee2e2;
}

.error-message {
  font-size: 0.75rem;
  color: #ef4444;
  margin-top: 0.125rem;
}

.auth-error-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.875rem;
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  border-radius: var(--radius-md);
  font-size: 0.8125rem;
}

.btn-submit {
  width: 100%;
  padding: 0.625rem 0.875rem;
  background-color: var(--primary-green);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}

.btn-submit:hover:not(:disabled) {
  background-color: #24925b;
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-demo {
  background: none;
  border: 1px dashed var(--primary-green);
  color: var(--primary-green);
  padding: 0.5rem;
  border-radius: var(--radius-md);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-demo:hover {
  background-color: var(--primary-green-light);
}

.auth-footer {
  text-align: center;
  font-size: 0.8125rem;
  color: var(--text-gray);
}

.auth-footer a {
  color: var(--primary-green);
  text-decoration: none;
  font-weight: 600;
}

.auth-footer a:hover {
  text-decoration: underline;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  width: 100%;
  background-color: var(--bg-gray);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-green);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.profile-container {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  max-width: 800px;
}

.profile-card {
  background-color: var(--bg-white);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.profile-success-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.875rem;
  background-color: var(--primary-green-light);
  border: 1px solid #d1fae5;
  color: #065f46;
  border-radius: var(--radius-md);
  font-size: 0.8125rem;
  margin-bottom: 1.25rem;
}

.profile-error-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.875rem;
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  border-radius: var(--radius-md);
  font-size: 0.8125rem;
  margin-bottom: 1.25rem;
}

.profile-avatar-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding-bottom: 1.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.profile-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  background-color: var(--primary-green-light);
  color: var(--primary-green);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--border-color);
}

.profile-avatar-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-presets-wrapper {
  display: flex;
  flex-direction: column;
}

.avatar-presets {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preset-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid transparent;
  cursor: pointer;
  padding: 0;
  transition: all 0.2s;
  background: none;
}

.preset-btn img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preset-btn:hover, .preset-btn.active {
  border-color: var(--primary-green);
  transform: scale(1.05);
}

.preset-btn-clear {
  background: none;
  border: 1px solid var(--text-gray);
  color: var(--text-gray);
  padding: 4px 8px;
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.preset-btn-clear:hover, .preset-btn-clear.active {
  border-color: var(--text-dark);
  color: var(--text-dark);
  background-color: var(--bg-gray);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem 1.5rem;
}

.btn-logout-link:hover {
  background-color: #fee2e2 !important;
  color: #ef4444 !important;
}

.avatar-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-wrapper img.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## 5. Verification Method
To independently verify the implementation, execute the following procedures:
1. **Lints & Build Testing**:
   - Run `npm run lint` inside the frontend directory and confirm no syntax/compilation issues are reported by `oxlint`.
   - Run `npm run build` and check for clean bundle generation without rollup errors.
2. **Access Guards Validation**:
   - Start the Vite local server: `npm run dev`.
   - Try navigating to `http://localhost:5173/` or `http://localhost:5173/profile`. Confirm that the app immediately redirects to `/login` due to missing token/user data in local storage.
   - Enter `http://localhost:5173/login`. Verify the auth card is displayed centered and without side/top nav layouts.
3. **Session Mock Verification**:
   - On `/login`, hit the dashed "Autofill Demo Account" button, then submit the form. Verify successful redirect to the dashboard page (`/`).
   - Check if Sidebar active element styles correctly highlight the "Dashboard" nav item.
   - Navigate to `/profile`. Change details (e.g. IELTS to `8.5`, choose another avatar preset).
   - Press "Save Changes". Confirm the toast alerts success, and the topbar avatar immediately updates.
   - Refresh the page manually. Inspect that all changes (name, score, avatar) remain persisted.
   - Click "Logout" at the bottom of the sidebar. Confirm immediate redirect back to `/login` and verify that typing `/profile` redirects to `/login` again.
