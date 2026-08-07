import { apiClient } from './apiClient';
import { type AgencyCreate, type AgencyUpdate, type AgencyResponse } from '../../types/agency.types';
import { type SuccessResponse } from '../../types/common.types';

export class AgencyAPI {
  static async getAgencies(skip = 0, limit = 100): Promise<SuccessResponse<AgencyResponse[]>> {
    const response = await apiClient.get<SuccessResponse<AgencyResponse[]>>('/agencies', {
      params: { skip, limit },
    });
    return response.data;
  }

  static async getAgency(id: string): Promise<SuccessResponse<AgencyResponse>> {
    const response = await apiClient.get<SuccessResponse<AgencyResponse>>(`/agencies/${id}`);
    return response.data;
  }

  static async createAgency(data: AgencyCreate): Promise<SuccessResponse<AgencyResponse>> {
    const response = await apiClient.post<SuccessResponse<AgencyResponse>>('/agencies', data);
    return response.data;
  }

  static async updateAgency(id: string, data: AgencyUpdate): Promise<SuccessResponse<AgencyResponse>> {
    const response = await apiClient.patch<SuccessResponse<AgencyResponse>>(`/agencies/${id}`, data);
    return response.data;
  }
}
