import React from 'react';
import { Link } from 'react-router-dom';
import { useStudentLeads } from '../hooks/useLeads';
import { useStudentDocuments } from '../hooks/useDocuments';
import { useStudentBookmarks } from '../hooks/useBookmarks';
import { 
  User, Search, FileText, CheckCircle, Clock, TrendingUp
} from 'lucide-react';

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

const Dashboard = () => {
  const { data: leads, isLoading } = useStudentLeads();
  const { data: documents = [] } = useStudentDocuments();
  const { data: bookmarks = [] } = useStudentBookmarks();

  const savedScholarshipsCount = bookmarks.filter(b => b.bookmark_type === 'scholarship').length;
  const activeApplicationsCount = (leads || []).filter(a => a.status !== 'accepted' && a.status !== 'rejected').length;
  const verifiedDocsCount = documents.filter(d => d.verified).length;
  const totalDocsCount = documents.length;

  return (
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
          <div className="stat-value">{savedScholarshipsCount}</div>
          <div className="stat-trend">{savedScholarshipsCount > 0 ? 'Deadlines approaching' : 'Explore now'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-header">
            Active Applications
            <div className="icon-wrapper"><FileText size={18} /></div>
          </div>
          <div className="stat-value">{isLoading ? '...' : activeApplicationsCount}</div>
          <div className="stat-trend positive">Stay updated</div>
        </div>
        <div className="stat-card">
          <div className="stat-header">
            Documents Verified
            <div className="icon-wrapper"><CheckCircle size={18} /></div>
          </div>
          <div className="stat-value">{verifiedDocsCount}/{totalDocsCount || 1}</div>
          <div className="stat-trend">Manage your files</div>
        </div>
      </div>

      <div className="widgets-grid">
        <div className="widget">
          <div className="widget-header">
            <h3 className="widget-title">Recent Applications</h3>
            <Link to="/applications" style={{ color: 'var(--primary-green)', textDecoration: 'none', fontSize: '0.875rem' }}>View All →</Link>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ color: 'var(--text-gray)', fontSize: '0.875rem', borderBottom: '1px solid var(--border-color)' }}>
                  <th style={{ paddingBottom: '1rem', whiteSpace: 'nowrap' }}>University</th>
                  <th style={{ paddingBottom: '1rem', whiteSpace: 'nowrap' }}>Program</th>
                  <th style={{ paddingBottom: '1rem', whiteSpace: 'nowrap' }}>Intake</th>
                  <th style={{ paddingBottom: '1rem', whiteSpace: 'nowrap' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan="4" style={{ padding: '1rem 0' }}>Loading recent applications...</td>
                  </tr>
                ) : (
                  (leads || []).slice(0, 3).map(a => {
                    const uiStatus = mapStatus(a.status);
                    const styles = getStatusStyles(uiStatus);
                    return (
                      <tr key={a.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td style={{ padding: '1rem 0', whiteSpace: 'nowrap', paddingRight: '1rem' }}>{a.scholarship_university || '—'}</td>
                        <td style={{ padding: '1rem 0', whiteSpace: 'nowrap', paddingRight: '1rem' }}>{a.scholarship_title || '—'}</td>
                        <td style={{ padding: '1rem 0', whiteSpace: 'nowrap', paddingRight: '1rem' }}>—</td>
                        <td style={{ padding: '1rem 0', whiteSpace: 'nowrap' }}>
                          <span style={{ 
                            color: styles.color, 
                            background: styles.background, 
                            padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem' 
                          }}>
                            {uiStatus}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
                {!isLoading && (!leads || leads.length === 0) && (
                  <tr><td colSpan="4" style={{ padding: '1rem 0' }}>No applications yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
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
