import React from 'react';
import { useCurrentAgency } from '../../hooks/useCurrentAgency';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/shared/Card';
import { Button } from '../../components/shared/Button';
import { Skeleton } from '../../components/shared/Skeleton';
import { Alert } from '../../components/shared/Alert';
import { useNavigate } from 'react-router-dom';

const AgencyProfilePage: React.FC = () => {
  const { data: agency, isLoading, isError, error } = useCurrentAgency();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto">
        <Skeleton className="h-8 w-64" />
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48 mb-2" />
            <Skeleton className="h-4 w-96" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="max-w-4xl mx-auto mt-8">
        <Alert variant="destructive" title="Error loading profile">
          {error instanceof Error ? error.message : 'An unexpected error occurred.'}
        </Alert>
      </div>
    );
  }

  if (!agency) {
    return (
      <div className="max-w-4xl mx-auto mt-8">
        <Card className="text-center p-8">
          <CardHeader>
            <CardTitle>No Agency Profile</CardTitle>
            <CardDescription>You haven't created your agency profile yet.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => navigate('/profile/create')}>Create Profile</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Agency Profile</h2>
        <Button onClick={() => navigate('/profile/edit')}>Edit Profile</Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center space-x-4">
            {agency.logo_url && (
              <img src={agency.logo_url} alt="Logo" className="w-16 h-16 rounded-full object-cover border border-border" />
            )}
            <div>
              <CardTitle className="text-2xl">{agency.agency_name}</CardTitle>
              <CardDescription className="flex items-center mt-1">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  agency.verification_status === 'verified' ? 'bg-green-100 text-green-800' : 
                  agency.verification_status === 'suspended' ? 'bg-red-100 text-red-800' : 
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {agency.verification_status.toUpperCase()}
                </span>
                {agency.registration_number && (
                  <span className="ml-3 text-muted-foreground">Reg No: {agency.registration_number}</span>
                )}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {agency.description && (
            <div>
              <h3 className="text-lg font-medium">About Us</h3>
              <p className="mt-2 text-sm text-muted-foreground">{agency.description}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium">Contact Information</h3>
              <dl className="mt-2 space-y-2 text-sm text-muted-foreground">
                {agency.email && (
                  <div className="flex"><dt className="w-24">Email:</dt><dd className="font-medium text-foreground">{agency.email}</dd></div>
                )}
                {agency.phone && (
                  <div className="flex"><dt className="w-24">Phone:</dt><dd className="font-medium text-foreground">{agency.phone}</dd></div>
                )}
                {agency.website && (
                  <div className="flex"><dt className="w-24">Website:</dt><dd className="font-medium text-primary hover:underline"><a href={agency.website} target="_blank" rel="noreferrer">{agency.website}</a></dd></div>
                )}
              </dl>
            </div>
            
            <div>
              <h3 className="text-sm font-medium">Location</h3>
              <dl className="mt-2 space-y-2 text-sm text-muted-foreground">
                {agency.country && (
                  <div className="flex"><dt className="w-24">Country:</dt><dd className="font-medium text-foreground">{agency.country}</dd></div>
                )}
                {agency.city && (
                  <div className="flex"><dt className="w-24">City:</dt><dd className="font-medium text-foreground">{agency.city}</dd></div>
                )}
                {agency.address && (
                  <div className="flex"><dt className="w-24">Address:</dt><dd className="font-medium text-foreground">{agency.address}</dd></div>
                )}
              </dl>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AgencyProfilePage;
