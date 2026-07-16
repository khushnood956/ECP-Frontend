import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { ArrowLeft, Bookmark } from 'lucide-react';

const ScholarshipDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { scholarships, toggleBookmark } = useAppContext();
  
  const scholarship = scholarships.find(s => s.id === id);

  if (!scholarship) {
    return <div className="dashboard-content"><p>Scholarship not found.</p><button className="btn" onClick={() => navigate(-1)}>Go Back</button></div>;
  }

  return (
    <div className="dashboard-content">
      <button onClick={() => navigate(-1)} style={{ background: 'none', border: 'none', color: 'var(--text-gray)', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
        <ArrowLeft size={16} /> Back
      </button>
      
      <div className="widget" style={{ maxWidth: '800px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>{scholarship.title}</h1>
            <p style={{ color: 'var(--text-gray)', fontSize: '1rem' }}>{scholarship.provider}</p>
          </div>
          <button className="icon-btn" onClick={() => toggleBookmark('scholarship', scholarship.id)}>
            <Bookmark size={24} fill={scholarship.bookmarked ? 'var(--primary-green)' : 'none'} color={scholarship.bookmarked ? 'var(--primary-green)' : 'var(--text-gray)'} />
          </button>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem', padding: '1.5rem', background: 'var(--bg-gray)', borderRadius: 'var(--radius-md)' }}>
          <div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Amount</p>
            <p style={{ fontWeight: 600, color: 'var(--primary-green)' }}>{scholarship.amount}</p>
          </div>
          <div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Type</p>
            <p style={{ fontWeight: 600 }}>{scholarship.type}</p>
          </div>
          <div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Deadline</p>
            <p style={{ fontWeight: 600, color: '#ef4444' }}>{scholarship.deadline}</p>
          </div>
        </div>
        
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.75rem' }}>Description</h3>
          <p style={{ color: 'var(--text-dark)', lineHeight: 1.6 }}>
            This is a mock description for {scholarship.title}. It provides financial support to outstanding students pursuing their education at {scholarship.provider}. The scholarship aims to recognize academic excellence and leadership potential.
          </p>
        </div>

        <button className="btn btn-primary">Apply Now</button>
      </div>
    </div>
  );
};

export default ScholarshipDetail;
