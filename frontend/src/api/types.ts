export interface Participant {
  id: number;
  name: string;
  email: string;
  chronotype: 'morning' | 'evening' | 'intermediate';
  peak_hours_start: number;
  peak_hours_end: number;
  emotional_intelligence: number;
  social_intelligence: number;
  created_at: string;
  updated_at: string;
}

export interface ParticipantCreate {
  name: string;
  email: string;
  chronotype: 'morning' | 'evening' | 'intermediate';
  peak_hours_start: number;
  peak_hours_end: number;
  emotional_intelligence: number;
  social_intelligence: number;
}

export interface Meeting {
  id: number;
  title: string;
  meeting_type: 'brainstorm' | 'review' | 'planning' | 'status_update';
  scheduled_time: string;
  created_at: string;
  participants: Participant[];
}

export interface MeetingCreate {
  title: string;
  meeting_type: 'brainstorm' | 'review' | 'planning' | 'status_update';
  scheduled_time: string;
  participant_ids: number[];
}

export interface RoleAssignment {
  id: number;
  meeting_id: number;
  participant_id: number;
  participant_name?: string;
  role: string;
  fitness_score: number;
  created_at: string;
}

export interface RoleAssignmentResult {
  meeting_id: number;
  assignments: RoleAssignment[];
  total_assigned: number;
}

export interface DailyRoleBreakdown {
  date: string;
  roles: Record<string, number>;
  total: number;
}

export interface ParticipantStatistics {
  participant_id: number;
  participant_name: string;
  period_days: number;
  start_date: string;
  end_date: string;
  total_meetings: number;
  role_distribution: Record<string, number>;
  daily_breakdown: DailyRoleBreakdown[];
}
