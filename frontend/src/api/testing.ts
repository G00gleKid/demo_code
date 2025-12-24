/**
 * TEMPORARY: Testing API client for demo purposes only.
 * This module will be removed when real EI/SI integration is implemented.
 */

import client from './client';

export interface TeamBasic {
  id: number;
  name: string;
}

export interface ParticipantWithEI {
  id: number;
  name: string;
  email: string;
  emotional_intelligence: number;
}

export interface ParticipantWithSI {
  id: number;
  name: string;
  email: string;
  social_intelligence: number;
}

export interface EIScoreUpdate {
  ei_score: number;
}

export interface SIScoreUpdate {
  si_score: number;
}

export const testingApi = {
  // Common endpoints
  getAllTeams: async (): Promise<TeamBasic[]> => {
    const response = await client.get('/testing/teams');
    return response.data;
  },

  // EI Testing endpoints
  getTeamParticipants: async (teamId: number): Promise<ParticipantWithEI[]> => {
    const response = await client.get(`/testing/teams/${teamId}/participants`);
    return response.data;
  },

  getParticipant: async (participantId: number): Promise<ParticipantWithEI> => {
    const response = await client.get(`/testing/participants/${participantId}`);
    return response.data;
  },

  updateEIScore: async (participantId: number, score: number): Promise<ParticipantWithEI> => {
    const response = await client.put(`/testing/participants/${participantId}/ei-score`, {
      ei_score: score
    });
    return response.data;
  },

  // SI Testing endpoints
  getTeamParticipantsSI: async (teamId: number): Promise<ParticipantWithSI[]> => {
    const response = await client.get(`/testing/teams/${teamId}/participants/si`);
    return response.data;
  },

  getParticipantSI: async (participantId: number): Promise<ParticipantWithSI> => {
    const response = await client.get(`/testing/participants/${participantId}/si`);
    return response.data;
  },

  updateSIScore: async (participantId: number, score: number): Promise<ParticipantWithSI> => {
    const response = await client.put(`/testing/participants/${participantId}/si-score`, {
      si_score: score
    });
    return response.data;
  },
};
