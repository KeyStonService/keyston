/**
 * 責任治理框架 (Responsibility Governance)
 * Monitors and enforces SLA compliance and escalation
 */

import { Assignment, Priority, EscalationRule } from '../../types/assignment';

interface PerformanceMetric {
  recordedAt: Date;
  responseTime?: number;
  resolutionTime?: number;
  slaCompliant?: boolean;
  qualityScore?: number;
}

export class ResponsibilityGovernance {
  private escalationRules: Map<Priority, EscalationRule>;
  private performanceMetrics: Map<string, PerformanceMetric>;

  constructor() {
    this.escalationRules = new Map();
    this.performanceMetrics = new Map();
    this.initializeEscalationRules();
  }

  /**
   * 初始化升級規則
   * Initialize escalation rules
   */
  private initializeEscalationRules(): void {
    this.escalationRules.set('CRITICAL', {
      priority: 'CRITICAL',
      noResponseTimeout: 5, // 5 分鐘無回應
      noProgressTimeout: 15, // 15 分鐘無進展
      unresolvedTimeout: 60, // 60 分鐘未解決
    });

    this.escalationRules.set('HIGH', {
      priority: 'HIGH',
      noResponseTimeout: 15, // 15 分鐘無回應
      noProgressTimeout: 30, // 30 分鐘無進展
      unresolvedTimeout: 240, // 240 分鐘未解決
    });

    this.escalationRules.set('MEDIUM', {
      priority: 'MEDIUM',
      noResponseTimeout: 60, // 60 分鐘無回應
      noProgressTimeout: 120, // 120 分鐘無進展
      unresolvedTimeout: 480, // 480 分鐘未解決
    });

    this.escalationRules.set('LOW', {
      priority: 'LOW',
      noResponseTimeout: 240, // 240 分鐘無回應
      noProgressTimeout: 480, // 480 分鐘無進展
      unresolvedTimeout: 1440, // 1440 分鐘未解決
    });
  }

  /**
   * 檢查是否需要升級
   * Check if escalation is needed
   */
  checkEscalationNeeded(
    assignment: Assignment,
    priority: Priority
  ): {
    needed: boolean;
    reason?: string;
    timeout?: number;
  } {
    const rule = this.escalationRules.get(priority);
    if (!rule) {
      return { needed: false };
    }

    const now = new Date();
    const assignedMinutes = this.getMinutesDiff(assignment.assignedAt, now);

    // 檢查無回應超時
    if (!assignment.acknowledgedAt && assignedMinutes >= rule.noResponseTimeout) {
      return {
        needed: true,
        reason: 'No response timeout',
        timeout: rule.noResponseTimeout,
      };
    }

    // 檢查無進展超時
    if (
      assignment.acknowledgedAt &&
      !assignment.startedAt &&
      this.getMinutesDiff(assignment.acknowledgedAt, now) >= rule.noProgressTimeout
    ) {
      return {
        needed: true,
        reason: 'No progress timeout',
        timeout: rule.noProgressTimeout,
      };
    }

    // 檢查未解決超時
    if (
      assignment.startedAt &&
      !assignment.resolvedAt &&
      this.getMinutesDiff(assignment.startedAt, now) >= rule.unresolvedTimeout
    ) {
      return {
        needed: true,
        reason: 'Unresolved timeout',
        timeout: rule.unresolvedTimeout,
      };
    }

    return { needed: false };
  }

  /**
   * 監控分派表現
   * Monitor assignment performance
   */
  monitorAssignmentPerformance(assignment: Assignment): {
    compliant: boolean;
    responseTime?: number;
    resolutionTime?: number;
    violations: string[];
  } {
    const violations: string[] = [];
    let responseTime: number | undefined;
    let resolutionTime: number | undefined;

    // 計算回應時間
    if (assignment.acknowledgedAt) {
      responseTime = this.getMinutesDiff(assignment.assignedAt, assignment.acknowledgedAt);
      if (responseTime > assignment.slaTarget.responseTime) {
        violations.push(
          `Response time exceeded: ${responseTime}min > ${assignment.slaTarget.responseTime}min`
        );
      }
    }

    // 計算解決時間
    if (assignment.resolvedAt) {
      resolutionTime = this.getMinutesDiff(assignment.assignedAt, assignment.resolvedAt);
      if (resolutionTime > assignment.slaTarget.resolutionTime) {
        violations.push(
          `Resolution time exceeded: ${resolutionTime}min > ${assignment.slaTarget.resolutionTime}min`
        );
      }
    }

    return {
      compliant: violations.length === 0,
      responseTime,
      resolutionTime,
      violations,
    };
  }

  /**
   * 評估解決方案品質
   * Evaluate resolution quality
   */
  evaluateResolutionQuality(assignment: Assignment): {
    score: number;
    criteria: {
      timeliness: number;
      completeness: number;
    };
  } {
    let timelinessScore = 0;
    let completenessScore = 0;

    // 評估時效性 (0-1)
    if (assignment.resolvedAt) {
      const resolutionTime = this.getMinutesDiff(assignment.assignedAt, assignment.resolvedAt);
      const targetTime = assignment.slaTarget.resolutionTime;

      if (resolutionTime <= targetTime * 0.5) {
        timelinessScore = 1.0; // 非常快
      } else if (resolutionTime <= targetTime) {
        timelinessScore = 0.8; // 及時
      } else if (resolutionTime <= targetTime * 1.5) {
        timelinessScore = 0.5; // 稍微延遲
      } else {
        timelinessScore = 0.2; // 嚴重延遲
      }
    }

    // 評估完整性 (0-1)
    if (assignment.status === 'RESOLVED') {
      completenessScore = 1.0; // 假設已解決即為完整
    } else {
      completenessScore = 0.0;
    }

    const overallScore = timelinessScore * 0.6 + completenessScore * 0.4;

    return {
      score: overallScore,
      criteria: {
        timeliness: timelinessScore,
        completeness: completenessScore,
      },
    };
  }

  /**
   * 計算時間差（分鐘）
   * Calculate time difference in minutes
   */
  private getMinutesDiff(start: Date, end: Date): number {
    return Math.floor((end.getTime() - start.getTime()) / (1000 * 60));
  }

  /**
   * 獲取升級規則
   * Get escalation rule
   */
  getEscalationRule(priority: Priority): EscalationRule | undefined {
    return this.escalationRules.get(priority);
  }

  /**
   * 記錄效能指標
   * Record performance metrics
   */
  recordPerformanceMetrics(assignmentId: string, metrics: Record<string, unknown>): void {
    this.performanceMetrics.set(assignmentId, {
      ...metrics,
      recordedAt: new Date(),
    });
  }

  /**
   * 獲取效能指標
   * Get performance metrics
   */
  getPerformanceMetrics(assignmentId: string): PerformanceMetric | undefined {
    return this.performanceMetrics.get(assignmentId);
  }

  /**
   * 生成效能報告
   * Generate performance report
   */
  generatePerformanceReport(assignments: Assignment[]): {
    totalAssignments: number;
    resolved: number;
    averageResponseTime: number;
    averageResolutionTime: number;
    slaCompliance: number;
  } {
    const resolved = assignments.filter((a) => a.status === 'RESOLVED');

    let totalResponseTime = 0;
    let totalResolutionTime = 0;
    let slaCompliant = 0;
    let responseCount = 0;

    resolved.forEach((assignment) => {
      const performance = this.monitorAssignmentPerformance(assignment);

      if (performance.responseTime !== undefined) {
        totalResponseTime += performance.responseTime;
        responseCount++;
      }

      if (performance.resolutionTime !== undefined) {
        totalResolutionTime += performance.resolutionTime;
      }

      if (performance.compliant) {
        slaCompliant++;
      }
    });

    return {
      totalAssignments: assignments.length,
      resolved: resolved.length,
      averageResponseTime: responseCount > 0 ? totalResponseTime / responseCount : 0,
      averageResolutionTime: resolved.length > 0 ? totalResolutionTime / resolved.length : 0,
      slaCompliance: resolved.length > 0 ? (slaCompliant / resolved.length) * 100 : 0,
    };
  }
}
