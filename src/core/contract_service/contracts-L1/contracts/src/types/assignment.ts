/**
 * 自動化專責負責人員系統類型定義
 * Type definitions for Auto-Assignment System
 */

export type ProblemType =
  | 'FRONTEND_ERROR'
  | 'BACKEND_API'
  | 'DATABASE_ISSUE'
  | 'PERFORMANCE'
  | 'SECURITY'
  | 'INFRASTRUCTURE';

export type Priority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export type AssignmentStatus =
  | 'ASSIGNED'
  | 'ACKNOWLEDGED'
  | 'IN_PROGRESS'
  | 'ESCALATED'
  | 'RESOLVED';

export interface TeamMember {
  id: string;
  name: string;
  email: string;
  specialties: string[];
  timezone: string;
}

export interface TeamStructure {
  name: string;
  members: TeamMember[];
  specialties: string[];
  timezone: string;
}

export interface Incident {
  id: string;
  type: ProblemType;
  priority: Priority;
  description: string;
  affectedFiles?: string[];
  errorMessage?: string;
  createdAt: Date;
}

export interface Assignment {
  id: string;
  incidentId: string;
  primaryOwner: TeamMember;
  secondaryOwner?: TeamMember;
  escalationOwner?: TeamMember;
  status: AssignmentStatus;
  assignedAt: Date;
  acknowledgedAt?: Date;
  startedAt?: Date;
  resolvedAt?: Date;
  slaTarget: {
    responseTime: number; // 分鐘
    resolutionTime: number; // 分鐘
  };
}

export interface WorkloadMetrics {
  memberId: string;
  activeAssignments: number;
  totalAssignments: number;
  averageResolutionTime: number;
  successRate: number;
}

export interface AssignmentScore {
  member: TeamMember;
  score: number;
  factors: {
    expertise: number;
    availability: number;
    currentLoad: number;
    responseHistory: number;
  };
}

export interface EscalationRule {
  priority: Priority;
  noResponseTimeout: number; // 分鐘
  noProgressTimeout: number; // 分鐘
  unresolvedTimeout: number; // 分鐘
}
