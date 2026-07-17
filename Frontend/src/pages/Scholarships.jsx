import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { Bookmark, MapPin, GraduationCap, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';

const Scholarships = () => {
  const { scholarships, toggleBookmark, searchQuery } = useAppContext();
  
  const [levelFilter, setLevelFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [amountFilter, setAmountFilter] = useState('');
  const [countryFilter, setCountryFilter] = useState('');

  const filtered = scholarships.filter(s => {
    const matchesSearch = s.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          s.provider.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesLevel = levelFilter ? s.studyLevel === levelFilter : true;
    const matchesType = typeFilter ? s.type === typeFilter : true;
    const matchesAmount = amountFilter ? s.amountCategory === amountFilter : true;
    const matchesCountry = countryFilter ? s.country === countryFilter : true;
    
    return matchesSearch && matchesLevel && matchesType && matchesAmount && matchesCountry;
  });

  return (
    <div className="dashboard-content">
      <div className="page-header">
        <h1 className="page-title">Scholarships</h1>
        <p className="page-subtitle">Find and apply for financial aid globally.</p>
      </div>
      
      <div className="widget" style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <select className="input-field" style={{ width: 'auto', minWidth: '150px' }} value={levelFilter} onChange={e => setLevelFilter(e.target.value)}>
          <option value="">All Study Levels</option>
          <option value="Undergraduate">Undergraduate</option>
          <option value="Postgraduate">Postgraduate</option>
        </select>
        <select className="input-field" style={{ width: 'auto', minWidth: '150px' }} value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
          <option value="">All Types</option>
          <option value="Merit-based">Merit-based</option>
          <option value="Need-based">Need-based</option>
          <option value="Diversity">Diversity</option>
        </select>
        <select className="input-field" style={{ width: 'auto', minWidth: '150px' }} value={amountFilter} onChange={e => setAmountFilter(e.target.value)}>
          <option value="">All Amounts</option>
          <option value="Partial">Partial Funding</option>
          <option value="Full">Full Tuition</option>
        </select>
        <select className="input-field" style={{ width: 'auto', minWidth: '150px' }} value={countryFilter} onChange={e => setCountryFilter(e.target.value)}>
          <option value="">All Countries</option>
          <option value="Canada">Canada</option>
          <option value="USA">USA</option>
          <option value="Australia">Australia</option>
        </select>
        {(levelFilter || typeFilter || amountFilter || countryFilter) && (
          <button className="btn" onClick={() => { setLevelFilter(''); setTypeFilter(''); setAmountFilter(''); setCountryFilter(''); }} style={{ background: 'none', color: 'var(--text-gray)', border: 'none', cursor: 'pointer' }}>Clear Filters</button>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {filtered.map(s => (
          <div key={s.id} className="widget" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', position: 'relative', transition: 'transform 0.2s, box-shadow 0.2s' }} onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = 'var(--shadow-md)'; }} onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = 'var(--shadow-sm)'; }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <span style={{ display: 'inline-block', background: 'var(--primary-green-light)', color: 'var(--primary-green)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.75rem' }}>{s.amount}</span>
                <h4 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.25rem', lineHeight: 1.3 }}>
                  <Link to={`/scholarships/${s.id}`} style={{ color: 'var(--text-dark)', textDecoration: 'none' }}>{s.title}</Link>
                </h4>
                <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <GraduationCap size={16} /> {s.provider}
                </p>
              </div>
              <button className="icon-btn" onClick={() => toggleBookmark('scholarship', s.id)} style={{ padding: '0.25rem', margin: '-0.25rem' }}>
                <Bookmark size={24} fill={s.bookmarked ? 'var(--primary-green)' : 'none'} color={s.bookmarked ? 'var(--primary-green)' : 'var(--text-gray)'} />
              </button>
            </div>
            
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', fontSize: '0.875rem', color: 'var(--text-gray)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><MapPin size={16} /> {s.country || 'Global'}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Calendar size={16} color="#ef4444" /> <span style={{ color: '#ef4444' }}>{s.deadline}</span></div>
            </div>
            
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <span style={{ background: 'var(--bg-gray)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem' }}>{s.type}</span>
              {s.studyLevel && <span style={{ background: 'var(--bg-gray)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem' }}>{s.studyLevel}</span>}
            </div>
          </div>
        ))}
      </div>
      
      {filtered.length === 0 && (
        <div className="widget" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <p style={{ color: 'var(--text-gray)', fontSize: '1.125rem' }}>No scholarships match your filters.</p>
          <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => { setLevelFilter(''); setTypeFilter(''); setAmountFilter(''); setCountryFilter(''); }}>Clear Filters</button>
        </div>
      )}
    </div>
  );
};

export default Scholarships;
