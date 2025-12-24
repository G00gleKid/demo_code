import client from './client';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface Team {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  team_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  team: Team;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const authAPI = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await client.post<LoginResponse>('/auth/login', credentials);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await client.get<User>('/auth/me');
    return response.data;
  },

  async logout(): Promise<void> {
    await client.post('/auth/logout');
  },
};
