/**
 * 自動分派控制器 (Assignment Controller)
 * Handles auto-assignment API requests
 */

import { Request, Response } from 'express';
import { z } from 'zod';

import {
  sendSuccess,
  sendError,
  handleControllerError,
  getErrorMessage,
} from '../middleware/response';
import { AutoAssignmentEngine } from '../services/assignment/auto-assignment-engine';
import { ResponsibilityGovernance } from '../services/assignment/responsibility-governance';
import { Incident, Priority, ProblemType, AssignmentStatus } from '../types/assignment';

// 驗證 Schema
const incidentSchema = z.object({
  type: z.enum([
    'FRONTEND_ERROR',
    'BACKEND_API',
    'DATABASE_ISSUE',
    'PERFORMANCE',
    'SECURITY',
    'INFRASTRUCTURE',
  ]),
  priority: z.enum(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']),
  description: z.string().min(1),
  affectedFiles: z.array(z.string()).optional(),
  errorMessage: z.string().optional(),
});

const updateStatusSchema = z.object({
  status: z.enum(['ASSIGNED', 'ACKNOWLEDGED', 'IN_PROGRESS', 'ESCALATED', 'RESOLVED']),
});

const reassignSchema = z.object({
  newOwnerId: z.string().min(1),
});

export class AssignmentController {
  private engine: AutoAssignmentEngine;
  private governance: ResponsibilityGovernance;

  constructor() {
    this.engine = new AutoAssignmentEngine();
    this.governance = new ResponsibilityGovernance();
  }

  /**
   * 創建新分派
   * POST /api/v1/assignment/assign
   */
  assignResponsibility = async (req: Request, res: Response): Promise<void> => {
    try {
      const validatedData = incidentSchema.parse(req.body);

      const incident: Incident = {
        id: `incident-${Date.now()}`,
        type: validatedData.type as ProblemType,
        priority: validatedData.priority as Priority,
        description: validatedData.description,
        affectedFiles: validatedData.affectedFiles,
        errorMessage: validatedData.errorMessage,
        createdAt: new Date(),
      };

      const assignment = await this.engine.assignResponsibility(incident);

      sendSuccess(res, { assignment, incident }, { status: 201 });
    } catch (error) {
      handleControllerError(res, error);
    }
  };

  /**
   * 更新分派狀態
   * POST /api/v1/assignment/status/:id
   */
  updateStatus = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params;
      const validatedData = updateStatusSchema.parse(req.body);

      const assignment = await this.engine.updateAssignmentStatus(
        id,
        validatedData.status as AssignmentStatus
      );

      sendSuccess(res, assignment);
    } catch (error) {
      handleControllerError(res, error, {
        notFoundCheck: (msg) => msg.includes('not found'),
      });
    }
  };

  /**
   * 查詢分派狀態
   * GET /api/v1/assignment/status/:id
   */
  getAssignmentStatus = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params;
      const assignment = this.engine.getAssignment(id);

      if (!assignment) {
        sendError(res, `Assignment ${id} not found`, { status: 404 });
        return;
      }

      sendSuccess(res, assignment);
    } catch (error) {
      sendError(res, getErrorMessage(error));
    }
  };

  /**
   * 查詢工作負載
   * GET /api/v1/assignment/workload
   */
  getWorkload = async (_req: Request, res: Response): Promise<void> => {
    try {
      const workloadStats = this.engine.getWorkloadStatistics();
      const workloadArray = Array.from(workloadStats.entries()).map(([, metrics]) => metrics);

      sendSuccess(res, workloadArray);
    } catch (error) {
      sendError(res, getErrorMessage(error));
    }
  };

  /**
   * 重新分派責任
   * POST /api/v1/assignment/reassign/:id
   */
  reassign = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params;
      const validatedData = reassignSchema.parse(req.body);

      const assignment = await this.engine.reassignResponsibility(id, validatedData.newOwnerId);

      sendSuccess(res, assignment);
    } catch (error) {
      handleControllerError(res, error, {
        notFoundCheck: (msg) => msg.includes('not found'),
        notFoundStatus: 404,
      });
    }
  };

  /**
   * 升級分派
   * POST /api/v1/assignment/escalate/:id
   */
  escalate = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params;
      const assignment = this.engine.getAssignment(id);

      if (!assignment) {
        sendError(res, `Assignment ${id} not found`, { status: 404 });
        return;
      }

      // 更新為升級狀態
      const updatedAssignment = await this.engine.updateAssignmentStatus(id, 'ESCALATED');

      sendSuccess(res, updatedAssignment, { message: 'Assignment escalated successfully' });
    } catch (error) {
      sendError(res, getErrorMessage(error));
    }
  };

  /**
   * 獲取所有分派
   * GET /api/v1/assignment/all
   */
  getAllAssignments = async (_req: Request, res: Response): Promise<void> => {
    try {
      const assignments = this.engine.getAllAssignments();

      sendSuccess(res, assignments, { count: assignments.length });
    } catch (error) {
      sendError(res, getErrorMessage(error));
    }
  };

  /**
   * 獲取效能報告
   * GET /api/v1/assignment/report
   */
  getPerformanceReport = async (_req: Request, res: Response): Promise<void> => {
    try {
      const assignments = this.engine.getAllAssignments();
      const report = this.governance.generatePerformanceReport(assignments);

      sendSuccess(res, report);
    } catch (error) {
      sendError(res, getErrorMessage(error));
    }
  };
}
