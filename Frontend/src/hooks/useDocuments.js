import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { StudentAPI } from '../services/api/student.api';

export const useStudentDocuments = () => {
  return useQuery({
    queryKey: ['student-documents'],
    queryFn: StudentAPI.getDocuments,
  });
};

export const useCreateDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: StudentAPI.createDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['student-documents'] });
    },
  });
};

export const useDeleteDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: StudentAPI.deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['student-documents'] });
    },
  });
};
