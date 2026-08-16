import { apiClient } from './apiClient';

export class UniversityAPI {
  static async getUniversities(page = 1, pageSize = 10) {
    const response = await apiClient.get('/universities', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  }

  static async searchUniversities(params) {
    const response = await apiClient.get('/universities/search', {
      params,
    });
    return response.data;
  }

  static async getUniversity(id) {
    const response = await apiClient.get(`/universities/${id}`);
    return response.data;
  }
}
