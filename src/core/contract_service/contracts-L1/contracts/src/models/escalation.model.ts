/**
 * Escalation Models and Validation Schemas
 * Centralized data models for escalation operations
 */

import { z } from 'zod';

// ==================== Validation Schemas ====================

/**
 * Schema for creating an escalation
 */
export const createEscalationSchema = z.object({
  incidentId: z.string().min(1, 'Incident ID is required'),
  trigger: z.enum([
    'AUTO_FIX_FAILED',
    'TIMEOUT_NO_RESPONSE',
    'TIMEOUT_NO_PROGRESS',
    'CRITICAL_SEVERITY',
    'REPEATED_FAILURES',
    'SAFETY_CRITICAL',
    'MANUAL_REQUEST',
  ]),
  priority: z.enum(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']),
  context: z.record(z.any()),
  assignmentId: z.string().optional(),
});

/**
 * Schema for updating escalation status
 */
export const updateEscalationStatusSchema = z.object({
  status: z.enum(['PENDING', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']),
  notes: z.string().optional(),
});

/**
 * Schema for resolving an escalation
 */
export const resolveEscalationSchema = z.object({
  resolution: z.string().min(1, 'Resolution details are required'),
  rootCause: z.string().optional(),
  preventiveMeasures: z.string().optional(),
});

// ==================== TypeScript Types ====================

/**
 * Infer TypeScript types from Zod schemas
 */
export type CreateEscalationInput = z.infer<typeof createEscalationSchema>;
export type UpdateEscalationStatusInput = z.infer<typeof updateEscalationStatusSchema>;
export type ResolveEscalationInput = z.infer<typeof resolveEscalationSchema>;
