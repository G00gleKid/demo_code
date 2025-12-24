import api from './client';

export interface RoleRequirement {
  ei_min: number;
  ei_max: number;
  si_min: number;
  si_max: number;
  energy_min: number;
  energy_max: number;
}

export interface RoleRequirements {
  [role: string]: RoleRequirement;
}

export interface MeetingMultipliers {
  [meetingType: string]: {
    [role: string]: number;
  };
}

export const settingsApi = {
  getRoleRequirements: async (): Promise<RoleRequirements> => {
    const response = await api.get('/settings/role-requirements');
    return response.data;
  },

  getMeetingMultipliers: async (): Promise<MeetingMultipliers> => {
    const response = await api.get('/settings/meeting-multipliers');
    return response.data;
  },
};
