import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';
import { UserAPI } from '../services/api/user.api';
import { AgencyAPI } from '../services/api/agency.api';
import { type AgencyResponse } from '../types/agency.types';

export const useCurrentAgency = () => {
  const { user } = useAuth();

  return useQuery<AgencyResponse | null>({
    queryKey: ['currentAgency', user?.sub],
    queryFn: async () => {
      if (!user?.sub) return null;
      
      // 1. Get user_id from email
      const userRes = await UserAPI.getUsersByEmail(user.sub);
      const currentUser = userRes.data.items[0];
      
      if (!currentUser) throw new Error('User not found');

      // 2. Fetch all agencies (since no /agencies/me exists)
      const agenciesRes = await AgencyAPI.getAgencies(0, 1000);
      
      // 3. Filter by user_id
      const agency = agenciesRes.data.find(a => a.user_id === currentUser.id);
      
      return agency || null;
    },
    enabled: !!user?.sub,
  });
};
