import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAgencyLead, useUpdateLead } from '../../hooks/useLeads';
import { 
  ArrowLeft, 
  User, 
  GraduationCap, 
  FileText, 
  Activity, 
  MapPin, 
  Calendar, 
  Globe, 
  DollarSign 
} from 'lucide-react';
import { 
  formatDate, 
  getStatusBadgeClass, 
  getStatusLabel, 
  formatCurrency, 
  formatNullable, 
  formatName 
} from '../../utils/formatters';

const LeadDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const { data: lead, isLoading, error } = useAgencyLead(id || '');
  const updateLeadMutation = useUpdateLead();

  if (isLoading) {
    return (
      <div className="dashboard-content">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <div style={{ height: '36px', width: '120px', backgroundColor: 'var(--bg-gray)', borderRadius: '4px' }}></div>
        </div>
        <div className="widgets-grid" style={{ gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
          <div className="widget" style={{ height: '300px' }}></div>
          <div className="widget" style={{ height: '300px' }}></div>
        </div>
      </div>
    );
  }

  if (error || !lead) {
    const is403 = error?.response?.status === 403;
    const is404 = error?.response?.status === 404;

    let message = 'Failed to load lead details. Please try again.';
    if (is403) message = 'Access Denied: You do not have permission to view this lead.';
    if (is404) message = 'Lead not found.';

    return (
      <div className="dashboard-content">
        <button className="btn" onClick={() => navigate('/agency/leads')} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <ArrowLeft size={16} /> Back to Leads
        </button>
        <div className="alert alert-error">{message}</div>
      </div>
    );
  }

  const { student, scholarship } = lead;

  const getAllowedTransitions = (currentStatus) => {
    if (currentStatus === 'submitted') {
      return [{ value: 'under_review', label: 'Move to Under Review' }];
    }
    if (currentStatus === 'under_review') {
      return [
        { value: 'under_review', label: 'Keep Under Review' },
        { value: 'accepted', label: 'Accept Application' },
        { value: 'rejected', label: 'Reject Application' },
      ];
    }
    return [];
  };

  const allowedTransitions = getAllowedTransitions(lead.status);

  const handleStatusChange = async (targetStatus) => {
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await updateLeadMutation.mutateAsync({
        id: lead.id,
        data: { status: targetStatus },
      });
      setSuccessMsg('Lead status updated successfully!');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to update lead status.';
      setErrorMsg(errorMsg);
    }
  };

  return (
    <div className="dashboard-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <button className="btn" onClick={() => navigate('/agency/leads')} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ArrowLeft size={16} /> Back to Leads
        </button>
        <span style={{ 
          padding: '6px 12px', 
          borderRadius: '4px', 
          fontSize: '0.875rem', 
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }} className={getStatusBadgeClass(lead.status)}>
          Status: {getStatusLabel(lead.status)}
        </span>
      </div>

      {successMsg && <div className="alert alert-success toast-success" style={{ marginBottom: '1.5rem' }}>{successMsg}</div>}
      {errorMsg && <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>{errorMsg}</div>}

      <div className="widgets-grid" style={{ gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        {/* Left Columns - Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Student Profile Card */}
          <div className="widget" style={{ padding: '2rem' }}>
            <h3 className="widget-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem', color: 'var(--text-dark)' }}>
              <User size={20} style={{ color: 'var(--primary-green)' }} />
              Student Profile
            </h3>
            {student ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem', fontSize: '0.875rem' }}>
                <div>
                  <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Full Name</span>
                  <span style={{ fontWeight: 600, color: 'var(--text-dark)' }}>{formatName(student.first_name, student.last_name)}</span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Country</span>
                  <span style={{ fontWeight: 600, color: 'var(--text-dark)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <MapPin size={16} style={{ color: 'var(--text-gray)' }} />
                    {formatNullable(student.country)}
                  </span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Phone</span>
                  <span style={{ fontWeight: 600, color: 'var(--text-dark)' }}>{formatNullable(student.phone)}</span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Highest Qualification</span>
                  <span style={{ fontWeight: 600, color: 'var(--text-dark)' }}>{formatNullable(student.highest_qualification)}</span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>CGPA / Percentage</span>
                  <span style={{ fontWeight: 600, color: 'var(--text-dark)' }}>{formatNullable(student.cgpa_or_percentage)}</span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Preferred Degree</span>
                  <span style={{ fontWeight: 600, color: 'var(--text-dark)' }}>{formatNullable(student.preferred_degree)}</span>
                </div>
                <div style={{ gridColumn: 'span 2' }}>
                  <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.5rem' }}>Bio</span>
                  <p style={{ color: 'var(--text-dark)', lineHeight: 1.5, whiteSpace: 'pre-wrap', backgroundColor: 'var(--bg-gray)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                    {formatNullable(student.bio, 'No bio provided.')}
                  </p>
                </div>
              </div>
            ) : (
              <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem' }}>Student details are not available or access is restricted.</p>
            )}
          </div>

          {/* Application Materials (Motivation Letter, etc.) */}
          <div className="widget" style={{ padding: '2rem' }}>
            <h3 className="widget-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem', color: 'var(--text-dark)' }}>
              <FileText size={20} style={{ color: 'var(--primary-green)' }} />
              Application Materials
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', fontSize: '0.875rem' }}>
              <div>
                <span style={{ color: 'var(--text-gray)', fontWeight: 500, display: 'block', marginBottom: '0.5rem' }}>Motivation Letter</span>
                <p style={{ lineHeight: 1.5, whiteSpace: 'pre-wrap', backgroundColor: 'var(--bg-gray)', padding: '1rem', borderRadius: 'var(--radius-md)', color: 'var(--text-dark)', border: '1px solid var(--border-color)' }}>
                  {formatNullable(lead.motivation_letter, 'No motivation letter provided.')}
                </p>
              </div>
              <div>
                <span style={{ color: 'var(--text-gray)', fontWeight: 500, display: 'block', marginBottom: '0.25rem' }}>Supporting Documents</span>
                <p style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                  {lead.documents ? (
                    <a href={lead.documents} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary-green)', fontWeight: 500, textDecoration: 'none' }}>
                      {lead.documents}
                    </a>
                  ) : (
                    <span style={{ color: 'var(--text-gray)' }}>No documents uploaded.</span>
                  )}
                </p>
              </div>
              <div>
                <span style={{ color: 'var(--text-gray)', fontWeight: 500, display: 'block', marginBottom: '0.25rem' }}>Additional Notes</span>
                <p style={{ color: 'var(--text-dark)' }}>{formatNullable(lead.notes, 'No additional notes.')}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Status & Scholarship */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Status Processing Box */}
          <div className="widget" style={{ padding: '2rem', backgroundColor: 'var(--primary-green-light)', border: 'none' }}>
            <h3 className="widget-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary-green)', marginBottom: '1rem' }}>
              <Activity size={20} />
              Process Application
            </h3>
            {allowedTransitions.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)' }}>
                  Select a status transition to update the state of this lead.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {allowedTransitions.map((t) => (
                    <button
                      key={t.value}
                      onClick={() => handleStatusChange(t.value)}
                      disabled={updateLeadMutation.isPending}
                      className={`btn btn-block ${t.value === 'accepted' ? 'btn-primary' : 'btn-outline'}`}
                      style={{ cursor: 'pointer', textAlign: 'left', padding: '0.75rem 1rem' }}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <p style={{ fontSize: '0.875rem', color: 'var(--text-dark)' }}>
                No further status transitions are allowed. This lead is finalized as <strong>{getStatusLabel(lead.status)}</strong>.
              </p>
            )}
          </div>

          {/* Scholarship Details */}
          <div className="widget" style={{ padding: '2rem' }}>
            <h3 className="widget-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem', color: 'var(--text-dark)' }}>
              <GraduationCap size={20} style={{ color: 'var(--primary-green)' }} />
              Scholarship
            </h3>
            {scholarship ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', fontSize: '0.875rem' }}>
                <div>
                  <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Title</span>
                  <span style={{ fontWeight: 600, color: 'var(--text-dark)', fontSize: '1rem' }}>{scholarship.title}</span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>University</span>
                  <span style={{ fontWeight: 500, color: 'var(--text-dark)' }}>{formatNullable(scholarship.university)}</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Country</span>
                    <span style={{ fontWeight: 500, color: 'var(--text-dark)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Globe size={16} style={{ color: 'var(--text-gray)' }} />
                      {formatNullable(scholarship.country)}
                    </span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Degree Level</span>
                    <span style={{ fontWeight: 500, color: 'var(--text-dark)' }}>{formatNullable(scholarship.degree_level)}</span>
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Funding Type</span>
                    <span style={{ fontWeight: 500, color: 'var(--text-dark)', textTransform: 'capitalize' }}>{formatNullable(scholarship.funding_type)}</span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Amount</span>
                    <span style={{ fontWeight: 600, color: 'var(--primary-green)', display: 'flex', alignItems: 'center' }}>
                      <DollarSign size={16} />
                      {formatCurrency(scholarship.amount, scholarship.currency)}
                    </span>
                  </div>
                </div>
                <div>
                  <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Deadline</span>
                  <span style={{ fontWeight: 500, color: 'var(--text-dark)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Calendar size={16} style={{ color: 'var(--text-gray)' }} />
                    {formatDate(scholarship.deadline)}
                  </span>
                </div>
              </div>
            ) : (
              <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem' }}>Scholarship details are not available or access is restricted.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeadDetailsPage;
