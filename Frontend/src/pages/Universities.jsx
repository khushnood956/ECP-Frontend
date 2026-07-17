import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { Bookmark, MapPin, Award, BookOpen, Building2 } from 'lucide-react';
import { Link } from 'react-router-dom';

const Universities = () => {
  const { universities, toggleBookmark, searchQuery } = useAppContext();
  
  const [locationFilter, setLocationFilter] = useState('');
  const [rankingFilter, setRankingFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [tuitionFilter, setTuitionFilter] = useState('');

  const filtered = universities.filter(u => {
    const matchesSearch = u.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          u.location.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesLocation = locationFilter ? u.location === locationFilter : true;
    const matchesRanking = rankingFilter ? u.ranking === rankingFilter : true;
    const matchesType = typeFilter ? u.type === typeFilter : true;
    const matchesTuition = tuitionFilter ? u.tuitionCategory === tuitionFilter : true;
    
    return matchesSearch && matchesLocation && matchesRanking && matchesType && matchesTuition;
  });

  return (
    <div className="dashboard-content">
      <div className="page-header">
        <h1 className="page-title">Universities</h1>
        <p className="page-subtitle">Explore and discover top institutions globally.</p>
      </div>
      
      <div className="widget" style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <select className="input-field" style={{ width: 'auto', minWidth: '150px' }} value={locationFilter} onChange={e => setLocationFilter(e.target.value)}>
          <option value="">All Locations</option>
          <option value="Canada">Canada</option>
          <option value="USA">USA</option>
          <option value="Australia">Australia</option>
        </select>
        <select className="input-field" style={{ width: 'auto', minWidth: '150px' }} value={rankingFilter} onChange={e => setRankingFilter(e.target.value)}>
          <option value="">All Rankings</option>
          <option value="Top 10">Top 10</option>
          <option value="Top 50">Top 50</option>
          <option value="Top 100">Top 100</option>
        </select>
        <select className="input-field" style={{ width: 'auto', minWidth: '150px' }} value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
          <option value="">All Types</option>
          <option value="Public">Public</option>
          <option value="Private">Private</option>
        </select>
        <select className="input-field" style={{ width: 'auto', minWidth: '150px' }} value={tuitionFilter} onChange={e => setTuitionFilter(e.target.value)}>
          <option value="">All Tuition Levels</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
        {(locationFilter || rankingFilter || typeFilter || tuitionFilter) && (
          <button className="btn" onClick={() => { setLocationFilter(''); setRankingFilter(''); setTypeFilter(''); setTuitionFilter(''); }} style={{ background: 'none', color: 'var(--text-gray)', border: 'none', cursor: 'pointer' }}>Clear Filters</button>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {filtered.map(u => (
          <div key={u.id} className="widget" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', position: 'relative', transition: 'transform 0.2s, box-shadow 0.2s' }} onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = 'var(--shadow-md)'; }} onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = 'var(--shadow-sm)'; }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <span style={{ display: 'inline-flex', background: 'var(--bg-gray)', color: 'var(--text-dark)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.75rem', alignItems: 'center', gap: '0.25rem' }}>
                  <Award size={14} /> {u.ranking}
                </span>
                <h4 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.25rem', lineHeight: 1.3 }}>
                  <Link to={`/universities/${u.id}`} style={{ color: 'var(--text-dark)', textDecoration: 'none' }}>{u.name}</Link>
                </h4>
                <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <MapPin size={16} /> {u.location}
                </p>
              </div>
              <button className="icon-btn" onClick={() => toggleBookmark('university', u.id)} style={{ padding: '0.25rem', margin: '-0.25rem' }}>
                <Bookmark size={24} fill={u.bookmarked ? 'var(--primary-green)' : 'none'} color={u.bookmarked ? 'var(--primary-green)' : 'var(--text-gray)'} />
              </button>
            </div>
            
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <span style={{ background: 'var(--bg-gray)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Building2 size={12} /> {u.type}</span>
              {u.programs && <span style={{ background: 'var(--bg-gray)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}><BookOpen size={12} /> {u.programs.length} Programs</span>}
              {u.tuitionCategory && <span style={{ background: 'var(--bg-gray)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem' }}>Tuition: {u.tuitionCategory}</span>}
            </div>
          </div>
        ))}
      </div>
      
      {filtered.length === 0 && (
        <div className="widget" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <p style={{ color: 'var(--text-gray)', fontSize: '1.125rem' }}>No universities match your filters.</p>
          <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => { setLocationFilter(''); setRankingFilter(''); setTypeFilter(''); setTuitionFilter(''); }}>Clear Filters</button>
        </div>
      )}
    </div>
  );
};

export default Universities;
