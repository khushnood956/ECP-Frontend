import { apiClient } from './apiClient';

export class ScholarshipAPI {
  static async getScholarships(page = 1, pageSize = 10) {
    const response = await apiClient.get('/scholarships', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  }

  static async searchScholarships(params) {
    const response = await apiClient.get('/scholarships/search', {
      params,
    });
    return response.data;
  }

  static async getScholarship(id) {
    const response = await apiClient.get(`/scholarships/${id}`);
    return response.data;
  }

  static async createScholarship(data) {
    const response = await apiClient.post('/scholarships', data);
    return response.data;
  }

  static async updateScholarship(id, data) {
    const response = await apiClient.patch(`/scholarships/${id}`, data);
    return response.data;
  }

  static async deleteScholarship(id) {
    const response = await apiClient.delete(`/scholarships/${id}`);
    return response.data;
  }

  static async publishScholarship(id) {
    const response = await apiClient.post(`/scholarships/${id}/publish`);
    return response.data;
  }

  static async unpublishScholarship(id) {
    const response = await apiClient.post(`/scholarships/${id}/unpublish`);
    return response.data;
  }
}
