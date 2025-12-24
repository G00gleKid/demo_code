import client from './client';
import { Meeting, MeetingCreate, RoleAssignment, RoleAssignmentResult } from './types';

export const meetingsApi = {
  getAll: async (): Promise<Meeting[]> => {
    const response = await client.get('/meetings/');
    return response.data;
  },

  create: async (data: MeetingCreate): Promise<Meeting> => {
    const response = await client.post('/meetings/', data);
    return response.data;
  },

  getById: async (id: number): Promise<Meeting> => {
    const response = await client.get(`/meetings/${id}`);
    return response.data;
  },

  update: async (id: number, data: Partial<MeetingCreate>): Promise<Meeting> => {
    const response = await client.put(`/meetings/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await client.delete(`/meetings/${id}`);
  },

  assignRoles: async (id: number): Promise<RoleAssignmentResult> => {
    const response = await client.post(`/meetings/${id}/assign-roles`);
    return response.data;
  },

  getAssignments: async (id: number): Promise<RoleAssignment[]> => {
    const response = await client.get(`/meetings/${id}/assignments`);
    return response.data;
  },
};
