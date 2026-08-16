import { useQuery } from '@tanstack/react-query';
import { UniversityAPI } from '../services/api/university.api';

export const useStudentUniversities = (filters) => {
  return useQuery({
    queryKey: ['student-universities', filters],
    queryFn: async () => {
      // If filters are active, call search endpoint; otherwise call regular list
      const hasFilters = filters && Object.keys(filters).some(k => filters[k] !== undefined && filters[k] !== '');
      const response = hasFilters 
        ? await UniversityAPI.searchUniversities(filters)
        : await UniversityAPI.getUniversities(1, 100);
      return response.data; // Extracts inner list from SuccessResponse
    },
  });
};

export const useStudentUniversity = (id) => {
  return useQuery({
    queryKey: ['student-university', id],
    queryFn: async () => {
      const response = await UniversityAPI.getUniversity(id);
      return response.data; // Extracts inner UniversityResponse from SuccessResponse
    },
    enabled: !!id,
  });
};
