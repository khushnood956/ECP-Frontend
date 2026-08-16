import React from 'react';
import { useCurrentAgency } from '../../hooks/useCurrentAgency';
import { useNavigate } from 'react-router-dom';
import { 
  getStatusBadgeClass, 
  getStatusLabel, 
  formatNullable 
} from '../../utils/formatters';

const AgencyProfilePage = () => {
  const { data: agency, isLoading, isError, error } = useCurrentAgency();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="dashboard-content">
        <div style={{ height: '36px', width: '200px', backgroundColor: 'var(--bg-gray)', borderRadius: '4px', marginBottom: '1.5rem' }}></div>
        <div className="widget" style={{ height: '300px' }}></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="dashboard-content">
        <div className="alert alert-error">
          {error instanceof Error ? error.message : 'An unexpected error occurred.'}
        </div>
      </div>
    );
  }

  if (!agency) {
    return (
      <div className="dashboard-content">
        <div className="widget" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '3rem', textAlign: 'center' }}>
          <h3 className="widget-title" style={{ marginBottom: '0.5rem' }}>No Agency Profile</h3>
          <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>You haven't created your agency profile yet.</p>
          <button className="btn btn-primary" onClick={() => navigate('/agency/profile/create')}>Create Profile</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-content">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 className="page-title">Agency Profile</h1>
          <p className="page-subtitle">View and manage your consulting agency profile details.</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/agency/profile/edit')}>Edit Profile</button>
      </div>

      <div className="widget" style={{ padding: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '2rem', marginBottom: '2rem' }}>
          {agency.logo_url ? (
            <img 
              src={agency.logo_url} 
              alt="Logo" 
              style={{ width: '80px', height: '80px', borderRadius: '50%', objectFit: 'cover', border: '3px solid var(--primary-green-light)' }} 
            />
          ) : (
            <div style={{ width: '80px', height: '80px', borderRadius: '50%', backgroundColor: 'var(--primary-green-light)', display: 'flex', justifyContent: 'center', alignItems: 'center', color: 'var(--primary-green)', fontSize: '1.5rem', fontWeight: 700 }}>
              {agency.agency_name.charAt(0).toUpperCase()}
            </div>
          )}
          
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-dark)', marginBottom: '0.5rem' }}>{agency.agency_name}</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span style={{ 
                padding: '4px 8px', 
                borderRadius: '4px', 
                fontSize: '0.75rem', 
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }} className={getStatusBadgeClass(agency.verification_status)}>
                {getStatusLabel(agency.verification_status)}
              </span>
              {agency.registration_number && (
                <span style={{ fontSize: '0.875rem', color: 'var(--text-gray)' }}>Reg No: {agency.registration_number}</span>
              )}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {agency.description && (
            <div>
              <h3 className="widget-title" style={{ marginBottom: '0.75rem', fontSize: '1.125rem' }}>About Us</h3>
              <p style={{ color: 'var(--text-dark)', lineHeight: 1.6, fontSize: '0.925rem' }}>{agency.description}</p>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '3rem', borderTop: '1px solid var(--border-color)', paddingTop: '2rem' }}>
            <div>
              <h3 className="widget-title" style={{ marginBottom: '1rem', fontSize: '1rem' }}>Contact Information</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem' }}>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <span style={{ color: 'var(--text-gray)', width: '80px', flexShrink: 0 }}>Email:</span>
                  <span style={{ color: 'var(--text-dark)', fontWeight: 500 }}>{formatNullable(agency.email)}</span>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <span style={{ color: 'var(--text-gray)', width: '80px', flexShrink: 0 }}>Phone:</span>
                  <span style={{ color: 'var(--text-dark)', fontWeight: 500 }}>{formatNullable(agency.phone)}</span>
                </div>
                {agency.website && (
                  <div style={{ display: 'flex', gap: '1rem' }}>
                    <span style={{ color: 'var(--text-gray)', width: '80px', flexShrink: 0 }}>Website:</span>
                    <a href={agency.website} target="_blank" rel="noreferrer" style={{ color: 'var(--primary-green)', fontWeight: 500, textDecoration: 'none' }}>
                      {agency.website}
                    </a>
                  </div>
                )}
              </div>
            </div>
            
            <div>
              <h3 className="widget-title" style={{ marginBottom: '1rem', fontSize: '1rem' }}>Location</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem' }}>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <span style={{ color: 'var(--text-gray)', width: '80px', flexShrink: 0 }}>Country:</span>
                  <span style={{ color: 'var(--text-dark)', fontWeight: 500 }}>{formatNullable(agency.country)}</span>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <span style={{ color: 'var(--text-gray)', width: '80px', flexShrink: 0 }}>City:</span>
                  <span style={{ color: 'var(--text-dark)', fontWeight: 500 }}>{formatNullable(agency.city)}</span>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <span style={{ color: 'var(--text-gray)', width: '80px', flexShrink: 0 }}>Address:</span>
                  <span style={{ color: 'var(--text-dark)', fontWeight: 500 }}>{formatNullable(agency.address)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgencyProfilePage;
