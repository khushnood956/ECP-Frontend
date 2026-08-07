export type AgencyVerificationStatus = 'pending' | 'verified' | 'suspended';

export interface AgencyBase {
  agency_name: string;
  description?: string;
  website?: string;
  logo_url?: string;
  registration_number?: string;
  email?: string;
  phone?: string;
  country?: string;
  city?: string;
  address?: string;
}

export interface AgencyCreate extends AgencyBase {}

export interface AgencyUpdate extends Partial<AgencyBase> {}

export interface AgencyResponse extends AgencyBase {
  id: string;
  user_id: string;
  verification_status: AgencyVerificationStatus;
  verified_at?: string;
  created_at: string;
  updated_at: string;
}
