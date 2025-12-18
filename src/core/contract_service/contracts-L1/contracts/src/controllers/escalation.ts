/**
 * 升級控制器 (Escalation Controller)
 *
 * 提供進階升級系統的 REST API 端點
 * Provides REST API endpoints for advanced escalation system
 */

import { Request, Response } from 'express';

import { sendSuccess, sendError, sendValidationError, sendNotFound } from '../middleware/response';
import { EscalationEngine } from '../services/escalation/escalation-engine';
import { Priority } from '../types/assignment';
import {
  EscalationTrigger,
  EscalationStatus,
  EscalationContext,
  EscalationResolution,
} from '../types/escalation';

export class EscalationController {
  private escalationEngine: EscalationEngine;

  constructor() {
    this.escalationEngine = new EscalationEngine({
      autoRetryLimit: 3,
      enableSmartRouting: true,
      notificationEnabled: true,
    });
  }

  /**
   * 創建升級事件
   * POST /api/v1/escalation/create
   */
  async createEscalation(req: Request, res: Response): Promise<void> {
    try {
      const { incidentId, trigger, priority, context, assignmentId } = req.body;

      // 驗證必要欄位
      if (!incidentId || !trigger || !priority || !context) {
        sendValidationError(res, 'Missing required fields: incidentId, trigger, priority, context');
        return;
      }

      // 驗證觸發原因
      const validTriggers: EscalationTrigger[] = [
        'AUTO_FIX_FAILED',
        'TIMEOUT_NO_RESPONSE',
        'TIMEOUT_NO_PROGRESS',
        'CRITICAL_SEVERITY',
        'REPEATED_FAILURES',
        'SAFETY_CRITICAL',
        'MANUAL_REQUEST',
      ];

      if (!validTriggers.includes(trigger)) {
        sendValidationError(res, `Invalid trigger. Must be one of: ${validTriggers.join(', ')}`);
        return;
      }

      // 驗證優先級
      const validPriorities: Priority[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
      if (!validPriorities.includes(priority)) {
        sendValidationError(res, `Invalid priority. Must be one of: ${validPriorities.join(', ')}`);
        return;
      }

      // 創建升級事件
      const escalation = this.escalationEngine.createEscalation(
        incidentId,
        trigger as EscalationTrigger,
        priority as Priority,
        context as EscalationContext,
        assignmentId
      );

      sendSuccess(res, { escalation }, { status: 201 });
    } catch (error) {
      console.error('Error creating escalation:', error);
      sendError(res, 'Failed to create escalation');
    }
  }

  /**
   * 取得升級事件詳情
   * GET /api/v1/escalation/:escalationId
   */
  async getEscalation(req: Request, res: Response): Promise<void> {
    try {
      const { escalationId } = req.params;

      const escalation = this.escalationEngine.getEscalation(escalationId);

      if (!escalation) {
        sendNotFound(res, 'Escalation');
        return;
      }

      sendSuccess(res, { escalation });
    } catch (error) {
      console.error('Error getting escalation:', error);
      sendError(res, 'Failed to get escalation');
    }
  }

  /**
   * 取得事件的所有升級
   * GET /api/v1/escalation/incident/:incidentId
   */
  async getEscalationsByIncident(req: Request, res: Response): Promise<void> {
    try {
      const { incidentId } = req.params;

      const escalations = this.escalationEngine.getEscalationsByIncident(incidentId);

      sendSuccess(res, { escalations, count: escalations.length });
    } catch (error) {
      console.error('Error getting escalations by incident:', error);
      sendError(res, 'Failed to get escalations');
    }
  }

  /**
   * 更新升級狀態
   * POST /api/v1/escalation/:escalationId/status
   */
  async updateEscalationStatus(req: Request, res: Response): Promise<void> {
    try {
      const { escalationId } = req.params;
      const { status, assignedTo } = req.body;

      if (!status) {
        sendValidationError(res, 'Missing required field: status');
        return;
      }

      const validStatuses: EscalationStatus[] = [
        'PENDING',
        'IN_REVIEW',
        'ASSIGNED',
        'IN_PROGRESS',
        'RESOLVED',
        'CLOSED',
      ];

      if (!validStatuses.includes(status)) {
        sendValidationError(res, `Invalid status. Must be one of: ${validStatuses.join(', ')}`);
        return;
      }

      const updatedEscalation = this.escalationEngine.updateEscalationStatus(
        escalationId,
        status as EscalationStatus,
        assignedTo
      );

      if (!updatedEscalation) {
        sendNotFound(res, 'Escalation');
        return;
      }

      sendSuccess(res, { escalation: updatedEscalation });
    } catch (error) {
      console.error('Error updating escalation status:', error);
      sendError(res, 'Failed to update escalation status');
    }
  }

  /**
   * 解決升級事件
   * POST /api/v1/escalation/:escalationId/resolve
   */
  async resolveEscalation(req: Request, res: Response): Promise<void> {
    try {
      const { escalationId } = req.params;
      const resolution = req.body as EscalationResolution;

      if (!resolution?.solutionType || !resolution.description || !resolution.implementedBy) {
        sendValidationError(
          res,
          'Missing required resolution fields: solutionType, description, implementedBy'
        );
        return;
      }

      const resolvedEscalation = this.escalationEngine.resolveEscalation(escalationId, resolution);

      if (!resolvedEscalation) {
        sendNotFound(res, 'Escalation');
        return;
      }

      sendSuccess(res, { escalation: resolvedEscalation });
    } catch (error) {
      console.error('Error resolving escalation:', error);
      sendError(res, 'Failed to resolve escalation');
    }
  }

  /**
   * 進一步升級
   * POST /api/v1/escalation/:escalationId/escalate
   */
  async escalateFurther(req: Request, res: Response): Promise<void> {
    try {
      const { escalationId } = req.params;
      const { reason } = req.body;

      if (!reason) {
        sendValidationError(res, 'Missing required field: reason');
        return;
      }

      const newEscalation = this.escalationEngine.escalateFurther(escalationId, reason);

      if (!newEscalation) {
        sendError(res, 'Cannot escalate further or escalation not found', { status: 400 });
        return;
      }

      sendSuccess(res, { escalation: newEscalation }, { status: 201 });
    } catch (error) {
      console.error('Error escalating further:', error);
      sendError(res, 'Failed to escalate further');
    }
  }

  /**
   * 取得可用的客服人員
   * GET /api/v1/escalation/customer-service/available
   */
  async getAvailableCustomerServiceAgents(_req: Request, res: Response): Promise<void> {
    try {
      const agents = this.escalationEngine.getAvailableCustomerServiceAgents();

      sendSuccess(res, { agents, count: agents.length });
    } catch (error) {
      console.error('Error getting available customer service agents:', error);
      sendError(res, 'Failed to get available agents');
    }
  }

  /**
   * 取得升級統計
   * GET /api/v1/escalation/statistics
   */
  async getEscalationStatistics(req: Request, res: Response): Promise<void> {
    try {
      const { startDate, endDate } = req.query;

      // 驗證和解析日期參數
      let start: Date;
      let end: Date;

      if (startDate) {
        start = new Date(startDate as string);
        if (isNaN(start.getTime())) {
          sendValidationError(res, 'Invalid startDate format. Please use ISO 8601 format.');
          return;
        }
      } else {
        // 默認為最近 7 天
        start = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      }

      if (endDate) {
        end = new Date(endDate as string);
        if (isNaN(end.getTime())) {
          sendValidationError(res, 'Invalid endDate format. Please use ISO 8601 format.');
          return;
        }
      } else {
        end = new Date();
      }

      const statistics = this.escalationEngine.getEscalationStatistics(start, end);

      sendSuccess(res, { period: { start, end }, statistics });
    } catch (error) {
      console.error('Error getting escalation statistics:', error);
      sendError(res, 'Failed to get statistics');
    }
  }
}
