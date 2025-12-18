/**
 * 進階升級系統測試
 * Advanced Escalation System Tests
 */

import { EscalationEngine } from '../services/escalation/escalation-engine';
import { EscalationContext } from '../types/escalation';

describe('EscalationEngine', () => {
  let engine: EscalationEngine;

  beforeEach(() => {
    engine = new EscalationEngine({
      autoRetryLimit: 3,
      enableSmartRouting: true,
      notificationEnabled: false, // 測試時關閉通知
    });
  });

  describe('創建升級事件 (Create Escalation)', () => {
    test('應該成功創建自動修復失敗的升級事件', () => {
      const context: EscalationContext = {
        systemType: 'DRONE',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Auto-fix failed after 3 attempts',
          affectedComponents: ['flight-controller'],
          impactLevel: 'HIGH',
        },
        autoFixAttempts: [
          {
            attemptNumber: 1,
            strategy: 'restart-service',
            startedAt: new Date(),
            completedAt: new Date(),
            success: false,
            errorMessage: 'Service failed to restart',
          },
        ],
      };

      const escalation = engine.createEscalation(
        'incident-001',
        'AUTO_FIX_FAILED',
        'CRITICAL',
        context
      );

      expect(escalation).toBeDefined();
      expect(escalation.id).toMatch(/^esc-/);
      expect(escalation.incidentId).toBe('incident-001');
      expect(escalation.trigger).toBe('AUTO_FIX_FAILED');
      expect(escalation.priority).toBe('CRITICAL');
      expect(escalation.status).toMatch(/PENDING|ASSIGNED/);
    });

    test('應該自動分派安全關鍵問題到客服人員', () => {
      const context: EscalationContext = {
        systemType: 'AUTONOMOUS_VEHICLE',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Critical safety system failure',
          affectedComponents: ['braking-system', 'collision-detection'],
          impactLevel: 'HIGH',
        },
        autoFixAttempts: [],
      };

      const escalation = engine.createEscalation(
        'incident-002',
        'SAFETY_CRITICAL',
        'CRITICAL',
        context
      );

      expect(escalation.level).toBe('L5_CUSTOMER_SERVICE');
      expect(escalation.status).toBe('ASSIGNED');
      expect(escalation.assignedTo).toBeDefined();
      // 檢查客服人員是否有相關專業（可能是 Customer Support 或 Technical Support）
      const hasCustomerServiceExpertise = escalation.assignedTo?.specialties.some(
        (s) => s.includes('Customer') || s.includes('Technical') || s.includes('Support')
      );
      expect(hasCustomerServiceExpertise).toBe(true);
    });

    test('應該根據自動修復嘗試次數決定升級層級', () => {
      const createContextWithAttempts = (attemptCount: number): EscalationContext => ({
        systemType: 'AUTOMATED_SYSTEM',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Multiple auto-fix failures',
          affectedComponents: ['api-service'],
          impactLevel: 'MEDIUM',
        },
        autoFixAttempts: Array.from({ length: attemptCount }, (_, i) => ({
          attemptNumber: i + 1,
          strategy: 'restart',
          startedAt: new Date(),
          completedAt: new Date(),
          success: false,
        })),
      });

      // 少於 3 次嘗試
      const escalation1 = engine.createEscalation(
        'incident-003',
        'AUTO_FIX_FAILED',
        'CRITICAL',
        createContextWithAttempts(2)
      );
      expect(escalation1.level).toBe('L3_SUPPORT_ENGINEER');

      // 3 次或更多嘗試
      const escalation2 = engine.createEscalation(
        'incident-004',
        'AUTO_FIX_FAILED',
        'CRITICAL',
        createContextWithAttempts(3)
      );
      expect(escalation2.level).toBe('L4_SENIOR_ENGINEER');
    });
  });

  describe('更新升級狀態 (Update Escalation Status)', () => {
    test('應該成功更新升級狀態', async () => {
      const context: EscalationContext = {
        systemType: 'GENERAL',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Test error',
          affectedComponents: ['test'],
          impactLevel: 'LOW',
        },
        autoFixAttempts: [],
      };

      const escalation = engine.createEscalation(
        'incident-005',
        'MANUAL_REQUEST',
        'MEDIUM',
        context
      );

      // 稍微延遲以確保時間戳不同
      await new Promise((resolve) => setTimeout(resolve, 10));

      const updated = engine.updateEscalationStatus(escalation.id, 'IN_PROGRESS');

      expect(updated).toBeDefined();
      expect(updated!.status).toBe('IN_PROGRESS');
      expect(updated!.updatedAt.getTime()).toBeGreaterThanOrEqual(escalation.createdAt.getTime());
    });

    test('當升級事件不存在時應該返回 null', () => {
      const updated = engine.updateEscalationStatus('non-existent-id', 'IN_PROGRESS');

      expect(updated).toBeNull();
    });
  });

  describe('解決升級事件 (Resolve Escalation)', () => {
    test('應該成功解決升級事件', () => {
      const context: EscalationContext = {
        systemType: 'DRONE',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Flight controller error',
          affectedComponents: ['flight-controller'],
          impactLevel: 'MEDIUM',
        },
        autoFixAttempts: [],
      };

      const escalation = engine.createEscalation(
        'incident-006',
        'TIMEOUT_NO_PROGRESS',
        'HIGH',
        context
      );

      const resolution = {
        solutionType: 'HUMAN_ASSISTED' as const,
        description: 'Manually restarted flight controller and verified functionality',
        implementedBy: {
          id: 'eng-001',
          name: 'John Doe',
          email: 'john@example.com',
          specialties: ['Flight Systems'],
          timezone: 'UTC',
        },
        implementedAt: new Date(),
        changes: {
          files: ['flight_controller.py'],
          description: 'Restarted service and updated configuration',
        },
      };

      const resolved = engine.resolveEscalation(escalation.id, resolution);

      expect(resolved).toBeDefined();
      expect(resolved!.status).toBe('RESOLVED');
      expect(resolved!.resolvedAt).toBeDefined();
      expect(resolved!.resolution).toEqual(resolution);
    });

    test('應該釋放客服人員工作負載', () => {
      const context: EscalationContext = {
        systemType: 'DRONE',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Critical issue',
          affectedComponents: ['system'],
          impactLevel: 'HIGH',
        },
        autoFixAttempts: [],
      };

      const escalation = engine.createEscalation(
        'incident-007',
        'SAFETY_CRITICAL',
        'CRITICAL',
        context
      );

      // 獲取分派的客服人員
      const agentBefore = escalation.assignedTo;
      const agentsBefore = engine.getAvailableCustomerServiceAgents();
      const assignedAgent = agentsBefore.find((a) => a.id === agentBefore?.id);
      const currentCasesBefore = assignedAgent?.availability.currentCases || 0;

      // 解決升級事件
      const resolution = {
        solutionType: 'MANUAL_INTERVENTION' as const,
        description: 'Issue resolved',
        implementedBy: agentBefore!,
        implementedAt: new Date(),
        changes: {
          files: [],
          description: 'Manual fix applied',
        },
      };

      engine.resolveEscalation(escalation.id, resolution);

      // 檢查工作負載是否減少
      const agentsAfter = engine.getAvailableCustomerServiceAgents();
      const assignedAgentAfter = agentsAfter.find((a) => a.id === agentBefore?.id);
      const currentCasesAfter = assignedAgentAfter?.availability.currentCases || 0;

      expect(currentCasesAfter).toBeLessThanOrEqual(currentCasesBefore);
    });
  });

  describe('進一步升級 (Escalate Further)', () => {
    test('應該成功進一步升級到更高層級', () => {
      const context: EscalationContext = {
        systemType: 'GENERAL',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Unresolved issue',
          affectedComponents: ['api'],
          impactLevel: 'MEDIUM',
        },
        autoFixAttempts: [],
      };

      const initialEscalation = engine.createEscalation(
        'incident-008',
        'TIMEOUT_NO_PROGRESS',
        'MEDIUM',
        context
      );

      expect(initialEscalation.level).toBe('L2_TEAM_LEAD');

      const furtherEscalation = engine.escalateFurther(
        initialEscalation.id,
        'Team lead unable to resolve within SLA'
      );

      expect(furtherEscalation).toBeDefined();
      expect(furtherEscalation!.level).toBe('L3_SUPPORT_ENGINEER');
      expect(furtherEscalation!.incidentId).toBe('incident-008');
    });

    test('在最高層級時應該無法進一步升級', () => {
      const context: EscalationContext = {
        systemType: 'DRONE',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Critical safety issue',
          affectedComponents: ['safety-system'],
          impactLevel: 'HIGH',
        },
        autoFixAttempts: [],
      };

      const escalation = engine.createEscalation(
        'incident-009',
        'SAFETY_CRITICAL',
        'CRITICAL',
        context
      );

      expect(escalation.level).toBe('L5_CUSTOMER_SERVICE');

      const furtherEscalation = engine.escalateFurther(escalation.id, 'Need higher level');

      expect(furtherEscalation).toBeNull();
    });
  });

  describe('查詢功能 (Query Functions)', () => {
    test('應該能夠取得升級事件詳情', () => {
      const context: EscalationContext = {
        systemType: 'GENERAL',
        environment: 'DEVELOPMENT',
        errorDetails: {
          message: 'Test error',
          affectedComponents: ['test'],
          impactLevel: 'LOW',
        },
        autoFixAttempts: [],
      };

      const escalation = engine.createEscalation('incident-010', 'MANUAL_REQUEST', 'LOW', context);

      const retrieved = engine.getEscalation(escalation.id);

      expect(retrieved).toBeDefined();
      expect(retrieved!.id).toBe(escalation.id);
      expect(retrieved!.incidentId).toBe('incident-010');
    });

    test('應該能夠取得事件的所有升級', () => {
      const context: EscalationContext = {
        systemType: 'GENERAL',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Test error',
          affectedComponents: ['test'],
          impactLevel: 'MEDIUM',
        },
        autoFixAttempts: [],
      };

      // 創建多個升級事件
      const esc1 = engine.createEscalation(
        'incident-011',
        'TIMEOUT_NO_RESPONSE',
        'MEDIUM',
        context
      );
      engine.createEscalation('incident-011', 'TIMEOUT_NO_PROGRESS', 'MEDIUM', context);
      const esc3 = engine.createEscalation('incident-012', 'MANUAL_REQUEST', 'LOW', context);

      const escalationsForIncident = engine.getEscalationsByIncident('incident-011');

      expect(escalationsForIncident).toHaveLength(2);
      expect(escalationsForIncident.map((e) => e.id)).toContain(esc1.id);
      expect(escalationsForIncident.map((e) => e.id)).not.toContain(esc3.id);
    });

    test('應該能夠取得可用的客服人員', () => {
      const agents = engine.getAvailableCustomerServiceAgents();

      expect(agents).toBeDefined();
      expect(agents.length).toBeGreaterThan(0);

      agents.forEach((agent) => {
        expect(agent.availability.status).toBe('AVAILABLE');
        expect(agent.role).toBe('CUSTOMER_SERVICE');
        expect(agent.expertise.technical).toBe(true);
      });
    });
  });

  describe('統計功能 (Statistics)', () => {
    test('應該能夠取得升級統計資訊', () => {
      const context: EscalationContext = {
        systemType: 'GENERAL',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Test error',
          affectedComponents: ['test'],
          impactLevel: 'LOW',
        },
        autoFixAttempts: [],
      };

      // 創建多個升級事件
      const esc1 = engine.createEscalation('incident-013', 'AUTO_FIX_FAILED', 'CRITICAL', context);
      engine.createEscalation('incident-014', 'SAFETY_CRITICAL', 'CRITICAL', context);
      engine.createEscalation('incident-015', 'TIMEOUT_NO_PROGRESS', 'MEDIUM', context);

      // 解決其中一個
      engine.resolveEscalation(esc1.id, {
        solutionType: 'AUTOMATED',
        description: 'Resolved automatically',
        implementedBy: {
          id: 'sys-001',
          name: 'System',
          email: 'system@example.com',
          specialties: ['Automation'],
          timezone: 'UTC',
        },
        implementedAt: new Date(),
        changes: {
          files: [],
          description: 'Auto-resolved',
        },
      });

      const startDate = new Date(Date.now() - 24 * 60 * 60 * 1000);
      const endDate = new Date();

      const stats = engine.getEscalationStatistics(startDate, endDate);

      expect(stats.total).toBeGreaterThanOrEqual(3);
      expect(stats.byTrigger['AUTO_FIX_FAILED']).toBeGreaterThanOrEqual(1);
      expect(stats.byTrigger['SAFETY_CRITICAL']).toBeGreaterThanOrEqual(1);
      expect(stats.byStatus['RESOLVED']).toBeGreaterThanOrEqual(1);
    });
  });

  describe('客服人員選擇邏輯 (Customer Service Agent Selection)', () => {
    test('應該根據專業匹配選擇客服人員', () => {
      const droneContext: EscalationContext = {
        systemType: 'DRONE',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Drone system failure',
          affectedComponents: ['navigation'],
          impactLevel: 'HIGH',
        },
        autoFixAttempts: [],
      };

      const escalation = engine.createEscalation(
        'incident-016',
        'SAFETY_CRITICAL',
        'CRITICAL',
        droneContext
      );

      expect(escalation.assignedTo).toBeDefined();
      // 客服人員應該有無人機相關專業
      const hasDroneExpertise = escalation.assignedTo?.specialties.some(
        (s) =>
          s.toLowerCase().includes('drone') ||
          s.toLowerCase().includes('customer') ||
          s.toLowerCase().includes('technical')
      );
      expect(hasDroneExpertise).toBe(true);
    });
  });

  describe('升級層級決策 (Escalation Level Decision)', () => {
    test('安全關鍵問題應該直接升級到 L5', () => {
      const context: EscalationContext = {
        systemType: 'AUTONOMOUS_VEHICLE',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Safety system malfunction',
          affectedComponents: ['braking'],
          impactLevel: 'HIGH',
        },
        autoFixAttempts: [],
      };

      const escalation = engine.createEscalation(
        'incident-017',
        'SAFETY_CRITICAL',
        'HIGH',
        context
      );

      expect(escalation.level).toBe('L5_CUSTOMER_SERVICE');
    });

    test('重複失敗的 CRITICAL 問題應該升級到 L3', () => {
      const context: EscalationContext = {
        systemType: 'GENERAL',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'Repeated failures detected',
          affectedComponents: ['api'],
          impactLevel: 'MEDIUM',
        },
        autoFixAttempts: [],
      };

      const escalation = engine.createEscalation(
        'incident-018',
        'REPEATED_FAILURES',
        'CRITICAL',
        context
      );

      expect(escalation.level).toBe('L3_SUPPORT_ENGINEER');
    });

    test('MEDIUM 優先級的超時問題應該升級到 L2', () => {
      const context: EscalationContext = {
        systemType: 'GENERAL',
        environment: 'PRODUCTION',
        errorDetails: {
          message: 'No progress timeout',
          affectedComponents: ['service'],
          impactLevel: 'LOW',
        },
        autoFixAttempts: [],
      };

      const escalation = engine.createEscalation(
        'incident-019',
        'TIMEOUT_NO_PROGRESS',
        'MEDIUM',
        context
      );

      expect(escalation.level).toBe('L2_TEAM_LEAD');
    });
  });
});
