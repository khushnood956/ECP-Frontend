import { apiClient } from './apiClient';

export class AdminAPI {
  static async getStatistics() {
    const response = await apiClient.get('/admin/statistics');
    return response.data;
  }
}
