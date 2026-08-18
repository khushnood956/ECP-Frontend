import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useStudentUniversity } from '../hooks/useUniversities';
import { ArrowLeft, MapPin, Award, Building2, BookOpen, Globe, Bookmark } from 'lucide-react';
import { formatNullable } from '../utils/formatters';
import { useStudentBookmarks, useCreateBookmark, useDeleteBookmark } from '../hooks/useBookmarks';

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

const UniversityDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const { data: university, isLoading, error } = useStudentUniversity(id || '');

  if (isLoading) {
    return (
      <div className="dashboard-content">
        <div style={{ height: '36px', width: '120px', backgroundColor: 'var(--bg-gray)', borderRadius: '4px', marginBottom: '1.5rem' }}></div>
        <div className="widget" style={{ height: '350px' }}></div>
      </div>
    );
  }

  if (error || !university) {
    return (
      <div className="dashboard-content">
        <button onClick={() => navigate('/universities')} style={{ background: 'none', border: 'none', color: 'var(--text-gray)', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', marginBottom: '1.5rem', fontSize: '0.875rem', padding: '0.5rem', borderRadius: '4px' }} className="hover-bg-gray">
          <ArrowLeft size={16} /> Back to Search
        </button>
        <div className="widget" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <p style={{ color: 'var(--text-gray)', fontSize: '1.125rem' }}>University not found.</p>
          <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => navigate('/universities')}>Browse Universities</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-content">
      <button onClick={() => navigate('/universities')} style={{ background: 'none', border: 'none', color: 'var(--text-gray)', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', marginBottom: '1.5rem', fontSize: '0.875rem', padding: '0.5rem', borderRadius: '4px' }} className="hover-bg-gray">
        <ArrowLeft size={16} /> Back to Search
      </button>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem' }}>
        <div className="widget" style={{ position: 'relative' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem', width: '100%' }}>
            <div>
              {university.ranking && (
                <span style={{ display: 'inline-flex', background: 'var(--bg-gray)', color: 'var(--text-dark)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.75rem', alignItems: 'center', gap: '0.25rem' }}>
                  <Award size={14} /> {university.ranking}
                </span>
              )}
              <h1 style={{ fontSize: '2.25rem', fontWeight: 800, marginBottom: '0.5rem', lineHeight: 1.2 }}>{university.name}</h1>
              <p style={{ color: 'var(--text-gray)', fontSize: '1.125rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <MapPin size={20} /> {university.location}
              </p>
            </div>
            <BookmarkButton type="university" resourceId={university.id} />
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', padding: '1.5rem', background: 'var(--bg-gray)', borderRadius: 'var(--radius-md)', marginBottom: '2rem' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Building2 size={16} /> Institution Type</p>
              <p style={{ fontWeight: 600, fontSize: '1.125rem' }}>{formatNullable(university.type)}</p>
            </div>
            {university.tuition_category && (
              <div>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Globe size={16} /> Tuition Category</p>
                <p style={{ fontWeight: 600, fontSize: '1.125rem' }}>{university.tuition_category}</p>
              </div>
            )}
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><BookOpen size={16} /> Featured Programs</p>
              <p style={{ fontWeight: 600, fontSize: '1.125rem' }}>{university.programs?.length || 0} Programs</p>
            </div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <section>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-dark)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Overview</h3>
              <p style={{ color: 'var(--text-gray)', lineHeight: 1.7, fontSize: '1rem' }}>
                {university.name} is a premier {university.type ? university.type.toLowerCase() : 'academic'} institution located in {university.location}. Recognized globally for its academic rigor, innovative research, and vibrant campus life, it continually ranks among the best universities worldwide. With state-of-the-art facilities and a diverse community, it provides an enriching environment for students to excel and grow.
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
                  <span>Consistently ranked in the {university.ranking || 'top tiers'} worldwide for research and teaching quality.</span>
                </li>
                <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', color: 'var(--text-gray)', lineHeight: 1.5 }}>
                  <MapPin size={18} color="var(--primary-green)" style={{ marginTop: '0.125rem', flexShrink: 0 }} />
                  <span>Located in a highly desirable, globally connected region in {university.location}.</span>
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
