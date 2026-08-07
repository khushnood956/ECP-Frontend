import { apiClient } from './apiClient';
import { type SuccessResponse } from '../../types/common.types';
import { type PaginatedUserResponse } from '../../types/user.types';

export class UserAPI {
  static async getUsersByEmail(email: string): Promise<SuccessResponse<PaginatedUserResponse>> {
    const response = await apiClient.get<SuccessResponse<PaginatedUserResponse>>('/users', {
      params: { email },
    });
    return response.data;
  }
}
