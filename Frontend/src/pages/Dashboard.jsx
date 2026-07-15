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
