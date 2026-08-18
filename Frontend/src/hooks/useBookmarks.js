import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { StudentAPI } from '../services/api/student.api';

export const useStudentBookmarks = () => {
  return useQuery({
    queryKey: ['bookmarks'],
    queryFn: StudentAPI.getBookmarks,
    staleTime: 5 * 60 * 1000
  });
};

export const useCreateBookmark = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ bookmarkType, scholarshipId, universityId }) => 
      StudentAPI.createBookmark(bookmarkType, scholarshipId, universityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookmarks'] });
    }
  });
};

export const useDeleteBookmark = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: StudentAPI.deleteBookmark,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookmarks'] });
    }
  });
};
