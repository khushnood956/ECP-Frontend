import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { ArrowLeft, Bookmark, Calendar, DollarSign, GraduationCap, MapPin, CheckCircle, Info } from 'lucide-react';

const ScholarshipDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { scholarships, toggleBookmark } = useAppContext();
  
  const scholarship = scholarships.find(s => s.id === id);

  if (!scholarship) {
    return (
      <div className="dashboard-content">
        <div className="widget" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <p style={{ color: 'var(--text-gray)', fontSize: '1.125rem' }}>Scholarship not found.</p>
          <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => navigate('/scholarships')}>Browse Scholarships</button>
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
              <span style={{ display: 'inline-block', background: 'var(--primary-green-light)', color: 'var(--primary-green)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.75rem' }}>{scholarship.amountCategory || 'Funding Available'}</span>
              <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem', lineHeight: 1.2 }}>{scholarship.title}</h1>
              <p style={{ color: 'var(--text-gray)', fontSize: '1.125rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <GraduationCap size={20} /> {scholarship.provider}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className="btn" onClick={() => toggleBookmark('scholarship', scholarship.id)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: scholarship.bookmarked ? 'var(--primary-green-light)' : 'var(--bg-gray)', color: scholarship.bookmarked ? 'var(--primary-green)' : 'var(--text-dark)', border: 'none' }}>
                <Bookmark size={20} fill={scholarship.bookmarked ? 'var(--primary-green)' : 'none'} />
                {scholarship.bookmarked ? 'Saved' : 'Save'}
              </button>
              <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                Apply Now
              </button>
            </div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', padding: '1.5rem', background: 'var(--bg-gray)', borderRadius: 'var(--radius-md)', marginBottom: '2rem' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><DollarSign size={16} /> Amount</p>
              <p style={{ fontWeight: 600, color: 'var(--primary-green)', fontSize: '1.125rem' }}>{scholarship.amount}</p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Calendar size={16} /> Deadline</p>
              <p style={{ fontWeight: 600, color: '#ef4444', fontSize: '1.125rem' }}>{scholarship.deadline}</p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Info size={16} /> Type</p>
              <p style={{ fontWeight: 600, fontSize: '1.125rem' }}>{scholarship.type}</p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><MapPin size={16} /> Location</p>
              <p style={{ fontWeight: 600, fontSize: '1.125rem' }}>{scholarship.country || 'Global'}</p>
            </div>
            {scholarship.studyLevel && (
              <div>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><GraduationCap size={16} /> Study Level</p>
                <p style={{ fontWeight: 600, fontSize: '1.125rem' }}>{scholarship.studyLevel}</p>
              </div>
            )}
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <section>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-dark)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Overview</h3>
              <p style={{ color: 'var(--text-gray)', lineHeight: 1.7, fontSize: '1rem' }}>
                The {scholarship.title} is a prestigious award provided by {scholarship.provider} designed to support exceptional students who demonstrate academic excellence, leadership potential, and a commitment to their community. This {scholarship.type.toLowerCase()} opportunity provides {scholarship.amount} to help alleviate the financial burden of higher education and allow students to focus on their studies and extracurricular pursuits.
              </p>
            </section>
            
            <section>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-dark)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Eligibility & Requirements</h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', color: 'var(--text-gray)', lineHeight: 1.5 }}>
                  <CheckCircle size={18} color="var(--primary-green)" style={{ marginTop: '0.125rem', flexShrink: 0 }} />
                  <span>Must be enrolling in a full-time {scholarship.studyLevel ? scholarship.studyLevel.toLowerCase() : 'degree'} program for the upcoming academic year.</span>
                </li>
                <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', color: 'var(--text-gray)', lineHeight: 1.5 }}>
                  <CheckCircle size={18} color="var(--primary-green)" style={{ marginTop: '0.125rem', flexShrink: 0 }} />
                  <span>Maintain a minimum GPA of 3.5 or equivalent academic standing.</span>
                </li>
                <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', color: 'var(--text-gray)', lineHeight: 1.5 }}>
                  <CheckCircle size={18} color="var(--primary-green)" style={{ marginTop: '0.125rem', flexShrink: 0 }} />
                  <span>Submit a comprehensive personal statement and two letters of recommendation.</span>
                </li>
                <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', color: 'var(--text-gray)', lineHeight: 1.5 }}>
                  <CheckCircle size={18} color="var(--primary-green)" style={{ marginTop: '0.125rem', flexShrink: 0 }} />
                  <span>Meet all standard admission requirements for {scholarship.provider}.</span>
                </li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScholarshipDetail;
