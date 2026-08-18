import React, { useState, useRef } from 'react';
import { useAppContext } from '../context/AppContext';
import { useStudentDocuments, useCreateDocument, useDeleteDocument } from '../hooks/useDocuments';
import { StudentAPI } from '../services/api/student.api';
import { Trash2, Upload, File, Download, AlertCircle, CloudOff } from 'lucide-react';
import EdutantLoader from '../components/ui/EdutantLoader';

const Documents = () => {
  const { searchQuery } = useAppContext();
  const { data: documents = [], isLoading, isError, error } = useStudentDocuments();
  const createMutation = useCreateDocument();
  const deleteMutation = useDeleteDocument();

  const [newDocType, setNewDocType] = useState('Academic');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadError, setUploadError] = useState('');
  const fileInputRef = useRef(null);

  const filtered = documents.filter(d => 
    (d.filename || '').toLowerCase().includes((searchQuery || '').toLowerCase())
  );

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        alert('File size exceeds the maximum limit of 10MB.');
        e.target.value = null;
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    setUploadError('');

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('doc_type', newDocType);

    createMutation.mutate(formData, {
      onSuccess: () => {
        setSelectedFile(null);
        setUploadError('');
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      },
      onError: (err) => {
        const detail = err.response?.data?.detail || err.message || 'Unknown upload error';
        setUploadError(detail);
      }
    });
  };

  const handleDownload = async (id) => {
    try {
      const url = await StudentAPI.getDocumentDownloadUrl(id);
      window.open(url, '_blank');
    } catch (err) {
      alert('Failed to obtain download URL: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to permanently delete this document? This will remove the file from cloud storage.')) {
      deleteMutation.mutate(id, {
        onError: (err) => {
          alert('Deletion failed: ' + (err.response?.data?.detail || err.message));
        }
      });
    }
  };

  const formatSize = (bytes) => {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (isLoading) {
    return (
      <div className="dashboard-content">
        <EdutantLoader variant="inline" message="Loading your documents..." />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="dashboard-content">
        <div className="page-header">
          <h1 className="page-title">Documents</h1>
        </div>
        <div className="widget" style={{ display: 'flex', gap: '0.75rem', color: '#ef4444', backgroundColor: '#fef2f2', border: '1px solid #fca5a5', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
          <AlertCircle size={20} />
          <span>Failed to load documents: {error?.response?.data?.detail || error.message || 'Unknown error'}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-content">
      <div className="page-header">
        <h1 className="page-title">Documents</h1>
        <p className="page-subtitle">Manage and upload your official application documents securely on Amazon S3.</p>
      </div>
      
      <div className="widgets-grid">
        <div className="widget">
          <div className="widget-header">
            <h3 className="widget-title">My S3 Documents</h3>
          </div>
          <div style={{ display: 'grid', gap: '1rem' }}>
            {filtered.map(d => (
              <div key={d.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ color: 'var(--primary-green)', background: 'var(--primary-green-light)', padding: '0.5rem', borderRadius: '50%' }}>
                    <File size={20} />
                  </div>
                  <div>
                    <h4 style={{ fontSize: '0.875rem', fontWeight: 600 }}>{d.filename}</h4>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-gray)' }}>
                      {d.doc_type} · {formatSize(d.file_size)} · Uploaded {d.upload_date}
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <span style={{ fontSize: '0.75rem', color: d.verified ? 'var(--primary-green)' : '#eab308', background: d.verified ? 'var(--primary-green-light)' : '#fef9c3', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>
                    {d.verified ? 'Verified' : 'Pending'}
                  </span>
                  <button 
                    className="icon-btn" 
                    onClick={() => handleDownload(d.id)}
                    style={{ color: 'var(--primary-green)' }}
                    title="Download File"
                  >
                    <Download size={18} />
                  </button>
                  <button 
                    className="icon-btn" 
                    onClick={() => handleDelete(d.id)} 
                    style={{ color: '#ef4444' }}
                    disabled={deleteMutation.isPending}
                    title="Delete File"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))}
            {filtered.length === 0 && <p style={{ color: 'var(--text-gray)', fontSize: '0.875rem' }}>No documents found.</p>}
          </div>
        </div>

        <div className="widget" style={{ height: 'fit-content' }}>
          <div className="widget-header">
            <h3 className="widget-title">Upload Document</h3>
          </div>
          <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Document Type</label>
              <select className="form-input" value={newDocType} onChange={(e) => setNewDocType(e.target.value)}>
                <option value="Academic">Academic</option>
                <option value="ID">ID / Passport</option>
                <option value="Language Test">Language Test</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Choose File</label>
              <input 
                type="file" 
                className="form-input" 
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                style={{ padding: '0.5rem 0.75rem' }}
                required
              />
              <span style={{ fontSize: '0.7rem', color: 'var(--text-gray)', marginTop: '0.25rem', display: 'block' }}>
                Allowed formats: PDF, DOC, DOCX, JPG, JPEG, PNG (max 10MB).
              </span>
            </div>
            {uploadError && (
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start', padding: '0.9rem 1rem', borderRadius: 'var(--radius-md)', background: uploadError.toLowerCase().includes('storage') || uploadError.toLowerCase().includes('s3') ? '#fff7ed' : '#fef2f2', border: uploadError.toLowerCase().includes('storage') || uploadError.toLowerCase().includes('s3') ? '1px solid #fdba74' : '1px solid #fca5a5', color: uploadError.toLowerCase().includes('storage') || uploadError.toLowerCase().includes('s3') ? '#9a3412' : '#b91c1c' }}>
                <CloudOff size={18} style={{ flexShrink: 0, marginTop: '0.1rem' }} />
                <div style={{ display: 'grid', gap: '0.25rem' }}>
                  <strong style={{ fontSize: '0.85rem' }}>
                    {uploadError.toLowerCase().includes('storage') || uploadError.toLowerCase().includes('s3')
                      ? 'Document storage is not available in this environment.'
                      : 'Upload failed.'}
                  </strong>
                  <span style={{ fontSize: '0.8rem', lineHeight: 1.4 }}>
                    {uploadError.toLowerCase().includes('storage') || uploadError.toLowerCase().includes('s3')
                      ? 'Uploads require a configured S3 bucket and valid AWS credentials on the backend.'
                      : uploadError}
                  </span>
                </div>
              </div>
            )}
            <button 
              type="submit" 
              className="btn btn-primary btn-block" 
              style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', justifyContent: 'center', alignItems: 'center' }}
              disabled={createMutation.isPending || !selectedFile}
            >
              <Upload size={18} /> {createMutation.isPending ? 'Uploading to S3...' : 'Upload File'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Documents;
