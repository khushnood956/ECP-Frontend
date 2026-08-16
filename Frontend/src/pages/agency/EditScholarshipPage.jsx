import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAgencyScholarship, useUpdateScholarship } from '../../hooks/useScholarships';
import { ScholarshipForm } from './ScholarshipForm';
import { ArrowLeft } from 'lucide-react';

const EditScholarshipPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [errorMsg, setErrorMsg] = useState(null);

  const { data: scholarship, isLoading, error } = useAgencyScholarship(id || '');
  const updateMutation = useUpdateScholarship();

  const handleSubmit = (data) => {
    if (!scholarship?.id) return;
    setErrorMsg(null);
    updateMutation.mutate({ id: scholarship.id, data }, {
      onSuccess: () => {
        navigate(`/agency/scholarships/${scholarship.id}`);
      },
      onError: (err) => {
        setErrorMsg(err.response?.data?.detail || err.message || 'Failed to update scholarship program.');
      }
    });
  };

  if (isLoading) {
    return (
      <div className="dashboard-content">
        <div style={{ height: '36px', width: '120px', backgroundColor: 'var(--bg-gray)', borderRadius: '4px', marginBottom: '1.5rem' }}></div>
        <div className="widget" style={{ height: '300px' }}></div>
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

  return (
    <div className="dashboard-content">
      <div style={{ marginBottom: '1.5rem' }}>
        <button className="btn" onClick={() => navigate(`/agency/scholarships/${scholarship.id}`)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ArrowLeft size={16} /> Cancel
        </button>
      </div>

      <div className="page-header" style={{ marginBottom: '2rem' }}>
        <h1 className="page-title">Edit Scholarship Program</h1>
        <p className="page-subtitle">Update program eligibility, funding amounts, or application links.</p>
      </div>

      {errorMsg && (
        <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
          {errorMsg}
        </div>
      )}

      <div className="widget" style={{ padding: '2rem', maxWidth: '800px' }}>
        <ScholarshipForm initialValues={scholarship} onSubmit={handleSubmit} isSubmitting={updateMutation.isPending} />
      </div>
    </div>
  );
};

export default EditScholarshipPage;
