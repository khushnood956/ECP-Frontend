import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useCreateLead } from '../hooks/useLeads';
import { Button } from './shared/Button';
import { Input } from './shared/Input';
import { Textarea } from './shared/Textarea';
import { Label } from './shared/Label';
import { StudentAPI } from '../services/api/student.api';

export const ApplyModal = ({ scholarship, onClose }) => {
  const [formData, setFormData] = useState({
    motivation_letter: '',
    notes: '',
    documents: ''
  });
  
  const [customResponses, setCustomResponses] = useState({});
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  
  const createLeadMutation = useCreateLead();

  const handleCustomChange = (requirementId, value) => {
    setCustomResponses(prev => ({
      ...prev,
      [requirementId]: value
    }));
  };

  const handleFileUpload = async (requirementId, file) => {
    if (!file) return;
    try {
      const form = new FormData();
      form.append('file', file);
      form.append('doc_type', 'Application Material');
      // Currently using document upload API for custom files as well, 
      // or we can just store the S3 URL returned.
      const uploaded = await StudentAPI.createDocument(form);
      handleCustomChange(requirementId, uploaded.file_url);
    } catch (err) {
      console.error('File upload failed', err);
      setErrorMsg('Failed to upload file. Please try again.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);
    
    // Validate required custom fields
    if (scholarship.application_requirements) {
      for (const req of scholarship.application_requirements) {
        if (req.is_required && !customResponses[req.id]) {
          setErrorMsg(`Please fill out the required field: ${req.label}`);
          return;
        }
      }
    }

    try {
      const application_responses = scholarship.application_requirements?.map(req => {
        const val = customResponses[req.id];
        return {
          requirement_id: req.id,
          value: req.field_type !== 'file' ? val : null,
          file_url: req.field_type === 'file' ? val : null
        };
      }) || [];

      await createLeadMutation.mutateAsync({
        scholarship_id: scholarship.id,
        motivation_letter: formData.motivation_letter || null,
        notes: formData.notes || null,
        documents: formData.documents || null,
        application_responses
      });
      
      setSuccessMsg('Application submitted successfully!');
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Failed to submit application.';
      setErrorMsg(msg);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div style={{
        backgroundColor: 'var(--bg-white)',
        borderRadius: 'var(--radius-lg)',
        width: '100%',
        maxWidth: '600px',
        maxHeight: '90vh',
        overflowY: 'auto',
        position: 'relative'
      }}>
        <button 
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1.5rem',
            right: '1.5rem',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: 'var(--text-gray)'
          }}
        >
          <X size={24} />
        </button>
        
        <div style={{ padding: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-dark)' }}>
            Apply for Scholarship
          </h2>
          <p style={{ color: 'var(--text-gray)', marginBottom: '2rem' }}>
            {scholarship.title}
          </p>

          {errorMsg && <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>{errorMsg}</div>}
          {successMsg && <div className="alert alert-success" style={{ marginBottom: '1.5rem' }}>{successMsg}</div>}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="form-group">
              <Label>Motivation Letter</Label>
              <Textarea 
                rows={4}
                value={formData.motivation_letter}
                onChange={e => setFormData({...formData, motivation_letter: e.target.value})}
                placeholder="Why are you a good fit for this scholarship?"
              />
            </div>
            
            <div className="form-group">
              <Label>Additional Notes</Label>
              <Textarea 
                rows={2}
                value={formData.notes}
                onChange={e => setFormData({...formData, notes: e.target.value})}
                placeholder="Any extra information..."
              />
            </div>

            {scholarship.application_requirements?.length > 0 && (
              <>
                <div style={{ height: '1px', backgroundColor: 'var(--border-color)', margin: '0.5rem 0' }}></div>
                <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-dark)' }}>Custom Requirements</h3>
                
                {scholarship.application_requirements.map(req => (
                  <div key={req.id} className="form-group">
                    <Label>{req.label} {req.is_required && '*'}</Label>
                    
                    {req.field_type === 'text' && (
                      <Input 
                        value={customResponses[req.id] || ''}
                        onChange={e => handleCustomChange(req.id, e.target.value)}
                        required={req.is_required}
                      />
                    )}
                    
                    {req.field_type === 'textarea' && (
                      <Textarea 
                        value={customResponses[req.id] || ''}
                        onChange={e => handleCustomChange(req.id, e.target.value)}
                        required={req.is_required}
                      />
                    )}
                    
                    {req.field_type === 'select' && (
                      <select
                        value={customResponses[req.id] || ''}
                        onChange={e => handleCustomChange(req.id, e.target.value)}
                        required={req.is_required}
                        style={{
                          width: '100%',
                          padding: '0.625rem',
                          borderRadius: 'var(--radius-md)',
                          border: '1px solid var(--border-color)',
                          backgroundColor: 'var(--bg-white)',
                          color: 'var(--text-dark)',
                          fontSize: '0.875rem'
                        }}
                      >
                        <option value="">Select an option</option>
                        {req.options?.split(',').map(opt => (
                          <option key={opt.trim()} value={opt.trim()}>{opt.trim()}</option>
                        ))}
                      </select>
                    )}
                    
                    {req.field_type === 'file' && (
                      <div>
                        <input 
                          type="file" 
                          onChange={e => handleFileUpload(req.id, e.target.files[0])} 
                          required={req.is_required && !customResponses[req.id]}
                          style={{
                            display: 'block',
                            width: '100%',
                            padding: '0.5rem',
                            border: '1px dashed var(--border-color)',
                            borderRadius: 'var(--radius-md)',
                            cursor: 'pointer'
                          }}
                        />
                        {customResponses[req.id] && (
                          <p style={{ fontSize: '0.875rem', color: 'var(--primary-green)', marginTop: '0.5rem' }}>
                            File uploaded successfully!
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
              <Button type="button" variant="outline" onClick={onClose} disabled={createLeadMutation.isPending}>
                Cancel
              </Button>
              <Button type="submit" isLoading={createLeadMutation.isPending}>
                Submit Application
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
