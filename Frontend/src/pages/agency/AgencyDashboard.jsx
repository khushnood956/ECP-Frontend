import React from 'react';
import { Link } from 'react-router-dom';
import { useCurrentAgency } from '../../hooks/useCurrentAgency';
import { useAgencyLeads } from '../../hooks/useLeads';
import { Users, Building, GraduationCap, ArrowRight } from 'lucide-react';

const AgencyDashboard = () => {
  const { data: agency, isLoading: isAgencyLoading } = useCurrentAgency();
  const { data: leads, isLoading: isLeadsLoading } = useAgencyLeads();

  const activeLeadsCount = leads ? leads.filter(l => l.status === 'submitted' || l.status === 'under_review').length : 0;
  const acceptedCount = leads ? leads.filter(l => l.status === 'accepted').length : 0;
  const totalCount = leads ? leads.length : 0;

  if (isAgencyLoading) {
    return (
      <div className="dashboard-content">
        <div style={{ height: '36px', width: '250px', backgroundColor: 'var(--bg-gray)', borderRadius: '4px', marginBottom: '1.5rem' }}></div>
        <div className="stats-grid">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="stat-card" style={{ height: '120px' }}></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-content">
      <div className="page-header" style={{ marginBottom: '2rem' }}>
        <h1 className="page-title">
          Welcome back, {agency ? agency.agency_name : 'Agency Partner'}!
        </h1>
        <p className="page-subtitle">
          Manage your scholarship applications and track leads.
        </p>
      </div>

      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <div className="stat-card">
          <div className="stat-header">
            Active Leads
            <div className="icon-wrapper"><Users size={18} /></div>
          </div>
          <div className="stat-value">
            {isLeadsLoading ? '...' : activeLeadsCount}
          </div>
          <div className="stat-trend" style={{ color: 'var(--text-gray)' }}>
            Requires review or follow-up
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            Accepted Leads
            <div className="icon-wrapper" style={{ backgroundColor: '#e6f4ea', color: '#137333' }}>
              <GraduationCap size={18} />
            </div>
          </div>
          <div className="stat-value" style={{ color: '#137333' }}>
            {isLeadsLoading ? '...' : acceptedCount}
          </div>
          <div className="stat-trend positive">
            Successfully matched students
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            Total Applications
            <div className="icon-wrapper" style={{ backgroundColor: 'var(--bg-gray)', color: 'var(--text-gray)' }}>
              <Building size={18} />
            </div>
          </div>
          <div className="stat-value">
            {isLeadsLoading ? '...' : totalCount}
          </div>
          <div className="stat-trend" style={{ color: 'var(--text-gray)' }}>
            All-time history log
          </div>
        </div>
      </div>

      <div className="widgets-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)', gap: '2rem' }}>
        <div className="widget" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '160px' }}>
          <div>
            <div className="widget-header" style={{ marginBottom: '1rem' }}>
              <h3 className="widget-title">Profile Operations</h3>
            </div>
            <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1.5rem' }}>
              Keep your public consulting agency profile verified and detailed to build student trust.
            </p>
          </div>
          <div>
            <Link 
              to="/agency/profile" 
              style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary-green)', fontWeight: 600, textDecoration: 'none', fontSize: '0.875rem' }}
            >
              View Agency Profile
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>

        <div className="widget" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '160px' }}>
          <div>
            <div className="widget-header" style={{ marginBottom: '1rem' }}>
              <h3 className="widget-title">Lead Processing Pipeline</h3>
            </div>
            <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1.5rem' }}>
              Update application status records for new student leads and contact pending applications.
            </p>
          </div>
          <div>
            <Link 
              to="/agency/leads" 
              style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary-green)', fontWeight: 600, textDecoration: 'none', fontSize: '0.875rem' }}
            >
              Go to Leads Table
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgencyDashboard;
