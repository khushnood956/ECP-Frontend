import React from 'react';
import { useAppContext } from '../context/AppContext';
import { useStudentLeads } from '../hooks/useLeads';
import { Link } from 'react-router-dom';

const mapStatus = (status) => {
  const mapping = {
    'submitted': 'Submitted',
    'under_review': 'In Review',
    'accepted': 'Accepted',
    'rejected': 'Rejected'
  };
  return mapping[status] || status;
};

const getStatusStyles = (status) => {
  switch (status) {
    case 'Submitted':
      return { color: 'var(--primary-green)', background: 'var(--primary-green-light)' };
    case 'In Review':
      return { color: '#eab308', background: '#fef9c3' };
    case 'Accepted':
      return { color: 'var(--primary-green)', background: 'var(--primary-green-light)' };
    case 'Rejected':
      return { color: '#ef4444', background: '#fee2e2' };
    default:
      return { color: 'var(--text-gray)', background: 'var(--bg-gray)' };
  }
};

const Applications = () => {
  const { searchQuery } = useAppContext();
  const { data: leads, isLoading, error } = useStudentLeads();

  if (isLoading) {
    return (
      <div className="dashboard-content">
        <div className="page-header">
          <h1 className="page-title">Applications</h1>
          <p className="page-subtitle">Loading your applications...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-content">
        <div className="page-header">
          <h1 className="page-title">Applications</h1>
          <p className="page-subtitle" style={{ color: '#ef4444' }}>Failed to load applications. Please try again later.</p>
        </div>
      </div>
    );
  }

  const filtered = (leads || []).filter(a => 
    (a.scholarship_university || '').toLowerCase().includes(searchQuery.toLowerCase()) || 
    (a.scholarship_title || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="dashboard-content">
      <div className="page-header">
        <h1 className="page-title">Applications</h1>
        <p className="page-subtitle">Track your application statuses.</p>
      </div>
      
      <div className="widgets-grid" style={{ gridTemplateColumns: '1fr' }}>
        <div className="widget">
          <div className="widget-header">
            <h3 className="widget-title">My Applications</h3>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ color: 'var(--text-gray)', fontSize: '0.875rem', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ paddingBottom: '1rem' }}>University</th>
                <th style={{ paddingBottom: '1rem' }}>Program</th>
                <th style={{ paddingBottom: '1rem' }}>Intake</th>
                <th style={{ paddingBottom: '1rem' }}>Date Applied</th>
                <th style={{ paddingBottom: '1rem' }}>Status</th>
                <th style={{ paddingBottom: '1rem' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(a => {
                const uiStatus = mapStatus(a.status);
                const styles = getStatusStyles(uiStatus);
                const dateApplied = a.created_at ? a.created_at.split('T')[0] : '—';
                return (
                  <tr key={a.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '1rem 0' }}>{a.scholarship_university || '—'}</td>
                    <td style={{ padding: '1rem 0' }}>{a.scholarship_title || '—'}</td>
                    <td style={{ padding: '1rem 0' }}>—</td>
                    <td style={{ padding: '1rem 0' }}>{dateApplied}</td>
                    <td style={{ padding: '1rem 0' }}>
                      <span style={{ 
                        color: styles.color, 
                        background: styles.background, 
                        padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem' 
                      }}>
                        {uiStatus}
                      </span>
                    </td>
                    <td style={{ padding: '1rem 0' }}>
                      <Link to={`/applications/${a.id}`} style={{ color: 'var(--primary-green)', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 500 }}>View Details</Link>
                    </td>
                  </tr>
                );
              })}
              {filtered.length === 0 && <tr><td colSpan="6" style={{ padding: '1rem 0' }}>No applications found.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Applications;
