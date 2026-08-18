import { apiClient } from './apiClient';

export class AgencyAPI {
  static async getAgencies(skip = 0, limit = 100, verificationStatus = null) {
    const params = { skip, limit };
    if (verificationStatus) {
      params.verification_status = verificationStatus;
    }
    const response = await apiClient.get('/agencies', { params });
    return response.data;
  }

  static async getCurrentAgency() {
    const response = await apiClient.get('/agencies/me');
    return response.data;
  }

  static async getAgency(id) {
    const response = await apiClient.get(`/agencies/${id}`);
    return response.data;
  }

  static async createAgency(data) {
    const response = await apiClient.post('/agencies', data);
    return response.data;
  }

  static async updateAgency(id, data) {
    const response = await apiClient.patch(`/agencies/${id}`, data);
    return response.data;
  }

  static async verifyAgency(id) {
    const response = await apiClient.post(`/agencies/${id}/verify`);
    return response.data;
  }

  static async suspendAgency(id) {
    const response = await apiClient.post(`/agencies/${id}/suspend`);
    return response.data;
  }
}
