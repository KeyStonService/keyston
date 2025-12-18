/**
 * API Response Utilities
 *
 * Provides standardized response helpers to eliminate duplicated response patterns
 * across controllers. Ensures consistent API response format and error handling.
 */

import { Response } from 'express';
import { z } from 'zod';

/**
 * Standard API response interface
 */
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp?: string;
  details?: unknown;
  count?: number;
}

/**
 * Creates a standard timestamp in ISO 8601 format
 */
export const createTimestamp = (): string => new Date().toISOString();

/**
 * Send a successful response
 */
export const sendSuccess = <T>(
  res: Response,
  data: T,
  options: {
    message?: string;
    status?: number;
    count?: number;
    includeTimestamp?: boolean;
  } = {}
): void => {
  const { message, status = 200, count, includeTimestamp = false } = options;
  const response: ApiResponse<T> = {
    success: true,
    data,
  };

  if (message) {
    response.message = message;
  }

  if (count !== undefined) {
    response.count = count;
  }

  if (includeTimestamp) {
    response.timestamp = createTimestamp();
  }

  res.status(status).json(response);
};

/**
 * Send an error response
 */
export const sendError = (
  res: Response,
  error: string,
  options: {
    status?: number;
    details?: unknown;
    includeTimestamp?: boolean;
  } = {}
): void => {
  const { status = 500, details, includeTimestamp = false } = options;
  const response: ApiResponse = {
    success: false,
    error,
  };

  if (details) {
    response.details = details;
  }

  if (includeTimestamp) {
    response.timestamp = createTimestamp();
  }

  res.status(status).json(response);
};

/**
 * Send a validation error response
 */
export const sendValidationError = (res: Response, error: string, details?: unknown): void => {
  sendError(res, error, { status: 400, details });
};

/**
 * Send a not found error response
 */
export const sendNotFound = (res: Response, resource: string, includeTimestamp = false): void => {
  sendError(res, `${resource} not found`, { status: 404, includeTimestamp });
};

/**
 * Send an internal server error response
 */
export const sendInternalError = (
  res: Response,
  error: unknown,
  fallbackMessage = 'Internal server error',
  includeTimestamp = false
): void => {
  const errorMessage = error instanceof Error ? error.message : fallbackMessage;
  sendError(res, errorMessage, { status: 500, includeTimestamp });
};

/**
 * Get error message from unknown error type
 */
export const getErrorMessage = (
  error: unknown,
  fallbackMessage = 'Unknown error occurred'
): string => {
  if (error instanceof Error) {
    return error.message;
  }
  return fallbackMessage;
};

/**
 * Handle common error patterns with Zod validation support
 * Sends appropriate error response based on error type
 */
export const handleControllerError = (
  res: Response,
  error: unknown,
  options: {
    notFoundCheck?: (msg: string) => boolean;
    notFoundStatus?: number;
    fallbackMessage?: string;
  } = {}
): void => {
  const {
    notFoundCheck,
    notFoundStatus = 404,
    fallbackMessage = 'Unknown error occurred',
  } = options;

  if (error instanceof z.ZodError) {
    sendValidationError(res, 'Validation error', error.errors);
    return;
  }

  if (error instanceof Error) {
    if (notFoundCheck?.(error.message)) {
      sendError(res, error.message, { status: notFoundStatus });
      return;
    }
    sendError(res, error.message);
    return;
  }

  sendError(res, fallbackMessage);
};
