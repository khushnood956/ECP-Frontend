import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '../../components/shared/Button';
import { Input } from '../../components/shared/Input';
import { Textarea } from '../../components/shared/Textarea';
import { Label } from '../../components/shared/Label';

const scholarshipSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  country: z.string().min(1, 'Country is required'),
  university: z.string().min(1, 'University / Institution is required'),
  degree_level: z.enum(['high_school', 'bachelor', 'master', 'phd', 'postdoc', 'other'], {
    errorMap: () => ({ message: 'Degree level is required' }),
  }),
  funding_type: z.enum(['fully_funded', 'partial', 'tuition_fee_only', 'self_funded'], {
    errorMap: () => ({ message: 'Funding type is required' }),
  }),
  amount: z.preprocess(
    (val) => (val === '' ? null : Number(val)),
    z.number({ invalid_type_error: 'Amount must be a number' }).nullable()
  ),
  currency: z.string().optional().or(z.literal('')),
  deadline: z.string().min(1, 'Deadline date is required'),
  eligibility: z.string().optional().or(z.literal('')),
  description: z.string().optional().or(z.literal('')),
  application_link: z.string().url('Invalid URL format').optional().or(z.literal('')),
  is_active: z.boolean().default(true),
});

export const ScholarshipForm = ({ initialValues, onSubmit, isSubmitting }) => {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(scholarshipSchema),
    defaultValues: {
      title: initialValues?.title || '',
      country: initialValues?.country || '',
      university: initialValues?.university || '',
      degree_level: initialValues?.degree_level || 'master',
      funding_type: initialValues?.funding_type || 'fully_funded',
      amount: initialValues?.amount !== undefined && initialValues?.amount !== null ? initialValues.amount : '',
      currency: initialValues?.currency || 'USD',
      deadline: initialValues?.deadline || '',
      eligibility: initialValues?.eligibility || '',
      description: initialValues?.description || '',
      application_link: initialValues?.application_link || '',
      is_active: initialValues?.is_active !== undefined ? initialValues.is_active : true,
    },
  });

  const handleFormSubmit = (data) => {
    const cleanedData = { ...data };
    // Convert empty fields to null for backend compatibility
    if (cleanedData.currency === '') cleanedData.currency = null;
    if (cleanedData.eligibility === '') cleanedData.eligibility = null;
    if (cleanedData.description === '') cleanedData.description = null;
    if (cleanedData.application_link === '') cleanedData.application_link = null;
    onSubmit(cleanedData);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div className="form-group">
          <Label htmlFor="title">Scholarship Title *</Label>
          <Input id="title" {...register('title')} error={errors.title?.message} className="mt-1" />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          <div className="form-group">
            <Label htmlFor="university">University / Institution *</Label>
            <Input id="university" {...register('university')} error={errors.university?.message} className="mt-1" />
          </div>
          <div className="form-group">
            <Label htmlFor="country">Country *</Label>
            <Input id="country" {...register('country')} error={errors.country?.message} className="mt-1" />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          <div className="form-group">
            <Label htmlFor="degree_level">Degree Level *</Label>
            <select
              id="degree_level"
              {...register('degree_level')}
              style={{
                width: '100%',
                padding: '0.625rem',
                borderRadius: 'var(--radius-md)',
                border: errors.degree_level ? '1px solid #ef4444' : '1px solid var(--border-color)',
                backgroundColor: 'var(--bg-white)',
                color: 'var(--text-dark)',
                fontSize: '0.875rem',
                marginTop: '0.25rem',
                outline: 'none'
              }}
            >
              <option value="high_school">High School</option>
              <option value="bachelor">Bachelor / Undergraduate</option>
              <option value="master">Master / Postgraduate</option>
              <option value="phd">PhD / Doctoral</option>
              <option value="postdoc">Postdoc</option>
              <option value="other">Other</option>
            </select>
            {errors.degree_level && <p style={{ color: '#ef4444', fontSize: '0.875rem', marginTop: '0.25rem' }}>{errors.degree_level.message}</p>}
          </div>

          <div className="form-group">
            <Label htmlFor="funding_type">Funding Type *</Label>
            <select
              id="funding_type"
              {...register('funding_type')}
              style={{
                width: '100%',
                padding: '0.625rem',
                borderRadius: 'var(--radius-md)',
                border: errors.funding_type ? '1px solid #ef4444' : '1px solid var(--border-color)',
                backgroundColor: 'var(--bg-white)',
                color: 'var(--text-dark)',
                fontSize: '0.875rem',
                marginTop: '0.25rem',
                outline: 'none'
              }}
            >
              <option value="fully_funded">Fully Funded</option>
              <option value="partial">Partial Scholarship</option>
              <option value="tuition_fee_only">Tuition Fee Only</option>
              <option value="self_funded">Self Funded / Sponsored</option>
            </select>
            {errors.funding_type && <p style={{ color: '#ef4444', fontSize: '0.875rem', marginTop: '0.25rem' }}>{errors.funding_type.message}</p>}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          <div className="form-group">
            <Label htmlFor="amount">Funding Amount</Label>
            <Input id="amount" type="number" {...register('amount')} error={errors.amount?.message} className="mt-1" />
          </div>
          <div className="form-group">
            <Label htmlFor="currency">Currency Code</Label>
            <Input id="currency" type="text" placeholder="e.g. USD, EUR" {...register('currency')} error={errors.currency?.message} className="mt-1" />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          <div className="form-group">
            <Label htmlFor="deadline">Application Deadline *</Label>
            <Input id="deadline" type="date" {...register('deadline')} error={errors.deadline?.message} className="mt-1" />
          </div>
          <div className="form-group">
            <Label htmlFor="application_link">Online Application URL</Label>
            <Input id="application_link" type="text" placeholder="https://" {...register('application_link')} error={errors.application_link?.message} className="mt-1" />
          </div>
        </div>

        <div className="form-group">
          <Label htmlFor="eligibility">Eligibility Criteria</Label>
          <Textarea id="eligibility" rows={3} placeholder="Requirements like GPA, IELTS score, nationality, etc." {...register('eligibility')} error={errors.eligibility?.message} className="mt-1" />
        </div>

        <div className="form-group">
          <Label htmlFor="description">Scholarship Description</Label>
          <Textarea id="description" rows={5} placeholder="Describe the benefits, fields of study, etc." {...register('description')} error={errors.description?.message} className="mt-1" />
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'end', marginTop: '2rem' }}>
        <Button type="submit" isLoading={isSubmitting}>
          {initialValues ? 'Save Changes' : 'Create Scholarship'}
        </Button>
      </div>
    </form>
  );
};
