import React, { useState } from 'react';
import { AgencyForm } from './AgencyForm';
import { useUpdateAgency } from '../../hooks/useAgencyMutations';
import { useCurrentAgency } from '../../hooks/useCurrentAgency';
import { useNavigate } from 'react-router-dom';
import { Alert } from '../../components/shared/Alert';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/shared/Card';
import { Skeleton } from '../../components/shared/Skeleton';
import { Button } from '../../components/shared/Button';

const EditAgencyPage = () => {
  const [error, setError] = useState(null);
  const { data: agency, isLoading, isError, error: fetchError } = useCurrentAgency();
  const mutation = useUpdateAgency();
  const navigate = useNavigate();

  const handleSubmit = (data) => {
    if (!agency?.id) return;
    setError(null);
    mutation.mutate({ id: agency.id, data }, {
      onSuccess: () => {
        navigate('/agency/profile');
      },
      onError: (err) => {
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
        <Button onClick={() => navigate('/agency/profile')}>Go Back</Button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Edit Profile</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Update your agency's professional credentials.
          </p>
        </div>
        <Button variant="outline" onClick={() => navigate('/agency/profile')}>Cancel</Button>
      </div>

      {error && (
        <Alert variant="destructive" title="Error">
          {error}
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Agency Profile Details</CardTitle>
          <CardDescription>Keep your contact and logo URLs up-to-date.</CardDescription>
        </CardHeader>
        <CardContent>
          <AgencyForm initialValues={agency} onSubmit={handleSubmit} isSubmitting={mutation.isPending} />
        </CardContent>
      </Card>
    </div>
  );
};

export default EditAgencyPage;
