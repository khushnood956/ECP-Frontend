import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAgencyScholarships } from '../../hooks/useScholarships';
import { Calendar, Building, GraduationCap, Plus, Clock, FileText, ArrowRight } from 'lucide-react';
import { formatDate, getStatusBadgeClass, formatCurrency } from '../../utils/formatters';

const ScholarshipsListPage = () => {
  const navigate = useNavigate();
  const { data: scholarships, isLoading, error } = useAgencyScholarships();

  return (
    <div className="dashboard-content">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 className="page-title">Scholarships</h1>
          <p className="page-subtitle">Manage the scholarships offered by your agency.</p>
        </div>
        <button 
          onClick={() => navigate('/agency/scholarships/new')} 
          className="btn btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <Plus size={18} />
          Create Scholarship
        </button>
      </div>

      {isLoading && (
        <div className="widgets-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {[...Array(3)].map((_, i) => (
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
          Failed to load scholarships. Please try again later.
        </div>
      )}

      {!isLoading && !error && (!scholarships || scholarships.length === 0) && (
        <div className="widget" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem', textAlign: 'center' }}>
          <GraduationCap className="text-gray" size={48} style={{ marginBottom: '1rem', color: 'var(--text-gray)' }} />
          <h3 className="widget-title" style={{ marginBottom: '0.5rem' }}>No Scholarships Found</h3>
          <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem', maxWidth: '360px', marginBottom: '1.5rem' }}>
            You haven't listed any scholarships yet. Create your first scholarship program to receive student lead applications.
          </p>
          <button onClick={() => navigate('/agency/scholarships/new')} className="btn btn-primary">
            Create First Scholarship
          </button>
        </div>
      )}

      {!isLoading && !error && scholarships && scholarships.length > 0 && (
        <div className="widgets-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1.5rem' }}>
          {scholarships.map((s) => (
            <div key={s.id} className="widget" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '260px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    fontSize: '0.75rem', 
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }} className={s.is_active ? 'bg-green-100 text-green-800 border-green-200' : 'bg-gray-100 text-gray-800 border-gray-200'}>
                    {s.is_active ? 'Published' : 'Draft'}
                  </span>
                  <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--primary-green)' }}>
                    {formatCurrency(s.amount, s.currency, 'Funding Available')}
                  </span>
                </div>

                <div>
                  <h4 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-dark)', marginBottom: '0.25rem', lineClamp: 2 }}>
                    {s.title}
                  </h4>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Building size={16} />
                    {s.university || 'Various Universities'}
                  </p>
                </div>

                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-gray)' }}>
                    <GraduationCap size={16} />
                    <span style={{ color: 'var(--text-dark)', fontWeight: 500 }}>Degree:</span>
                    <span style={{ textTransform: 'capitalize' }}>{s.degree_level.replace('_', ' ')}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-gray)' }}>
                    <Calendar size={16} />
                    <span style={{ color: 'var(--text-dark)', fontWeight: 500 }}>Deadline:</span>
                    <span>{formatDate(s.deadline, 'No deadline')}</span>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                <button
                  onClick={() => navigate(`/agency/scholarships/${s.id}`)}
                  className="btn btn-outline"
                  style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                >
                  View details
                </button>
                <button
                  onClick={() => navigate(`/agency/scholarships/${s.id}/edit`)}
                  className="btn btn-primary"
                  style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                >
                  Edit Program
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ScholarshipsListPage;
