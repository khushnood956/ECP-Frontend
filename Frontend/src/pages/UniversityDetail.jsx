import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { ArrowLeft, Bookmark } from 'lucide-react';

const UniversityDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { universities, toggleBookmark } = useAppContext();
  
  const university = universities.find(u => u.id === id);

  if (!university) {
    return <div className="dashboard-content"><p>University not found.</p><button className="btn" onClick={() => navigate(-1)}>Go Back</button></div>;
  }

  return (
    <div className="dashboard-content">
      <button onClick={() => navigate(-1)} style={{ background: 'none', border: 'none', color: 'var(--text-gray)', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
        <ArrowLeft size={16} /> Back
      </button>
      
      <div className="widget" style={{ maxWidth: '800px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>{university.name}</h1>
            <p style={{ color: 'var(--text-gray)', fontSize: '1rem' }}>{university.location}</p>
          </div>
          <button className="icon-btn" onClick={() => toggleBookmark('university', university.id)}>
            <Bookmark size={24} fill={university.bookmarked ? 'var(--primary-green)' : 'none'} color={university.bookmarked ? 'var(--primary-green)' : 'var(--text-gray)'} />
          </button>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', marginBottom: '2rem', padding: '1.5rem', background: 'var(--bg-gray)', borderRadius: 'var(--radius-md)' }}>
          <div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Ranking</p>
            <p style={{ fontWeight: 600 }}>{university.ranking}</p>
          </div>
          <div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-gray)', marginBottom: '0.25rem' }}>Type</p>
            <p style={{ fontWeight: 600 }}>{university.type}</p>
          </div>
        </div>
        
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.75rem' }}>About</h3>
          <p style={{ color: 'var(--text-dark)', lineHeight: 1.6 }}>
            {university.name} is a leading {university.type.toLowerCase()} institution located in {university.location}. It is renowned globally for its research output, academic rigor, and vibrant campus life.
          </p>
        </div>

        <button className="btn btn-primary">Start Application</button>
      </div>
    </div>
  );
};

export default UniversityDetail;
