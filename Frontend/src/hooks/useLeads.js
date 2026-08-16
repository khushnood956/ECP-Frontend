import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { LeadAPI } from '../services/api/lead.api';
import { StudentAPI } from '../services/api/student.api';
import { ScholarshipAPI } from '../services/api/scholarship.api';

export const useAgencyLeads = (params) => {
  return useQuery({
    queryKey: ['leads', params],
    queryFn: async () => {
      const response = await LeadAPI.getLeads(params);
      return response.data;
    },
  });
};

export const useAgencyLead = (id) => {
  return useQuery({
    queryKey: ['lead', id],
    queryFn: async () => {
      const leadResponse = await LeadAPI.getLead(id);
      const lead = leadResponse.data;

      // Fetch student profile linked to this lead
      let student = null;
      try {
        const studentResponse = await StudentAPI.getStudentProfile(lead.student_id);
        student = studentResponse.data;
      } catch (err) {
        console.error('Failed to fetch student profile for lead', err);
      }

      // Fetch scholarship linked to this lead
      let scholarship = null;
      try {
        const scholarshipResponse = await ScholarshipAPI.getScholarship(lead.scholarship_id);
        scholarship = scholarshipResponse.data;
      } catch (err) {
        console.error('Failed to fetch scholarship for lead', err);
      }

      return {
        ...lead,
        student,
        scholarship,
      };
    },
    enabled: !!id,
  });
};

export const useUpdateLead = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await LeadAPI.updateLead(id, data);
      return response.data;
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      queryClient.invalidateQueries({ queryKey: ['lead', variables.id] });
    },
  });
};
