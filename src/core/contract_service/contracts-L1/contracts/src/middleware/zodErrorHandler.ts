/**
 * Zod Error Handler Utility
 * Helper for formatting Zod validation errors consistently
 */

import { ZodError } from 'zod';

/**
 * Format Zod errors into a human-readable error message
 */
export function formatZodError(error: ZodError): string {
  return `Invalid input: ${error.errors.map((e: { message: string }) => e.message).join(', ')}`;
}

/**
 * Check if error is a ZodError
 */
export function isZodError(error: unknown): error is ZodError {
  return error instanceof ZodError;
}
