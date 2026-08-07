import { apiClient } from './apiClient';

export class AuthAPI {
  static async login(data: URLSearchParams) {
    const response = await apiClient.post('/auth/login', data, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }
}
