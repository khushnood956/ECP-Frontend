import { apiClient } from './apiClient';

export class LeadAPI {
  static async getLeads(params) {
    const response = await apiClient.get('/leads', {
      params,
    });
    return response.data;
  }

  static async createLead(data) {
    const response = await apiClient.post('/leads', data);
    return response.data;
  }

  static async getLead(id) {
    const response = await apiClient.get(`/leads/${id}`);
    return response.data;
  }

  static async updateLead(id, data) {
    const response = await apiClient.patch(`/leads/${id}`, data);
    return response.data;
  }

  static async deleteLead(id) {
    const response = await apiClient.delete(`/leads/${id}`);
    return response.data;
  }
}
