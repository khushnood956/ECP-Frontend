import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ScholarshipAPI } from '../services/api/scholarship.api';

export const useStudentScholarships = (filters) => {
  return useQuery({
    queryKey: ['student-scholarships', filters],
    queryFn: async () => {
      const response = await ScholarshipAPI.searchScholarships(filters);
      return response.data; // Extracts inner list of ScholarshipResponse
    },
  });
};

export const useStudentScholarship = (id) => {
  return useQuery({
    queryKey: ['student-scholarship', id],
    queryFn: async () => {
      const response = await ScholarshipAPI.getScholarship(id);
      return response.data; // Extracts inner ScholarshipResponse
    },
    enabled: !!id,
  });
};

export const useAgencyScholarships = (page = 1, pageSize = 10) => {
  return useQuery({
    queryKey: ['agency-scholarships', page, pageSize],
    queryFn: async () => {
      const response = await ScholarshipAPI.getScholarships(page, pageSize);
      return response.data; // Extracts inner list of ScholarshipResponse
    },
  });
};

export const useAgencyScholarship = (id) => {
  return useQuery({
    queryKey: ['agency-scholarship', id],
    queryFn: async () => {
      const response = await ScholarshipAPI.getScholarship(id);
      return response.data; // Extracts inner ScholarshipResponse
    },
    enabled: !!id,
  });
};

export const useCreateScholarship = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data) => {
      const response = await ScholarshipAPI.createScholarship(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agency-scholarships'] });
    },
  });
};

export const useUpdateScholarship = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await ScholarshipAPI.updateScholarship(id, data);
      return response.data;
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['agency-scholarships'] });
      queryClient.invalidateQueries({ queryKey: ['agency-scholarship', variables.id] });
    },
  });
};

export const useDeleteScholarship = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id) => {
      const response = await ScholarshipAPI.deleteScholarship(id);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agency-scholarships'] });
    },
  });
};

export const usePublishScholarship = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id) => {
      const response = await ScholarshipAPI.publishScholarship(id);
      return response.data;
    },
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ['agency-scholarships'] });
      queryClient.invalidateQueries({ queryKey: ['agency-scholarship', id] });
    },
  });
};

export const useUnpublishScholarship = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id) => {
      const response = await ScholarshipAPI.unpublishScholarship(id);
      return response.data;
    },
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ['agency-scholarships'] });
      queryClient.invalidateQueries({ queryKey: ['agency-scholarship', id] });
    },
  });
};
