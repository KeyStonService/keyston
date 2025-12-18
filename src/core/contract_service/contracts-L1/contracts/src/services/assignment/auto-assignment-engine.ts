/**
 * 自動分派引擎 (Auto Assignment Engine)
 * Core engine for intelligent responsibility assignment
 */

import { v4 as uuidv4 } from 'uuid';

import {
  Incident,
  Assignment,
  AssignmentStatus,
  TeamMember,
  Priority,
  ProblemType,
  WorkloadMetrics,
} from '../../types/assignment';

import { ResponsibilityMatrix } from './responsibility-matrix';
import { WorkloadBalancer } from './workload-balancer';

export class AutoAssignmentEngine {
  private responsibilityMatrix: ResponsibilityMatrix;
  private workloadBalancer: WorkloadBalancer;
  private assignments: Map<string, Assignment>;

  constructor() {
    this.responsibilityMatrix = new ResponsibilityMatrix();
    this.workloadBalancer = new WorkloadBalancer();
    this.assignments = new Map();
  }

  /**
   * 分析問題類型
   * Analyze problem type from incident
   */
  async analyzeProblemType(incident: Incident): Promise<ProblemType> {
    // 簡化實作：直接使用 incident 的類型
    // Simplified: directly use incident type
    return incident.type;
  }

  /**
   * 識別相關團隊
   * Identify relevant teams for the problem
   */
  identifyRelevantTeams(problemType: ProblemType): string[] {
    const teams = this.responsibilityMatrix.identifyRelevantTeams(problemType);
    return teams.map((team) => team.name);
  }

  /**
   * 檢查成員可用性
   * Check member availability
   */
  async checkMemberAvailability(teamNames: string[]): Promise<TeamMember[]> {
    const availableMembers: TeamMember[] = [];

    for (const teamName of teamNames) {
      const team = this.responsibilityMatrix.getTeamStructure(teamName);
      if (team) {
        // 簡化：假設所有成員都可用
        // Simplified: assume all members are available
        // TODO: Future enhancement - integrate with calendar/vacation system for real availability
        availableMembers.push(...team.members);
      }
    }

    return availableMembers;
  }

  /**
   * 選擇最佳負責人
   * Select optimal assignee
   */
  selectOptimalAssignee(availableMembers: TeamMember[], incident: Incident): TeamMember {
    return this.workloadBalancer.selectOptimalAssignee(availableMembers, incident);
  }

  /**
   * 創建分派記錄
   * Create assignment record
   */
  async createAssignmentRecord(
    primaryOwner: TeamMember,
    incident: Incident,
    secondaryOwner?: TeamMember
  ): Promise<Assignment> {
    const slaTargets = this.getSLATargets(incident.priority);

    const assignment: Assignment = {
      id: uuidv4(),
      incidentId: incident.id,
      primaryOwner,
      secondaryOwner,
      status: 'ASSIGNED',
      assignedAt: new Date(),
      slaTarget: slaTargets,
    };

    this.assignments.set(assignment.id, assignment);

    // 更新工作負載
    this.updateMemberWorkload(primaryOwner.id, 1);

    return assignment;
  }

  /**
   * 獲取 SLA 目標
   * Get SLA targets based on priority
   */
  private getSLATargets(priority: Priority): { responseTime: number; resolutionTime: number } {
    const targets = {
      CRITICAL: { responseTime: 5, resolutionTime: 60 },
      HIGH: { responseTime: 15, resolutionTime: 240 },
      MEDIUM: { responseTime: 60, resolutionTime: 480 },
      LOW: { responseTime: 240, resolutionTime: 1440 },
    };

    return targets[priority];
  }

  /**
   * 自動分派責任
   * Automatically assign responsibility
   */
  async assignResponsibility(incident: Incident): Promise<Assignment> {
    // 步驟 1: 分析問題類型
    const problemType = await this.analyzeProblemType(incident);

    // 步驟 2: 識別相關團隊
    const candidateTeams = this.identifyRelevantTeams(problemType);

    // 步驟 3: 評估成員可用性
    const availableMembers = await this.checkMemberAvailability(candidateTeams);

    if (availableMembers.length === 0) {
      throw new Error('No available members for assignment');
    }

    // 步驟 4: 智慧選擇最佳負責人
    const primaryOwner = this.selectOptimalAssignee(availableMembers, incident);

    // 選擇備援負責人（第二優先）
    const remainingMembers = availableMembers.filter((m) => m.id !== primaryOwner.id);
    const secondaryOwner =
      remainingMembers.length > 0
        ? this.workloadBalancer.selectOptimalAssignee(remainingMembers, incident)
        : undefined;

    // 步驟 5: 建立責任追蹤
    const assignment = await this.createAssignmentRecord(primaryOwner, incident, secondaryOwner);

    return assignment;
  }

  /**
   * 更新分派狀態
   * Update assignment status
   * Note: This method is synchronous as it only performs in-memory Map operations.
   * Controllers may still use `await` for consistency in async flow.
   */
  async updateAssignmentStatus(assignmentId: string, status: AssignmentStatus): Promise<Assignment> {
    const assignment = this.assignments.get(assignmentId);

    if (!assignment) {
      throw new Error(`Assignment ${assignmentId} not found`);
    }

    assignment.status = status;

    // 更新時間戳記
    if (status === 'ACKNOWLEDGED' && !assignment.acknowledgedAt) {
      assignment.acknowledgedAt = new Date();
    } else if (status === 'IN_PROGRESS' && !assignment.startedAt) {
      assignment.startedAt = new Date();
    } else if (status === 'RESOLVED' && !assignment.resolvedAt) {
      assignment.resolvedAt = new Date();
      // 減少工作負載
      this.updateMemberWorkload(assignment.primaryOwner.id, -1);
    }

    this.assignments.set(assignmentId, assignment);

    return assignment;
  }

  /**
   * 獲取分派記錄
   * Get assignment record
   */
  getAssignment(assignmentId: string): Assignment | undefined {
    return this.assignments.get(assignmentId);
  }

  /**
   * 獲取所有分派記錄
   * Get all assignments
   */
  getAllAssignments(): Assignment[] {
    return Array.from(this.assignments.values());
  }

  /**
   * 重新分派責任
   * Reassign responsibility
   */
  async reassignResponsibility(assignmentId: string, newOwnerId: string): Promise<Assignment> {
    const assignment = this.assignments.get(assignmentId);

    if (!assignment) {
      throw new Error(`Assignment ${assignmentId} not found`);
    }

    const newOwner = this.responsibilityMatrix.getMemberById(newOwnerId);

    if (!newOwner) {
      throw new Error(`Member ${newOwnerId} not found`);
    }

    // 減少舊負責人的工作負載
    this.updateMemberWorkload(assignment.primaryOwner.id, -1);

    // 更新分派
    assignment.primaryOwner = newOwner;
    assignment.status = 'ASSIGNED';
    assignment.assignedAt = new Date();

    // 增加新負責人的工作負載
    this.updateMemberWorkload(newOwner.id, 1);

    this.assignments.set(assignmentId, assignment);

    return assignment;
  }

  /**
   * 更新成員工作負載
   * Update member workload
   */
  private updateMemberWorkload(memberId: string, delta: number): void {
    const current = this.workloadBalancer.getWorkloadMetrics(memberId) || {
      memberId,
      activeAssignments: 0,
      totalAssignments: 0,
      averageResolutionTime: 0,
      successRate: 0.5,
    };

    this.workloadBalancer.updateWorkloadMetrics(memberId, {
      activeAssignments: Math.max(0, current.activeAssignments + delta),
      totalAssignments: delta > 0 ? current.totalAssignments + delta : current.totalAssignments,
    });
  }

  /**
   * 獲取工作負載統計
   * Get workload statistics
   */
  getWorkloadStatistics(): Map<string, WorkloadMetrics> {
    return this.workloadBalancer.getAllWorkloadMetrics();
  }
}
