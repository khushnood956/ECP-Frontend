import React from 'react';
import { Button } from '../../components/shared/Button';
import { Input } from '../../components/shared/Input';
import { Label } from '../../components/shared/Label';
import { Plus, Trash2, GripVertical } from 'lucide-react';

export const ApplicationRequirementsBuilder = ({ requirements, setRequirements }) => {
  const addRequirement = () => {
    setRequirements([
      ...requirements,
      {
        field_key: `field_${Date.now()}`,
        label: '',
        field_type: 'text',
        is_required: true,
        options: '',
        display_order: requirements.length,
      }
    ]);
  };

  const removeRequirement = (index) => {
    const newReqs = [...requirements];
    newReqs.splice(index, 1);
    // update display order
    newReqs.forEach((r, i) => r.display_order = i);
    setRequirements(newReqs);
  };

  const updateRequirement = (index, field, value) => {
    const newReqs = [...requirements];
    newReqs[index][field] = value;
    if (field === 'label' && !newReqs[index].field_key.startsWith('field_')) {
        // optionally update field_key based on label if desired, but keeping it fixed is safer
    }
    setRequirements(newReqs);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-dark)' }}>Application Requirements</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-gray)' }}>Define custom fields that students must fill out when applying.</p>
        </div>
        <Button type="button" onClick={addRequirement} variant="outline" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Plus size={16} /> Add Field
        </Button>
      </div>

      {requirements.length === 0 ? (
        <div style={{ padding: '2rem', textAlign: 'center', backgroundColor: 'var(--bg-gray)', borderRadius: 'var(--radius-md)', color: 'var(--text-gray)' }}>
          No custom requirements defined. Students will only provide default information.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {requirements.map((req, index) => (
            <div key={req.field_key} style={{ 
              display: 'flex', 
              gap: '1rem', 
              padding: '1.5rem', 
              backgroundColor: 'var(--bg-white)', 
              border: '1px solid var(--border-color)', 
              borderRadius: 'var(--radius-md)',
              alignItems: 'flex-start'
            }}>
              <div style={{ padding: '0.5rem', cursor: 'grab', color: 'var(--text-gray)' }}>
                <GripVertical size={20} />
              </div>
              <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <Label>Field Label</Label>
                  <Input 
                    value={req.label} 
                    onChange={(e) => updateRequirement(index, 'label', e.target.value)} 
                    placeholder="e.g. Motivation Letter, Transcript"
                    required
                  />
                </div>
                <div className="form-group">
                  <Label>Field Type</Label>
                  <select
                    value={req.field_type}
                    onChange={(e) => updateRequirement(index, 'field_type', e.target.value)}
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
                    <option value="text">Short Text</option>
                    <option value="textarea">Long Text (Textarea)</option>
                    <option value="file">File Upload</option>
                    <option value="select">Dropdown Select</option>
                  </select>
                </div>
                {req.field_type === 'select' && (
                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <Label>Dropdown Options (Comma separated)</Label>
                    <Input 
                      value={req.options || ''} 
                      onChange={(e) => updateRequirement(index, 'options', e.target.value)} 
                      placeholder="e.g. Option 1, Option 2, Option 3"
                    />
                  </div>
                )}
                <div className="form-group" style={{ gridColumn: 'span 2', display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '0.5rem', marginBottom: 0 }}>
                  <input 
                    type="checkbox" 
                    id={`req_${index}`} 
                    checked={req.is_required}
                    onChange={(e) => updateRequirement(index, 'is_required', e.target.checked)}
                    style={{ width: '1rem', height: '1rem', cursor: 'pointer' }}
                  />
                  <Label htmlFor={`req_${index}`} style={{ margin: 0, cursor: 'pointer' }}>Required field</Label>
                </div>
              </div>
              <button 
                type="button" 
                onClick={() => removeRequirement(index)}
                style={{ padding: '0.5rem', color: '#ef4444', backgroundColor: 'transparent', border: 'none', cursor: 'pointer' }}
                title="Remove Field"
              >
                <Trash2 size={20} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
