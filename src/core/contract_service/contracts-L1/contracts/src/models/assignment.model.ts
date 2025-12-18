/**
 * Assignment Models and Validation Schemas
 * Centralized data models for assignment-related operations
 */

import { z } from 'zod';

// ==================== Validation Schemas ====================

/**
 * Schema for creating a new incident assignment
 */
export const incidentSchema = z.object({
  type: z.enum([
    'FRONTEND_ERROR',
    'BACKEND_API',
    'DATABASE_ISSUE',
    'PERFORMANCE',
    'SECURITY',
    'INFRASTRUCTURE',
  ]),
  priority: z.enum(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']),
  description: z.string().min(1, 'Description is required'),
  affectedFiles: z.array(z.string()).optional(),
  errorMessage: z.string().optional(),
});

/**
 * Schema for updating assignment status
 */
export const updateStatusSchema = z.object({
  status: z.enum(['ASSIGNED', 'ACKNOWLEDGED', 'IN_PROGRESS', 'ESCALATED', 'RESOLVED']),
});

/**
 * Schema for reassigning responsibility
 */
export const reassignSchema = z.object({
  newOwnerId: z.string().min(1, 'New owner ID is required'),
});

// ==================== TypeScript Types ====================

/**
 * Infer TypeScript types from Zod schemas
 */
export type IncidentInput = z.infer<typeof incidentSchema>;
export type UpdateStatusInput = z.infer<typeof updateStatusSchema>;
export type ReassignInput = z.infer<typeof reassignSchema>;
