import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAgencyLeads } from '../../hooks/useLeads';
import { Calendar, User, BookOpen, Clock, ArrowRight } from 'lucide-react';
import { 
  formatDate, 
  getStatusBadgeClass, 
  getStatusLabel, 
  truncateId 
} from '../../utils/formatters';

const LeadsPage = () => {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState('');

  const { data: leads, isLoading, error } = useAgencyLeads(
    statusFilter ? { status: statusFilter } : undefined
  );

  return (
    <div className="dashboard-content">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 className="page-title">Lead Management</h1>
          <p className="page-subtitle">Track and process scholarship applications submitted by students.</p>
        </div>

        {/* Filter Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <label htmlFor="status-filter" style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-dark)' }}>
            Status:
          </label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)',
              backgroundColor: 'var(--bg-white)',
              color: 'var(--text-dark)',
              fontSize: '0.875rem',
              fontWeight: 500,
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            <option value="">All Statuses</option>
            <option value="submitted">Submitted</option>
            <option value="under_review">Under Review</option>
            <option value="accepted">Accepted</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      {isLoading && (
        <div className="widgets-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {[...Array(6)].map((_, i) => (
            <div key={i} className="widget" style={{ minHeight: '220px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <div style={{ height: '20px', width: '80px', backgroundColor: 'var(--bg-gray)', borderRadius: '4px' }}></div>
                <div style={{ height: '16px', width: '60px', backgroundColor: 'var(--bg-gray)', borderRadius: '4px' }}></div>
              </div>
              <div style={{ height: '24px', width: '70%', backgroundColor: 'var(--bg-gray)', borderRadius: '4px' }}></div>
              <div style={{ height: '40px', width: '100%', backgroundColor: 'var(--bg-gray)', borderRadius: '4px' }}></div>
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
          Failed to load leads. Please check your connection and try again.
        </div>
      )}

      {!isLoading && !error && (!leads || leads.length === 0) && (
        <div className="widget" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem', textAlign: 'center' }}>
          <Clock className="text-gray" size={48} style={{ marginBottom: '1rem', color: 'var(--text-gray)' }} />
          <h3 className="widget-title" style={{ marginBottom: '0.5rem' }}>No Leads Found</h3>
          <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem', maxWidth: '320px' }}>
            There are currently no leads matching your selection. New student applications will appear here.
          </p>
        </div>
      )}

      {!isLoading && !error && leads && leads.length > 0 && (
        <div className="widgets-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {leads.map((lead) => (
            <div key={lead.id} className="widget" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '250px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    fontSize: '0.75rem', 
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }} className={getStatusBadgeClass(lead.status)}>
                    {getStatusLabel(lead.status)}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-gray)' }}>
                    Applied: {formatDate(lead.created_at)}
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  <h4 style={{ fontSize: '1.125rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-dark)' }}>
                    <BookOpen size={18} style={{ color: 'var(--text-gray)' }} />
                    Scholarship App
                  </h4>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', fontFamily: 'monospace' }}>
                    ID: {truncateId(lead.id)}
                  </p>
                </div>

                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-gray)' }}>
                    <User size={16} />
                    <span style={{ color: 'var(--text-dark)', fontWeight: 500 }}>Student ID:</span>
                    <span style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>{truncateId(lead.student_id)}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-gray)' }}>
                    <Calendar size={16} />
                    <span style={{ color: 'var(--text-dark)', fontWeight: 500 }}>Follow-up:</span>
                    <span>{formatDate(lead.follow_up_date, 'Not scheduled')}</span>
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '1.5rem' }}>
                <button
                  onClick={() => navigate(`/agency/leads/${lead.id}`)}
                  className="btn btn-primary btn-block"
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                >
                  View Details
                  <ArrowRight size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LeadsPage;
