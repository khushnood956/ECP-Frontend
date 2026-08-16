import { useMutation, useQueryClient } from '@tanstack/react-query';
import { AgencyAPI } from '../services/api/agency.api';

export const useCreateAgency = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => AgencyAPI.createAgency(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentAgency'] });
    },
  });
};

export const useUpdateAgency = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => AgencyAPI.updateAgency(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentAgency'] });
    },
  });
};
