
import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { Bookmark, MapPin, GraduationCap, Calendar, ChevronDown, X, ListFilter } from 'lucide-react';
import { Link } from 'react-router-dom';

// A single styled filter dropdown: icon + label + custom chevron, card-consistent look
// `options` accepts either an array of strings, or an array of { value, label } objects
const FilterSelect = ({ icon: Icon, label, value, onChange, options }) => {
  const isActive = value !== '';
  const normalized = options.map(opt =>
    typeof opt === 'string' ? { value: opt, label: opt } : opt
  );

  return (
    <div style={{ position: 'relative', flex: '1 1 180px', minWidth: '170px' }}>
      <label
        style={{
          display: 'block',
          fontSize: '0.7rem',
          fontWeight: 600,
          color: isActive ? 'var(--primary-green)' : 'var(--text-gray)',
          textTransform: 'uppercase',
          letterSpacing: '0.03em',
          marginBottom: '0.35rem',
          transition: 'color 0.15s',
        }}
      >
        {label}
      </label>

      <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
        <Icon
          size={16}
          color={isActive ? 'var(--primary-green)' : 'var(--text-gray)'}
          style={{ position: 'absolute', left: '0.75rem', pointerEvents: 'none' }}
        />
        <select
          value={value}
          onChange={onChange}
          style={{
            width: '100%',
            appearance: 'none',
            WebkitAppearance: 'none',
            background: isActive ? 'var(--primary-green-light)' : '#fff',
            border: `1px solid ${isActive ? 'var(--primary-green)' : 'var(--border-color)'}`,
            borderRadius: '10px',
            padding: '0.6rem 2rem 0.6rem 2.25rem',
            fontSize: '0.875rem',
            fontWeight: isActive ? 600 : 500,
            color: isActive ? 'var(--primary-green)' : 'var(--text-dark)',
            cursor: 'pointer',
            outline: 'none',
            transition: 'border-color 0.15s, box-shadow 0.15s, background 0.15s',
          }}
          onFocus={e => { e.currentTarget.style.boxShadow = '0 0 0 3px var(--primary-green-light)'; e.currentTarget.style.borderColor = 'var(--primary-green)'; }}
          onBlur={e => { e.currentTarget.style.boxShadow = 'none'; if (!isActive) e.currentTarget.style.borderColor = 'var(--border-color)'; }}
        >
          <option value="">{`All ${label}`}</option>
          {normalized.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <ChevronDown
          size={16}
          color={isActive ? 'var(--primary-green)' : 'var(--text-gray)'}
          style={{ position: 'absolute', right: '0.75rem', pointerEvents: 'none' }}
        />
      </div>
    </div>
  );
};

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

  const activeFilterCount = [levelFilter, typeFilter, amountFilter, countryFilter].filter(Boolean).length;

  const clearFilters = () => {
    setLevelFilter('');
    setTypeFilter('');
    setAmountFilter('');
    setCountryFilter('');
  };

  return (
    <div className="dashboard-content">
      <div className="page-header">
        <h1 className="page-title">Scholarships</h1>
        <p className="page-subtitle">Find and apply for financial aid globally.</p>
      </div>

      <div
        className="widget"
        style={{
          marginBottom: '1.5rem',
          padding: '1.25rem 1.5rem',
          display: 'flex',
          gap: '1.25rem',
          flexWrap: 'wrap',
          alignItems: 'flex-end',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-gray)', paddingBottom: '0.6rem' }}>
          <ListFilter size={18} />
          <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>Filters</span>
        </div>

        <FilterSelect
          icon={GraduationCap}
          label="Study Levels"
          value={levelFilter}
          onChange={e => setLevelFilter(e.target.value)}
          options={['Undergraduate', 'Postgraduate']}
        />
        <FilterSelect
          icon={ListFilter}
          label="Types"
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value)}
          options={['Merit-based', 'Need-based', 'Diversity']}
        />
        <FilterSelect
          icon={Bookmark}
          label="Amounts"
          value={amountFilter}
          onChange={e => setAmountFilter(e.target.value)}
          options={[
            { value: 'Partial', label: 'Partial Funding' },
            { value: 'Full', label: 'Full Tuition' },
          ]}
        />
        <FilterSelect
          icon={MapPin}
          label="Countries"
          value={countryFilter}
          onChange={e => setCountryFilter(e.target.value)}
          options={['Canada', 'USA', 'Australia']}
        />

        {activeFilterCount > 0 && (
          <button
            onClick={clearFilters}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              background: 'none',
              border: 'none',
              color: 'var(--text-gray)',
              fontSize: '0.8125rem',
              fontWeight: 600,
              cursor: 'pointer',
              padding: '0.6rem 0.25rem',
              marginBottom: '0.05rem',
            }}
            onMouseEnter={e => { e.currentTarget.style.color = '#ef4444'; }}
            onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-gray)'; }}
          >
            <X size={14} /> Clear ({activeFilterCount})
          </button>
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
          <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={clearFilters}>Clear Filters</button>
        </div>
      )}
    </div>
  );
};

export default Scholarships;