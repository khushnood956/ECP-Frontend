import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  useAgencyScholarship, 
  usePublishScholarship, 
  useUnpublishScholarship, 
  useDeleteScholarship 
} from '../../hooks/useScholarships';
import { 
  ArrowLeft, 
  Building, 
  Calendar, 
  Globe, 
  DollarSign, 
  Award, 
  FileText, 
  Link as LinkIcon,
  ToggleLeft,
  ToggleRight,
  Trash2
} from 'lucide-react';
import { formatDate, formatCurrency, formatNullable } from '../../utils/formatters';

const ScholarshipDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const { data: scholarship, isLoading, error } = useAgencyScholarship(id || '');
  const publishMutation = usePublishScholarship();
  const unpublishMutation = useUnpublishScholarship();
  const deleteMutation = useDeleteScholarship();

  if (isLoading) {
    return (
      <div className="dashboard-content">
        <div style={{ height: '36px', width: '120px', backgroundColor: 'var(--bg-gray)', borderRadius: '4px', marginBottom: '1.5rem' }}></div>
        <div className="widgets-grid" style={{ gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
          <div className="widget" style={{ height: '300px' }}></div>
          <div className="widget" style={{ height: '300px' }}></div>
        </div>
      </div>
    );
  }

  if (error || !scholarship) {
    const is403 = error?.response?.status === 403;
    const is404 = error?.response?.status === 404;

    let message = 'Failed to load scholarship details.';
    if (is403) message = 'Access Denied: You do not have ownership permissions for this program.';
    if (is404) message = 'Scholarship not found.';

    return (
      <div className="dashboard-content">
        <button className="btn" onClick={() => navigate('/agency/scholarships')} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <ArrowLeft size={16} /> Back to Scholarships
        </button>
        <div className="alert alert-error">{message}</div>
      </div>
    );
  }

  const handleToggleActive = async () => {
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      if (scholarship.is_active) {
        await unpublishMutation.mutateAsync(scholarship.id);
        setSuccessMsg('Scholarship program unpublished successfully!');
      } else {
        await publishMutation.mutateAsync(scholarship.id);
        setSuccessMsg('Scholarship program published successfully!');
      }
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || err.message || 'Failed to update publication state.');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this scholarship program permanently?')) {
      return;
    }
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await deleteMutation.mutateAsync(scholarship.id);
      navigate('/agency/scholarships');
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || err.message || 'Failed to delete scholarship.');
    }
  };

  return (
    <div className="dashboard-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <button className="btn" onClick={() => navigate('/agency/scholarships')} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ArrowLeft size={16} /> Back to Scholarships
        </button>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <button 
            onClick={() => navigate(`/agency/scholarships/${scholarship.id}/edit`)} 
            className="btn btn-outline"
          >
            Edit Program
          </button>
          <button 
            onClick={handleDelete} 
            className="btn" 
            style={{ borderColor: '#ef4444', color: '#ef4444', backgroundColor: 'transparent', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
          >
            <Trash2 size={16} />
            Delete
          </button>
        </div>
      </div>

      {successMsg && <div className="alert alert-success toast-success" style={{ marginBottom: '1.5rem' }}>{successMsg}</div>}
      {errorMsg && <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>{errorMsg}</div>}

      <div className="widgets-grid" style={{ gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        {/* Left Column: Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Base Details */}
          <div className="widget" style={{ padding: '2rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-dark)', marginBottom: '0.5rem' }}>{scholarship.title}</h2>
            <p style={{ color: 'var(--text-gray)', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem', marginBottom: '2rem' }}>
              <Building size={18} />
              {scholarship.university || 'Various Universities'}
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem', fontSize: '0.875rem' }}>
              <div>
                <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Country</span>
                <span style={{ fontWeight: 600, color: 'var(--text-dark)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Globe size={16} />
                  {formatNullable(scholarship.country)}
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Degree Level</span>
                <span style={{ fontWeight: 600, color: 'var(--text-dark)', textTransform: 'capitalize' }}>
                  {scholarship.degree_level.replace('_', ' ')}
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Funding Type</span>
                <span style={{ fontWeight: 600, color: 'var(--text-dark)', textTransform: 'capitalize' }}>
                  {scholarship.funding_type.replace('_', ' ')}
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Amount</span>
                <span style={{ fontWeight: 600, color: 'var(--primary-green)', display: 'flex', alignItems: 'center' }}>
                  <DollarSign size={16} />
                  {formatCurrency(scholarship.amount, scholarship.currency)}
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Deadline</span>
                <span style={{ fontWeight: 600, color: 'var(--text-dark)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Calendar size={16} />
                  {formatDate(scholarship.deadline)}
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--text-gray)', display: 'block', marginBottom: '0.25rem' }}>Online Application Link</span>
                {scholarship.application_link ? (
                  <a href={scholarship.application_link} target="_blank" rel="noreferrer" style={{ color: 'var(--primary-green)', fontWeight: 600, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <LinkIcon size={14} />
                    Apply Online
                  </a>
                ) : (
                  <span style={{ color: 'var(--text-gray)' }}>—</span>
                )}
              </div>
            </div>
          </div>

          {/* Description & Eligibility */}
          <div className="widget" style={{ padding: '2rem' }}>
            <h3 className="widget-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem', color: 'var(--text-dark)' }}>
              <Award size={20} style={{ color: 'var(--primary-green)' }} />
              Eligibility Criteria
            </h3>
            <p style={{ color: 'var(--text-dark)', lineHeight: 1.5, whiteSpace: 'pre-wrap', marginBottom: '2rem' }}>
              {formatNullable(scholarship.eligibility, 'No eligibility criteria specified.')}
            </p>

            <h3 className="widget-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem', color: 'var(--text-dark)' }}>
              <FileText size={20} style={{ color: 'var(--primary-green)' }} />
              Description
            </h3>
            <p style={{ color: 'var(--text-dark)', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
              {formatNullable(scholarship.description, 'No description provided.')}
            </p>
          </div>
        </div>

        {/* Right Column: Publication State */}
        <div>
          <div className="widget" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <h3 className="widget-title" style={{ marginBottom: '0.5rem' }}>Publication Settings</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', lineHeight: 1.4 }}>
                Control whether this scholarship is visible to students looking for opportunities.
              </p>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', backgroundColor: 'var(--bg-gray)', borderRadius: 'var(--radius-md)' }}>
              <div>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-dark)' }}>Status</span>
                <p style={{ fontSize: '0.75rem', color: scholarship.is_active ? 'var(--primary-green)' : 'var(--text-gray)', fontWeight: 500, marginTop: '0.125rem' }}>
                  {scholarship.is_active ? 'Visible to public' : 'Saved as draft'}
                </p>
              </div>
              <button 
                onClick={handleToggleActive}
                disabled={publishMutation.isPending || unpublishMutation.isPending}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: scholarship.is_active ? 'var(--primary-green)' : 'var(--text-gray)' }}
              >
                {scholarship.is_active ? <ToggleRight size={44} /> : <ToggleLeft size={44} />}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScholarshipDetailsPage;
