import React, { useState } from 'react';
import { useStudentUniversities } from '../hooks/useUniversities';
import { Bookmark, MapPin, Award, BookOpen, Building2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';

const Universities = () => {
  const { searchQuery } = useAppContext();
  
  const [locationFilter, setLocationFilter] = useState('');
  const [rankingFilter, setRankingFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [tuitionFilter, setTuitionFilter] = useState('');

  // Map only supported server-side filter to API request
  const apiFilters = {};
  if (locationFilter) {
    apiFilters.location = locationFilter;
  }

  const { data: dbUnis, isLoading, error } = useStudentUniversities(apiFilters);

  // Client-side text search and extra property filtering
  const filtered = (dbUnis || []).filter(u => {
    const matchesSearch = u.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          u.location.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRanking = rankingFilter ? u.ranking === rankingFilter : true;
    const matchesType = typeFilter ? u.type === typeFilter : true;
    const matchesTuition = tuitionFilter ? u.tuition_category === tuitionFilter : true;
    
    return matchesSearch && matchesRanking && matchesType && matchesTuition;
  });

  const clearFilters = () => {
    setLocationFilter('');
    setRankingFilter('');
    setTypeFilter('');
    setTuitionFilter('');
  };

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
          <button className="btn" onClick={clearFilters} style={{ background: 'none', color: 'var(--text-gray)', border: 'none', cursor: 'pointer' }}>Clear Filters</button>
        )}
      </div>

      {isLoading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {[...Array(3)].map((_, i) => (
            <div key={i} className="widget" style={{ height: '180px', backgroundColor: 'var(--bg-white)', borderRadius: 'var(--radius-lg)' }}>
              <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ height: '16px', width: '60px', backgroundColor: 'var(--bg-gray)', borderRadius: '4px' }}></div>
                <div style={{ height: '24px', width: '80%', backgroundColor: 'var(--bg-gray)', borderRadius: '4px' }}></div>
                <div style={{ height: '20px', width: '50%', backgroundColor: 'var(--bg-gray)', borderRadius: '4px' }}></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
          Failed to load universities. Please try again.
        </div>
      )}

      {!isLoading && !error && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {filtered.map(u => (
            <div key={u.id} className="widget" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', position: 'relative', transition: 'transform 0.2s, box-shadow 0.2s' }} onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = 'var(--shadow-md)'; }} onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = 'var(--shadow-sm)'; }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  {u.ranking && (
                    <span style={{ display: 'inline-flex', background: 'var(--bg-gray)', color: 'var(--text-dark)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.75rem', alignItems: 'center', gap: '0.25rem' }}>
                      <Award size={14} /> {u.ranking}
                    </span>
                  )}
                  <h4 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.25rem', lineHeight: 1.3 }}>
                    <Link to={`/universities/${u.id}`} style={{ color: 'var(--text-dark)', textDecoration: 'none' }}>{u.name}</Link>
                  </h4>
                  <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <MapPin size={16} /> {u.location}
                  </p>
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
                {u.type && <span style={{ background: 'var(--bg-gray)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Building2 size={12} /> {u.type}</span>}
                {u.programs && <span style={{ background: 'var(--bg-gray)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}><BookOpen size={12} /> {u.programs.length} Programs</span>}
                {u.tuition_category && <span style={{ background: 'var(--bg-gray)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem' }}>Tuition: {u.tuition_category}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
      
      {!isLoading && !error && filtered.length === 0 && (
        <div className="widget" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <p style={{ color: 'var(--text-gray)', fontSize: '1.125rem' }}>No universities match your filters.</p>
          <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={clearFilters}>Clear Filters</button>
        </div>
      )}
    </div>
  );
};

export default Universities;
