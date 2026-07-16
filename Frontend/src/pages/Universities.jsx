import React from 'react';
import { useAppContext } from '../context/AppContext';
import { Bookmark } from 'lucide-react';
import { Link } from 'react-router-dom';

const Universities = () => {
  const { universities, toggleBookmark, searchQuery } = useAppContext();

  const filtered = universities.filter(u => 
    u.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    u.location.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="dashboard-content">
      <div className="page-header">
        <h1 className="page-title">Universities</h1>
        <p className="page-subtitle">Explore top institutions worldwide.</p>
      </div>
      
      <div className="widgets-grid" style={{ gridTemplateColumns: '1fr' }}>
        <div className="widget">
          <div className="widget-header">
            <h3 className="widget-title">Featured Universities</h3>
          </div>
          <div style={{ display: 'grid', gap: '1rem' }}>
            {filtered.map(u => (
              <div key={u.id} style={{ padding: '1.5rem', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h4 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                    <Link to={`/universities/${u.id}`} style={{ color: 'var(--text-dark)', textDecoration: 'none' }}>{u.name}</Link>
                  </h4>
                  <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>{u.location}</p>
                  <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem' }}>
                    <span style={{ background: 'var(--bg-gray)', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>Ranking: {u.ranking}</span>
                    <span style={{ background: 'var(--bg-gray)', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>{u.type}</span>
                  </div>
                </div>
                <button className="icon-btn" onClick={() => toggleBookmark('university', u.id)}>
                  <Bookmark size={24} fill={u.bookmarked ? 'var(--primary-green)' : 'none'} color={u.bookmarked ? 'var(--primary-green)' : 'var(--text-gray)'} />
                </button>
              </div>
            ))}
            {filtered.length === 0 && <p>No universities found.</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Universities;
