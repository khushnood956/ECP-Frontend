import React from 'react';
import { useAppContext } from '../context/AppContext';
import { FileText } from 'lucide-react';
import { Link } from 'react-router-dom';

const Applications = () => {
  const { applications, searchQuery } = useAppContext();

  const filtered = applications.filter(a => 
    a.university.toLowerCase().includes(searchQuery.toLowerCase()) || 
    a.program.toLowerCase().includes(searchQuery.toLowerCase())
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
              {filtered.map(a => (
                <tr key={a.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '1rem 0' }}>{a.university}</td>
                  <td style={{ padding: '1rem 0' }}>{a.program}</td>
                  <td style={{ padding: '1rem 0' }}>{a.intake}</td>
                  <td style={{ padding: '1rem 0' }}>{a.date}</td>
                  <td style={{ padding: '1rem 0' }}>
                    <span style={{ 
                      color: a.status === 'Submitted' ? 'var(--primary-green)' : '#eab308', 
                      background: a.status === 'Submitted' ? 'var(--primary-green-light)' : '#fef9c3', 
                      padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem' 
                    }}>
                      {a.status}
                    </span>
                  </td>
                  <td style={{ padding: '1rem 0' }}>
                    <Link to={`/applications/${a.id}`} style={{ color: 'var(--primary-green)', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 500 }}>View Details</Link>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && <tr><td colSpan="6" style={{ padding: '1rem 0' }}>No applications found.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Applications;
