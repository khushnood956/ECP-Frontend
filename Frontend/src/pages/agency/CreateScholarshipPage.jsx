import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCreateScholarship } from '../../hooks/useScholarships';
import { ScholarshipForm } from './ScholarshipForm';
import { ArrowLeft } from 'lucide-react';

const CreateScholarshipPage = () => {
  const navigate = useNavigate();
  const [errorMsg, setErrorMsg] = useState(null);
  const mutation = useCreateScholarship();

  const handleSubmit = (data) => {
    setErrorMsg(null);
    mutation.mutate(data, {
      onSuccess: () => {
        navigate('/agency/scholarships');
      },
      onError: (err) => {
        setErrorMsg(err.response?.data?.detail || err.message || 'Failed to create scholarship program.');
      }
    });
  };

  return (
    <div className="dashboard-content">
      <div style={{ marginBottom: '1.5rem' }}>
        <button className="btn" onClick={() => navigate('/agency/scholarships')} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ArrowLeft size={16} /> Back to Scholarships
        </button>
      </div>

      <div className="page-header" style={{ marginBottom: '2rem' }}>
        <h1 className="page-title">New Scholarship Program</h1>
        <p className="page-subtitle">Publish a new program or save it as a draft for students.</p>
      </div>

      {errorMsg && (
        <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
          {errorMsg}
        </div>
      )}

      <div className="widget" style={{ padding: '2rem', maxWidth: '800px' }}>
        <ScholarshipForm onSubmit={handleSubmit} isSubmitting={mutation.isPending} />
      </div>
    </div>
  );
};

export default CreateScholarshipPage;
