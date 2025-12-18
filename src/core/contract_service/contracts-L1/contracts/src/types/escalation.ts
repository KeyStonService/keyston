/**
 * 進階升級系統類型定義
 * Advanced Escalation System Type Definitions
 *
 * 支援無人機、自動駕駛和自動化系統的智能升級機制
 * Supports intelligent escalation for drones, autonomous vehicles, and automated systems
 */

import { Priority, TeamMember } from './assignment';

/**
 * 升級觸發原因
 * Escalation trigger reasons
 */
export type EscalationTrigger =
  | 'AUTO_FIX_FAILED' // 自動修復失敗
  | 'TIMEOUT_NO_RESPONSE' // 超時無回應
  | 'TIMEOUT_NO_PROGRESS' // 超時無進展
  | 'CRITICAL_SEVERITY' // 嚴重等級
  | 'REPEATED_FAILURES' // 重複失敗
  | 'SAFETY_CRITICAL' // 安全關鍵
  | 'MANUAL_REQUEST'; // 手動請求

/**
 * 升級層級
 * Escalation levels
 */
export type EscalationLevel =
  | 'L1_AUTO' // L1: 自動化處理
  | 'L2_TEAM_LEAD' // L2: 團隊主管
  | 'L3_SUPPORT_ENGINEER' // L3: 支援工程師
  | 'L4_SENIOR_ENGINEER' // L4: 資深工程師
  | 'L5_CUSTOMER_SERVICE'; // L5: 客服人員介入

/**
 * 升級狀態
 * Escalation status
 */
export type EscalationStatus =
  | 'PENDING' // 等待中
  | 'IN_REVIEW' // 審查中
  | 'ASSIGNED' // 已分派
  | 'IN_PROGRESS' // 處理中
  | 'RESOLVED' // 已解決
  | 'CLOSED'; // 已關閉

/**
 * 解決方案類型
 * Solution types
 */
export type SolutionType =
  | 'AUTOMATED' // 自動化解決
  | 'HUMAN_ASSISTED' // 人工輔助
  | 'MANUAL_INTERVENTION' // 手動介入
  | 'WORKAROUND' // 臨時解決方案
  | 'ESCALATED_FURTHER'; // 進一步升級

/**
 * 升級事件
 * Escalation event
 */
export interface EscalationEvent {
  id: string;
  incidentId: string;
  assignmentId?: string;
  trigger: EscalationTrigger;
  level: EscalationLevel;
  status: EscalationStatus;
  priority: Priority;
  description: string;
  context: EscalationContext;
  assignedTo?: TeamMember;
  createdAt: Date;
  updatedAt: Date;
  resolvedAt?: Date;
  resolution?: EscalationResolution;
}

/**
 * 升級上下文
 * Escalation context
 */
export interface EscalationContext {
  // 系統資訊
  systemType: 'DRONE' | 'AUTONOMOUS_VEHICLE' | 'AUTOMATED_SYSTEM' | 'GENERAL';
  environment: 'PRODUCTION' | 'STAGING' | 'DEVELOPMENT';

  // 問題詳情
  errorDetails: {
    message: string;
    stackTrace?: string;
    affectedComponents: string[];
    impactLevel: 'HIGH' | 'MEDIUM' | 'LOW';
  };

  // 自動化嘗試記錄
  autoFixAttempts: AutoFixAttempt[];

  // 相關資料
  relatedIncidents?: string[];
  similarIssues?: string[];

  // 業務影響
  businessImpact?: {
    affectedUsers: number;
    downtimeMinutes: number;
    estimatedCost?: number;
  };
}

/**
 * 自動修復嘗試記錄
 * Auto-fix attempt record
 */
export interface AutoFixAttempt {
  attemptNumber: number;
  strategy: string;
  startedAt: Date;
  completedAt: Date;
  success: boolean;
  errorMessage?: string;
  changes?: string[];
}

/**
 * 升級解決方案
 * Escalation resolution
 */
export interface EscalationResolution {
  solutionType: SolutionType;
  description: string;
  implementedBy: TeamMember;
  implementedAt: Date;
  verifiedBy?: TeamMember;
  verifiedAt?: Date;

  // 解決方案詳情
  changes: {
    files: string[];
    description: string;
    commitHash?: string;
  };

  // 預防措施
  preventiveMeasures?: string[];

  // 知識庫文章
  knowledgeBaseArticle?: {
    id: string;
    title: string;
    url: string;
  };
}

/**
 * 客服人員
 * Customer service representative
 */
export interface CustomerServiceAgent extends TeamMember {
  role: 'CUSTOMER_SERVICE';
  availability: {
    status: 'AVAILABLE' | 'BUSY' | 'OFFLINE';
    maxConcurrentCases: number;
    currentCases: number;
  };
  expertise: {
    technical: boolean;
    languages: string[];
    specializations: string[];
  };
  performance: {
    averageResponseTime: number; // 分鐘
    resolutionRate: number; // 百分比
    customerSatisfaction: number; // 1-5 分
  };
}

/**
 * 升級規則配置
 * Escalation rule configuration
 */
export interface EscalationRuleConfig {
  trigger: EscalationTrigger;
  priority: Priority;

  // 升級層級對應
  targetLevel: EscalationLevel;

  // 時間閾值（分鐘）
  timeThresholds: {
    autoEscalation: number;
    maxWaitTime: number;
  };

  // 自動化重試次數
  maxAutoRetries: number;

  // 通知配置
  notifications: {
    channels: ('EMAIL' | 'SLACK' | 'SMS' | 'PHONE')[];
    recipients: string[];
  };
}

/**
 * 升級統計
 * Escalation statistics
 */
export interface EscalationStatistics {
  period: {
    start: Date;
    end: Date;
  };

  totalEscalations: number;

  byLevel: Record<EscalationLevel, number>;
  byTrigger: Record<EscalationTrigger, number>;
  byStatus: Record<EscalationStatus, number>;

  averageResolutionTime: number; // 分鐘

  solutionTypes: Record<SolutionType, number>;

  // 成功率
  successRate: {
    l1Auto: number;
    l2TeamLead: number;
    l3Support: number;
    l4Senior: number;
    l5CustomerService: number;
  };
}
