/**
 * Provenance Models and Validation Schemas
 * Centralized data models for build provenance operations
 */

import { z } from 'zod';

// ==================== Validation Schemas ====================

/**
 * Schema for creating a build attestation
 */
export const createAttestationSchema = z.object({
  filePath: z.string().min(1, 'File path is required'),
  builder: z.object({
    id: z.string().min(1, 'Builder ID is required'),
    version: z.string().min(1, 'Builder version is required'),
  }),
  metadata: z.record(z.any()).optional(),
});

/**
 * Schema for verifying an attestation
 */
export const verifyAttestationSchema = z.object({
  attestation: z.any().refine((val) => val !== undefined && val !== null, {
    message: 'Attestation is required',
  }),
});

/**
 * Schema for importing an attestation
 */
export const importAttestationSchema = z.object({
  attestation: z.any().refine((val) => val !== undefined && val !== null, {
    message: 'Attestation data is required',
  }),
});

/**
 * Schema for file digest request
 */
export const fileDigestSchema = z.object({
  filePath: z.string().min(1, 'File path is required'),
});

// ==================== TypeScript Types ====================

/**
 * Infer TypeScript types from Zod schemas
 */
export type CreateAttestationInput = z.infer<typeof createAttestationSchema>;
export type VerifyAttestationInput = z.infer<typeof verifyAttestationSchema>;
export type ImportAttestationInput = z.infer<typeof importAttestationSchema>;
export type FileDigestInput = z.infer<typeof fileDigestSchema>;
