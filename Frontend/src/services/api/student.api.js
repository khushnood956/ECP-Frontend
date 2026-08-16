import { apiClient } from './apiClient';

export class StudentAPI {
  static async getStudentProfile(id) {
    const response = await apiClient.get(`/student-profiles/${id}`);
    return response.data;
  }
}
