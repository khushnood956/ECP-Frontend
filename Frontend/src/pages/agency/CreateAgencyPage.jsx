import React, { useState } from 'react';
import { AgencyForm } from './AgencyForm';
import { useCreateAgency } from '../../hooks/useAgencyMutations';
import { useNavigate } from 'react-router-dom';
import { Alert } from '../../components/shared/Alert';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/shared/Card';

const CreateAgencyPage = () => {
  const [error, setError] = useState(null);
  const mutation = useCreateAgency();
  const navigate = useNavigate();

  const handleSubmit = (data) => {
    setError(null);
    mutation.mutate(data, {
      onSuccess: () => {
        navigate('/agency/profile');
      },
      onError: (err) => {
        setError(err.response?.data?.detail || err.message || 'Failed to create agency profile');
      }
    });
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Create Agency Profile</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Set up your educational consulting agency profile to get started.
        </p>
      </div>

      {error && (
        <Alert variant="destructive" title="Error">
          {error}
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Agency Information</CardTitle>
          <CardDescription>Enter details about your organization.</CardDescription>
        </CardHeader>
        <CardContent>
          <AgencyForm onSubmit={handleSubmit} isSubmitting={mutation.isPending} />
        </CardContent>
      </Card>
    </div>
  );
};

export default CreateAgencyPage;
