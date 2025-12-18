/**
 * 工作負載平衡器 (Workload Balancer)
 * Calculates optimal assignee based on multiple factors
 */

import { TeamMember, Incident, AssignmentScore, WorkloadMetrics } from '../../types/assignment';

export class WorkloadBalancer {
  private workloadMetrics: Map<string, WorkloadMetrics>;

  constructor() {
    this.workloadMetrics = new Map();
    this.initializeMetrics();
  }

  /**
   * 初始化工作負載指標
   * Initialize workload metrics
   */
  private initializeMetrics(): void {
    // 初始化時所有成員都沒有工作負載
    // Initialize all members with zero workload
  }

  /**
   * 計算專業匹配度
   * Calculate expertise match score (0-1)
   */
  calculateExpertiseMatch(member: TeamMember, incident: Incident): number {
    if (!incident.errorMessage && !incident.affectedFiles) {
      return 0.5; // 默認中等匹配
    }

    let matchScore = 0;
    let totalChecks = 0;

    // 檢查專業技能匹配
    const incidentKeywords = [
      incident.description.toLowerCase(),
      incident.errorMessage?.toLowerCase() || '',
      ...(incident.affectedFiles || []).map((f) => f.toLowerCase()),
    ].join(' ');

    member.specialties.forEach((specialty) => {
      totalChecks++;
      if (incidentKeywords.includes(specialty.toLowerCase())) {
        matchScore++;
      }
    });

    return totalChecks > 0 ? matchScore / totalChecks : 0.5;
  }

  /**
   * 計算可用性分數
   * Calculate availability score (0-1)
   */
  calculateAvailability(_member: TeamMember): number {
    // 簡化實作：基於時區計算可用性
    // Simplified: calculate availability based on timezone
    const now = new Date();
    const hour = now.getHours();

    // 假設工作時間是 9:00-18:00
    // Assume working hours are 9:00-18:00
    if (hour >= 9 && hour < 18) {
      return 1.0; // 完全可用
    } else if ((hour >= 7 && hour < 9) || (hour >= 18 && hour < 20)) {
      return 0.7; // 部分可用
    } else {
      return 0.3; // 可能不可用
    }
  }

  /**
   * 計算當前工作負載
   * Calculate current workload (0-1, lower is better)
   */
  calculateCurrentWorkload(member: TeamMember): number {
    const metrics = this.workloadMetrics.get(member.id);
    if (!metrics) {
      return 0; // 沒有工作負載
    }

    // 標準化工作負載：假設最多 10 個活動任務
    // Normalize workload: assume max 10 active assignments
    const normalizedLoad = Math.min(metrics.activeAssignments / 10, 1);
    return 1 - normalizedLoad; // 反轉，因為較低的負載更好
  }

  /**
   * 計算歷史表現
   * Calculate historical performance (0-1)
   */
  calculateHistoricalPerformance(member: TeamMember): number {
    const metrics = this.workloadMetrics.get(member.id);
    if (!metrics || metrics.totalAssignments === 0) {
      return 0.5; // 默認中等表現
    }

    return metrics.successRate;
  }

  /**
   * 計算分派分數
   * Calculate assignment score for a member
   */
  calculateAssignmentScore(member: TeamMember, incident: Incident): AssignmentScore {
    const factors = {
      expertise: this.calculateExpertiseMatch(member, incident) * 0.4,
      availability: this.calculateAvailability(member) * 0.3,
      currentLoad: this.calculateCurrentWorkload(member) * 0.2,
      responseHistory: this.calculateHistoricalPerformance(member) * 0.1,
    };

    const score = Object.values(factors).reduce((sum, value) => sum + value, 0);

    return {
      member,
      score,
      factors: {
        expertise: factors.expertise / 0.4,
        availability: factors.availability / 0.3,
        currentLoad: factors.currentLoad / 0.2,
        responseHistory: factors.responseHistory / 0.1,
      },
    };
  }

  /**
   * 選擇最佳負責人
   * Select optimal assignee from candidates
   */
  selectOptimalAssignee(candidates: TeamMember[], incident: Incident): TeamMember {
    if (candidates.length === 0) {
      throw new Error('No candidates available for assignment');
    }

    const scores = candidates
      .map((member) => this.calculateAssignmentScore(member, incident))
      .sort((a, b) => b.score - a.score);

    return scores[0].member;
  }

  /**
   * 更新工作負載指標
   * Update workload metrics
   */
  updateWorkloadMetrics(memberId: string, metrics: Partial<WorkloadMetrics>): void {
    const current = this.workloadMetrics.get(memberId) || {
      memberId,
      activeAssignments: 0,
      totalAssignments: 0,
      averageResolutionTime: 0,
      successRate: 0.5,
    };

    this.workloadMetrics.set(memberId, {
      ...current,
      ...metrics,
    });
  }

  /**
   * 獲取工作負載指標
   * Get workload metrics
   */
  getWorkloadMetrics(memberId: string): WorkloadMetrics | undefined {
    return this.workloadMetrics.get(memberId);
  }

  /**
   * 獲取所有工作負載指標
   * Get all workload metrics
   */
  getAllWorkloadMetrics(): Map<string, WorkloadMetrics> {
    return new Map(this.workloadMetrics);
  }
}
