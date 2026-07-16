import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { Trash2, Upload, File } from 'lucide-react';

const Documents = () => {
  const { documents, addDocument, deleteDocument, searchQuery } = useAppContext();
  const [newDocName, setNewDocName] = useState('');
  const [newDocType, setNewDocType] = useState('Academic');

  const filtered = documents.filter(d => 
    d.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleUpload = (e) => {
    e.preventDefault();
    if (!newDocName) return;
    addDocument({ name: newDocName, type: newDocType });
    setNewDocName('');
  };

  return (
    <div className="dashboard-content">
      <div className="page-header">
        <h1 className="page-title">Documents</h1>
        <p className="page-subtitle">Manage your application files securely.</p>
      </div>
      
      <div className="widgets-grid">
        <div className="widget">
          <div className="widget-header">
            <h3 className="widget-title">My Documents</h3>
          </div>
          <div style={{ display: 'grid', gap: '1rem' }}>
            {filtered.map(d => (
              <div key={d.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ color: 'var(--primary-green)', background: 'var(--primary-green-light)', padding: '0.5rem', borderRadius: '50%' }}>
                    <File size={20} />
                  </div>
                  <div>
                    <h4 style={{ fontSize: '0.875rem', fontWeight: 600 }}>{d.name}</h4>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-gray)' }}>{d.type} • Uploaded {d.uploadDate}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <span style={{ fontSize: '0.75rem', color: d.verified ? 'var(--primary-green)' : '#eab308', background: d.verified ? 'var(--primary-green-light)' : '#fef9c3', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>
                    {d.verified ? 'Verified' : 'Pending'}
                  </span>
                  <button className="icon-btn" onClick={() => deleteDocument(d.id)} style={{ color: '#ef4444' }}>
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))}
            {filtered.length === 0 && <p>No documents found.</p>}
          </div>
        </div>

        <div className="widget" style={{ height: 'fit-content' }}>
          <div className="widget-header">
            <h3 className="widget-title">Upload Document</h3>
          </div>
          <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Document Name</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="e.g. Passport.pdf" 
                value={newDocName}
                onChange={(e) => setNewDocName(e.target.value)}
              />
            </div>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Document Type</label>
              <select className="form-input" value={newDocType} onChange={(e) => setNewDocType(e.target.value)}>
                <option value="Academic">Academic</option>
                <option value="ID">ID / Passport</option>
                <option value="Language Test">Language Test</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <button type="submit" className="btn btn-primary btn-block" style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem' }}>
              <Upload size={18} /> Upload File
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Documents;
