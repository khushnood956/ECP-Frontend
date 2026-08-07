import { useMutation, useQueryClient } from '@tanstack/react-query';
import { AgencyAPI } from '../services/api/agency.api';
import { type AgencyCreate, type AgencyUpdate } from '../types/agency.types';

export const useCreateAgency = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AgencyCreate) => AgencyAPI.createAgency(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentAgency'] });
    },
  });
};

export const useUpdateAgency = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: AgencyUpdate }) => AgencyAPI.updateAgency(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentAgency'] });
    },
  });
};
