import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useStudentLead, useUpdateStudentLead, useDeleteStudentLead } from '../hooks/useLeads';
import { ArrowLeft, CheckCircle, Clock } from 'lucide-react';

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

const ApplicationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: application, isLoading, error } = useStudentLead(id);
  const updateLeadMutation = useUpdateStudentLead();
  const deleteLeadMutation = useDeleteStudentLead();

  const [isEditing, setIsEditing] = useState(false);
  const [motivationLetter, setMotivationLetter] = useState('');
  const [documents, setDocuments] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (application) {
      setMotivationLetter(application.motivation_letter || '');
      setDocuments(application.documents || '');
      setNotes(application.notes || '');
    }
  }, [application]);

  if (isLoading) {
    return (
      <div className="dashboard-content">
        <p>Loading application details...</p>
      </div>
    );
  }

  if (error) {
    const isForbidden = error.response?.status === 403;
    return (
      <div className="dashboard-content">
        <p style={{ color: '#ef4444' }}>
          {isForbidden ? "Access Denied: You do not have permission to view this application." : "Failed to load application details."}
        </p>
        <button className="btn" onClick={() => navigate(-1)} style={{ marginTop: '1rem' }}>Go Back</button>
      </div>
    );
  }

  if (!application) {
    return (
      <div className="dashboard-content">
        <p>Application not found.</p>
        <button className="btn" onClick={() => navigate(-1)}>Go Back</button>
      </div>
    );
  }

  const uiStatus = mapStatus(application.status);
  const isSubmitted = application.status === 'submitted';

  const steps = [
    { label: 'Application Started', completed: true },
    { label: 'Documents Uploaded', completed: true },
    { label: 'Application Submitted', completed: true },
    { label: 'Under Review', completed: uiStatus === 'In Review' || uiStatus === 'Accepted' || uiStatus === 'Rejected' },
    { label: 'Final Decision', completed: uiStatus === 'Accepted' || uiStatus === 'Rejected' }
  ];

  const handleSave = async () => {
    try {
      await updateLeadMutation.mutateAsync({
        id,
        data: {
          motivation_letter: motivationLetter,
          documents,
          notes
        }
      });
      setIsEditing(false);
    } catch (err) {
      console.error('Failed to update lead', err);
    }
  };

  const handleWithdraw = async () => {
    if (window.confirm('Are you sure you want to withdraw this application? This action cannot be undone.')) {
      try {
        await deleteLeadMutation.mutateAsync(id);
        navigate('/applications');
      } catch (err) {
        console.error('Failed to delete lead', err);
      }
    }
  };

  const statusStyles = getStatusStyles(uiStatus);

  return (
    <div className="dashboard-content">
      <button 
        onClick={() => navigate('/applications')} 
        style={{ 
          background: 'none', 
          border: 'none', 
          color: 'var(--text-gray)', 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem', 
          cursor: 'pointer', 
          marginBottom: '1.5rem', 
          fontSize: '0.875rem' 
        }}
      >
        <ArrowLeft size={16} /> Back to Applications
      </button>
      
      <div className="widget" style={{ maxWidth: '800px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>{application.scholarship_title || '—'}</h1>
            <p style={{ color: 'var(--text-gray)', fontSize: '1rem' }}>{application.scholarship_university || '—'}</p>
          </div>
          <span style={{ 
            color: statusStyles.color, 
            background: statusStyles.background, 
            padding: '6px 12px', borderRadius: '4px', fontSize: '0.875rem', fontWeight: 600 
          }}>
            {uiStatus}
          </span>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2.5rem', padding: '1.5rem', background: 'var(--bg-gray)', borderRadius: 'var(--radius-md)' }}>
          <div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Date Applied</p>
            <p style={{ fontWeight: 600 }}>{application.created_at ? application.created_at.split('T')[0] : '—'}</p>
          </div>
          <div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Follow-up Date</p>
            <p style={{ fontWeight: 600 }}>{application.follow_up_date ? application.follow_up_date.split('T')[0] : 'Not Scheduled'}</p>
          </div>
          <div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Intake</p>
            <p style={{ fontWeight: 600 }}>—</p>
          </div>
        </div>

        {/* Motivation and Notes Section */}
        <div style={{ marginBottom: '2.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.25rem' }}>Application Details</h3>
          
          {isEditing ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>Motivation Letter</label>
                <textarea 
                  value={motivationLetter}
                  onChange={(e) => setMotivationLetter(e.target.value)}
                  style={{ width: '100%', minHeight: '120px', padding: '0.75rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}
                />
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>Documents</label>
                <input 
                  type="text" 
                  value={documents}
                  onChange={(e) => setDocuments(e.target.value)}
                  style={{ width: '100%', padding: '0.75rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}
                />
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>Notes</label>
                <textarea 
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  style={{ width: '100%', minHeight: '80px', padding: '0.75rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', outline: 'none' }}
                />
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button className="btn btn-primary" onClick={handleSave} disabled={updateLeadMutation.isPending}>
                  {updateLeadMutation.isPending ? 'Saving...' : 'Save Changes'}
                </button>
                <button className="btn btn-secondary" onClick={() => setIsEditing(false)}>Cancel</button>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <h4 style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Motivation Letter</h4>
                <p style={{ whiteSpace: 'pre-line' }}>{application.motivation_letter || 'No motivation letter provided.'}</p>
              </div>
              <div>
                <h4 style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Documents</h4>
                <p>{application.documents || 'No documents listed.'}</p>
              </div>
              <div>
                <h4 style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Notes</h4>
                <p>{application.notes || 'No extra notes.'}</p>
              </div>
              
              {isSubmitted && (
                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
                  <button className="btn btn-secondary" onClick={() => setIsEditing(true)}>Edit Details</button>
                  <button className="btn btn-danger" onClick={handleWithdraw} disabled={deleteLeadMutation.isPending} style={{ backgroundColor: '#ef4444', color: '#fff' }}>
                    {deleteLeadMutation.isPending ? 'Withdrawing...' : 'Withdraw Application'}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
        
        <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>Application Timeline</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {steps.map((step, idx) => (
            <div key={idx} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
              <div style={{ color: step.completed ? 'var(--primary-green)' : 'var(--text-gray)' }}>
                {step.completed ? <CheckCircle size={24} /> : <Clock size={24} />}
              </div>
              <div>
                <h4 style={{ fontSize: '1rem', fontWeight: 500, color: step.completed ? 'var(--text-dark)' : 'var(--text-gray)' }}>{step.label}</h4>
                {step.completed && <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', marginTop: '0.25rem' }}>Completed</p>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ApplicationDetail;
