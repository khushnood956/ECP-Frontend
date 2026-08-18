import React, { useState } from 'react';
import { useAgenciesByVerificationStatus, useVerifyAgency, useSuspendAgency, useAdminStats } from '../../hooks/useAdminAgencies';
import { ShieldCheck, ExternalLink, Mail, Phone, Globe, Building2, CheckCircle2, XCircle, TrendingUp, Users, GraduationCap, DollarSign, ListFilter } from 'lucide-react';
import EdutantLoader from '../../components/ui/EdutantLoader';

const AdminDashboard = () => {
  const [selectedStatus, setSelectedStatus] = useState('pending');
  const { data: agencies = [], isLoading, isError, error } = useAgenciesByVerificationStatus(selectedStatus);
  const { data: stats } = useAdminStats();
  const verifyMutation = useVerifyAgency();
  const suspendMutation = useSuspendAgency();
  const [selectedAgency, setSelectedAgency] = useState(null);

  const statusTabs = [
    { value: 'pending', label: 'Pending', count: stats?.pending_agencies ?? 0 },
    { value: 'verified', label: 'Verified', count: stats?.verified_agencies ?? 0 },
    { value: 'rejected', label: 'Rejected', count: stats?.suspended_agencies ?? 0 },
  ];

  const handleVerify = (agency) => {
    if (window.confirm(`Are you sure you want to verify "${agency.agency_name}"? This will allow them to post scholarships.`)) {
      verifyMutation.mutate(agency.id, {
        onSuccess: () => {
          setSelectedAgency(null);
          alert('Agency verified successfully.');
        },
        onError: (err) => {
          alert('Action failed: ' + (err.response?.data?.detail || err.message));
        }
      });
    }
  };

  const handleSuspend = (agency) => {
    if (window.confirm(`Are you sure you want to reject/suspend "${agency.agency_name}"?`)) {
      suspendMutation.mutate(agency.id, {
        onSuccess: () => {
          setSelectedAgency(null);
          alert('Agency status updated to rejected.');
        },
        onError: (err) => {
          alert('Action failed: ' + (err.response?.data?.detail || err.message));
        }
      });
    }
  };

  if (isLoading) {
    return (
      <div className="dashboard-content">
        <EdutantLoader variant="inline" message="Loading pending registrations..." />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="dashboard-content">
        <div className="page-header">
          <h1 className="page-title">Admin Operations</h1>
        </div>
        <div className="widget" style={{ color: '#ef4444', backgroundColor: '#fef2f2', border: '1px solid #fca5a5', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
          Failed to retrieve pending agencies: {error?.response?.data?.detail || error.message || 'Unknown error'}
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-content">
      <div className="page-header">
        <h1 className="page-title">Admin Dashboard</h1>
        <p className="page-subtitle">Review agency registrations, verify partners, and monitor account status across the platform.</p>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-header">
              <span>Total Students</span>
              <div className="icon-wrapper"><Users size={16} /></div>
            </div>
            <div className="stat-value">{stats.total_students || 0}</div>
            <div className="stat-trend positive"><TrendingUp size={12} /> Active users</div>
          </div>
          <div className="stat-card">
            <div className="stat-header">
              <span>Total Agencies</span>
              <div className="icon-wrapper"><Building2 size={16} /></div>
            </div>
            <div className="stat-value">{stats.total_agencies || 0}</div>
            <div className="stat-trend positive"><TrendingUp size={12} /> Partnered</div>
          </div>
          <div className="stat-card">
            <div className="stat-header">
              <span>Active Scholarships</span>
              <div className="icon-wrapper"><GraduationCap size={16} /></div>
            </div>
            <div className="stat-value">{stats.active_scholarships || 0}</div>
            <div className="stat-trend positive"><TrendingUp size={12} /> Available</div>
          </div>
          <div className="stat-card">
            <div className="stat-header">
              <span>Total Leads</span>
              <div className="icon-wrapper"><DollarSign size={16} /></div>
            </div>
            <div className="stat-value">{stats.total_leads || 0}</div>
            <div className="stat-trend positive"><TrendingUp size={12} /> Generated</div>
          </div>
        </div>
      )}

      <div className="widget" style={{ marginBottom: '1.5rem' }}>
        <div className="widget-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
          <h3 className="widget-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ListFilter size={18} /> Agency Status
          </h3>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {statusTabs.map((tab) => (
              <button
                key={tab.value}
                type="button"
                onClick={() => {
                  setSelectedStatus(tab.value);
                  setSelectedAgency(null);
                }}
                className="btn"
                style={{
                  border: selectedStatus === tab.value ? 'none' : '1px solid var(--border-color)',
                  backgroundColor: selectedStatus === tab.value ? 'var(--primary-green)' : 'var(--bg-white)',
                  color: selectedStatus === tab.value ? 'var(--bg-white)' : 'var(--text-dark)',
                  padding: '0.6rem 0.9rem',
                  fontWeight: 600,
                }}
              >
                {tab.label} <span style={{ opacity: 0.8 }}>({tab.count})</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="widgets-grid" style={{ display: 'grid', gridTemplateColumns: selectedAgency ? '1fr 1fr' : '1fr', gap: '2rem', transition: 'all 0.3s ease' }}>
        {/* Left Column: Pending List */}
        <div className="widget" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="widget-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 className="widget-title">
              {selectedStatus === 'pending' && `Pending Approvals (${agencies.length})`}
              {selectedStatus === 'verified' && `Verified Agencies (${agencies.length})`}
              {selectedStatus === 'rejected' && `Rejected Agencies (${agencies.length})`}
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {agencies.map(a => (
              <div 
                key={a.id} 
                onClick={() => setSelectedAgency(a)}
                style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center', 
                  padding: '1.25rem', 
                  border: selectedAgency?.id === a.id ? '2px solid var(--primary-green)' : '1px solid var(--border-color)', 
                  borderRadius: 'var(--radius-md)',
                  cursor: 'pointer',
                  backgroundColor: 'var(--bg-white)',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ color: 'var(--primary-green)', background: 'var(--primary-green-light)', padding: '0.6rem', borderRadius: '50%' }}>
                    <Building2 size={22} />
                  </div>
                  <div>
                    <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-dark)', marginBottom: '0.15rem' }}>{a.agency_name}</h4>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-gray)' }}>
                      Reg: {a.registration_number || 'N/A'} · {a.country || 'International'}
                    </span>
                  </div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: '#eab308', background: '#fef9c3', padding: '0.25rem 0.5rem', borderRadius: '4px', textTransform: 'uppercase', fontWeight: 600 }}>
                    {a.verification_status}
                  </span>
                </div>
              </div>
            ))}

            {agencies.length === 0 && (
              <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-gray)' }}>
                <CheckCircle2 size={36} style={{ color: 'var(--primary-green)', marginBottom: '0.75rem' }} />
                <p style={{ fontSize: '0.9rem', fontWeight: 500 }}>
                  {selectedStatus === 'pending' ? 'All registrations processed.' : 'No agencies found in this status.'}
                </p>
                <span style={{ fontSize: '0.75rem' }}>
                  {selectedStatus === 'pending'
                    ? 'There are no pending agency approvals.'
                    : 'Switch tabs to review another agency state.'}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Detailed View */}
        {selectedAgency && (
          <div className="widget" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', border: '1px solid var(--border-color)', padding: '2rem' }}>
            <div>
              <div className="widget-header" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 className="widget-title">Agency Verification Profile</h3>
                <button 
                  onClick={() => setSelectedAgency(null)} 
                  style={{ background: 'none', border: 'none', color: 'var(--text-gray)', cursor: 'pointer', fontSize: '1.25rem', fontWeight: 600 }}
                >
                  ×
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', color: 'var(--text-dark)' }}>
                <div>
                  <h4 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.25rem' }}>{selectedAgency.agency_name}</h4>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-gray)' }}>{selectedAgency.description || 'No description provided.'}</p>
                </div>

                <div style={{ display: 'inline-flex', width: 'fit-content', fontSize: '0.75rem', color: 'var(--primary-green)', background: 'var(--primary-green-light)', padding: '0.35rem 0.6rem', borderRadius: '999px', fontWeight: 700, textTransform: 'uppercase' }}>
                  {selectedAgency.verification_status}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.85rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Mail size={16} style={{ color: 'var(--text-gray)' }} />
                    <span>{selectedAgency.email || 'No email'}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Phone size={16} style={{ color: 'var(--text-gray)' }} />
                    <span>{selectedAgency.phone || 'No phone'}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Globe size={16} style={{ color: 'var(--text-gray)' }} />
                    {selectedAgency.website ? (
                      <a href={selectedAgency.website} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary-green)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                        Visit Website <ExternalLink size={12} />
                      </a>
                    ) : (
                      <span>No website</span>
                    )}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <ShieldCheck size={16} style={{ color: 'var(--text-gray)' }} />
                    <span>Registration: {selectedAgency.registration_number || 'N/A'}</span>
                  </div>
                </div>

                <div style={{ fontSize: '0.85rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
                  <strong>Registered Address:</strong>
                  <p style={{ color: 'var(--text-gray)', marginTop: '0.25rem', lineHeight: 1.4 }}>
                    {selectedAgency.address || 'No address'}, {selectedAgency.city || ''}, {selectedAgency.country || ''}
                  </p>
                </div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem', marginTop: '2rem' }}>
              <button 
                onClick={() => handleSuspend(selectedAgency)} 
                className="btn btn-secondary" 
                style={{ 
                  backgroundColor: '#fee2e2', 
                  color: '#ef4444', 
                  border: 'none', 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center', 
                  gap: '0.5rem',
                  fontWeight: 600
                }}
                disabled={verifyMutation.isPending || suspendMutation.isPending}
              >
                <XCircle size={18} /> Reject / Suspend
              </button>
              <button 
                onClick={() => handleVerify(selectedAgency)} 
                className="btn btn-primary"
                style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center', 
                  gap: '0.5rem',
                  fontWeight: 600
                }}
                disabled={verifyMutation.isPending || suspendMutation.isPending}
              >
                <CheckCircle2 size={18} /> {verifyMutation.isPending ? 'Verifying...' : 'Approve Agency'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
