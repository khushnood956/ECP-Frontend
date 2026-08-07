import React, { useState } from 'react';
import { AgencyForm } from './AgencyForm';
import { useCreateAgency } from '../../hooks/useAgencyMutations';
import { useNavigate } from 'react-router-dom';
import { Alert } from '../../components/shared/Alert';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/shared/Card';

const CreateAgencyPage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const mutation = useCreateAgency();
  const navigate = useNavigate();

  const handleSubmit = (data: any) => {
    setError(null);
    mutation.mutate(data, {
      onSuccess: () => {
        navigate('/profile');
      },
      onError: (err: any) => {
        setError(err.response?.data?.detail || err.message || 'Failed to create agency profile');
      }
    });
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Create Agency Profile</h2>
      </div>

      {error && (
        <Alert variant="destructive" title="Creation Failed">
          {error}
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Agency Details</CardTitle>
          <CardDescription>Fill out the form below to set up your agency profile.</CardDescription>
        </CardHeader>
        <CardContent>
          <AgencyForm onSubmit={handleSubmit} isSubmitting={mutation.isPending} />
        </CardContent>
      </Card>
    </div>
  );
};

export default CreateAgencyPage;
