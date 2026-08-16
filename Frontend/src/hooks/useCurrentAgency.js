import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { AgencyAPI } from '../services/api/agency.api';

export const useCurrentAgency = () => {
  const { user } = useAuth();

  return useQuery({
    queryKey: ['currentAgency', user?.sub],
    queryFn: async () => {
      if (!user?.sub) return null;
      try {
        const response = await AgencyAPI.getCurrentAgency();
        return response.data;
      } catch (error) {
        if (error.response?.status === 404) {
          return null;
        }
        throw error;
      }
    },
    enabled: !!user?.sub,
  });
};
