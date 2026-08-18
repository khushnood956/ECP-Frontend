import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AgencyAPI } from '../services/api/agency.api';
import { AdminAPI } from '../services/api/admin.api';

export const useAdminStats = () => {
  return useQuery({
    queryKey: ['admin-stats'],
    queryFn: async () => {
      const response = await AdminAPI.getStatistics();
      return response.data;
    }
  });
};

export const useAgenciesByVerificationStatus = (verificationStatus = 'pending') => {
  return useQuery({
    queryKey: ['agencies', verificationStatus],
    queryFn: async () => {
      const response = await AgencyAPI.getAgencies(0, 100, verificationStatus);
      return response.data;
    }
  });
};

export const usePendingAgencies = () => useAgenciesByVerificationStatus('pending');

export const useVerifyAgency = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: AgencyAPI.verifyAgency,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agencies'] });
      queryClient.invalidateQueries({ queryKey: ['admin-stats'] });
    }
  });
};

export const useSuspendAgency = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: AgencyAPI.suspendAgency,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agencies'] });
      queryClient.invalidateQueries({ queryKey: ['admin-stats'] });
    }
  });
};
