export interface UserResponse {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface PaginatedUserResponse {
  items: UserResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
