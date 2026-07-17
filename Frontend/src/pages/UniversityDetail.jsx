import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { ArrowLeft, Bookmark, MapPin, Award, Building2, BookOpen, Users, Globe } from 'lucide-react';

const UniversityDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { universities, toggleBookmark } = useAppContext();
  
  const university = universities.find(u => u.id === id);

  if (!university) {
    return (
      <div className="dashboard-content">
        <div className="widget" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <p style={{ color: 'var(--text-gray)', fontSize: '1.125rem' }}>University not found.</p>
          <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => navigate('/universities')}>Browse Universities</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-content">
      <button onClick={() => navigate(-1)} style={{ background: 'none', border: 'none', color: 'var(--text-gray)', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', marginBottom: '1.5rem', fontSize: '0.875rem', padding: '0.5rem', borderRadius: '4px' }} className="hover-bg-gray">
        <ArrowLeft size={16} /> Back to Search
      </button>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem' }}>
        <div className="widget" style={{ position: 'relative' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <span style={{ display: 'inline-flex', background: 'var(--bg-gray)', color: 'var(--text-dark)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.75rem', alignItems: 'center', gap: '0.25rem' }}>
                <Award size={14} /> {university.ranking}
              </span>
              <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem', lineHeight: 1.2 }}>{university.name}</h1>
              <p style={{ color: 'var(--text-gray)', fontSize: '1.125rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <MapPin size={20} /> {university.location}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className="btn" onClick={() => toggleBookmark('university', university.id)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: university.bookmarked ? 'var(--primary-green-light)' : 'var(--bg-gray)', color: university.bookmarked ? 'var(--primary-green)' : 'var(--text-dark)', border: 'none' }}>
                <Bookmark size={20} fill={university.bookmarked ? 'var(--primary-green)' : 'none'} />
                {university.bookmarked ? 'Saved' : 'Save'}
              </button>
              <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                Start Application
              </button>
            </div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', padding: '1.5rem', background: 'var(--bg-gray)', borderRadius: 'var(--radius-md)', marginBottom: '2rem' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Building2 size={16} /> Institution Type</p>
              <p style={{ fontWeight: 600, fontSize: '1.125rem' }}>{university.type}</p>
            </div>
            {university.tuitionCategory && (
              <div>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Globe size={16} /> Tuition Category</p>
                <p style={{ fontWeight: 600, fontSize: '1.125rem' }}>{university.tuitionCategory}</p>
              </div>
            )}
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Users size={16} /> Student Body</p>
              <p style={{ fontWeight: 600, fontSize: '1.125rem' }}>~30,000</p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><BookOpen size={16} /> Popular Programs</p>
              <p style={{ fontWeight: 600, fontSize: '1.125rem' }}>{university.programs?.length || 0} Listed</p>
            </div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <section>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-dark)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Overview</h3>
              <p style={{ color: 'var(--text-gray)', lineHeight: 1.7, fontSize: '1rem' }}>
                {university.name} is a premier {university.type.toLowerCase()} institution located in the heart of {university.location}. Recognized globally for its academic rigor, innovative research, and vibrant campus life, it continually ranks among the best universities worldwide. With state-of-the-art facilities and a diverse community, it provides an enriching environment for students to excel and grow.
              </p>
            </section>
            
            {university.programs && university.programs.length > 0 && (
              <section>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-dark)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Featured Programs</h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                  {university.programs.map((prog, idx) => (
                    <span key={idx} style={{ background: 'var(--primary-green-light)', color: 'var(--primary-green)', padding: '0.5rem 1rem', borderRadius: '100px', fontSize: '0.875rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                      <BookOpen size={14} /> {prog}
                    </span>
                  ))}
                </div>
              </section>
            )}

            <section>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-dark)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Key Facts</h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', color: 'var(--text-gray)', lineHeight: 1.5 }}>
                  <Award size={18} color="var(--primary-green)" style={{ marginTop: '0.125rem', flexShrink: 0 }} />
                  <span>Consistently ranked in the {university.ranking} worldwide for research and teaching quality.</span>
                </li>
                <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', color: 'var(--text-gray)', lineHeight: 1.5 }}>
                  <Building2 size={18} color="var(--primary-green)" style={{ marginTop: '0.125rem', flexShrink: 0 }} />
                  <span>Extensive campus with modern laboratories, libraries, and student recreation centers.</span>
                </li>
                <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', color: 'var(--text-gray)', lineHeight: 1.5 }}>
                  <Globe size={18} color="var(--primary-green)" style={{ marginTop: '0.125rem', flexShrink: 0 }} />
                  <span>Strong global alumni network and numerous international exchange partnerships.</span>
                </li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UniversityDetail;
