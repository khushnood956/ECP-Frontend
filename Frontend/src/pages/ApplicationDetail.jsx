import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { ArrowLeft, FileText, CheckCircle, Clock } from 'lucide-react';

const ApplicationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { applications } = useAppContext();
  
  const application = applications.find(a => a.id === id);

  if (!application) {
    return <div className="dashboard-content"><p>Application not found.</p><button className="btn" onClick={() => navigate(-1)}>Go Back</button></div>;
  }

  const steps = [
    { label: 'Application Started', completed: true },
    { label: 'Documents Uploaded', completed: true },
    { label: 'Application Submitted', completed: true },
    { label: 'Under Review', completed: application.status === 'In Review' || application.status === 'Accepted' || application.status === 'Rejected' },
    { label: 'Final Decision', completed: application.status === 'Accepted' || application.status === 'Rejected' }
  ];

  return (
    <div className="dashboard-content">
      <button onClick={() => navigate(-1)} style={{ background: 'none', border: 'none', color: 'var(--text-gray)', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
        <ArrowLeft size={16} /> Back
      </button>
      
      <div className="widget" style={{ maxWidth: '800px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>{application.program}</h1>
            <p style={{ color: 'var(--text-gray)', fontSize: '1rem' }}>{application.university}</p>
          </div>
          <span style={{ 
            color: application.status === 'Submitted' ? 'var(--primary-green)' : '#eab308', 
            background: application.status === 'Submitted' ? 'var(--primary-green-light)' : '#fef9c3', 
            padding: '6px 12px', borderRadius: '4px', fontSize: '0.875rem', fontWeight: 600 
          }}>
            {application.status}
          </span>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', marginBottom: '2.5rem', padding: '1.5rem', background: 'var(--bg-gray)', borderRadius: 'var(--radius-md)' }}>
          <div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Intake</p>
            <p style={{ fontWeight: 600 }}>{application.intake}</p>
          </div>
          <div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Date Applied</p>
            <p style={{ fontWeight: 600 }}>{application.date}</p>
          </div>
        </div>
        
        <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem' }}>Application Timeline</h3>
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
