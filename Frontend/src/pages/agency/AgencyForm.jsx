import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '../../components/shared/Button';
import { Input } from '../../components/shared/Input';
import { Textarea } from '../../components/shared/Textarea';
import { Label } from '../../components/shared/Label';

const agencySchema = z.object({
  agency_name: z.string().min(1, 'Agency name is required'),
  description: z.string().optional(),
  website: z.string().url('Invalid URL format').optional().or(z.literal('')),
  logo_url: z.string().url('Invalid URL format').optional().or(z.literal('')),
  registration_number: z.string().optional(),
  email: z.string().email('Invalid email address').optional().or(z.literal('')),
  phone: z.string().optional(),
  country: z.string().optional(),
  city: z.string().optional(),
  address: z.string().optional(),
});

export const AgencyForm = ({ initialValues, onSubmit, isSubmitting }) => {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(agencySchema),
    defaultValues: {
      agency_name: initialValues?.agency_name || '',
      description: initialValues?.description || '',
      website: initialValues?.website || '',
      logo_url: initialValues?.logo_url || '',
      registration_number: initialValues?.registration_number || '',
      email: initialValues?.email || '',
      phone: initialValues?.phone || '',
      country: initialValues?.country || '',
      city: initialValues?.city || '',
      address: initialValues?.address || '',
    },
  });

  const handleFormSubmit = (data) => {
    const cleanedData = {};
    for (const [key, value] of Object.entries(data)) {
      if (value !== '') {
        cleanedData[key] = value;
      }
    }
    onSubmit(cleanedData);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <div className="space-y-4">
        <div>
          <Label htmlFor="agency_name">Agency Name *</Label>
          <Input id="agency_name" {...register('agency_name')} error={errors.agency_name?.message} className="mt-1" />
        </div>

        <div>
          <Label htmlFor="registration_number">Registration Number</Label>
          <Input id="registration_number" {...register('registration_number')} error={errors.registration_number?.message} className="mt-1" />
        </div>

        <div>
          <Label htmlFor="description">Description</Label>
          <Textarea id="description" {...register('description')} error={errors.description?.message} className="mt-1" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="email">Public Email</Label>
            <Input id="email" type="email" {...register('email')} error={errors.email?.message} className="mt-1" />
          </div>
          <div>
            <Label htmlFor="phone">Phone</Label>
            <Input id="phone" type="text" {...register('phone')} error={errors.phone?.message} className="mt-1" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="website">Website URL</Label>
            <Input id="website" type="text" placeholder="https://" {...register('website')} error={errors.website?.message} className="mt-1" />
          </div>
          <div>
            <Label htmlFor="logo_url">Logo URL</Label>
            <Input id="logo_url" type="text" placeholder="https://" {...register('logo_url')} error={errors.logo_url?.message} className="mt-1" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="country">Country</Label>
            <Input id="country" {...register('country')} error={errors.country?.message} className="mt-1" />
          </div>
          <div>
            <Label htmlFor="city">City</Label>
            <Input id="city" {...register('city')} error={errors.city?.message} className="mt-1" />
          </div>
        </div>

        <div>
          <Label htmlFor="address">Full Address</Label>
          <Textarea id="address" {...register('address')} error={errors.address?.message} className="mt-1" />
        </div>
      </div>

      <div className="flex justify-end">
        <Button type="submit" isLoading={isSubmitting}>
          {initialValues ? 'Save Changes' : 'Create Profile'}
        </Button>
      </div>
    </form>
  );
};
