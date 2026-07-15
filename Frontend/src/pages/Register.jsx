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
            {errors.name && <span className="field-error error-message">{errors.name}</span>}
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
            {errors.email && <span className="field-error error-message">{errors.email}</span>}
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
                <option value="Masters">Masters</option>
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
            {errors.password && <span className="field-error error-message">{errors.password}</span>}
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
            {errors.confirmPassword && <span className="field-error error-message">{errors.confirmPassword}</span>}
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
