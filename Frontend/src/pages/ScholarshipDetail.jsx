import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useStudentScholarship } from '../hooks/useScholarships';
import { ArrowLeft, Calendar, DollarSign, GraduationCap, MapPin, CheckCircle, Info, FileText, Bookmark } from 'lucide-react';
import { formatDate, formatCurrency, formatNullable } from '../utils/formatters';
import { useStudentBookmarks, useCreateBookmark, useDeleteBookmark } from '../hooks/useBookmarks';
import { ApplyModal } from '../components/ApplyModal';

const BookmarkButton = ({ type, resourceId }) => {
  const { data: bookmarks = [] } = useStudentBookmarks();
  const createMutation = useCreateBookmark();
  const deleteMutation = useDeleteBookmark();

  const bookmark = bookmarks.find(b => b.bookmark_type === type && (b.scholarship_id === resourceId || b.university_id === resourceId));
  const isBookmarked = !!bookmark;

  const handleToggle = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (isBookmarked) {
      deleteMutation.mutate(bookmark.id);
    } else {
      createMutation.mutate({
        bookmarkType: type,
        scholarshipId: type === 'scholarship' ? resourceId : null,
        universityId: type === 'university' ? resourceId : null
      });
    }
  };

  return (
    <button
      onClick={handleToggle}
      style={{
        background: 'none',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        cursor: 'pointer',
        color: isBookmarked ? 'var(--primary-green)' : 'var(--text-gray)',
        transition: 'all 0.15s ease',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '0.75rem',
        backgroundColor: 'var(--bg-white)',
      }}
      onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.05)'; e.currentTarget.style.borderColor = 'var(--primary-green)'; }}
      onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.borderColor = 'var(--border-color)'; }}
      disabled={createMutation.isPending || deleteMutation.isPending}
      title={isBookmarked ? "Remove Bookmark" : "Bookmark this"}
    >
      <Bookmark size={20} fill={isBookmarked ? 'var(--primary-green)' : 'none'} />
    </button>
  );
};

const ScholarshipDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: scholarship, isLoading, error } = useStudentScholarship(id || '');
  const [showApplyModal, setShowApplyModal] = useState(false);
  
  if (isLoading) {
    return (
      <div className="dashboard-content">
        <div style={{ height: '36px', width: '120px', backgroundColor: 'var(--bg-gray)', borderRadius: '4px', marginBottom: '1.5rem' }}></div>
        <div className="widget" style={{ height: '350px' }}></div>
      </div>
    );
  }

  if (error || !scholarship) {
    return (
      <div className="dashboard-content">
        <button onClick={() => navigate('/scholarships')} style={{ background: 'none', border: 'none', color: 'var(--text-gray)', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', marginBottom: '1.5rem', fontSize: '0.875rem', padding: '0.5rem', borderRadius: '4px' }} className="hover-bg-gray">
          <ArrowLeft size={16} /> Back to Search
        </button>
        <div className="widget" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <p style={{ color: 'var(--text-gray)', fontSize: '1.125rem' }}>Scholarship not found.</p>
          <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => navigate('/scholarships')}>Browse Scholarships</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-content">
      <button onClick={() => navigate('/scholarships')} style={{ background: 'none', border: 'none', color: 'var(--text-gray)', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', marginBottom: '1.5rem', fontSize: '0.875rem', padding: '0.5rem', borderRadius: '4px' }} className="hover-bg-gray">
        <ArrowLeft size={16} /> Back to Search
      </button>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem' }}>
        <div className="widget" style={{ position: 'relative' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <span style={{ display: 'inline-block', background: 'var(--primary-green-light)', color: 'var(--primary-green)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.75rem' }}>
                {formatCurrency(scholarship.amount, scholarship.currency, 'Funding Available')}
              </span>
              <h1 style={{ fontSize: '2.125rem', fontWeight: 800, marginBottom: '0.5rem', lineHeight: 1.2 }}>{scholarship.title}</h1>
              <p style={{ color: 'var(--text-gray)', fontSize: '1.125rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <GraduationCap size={20} /> {scholarship.university || 'Various Universities'}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <button 
                onClick={() => setShowApplyModal(true)} 
                className="btn btn-primary" 
                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
              >
                Apply Now
              </button>
              {scholarship.application_link && (
                <a 
                  href={scholarship.application_link} 
                  target="_blank" 
                  rel="noreferrer" 
                  className="btn btn-outline" 
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}
                >
                  External Link
                </a>
              )}
              <BookmarkButton type="scholarship" resourceId={scholarship.id} />
            </div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', padding: '1.5rem', background: 'var(--bg-gray)', borderRadius: 'var(--radius-md)', marginBottom: '2rem' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><DollarSign size={16} /> Amount</p>
              <p style={{ fontWeight: 600, color: 'var(--primary-green)', fontSize: '1.125rem' }}>
                {formatCurrency(scholarship.amount, scholarship.currency)}
              </p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Calendar size={16} /> Deadline</p>
              <p style={{ fontWeight: 600, color: '#ef4444', fontSize: '1.125rem' }}>{formatDate(scholarship.deadline)}</p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Info size={16} /> Type</p>
              <p style={{ fontWeight: 600, fontSize: '1.125rem', textTransform: 'capitalize' }}>
                {scholarship.funding_type.replace('_', ' ')}
              </p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><MapPin size={16} /> Location</p>
              <p style={{ fontWeight: 600, fontSize: '1.125rem' }}>{scholarship.country || 'Global'}</p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><GraduationCap size={16} /> Study Level</p>
              <p style={{ fontWeight: 600, fontSize: '1.125rem', textTransform: 'capitalize' }}>
                {scholarship.degree_level.replace('_', ' ')}
              </p>
            </div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <section>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-dark)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Description</h3>
              <p style={{ color: 'var(--text-dark)', lineHeight: 1.7, fontSize: '1rem', whiteSpace: 'pre-wrap' }}>
                {formatNullable(scholarship.description, 'No description provided.')}
              </p>
            </section>
            
            <section>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-dark)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Eligibility & Requirements</h3>
              <p style={{ color: 'var(--text-dark)', lineHeight: 1.7, fontSize: '1rem', whiteSpace: 'pre-wrap' }}>
                {formatNullable(scholarship.eligibility, 'No eligibility criteria specified.')}
              </p>
            </section>
          </div>
        </div>
      </div>

      {showApplyModal && (
        <ApplyModal 
          scholarship={scholarship} 
          onClose={() => setShowApplyModal(false)} 
        />
      )}
    </div>
  );
};

export default ScholarshipDetail;
