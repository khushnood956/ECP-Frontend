import React from 'react';
import { useAppContext } from '../context/AppContext';
import { Bookmark, Search } from 'lucide-react';
import { Link } from 'react-router-dom';

const Scholarships = () => {
  const { scholarships, toggleBookmark, searchQuery } = useAppContext();

  const filtered = scholarships.filter(s => 
    s.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
    s.provider.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="dashboard-content">
      <div className="page-header">
        <h1 className="page-title">Scholarships</h1>
        <p className="page-subtitle">Find and apply for financial aid.</p>
      </div>
      
      <div className="widgets-grid" style={{ gridTemplateColumns: '1fr' }}>
        <div className="widget">
          <div className="widget-header">
            <h3 className="widget-title">Available Scholarships</h3>
          </div>
          <div style={{ display: 'grid', gap: '1rem' }}>
            {filtered.map(s => (
              <div key={s.id} style={{ padding: '1.5rem', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h4 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                    <Link to={`/scholarships/${s.id}`} style={{ color: 'var(--text-dark)', textDecoration: 'none' }}>{s.title}</Link>
                  </h4>
                  <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>{s.provider}</p>
                  <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem' }}>
                    <span style={{ background: 'var(--bg-gray)', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>{s.type}</span>
                    <span style={{ background: 'var(--primary-green-light)', color: 'var(--primary-green)', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>{s.amount}</span>
                    <span style={{ color: '#ef4444' }}>Deadline: {s.deadline}</span>
                  </div>
                </div>
                <button className="icon-btn" onClick={() => toggleBookmark('scholarship', s.id)}>
                  <Bookmark size={24} fill={s.bookmarked ? 'var(--primary-green)' : 'none'} color={s.bookmarked ? 'var(--primary-green)' : 'var(--text-gray)'} />
                </button>
              </div>
            ))}
            {filtered.length === 0 && <p>No scholarships found.</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Scholarships;
