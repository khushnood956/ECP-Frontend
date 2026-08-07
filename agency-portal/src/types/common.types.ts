export interface SuccessResponse<T> {
  success: boolean;
  message: string;
  data: T;
  request_id?: string;
}

export interface ErrorResponse {
  success: boolean;
  message: string;
  error_code: string;
  details?: Record<string, any>;
  request_id?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  message: string;
  data: T[];
  total: number;
  page: number;
  size: number;
  request_id?: string;
}
