import React, { useState } from 'react';
import { AgencyForm } from './AgencyForm';
import { useUpdateAgency } from '../../hooks/useAgencyMutations';
import { useCurrentAgency } from '../../hooks/useCurrentAgency';
import { useNavigate } from 'react-router-dom';
import { Alert } from '../../components/shared/Alert';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/shared/Card';
import { Skeleton } from '../../components/shared/Skeleton';
import { Button } from '../../components/shared/Button';

const EditAgencyPage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const { data: agency, isLoading, isError, error: fetchError } = useCurrentAgency();
  const mutation = useUpdateAgency();
  const navigate = useNavigate();

  const handleSubmit = (data: any) => {
    if (!agency?.id) return;
    setError(null);
    mutation.mutate({ id: agency.id, data }, {
      onSuccess: () => {
        navigate('/profile');
      },
      onError: (err: any) => {
        setError(err.response?.data?.detail || err.message || 'Failed to update agency profile');
      }
    });
  };

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <Skeleton className="h-8 w-64" />
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48 mb-2" />
            <Skeleton className="h-4 w-96" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-10 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isError || !agency) {
    return (
      <div className="max-w-3xl mx-auto space-y-6 mt-8">
        <Alert variant="destructive" title="Error">
          {fetchError instanceof Error ? fetchError.message : 'Agency profile not found.'}
        </Alert>
        <Button onClick={() => navigate('/profile')}>Go Back</Button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Edit Agency Profile</h2>
      </div>

      {error && (
        <Alert variant="destructive" title="Update Failed">
          {error}
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Update Details</CardTitle>
          <CardDescription>Make changes to your agency profile information.</CardDescription>
        </CardHeader>
        <CardContent>
          <AgencyForm 
            initialValues={agency} 
            onSubmit={handleSubmit} 
            isSubmitting={mutation.isPending} 
          />
        </CardContent>
      </Card>
    </div>
  );
};

export default EditAgencyPage;
