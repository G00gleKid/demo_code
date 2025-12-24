import client from './client';
import { Participant, ParticipantCreate, ParticipantStatistics } from './types';

export const participantsApi = {
  getAll: async (): Promise<Participant[]> => {
    const response = await client.get('/participants/');
    return response.data;
  },

  create: async (data: ParticipantCreate): Promise<Participant> => {
    const response = await client.post('/participants/', data);
    return response.data;
  },

  getById: async (id: number): Promise<Participant> => {
    const response = await client.get(`/participants/${id}`);
    return response.data;
  },

  update: async (id: number, data: Partial<ParticipantCreate>): Promise<Participant> => {
    const response = await client.put(`/participants/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await client.delete(`/participants/${id}`);
  },

  getStatistics: async (id: number, days: number = 7): Promise<ParticipantStatistics> => {
    const response = await client.get(`/assignments/participant/${id}/statistics?days=${days}`);
    return response.data;
  },
};
