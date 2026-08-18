import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { StudentAPI } from '../services/api/student.api';

export const useStudentNotifications = () => {
  return useQuery({
    queryKey: ['notifications'],
    queryFn: StudentAPI.getNotifications,
    refetchInterval: 15 * 1000, // Poll every 15s to keep notifications reasonably updated
    staleTime: 5 * 1000
  });
};

export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: StudentAPI.markNotificationRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    }
  });
};

export const useMarkAllNotificationsRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: StudentAPI.markAllNotificationsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    }
  });
};

export const useDeleteNotification = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: StudentAPI.deleteNotification,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    }
  });
};
