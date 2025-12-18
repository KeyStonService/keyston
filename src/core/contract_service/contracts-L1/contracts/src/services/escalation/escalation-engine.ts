/**
 * 進階升級引擎 (Advanced Escalation Engine)
 *
 * 核心功能：
 * - 自動檢測需要升級的情況
 * - 智能選擇升級路徑和負責人
 * - 管理升級生命週期
 * - 追蹤升級效能和統計
 *
 * 設計用於無人機、自動駕駛和自動化系統的關鍵場景
 */

import { Priority, TeamMember } from '../../types/assignment';
import {
  EscalationEvent,
  EscalationTrigger,
  EscalationLevel,
  EscalationStatus,
  EscalationContext,
  EscalationResolution,
  CustomerServiceAgent,
  EscalationRuleConfig,
} from '../../types/escalation';

interface EscalationEngineConfig {
  autoRetryLimit: number;
  enableSmartRouting: boolean;
  notificationEnabled: boolean;
}

export class EscalationEngine {
  private escalations: Map<string, EscalationEvent>;
  private escalationRules: Map<string, EscalationRuleConfig>;
  private customerServiceAgents: Map<string, CustomerServiceAgent>;
  private config: EscalationEngineConfig;

  constructor(config?: Partial<EscalationEngineConfig>) {
    this.escalations = new Map();
    this.escalationRules = new Map();
    this.customerServiceAgents = new Map();
    this.config = {
      autoRetryLimit: 3,
      enableSmartRouting: true,
      notificationEnabled: true,
      ...config,
    };

    this.initializeEscalationRules();
    this.initializeCustomerServiceAgents();
  }

  /**
   * 初始化升級規則
   * Initialize escalation rules
   */
  private initializeEscalationRules(): void {
    // CRITICAL 優先級 - 自動修復失敗
    this.escalationRules.set('CRITICAL_AUTO_FIX_FAILED', {
      trigger: 'AUTO_FIX_FAILED',
      priority: 'CRITICAL',
      targetLevel: 'L4_SENIOR_ENGINEER',
      timeThresholds: {
        autoEscalation: 5,
        maxWaitTime: 15,
      },
      maxAutoRetries: 2,
      notifications: {
        channels: ['SLACK', 'SMS', 'EMAIL'],
        recipients: ['on-call-engineer', 'team-lead'],
      },
    });

    // CRITICAL 優先級 - 安全關鍵
    this.escalationRules.set('CRITICAL_SAFETY', {
      trigger: 'SAFETY_CRITICAL',
      priority: 'CRITICAL',
      targetLevel: 'L5_CUSTOMER_SERVICE',
      timeThresholds: {
        autoEscalation: 2,
        maxWaitTime: 10,
      },
      maxAutoRetries: 1,
      notifications: {
        channels: ['PHONE', 'SMS', 'SLACK'],
        recipients: ['safety-officer', 'customer-service-lead'],
      },
    });

    // HIGH 優先級 - 重複失敗
    this.escalationRules.set('HIGH_REPEATED_FAILURES', {
      trigger: 'REPEATED_FAILURES',
      priority: 'HIGH',
      targetLevel: 'L3_SUPPORT_ENGINEER',
      timeThresholds: {
        autoEscalation: 10,
        maxWaitTime: 30,
      },
      maxAutoRetries: 3,
      notifications: {
        channels: ['SLACK', 'EMAIL'],
        recipients: ['support-team', 'team-lead'],
      },
    });

    // MEDIUM 優先級 - 超時無進展
    this.escalationRules.set('MEDIUM_NO_PROGRESS', {
      trigger: 'TIMEOUT_NO_PROGRESS',
      priority: 'MEDIUM',
      targetLevel: 'L2_TEAM_LEAD',
      timeThresholds: {
        autoEscalation: 30,
        maxWaitTime: 60,
      },
      maxAutoRetries: 2,
      notifications: {
        channels: ['SLACK', 'EMAIL'],
        recipients: ['team-lead'],
      },
    });
  }

  /**
   * 初始化客服人員
   * Initialize customer service agents
   */
  private initializeCustomerServiceAgents(): void {
    const agent1: CustomerServiceAgent = {
      id: 'cs-001',
      name: 'Sarah Johnson',
      email: 'sarah.johnson@synergymesh.dev',
      specialties: ['Customer Support', 'Technical Support', 'Escalation Management'],
      timezone: 'America/New_York',
      role: 'CUSTOMER_SERVICE',
      availability: {
        status: 'AVAILABLE',
        maxConcurrentCases: 5,
        currentCases: 0,
      },
      expertise: {
        technical: true,
        languages: ['en', 'zh-TW'],
        specializations: ['Drones', 'Autonomous Systems', 'Emergency Response'],
      },
      performance: {
        averageResponseTime: 3,
        resolutionRate: 92,
        customerSatisfaction: 4.7,
      },
    };

    const agent2: CustomerServiceAgent = {
      id: 'cs-002',
      name: 'Michael Chen',
      email: 'michael.chen@synergymesh.dev',
      specialties: ['Technical Support', 'System Integration', 'Critical Issues'],
      timezone: 'Asia/Taipei',
      role: 'CUSTOMER_SERVICE',
      availability: {
        status: 'AVAILABLE',
        maxConcurrentCases: 5,
        currentCases: 0,
      },
      expertise: {
        technical: true,
        languages: ['zh-TW', 'en'],
        specializations: ['Autonomous Vehicles', 'Safety Systems', 'Performance Optimization'],
      },
      performance: {
        averageResponseTime: 2.5,
        resolutionRate: 95,
        customerSatisfaction: 4.8,
      },
    };

    this.customerServiceAgents.set(agent1.id, agent1);
    this.customerServiceAgents.set(agent2.id, agent2);
  }

  /**
   * 創建升級事件
   * Create escalation event
   */
  createEscalation(
    incidentId: string,
    trigger: EscalationTrigger,
    priority: Priority,
    context: EscalationContext,
    assignmentId?: string
  ): EscalationEvent {
    const escalationId = `esc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // 根據觸發原因和優先級決定升級層級
    const level = this.determineEscalationLevel(trigger, priority, context);

    const escalation: EscalationEvent = {
      id: escalationId,
      incidentId,
      assignmentId,
      trigger,
      level,
      status: 'PENDING',
      priority,
      description: this.generateEscalationDescription(trigger, context),
      context,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    // 智能分派
    if (this.config.enableSmartRouting) {
      const assignee = this.selectBestAgent(escalation);
      if (assignee) {
        escalation.assignedTo = assignee;
        escalation.status = 'ASSIGNED';
      }
    }

    this.escalations.set(escalationId, escalation);

    // 發送通知
    if (this.config.notificationEnabled) {
      this.sendEscalationNotification(escalation);
    }

    return escalation;
  }

  /**
   * 決定升級層級
   * Determine escalation level
   */
  private determineEscalationLevel(
    trigger: EscalationTrigger,
    priority: Priority,
    context: EscalationContext
  ): EscalationLevel {
    // 安全關鍵問題直接升級到客服
    if (trigger === 'SAFETY_CRITICAL' || context.errorDetails.impactLevel === 'HIGH') {
      return 'L5_CUSTOMER_SERVICE';
    }

    // CRITICAL 優先級的自動修復失敗
    if (trigger === 'AUTO_FIX_FAILED' && priority === 'CRITICAL') {
      // 檢查自動修復嘗試次數
      if (context.autoFixAttempts.length >= this.config.autoRetryLimit) {
        return 'L4_SENIOR_ENGINEER';
      }
      return 'L3_SUPPORT_ENGINEER';
    }

    // 重複失敗
    if (trigger === 'REPEATED_FAILURES') {
      return priority === 'CRITICAL' || priority === 'HIGH'
        ? 'L3_SUPPORT_ENGINEER'
        : 'L2_TEAM_LEAD';
    }

    // 超時問題
    if (trigger === 'TIMEOUT_NO_RESPONSE' || trigger === 'TIMEOUT_NO_PROGRESS') {
      return priority === 'CRITICAL' ? 'L3_SUPPORT_ENGINEER' : 'L2_TEAM_LEAD';
    }

    // 手動請求
    if (trigger === 'MANUAL_REQUEST') {
      return 'L3_SUPPORT_ENGINEER';
    }

    // 默認層級
    return 'L2_TEAM_LEAD';
  }

  /**
   * 選擇最佳處理人員
   * Select best agent
   */
  private selectBestAgent(escalation: EscalationEvent): TeamMember | undefined {
    if (escalation.level === 'L5_CUSTOMER_SERVICE') {
      return this.selectBestCustomerServiceAgent(escalation);
    }

    // 對於其他層級，這裡可以整合現有的 WorkloadBalancer
    // 暫時返回 undefined，表示需要手動分派
    return undefined;
  }

  /**
   * 選擇最佳客服人員
   * Select best customer service agent
   */
  private selectBestCustomerServiceAgent(
    escalation: EscalationEvent
  ): CustomerServiceAgent | undefined {
    const availableAgents = Array.from(this.customerServiceAgents.values()).filter(
      (agent) =>
        agent.availability.status === 'AVAILABLE' &&
        agent.availability.currentCases < agent.availability.maxConcurrentCases
    );

    if (availableAgents.length === 0) {
      return undefined;
    }

    // 評分系統
    const scores = availableAgents.map((agent) => {
      let score = 0;

      // 專業匹配 (40%)
      const systemType = escalation.context.systemType;
      if (systemType === 'DRONE' && agent.expertise.specializations.includes('Drones')) {
        score += 40;
      } else if (
        systemType === 'AUTONOMOUS_VEHICLE' &&
        agent.expertise.specializations.includes('Autonomous Vehicles')
      ) {
        score += 40;
      } else if (agent.expertise.specializations.includes('Autonomous Systems')) {
        score += 30;
      }

      // 當前負載 (30%)
      const loadScore =
        (1 - agent.availability.currentCases / agent.availability.maxConcurrentCases) * 30;
      score += loadScore;

      // 績效表現 (30%)
      const perfScore =
        (agent.performance.resolutionRate / 100) * 15 +
        (agent.performance.customerSatisfaction / 5) * 15;
      score += perfScore;

      return { agent, score };
    });

    // 選擇得分最高的
    scores.sort((a, b) => b.score - a.score);
    return scores[0]?.agent;
  }

  /**
   * 生成升級描述
   * Generate escalation description
   */
  private generateEscalationDescription(
    trigger: EscalationTrigger,
    context: EscalationContext
  ): string {
    const descriptions: Record<EscalationTrigger, string> = {
      AUTO_FIX_FAILED: `自動修復失敗 (${context.autoFixAttempts.length} 次嘗試)：${context.errorDetails.message}`,
      TIMEOUT_NO_RESPONSE: `超時無回應：${context.errorDetails.message}`,
      TIMEOUT_NO_PROGRESS: `超時無進展：${context.errorDetails.message}`,
      CRITICAL_SEVERITY: `關鍵嚴重性問題：${context.errorDetails.message}`,
      REPEATED_FAILURES: `重複失敗 (影響 ${context.errorDetails.affectedComponents.join(', ')})`,
      SAFETY_CRITICAL: `安全關鍵問題：${context.errorDetails.message} - 影響等級: ${context.errorDetails.impactLevel}`,
      MANUAL_REQUEST: `手動升級請求：${context.errorDetails.message}`,
    };

    return descriptions[trigger] || context.errorDetails.message;
  }

  /**
   * 發送升級通知
   * Send escalation notification
   */
  private sendEscalationNotification(escalation: EscalationEvent): void {
    // 模擬通知邏輯
    console.log(`[ESCALATION NOTIFICATION] Level: ${escalation.level}`);
    console.log(`  ID: ${escalation.id}`);
    console.log(`  Trigger: ${escalation.trigger}`);
    console.log(`  Priority: ${escalation.priority}`);
    console.log(`  Description: ${escalation.description}`);
    if (escalation.assignedTo) {
      console.log(`  Assigned to: ${escalation.assignedTo.name}`);
    }
  }

  /**
   * 更新升級狀態
   * Update escalation status
   */
  updateEscalationStatus(
    escalationId: string,
    status: EscalationStatus,
    assignedTo?: TeamMember
  ): EscalationEvent | null {
    const escalation = this.escalations.get(escalationId);
    if (!escalation) {
      return null;
    }

    escalation.status = status;
    escalation.updatedAt = new Date();

    if (assignedTo) {
      escalation.assignedTo = assignedTo;
    }

    // 更新客服人員工作負載
    if (
      status === 'ASSIGNED' &&
      escalation.assignedTo &&
      escalation.level === 'L5_CUSTOMER_SERVICE'
    ) {
      const agent = this.customerServiceAgents.get(escalation.assignedTo.id);
      if (agent) {
        agent.availability.currentCases++;
      }
    }

    return escalation;
  }

  /**
   * 解決升級事件
   * Resolve escalation event
   */
  resolveEscalation(
    escalationId: string,
    resolution: EscalationResolution
  ): EscalationEvent | null {
    const escalation = this.escalations.get(escalationId);
    if (!escalation) {
      return null;
    }

    escalation.status = 'RESOLVED';
    escalation.resolvedAt = new Date();
    escalation.resolution = resolution;
    escalation.updatedAt = new Date();

    // 釋放客服人員工作負載
    if (escalation.assignedTo && escalation.level === 'L5_CUSTOMER_SERVICE') {
      const agent = this.customerServiceAgents.get(escalation.assignedTo.id);
      if (agent && agent.availability.currentCases > 0) {
        agent.availability.currentCases--;
      }
    }

    return escalation;
  }

  /**
   * 進一步升級
   * Escalate further
   */
  escalateFurther(escalationId: string, reason: string): EscalationEvent | null {
    const currentEscalation = this.escalations.get(escalationId);
    if (!currentEscalation) {
      return null;
    }

    // 決定下一個升級層級
    const nextLevel = this.getNextEscalationLevel(currentEscalation.level);
    if (!nextLevel) {
      console.log(`Already at highest escalation level: ${currentEscalation.level}`);
      return null;
    }

    // 創建新的升級事件
    const newEscalation = this.createEscalation(
      currentEscalation.incidentId,
      'MANUAL_REQUEST',
      currentEscalation.priority,
      {
        ...currentEscalation.context,
        errorDetails: {
          ...currentEscalation.context.errorDetails,
          message: `Escalated from ${currentEscalation.level}: ${reason}`,
        },
      },
      currentEscalation.assignmentId
    );

    // 強制設定為下一個層級
    newEscalation.level = nextLevel;

    return newEscalation;
  }

  /**
   * 取得下一個升級層級
   * Get next escalation level
   */
  private getNextEscalationLevel(currentLevel: EscalationLevel): EscalationLevel | null {
    const levelHierarchy: EscalationLevel[] = [
      'L1_AUTO',
      'L2_TEAM_LEAD',
      'L3_SUPPORT_ENGINEER',
      'L4_SENIOR_ENGINEER',
      'L5_CUSTOMER_SERVICE',
    ];

    const currentIndex = levelHierarchy.indexOf(currentLevel);
    if (currentIndex === -1 || currentIndex === levelHierarchy.length - 1) {
      return null;
    }

    return levelHierarchy[currentIndex + 1];
  }

  /**
   * 取得升級事件
   * Get escalation event
   */
  getEscalation(escalationId: string): EscalationEvent | null {
    return this.escalations.get(escalationId) || null;
  }

  /**
   * 取得事件的所有升級
   * Get all escalations for an incident
   */
  getEscalationsByIncident(incidentId: string): EscalationEvent[] {
    return Array.from(this.escalations.values())
      .filter((esc) => esc.incidentId === incidentId)
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  /**
   * 取得可用的客服人員
   * Get available customer service agents
   */
  getAvailableCustomerServiceAgents(): CustomerServiceAgent[] {
    return Array.from(this.customerServiceAgents.values())
      .filter((agent) => agent.availability.status === 'AVAILABLE')
      .sort((a, b) => {
        // 按負載和績效排序
        const loadA = a.availability.currentCases / a.availability.maxConcurrentCases;
        const loadB = b.availability.currentCases / b.availability.maxConcurrentCases;
        return loadA - loadB;
      });
  }

  /**
   * 取得所有升級統計
   * Get escalation statistics
   */
  getEscalationStatistics(
    startDate: Date,
    endDate: Date
  ): {
    total: number;
    byLevel: Record<EscalationLevel, number>;
    byTrigger: Record<EscalationTrigger, number>;
    byStatus: Record<EscalationStatus, number>;
    averageResolutionTime: number;
  } {
    const escalationsInPeriod = Array.from(this.escalations.values()).filter(
      (esc) => esc.createdAt >= startDate && esc.createdAt <= endDate
    );

    const stats = {
      total: escalationsInPeriod.length,
      byLevel: {} as Record<EscalationLevel, number>,
      byTrigger: {} as Record<EscalationTrigger, number>,
      byStatus: {} as Record<EscalationStatus, number>,
      averageResolutionTime: 0,
    };

    let totalResolutionTime = 0;
    let resolvedCount = 0;

    for (const esc of escalationsInPeriod) {
      // 按層級統計
      stats.byLevel[esc.level] = (stats.byLevel[esc.level] || 0) + 1;

      // 按觸發原因統計
      stats.byTrigger[esc.trigger] = (stats.byTrigger[esc.trigger] || 0) + 1;

      // 按狀態統計
      stats.byStatus[esc.status] = (stats.byStatus[esc.status] || 0) + 1;

      // 計算平均解決時間
      if (esc.resolvedAt) {
        const resolutionTime = esc.resolvedAt.getTime() - esc.createdAt.getTime();
        totalResolutionTime += resolutionTime;
        resolvedCount++;
      }
    }

    if (resolvedCount > 0) {
      stats.averageResolutionTime = totalResolutionTime / resolvedCount / (1000 * 60); // 轉換為分鐘
    }

    return stats;
  }
}
