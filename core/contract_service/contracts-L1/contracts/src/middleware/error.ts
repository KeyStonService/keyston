/**
 * @fileoverview Centralized error handling middleware for Express applications.
 *
 * This module provides robust error handling that:
 * - Normalizes all errors to a consistent format
 * - Distinguishes between application errors and unexpected exceptions
 * - Provides appropriate error responses based on environment
 * - Maintains trace IDs for distributed debugging
 * - Handles 404 Not Found responses
 *
 * @module middleware/error
 */

import { randomUUID } from 'crypto';

import { Request, Response, NextFunction } from 'express';

import config from '../config';
import { AppError, ErrorCode, createError } from '../errors';

const UNKNOWN_ERROR_FALLBACK = 'Unknown error';

/**
 * Centralized holder for regex patterns used by the error middleware.
 * Ensures patterns are compiled once and reused.
 */
export class ErrorCleanupPatterns {
  // Matches ANSI escape sequences to strip terminal color/style codes from error messages
  public static readonly ansiEscapePattern: RegExp = /\x1B\[[0-?]*[ -/]*[@-~]/g;

  public static sanitizeMessage(message: string): string {
    const sanitized = message.replace(ErrorCleanupPatterns.ansiEscapePattern, '').trim();
    return sanitized || UNKNOWN_ERROR_FALLBACK;
  }
}

/**
 * Safely converts any thrown value to an Error object.
 *
 * JavaScript allows throwing any value, not just Error objects. This function
 * ensures that any caught value is converted to a proper Error instance for
 * consistent error handling and logging.
 *
 * Conversion rules:
 * - Error instances: returned as-is
 * - null/undefined: returns Error with 'Unknown error' message
 * - strings: wraps in Error with the string as message
 * - numbers/booleans: converts to string, wraps in Error
 * - objects: attempts JSON.stringify, wraps result in Error
 * - other types (symbol, bigint, function): returns Error with type indicator
 *
 * @param err - Any value that was thrown
 * @returns A proper Error object
 *
 * @example
 * try {
 *   throw 'Something went wrong'; // Bad practice, but supported
 * } catch (e) {
 *   const error = convertToError(e);
 *   console.log(error.message); // 'Something went wrong'
 * }
 *
 * @example
 * try {
 *   throw { code: 'ERR_001', reason: 'Invalid input' };
 * } catch (e) {
 *   const error = convertToError(e);
 *   console.log(error.message); // '{"code":"ERR_001","reason":"Invalid input"}'
 * }
 */
const convertToError = (err: unknown): Error => {
  if (err instanceof Error) {
    return err;
  }
  if (err === null || err === undefined) {
    return new Error(UNKNOWN_ERROR_FALLBACK);
  }
  // Safely convert to string for non-Error types
  let message: string;
  if (typeof err === 'string') {
    message = err;
  } else if (typeof err === 'number' || typeof err === 'boolean') {
    message = String(err);
  } else if (typeof err === 'object') {
    try {
      message = JSON.stringify(err);
    } catch {
      message = 'Unknown error (could not stringify)';
    }
  } else {
    // symbol, bigint, function, etc.
    message = 'Unknown error (unsupported type)';
  }
  return new Error(ErrorCleanupPatterns.sanitizeMessage(message));
};

/**
 * Global error handling middleware for Express applications.
 *
 * This middleware catches all errors passed to `next(error)` and provides
 * consistent error responses. It differentiates between:
 *
 * 1. **AppError instances**: Custom application errors with structured data
 *    - Uses the error's status code, message, and trace ID
 *    - Includes validation errors if present
 *    - Logs at appropriate level based on status code
 *
 * 2. **Unexpected errors**: All other errors (programming errors, etc.)
 *    - Returns 500 Internal Server Error
 *    - Hides internal details in production (security)
 *    - Shows full details in development for debugging
 *    - Generates new trace ID if not present
 *
 * Response format:
 * ```json
 * {
 *   "error": {
 *     "code": "ERROR_CODE",
 *     "message": "Human-readable message",
 *     "status": 400,
 *     "traceId": "uuid-v4",
 *     "timestamp": "2025-12-01T00:00:00.000Z",
 *     "details": {} // Optional validation errors
 *   }
 * }
 * ```
 *
 * @param err - The error that was thrown or passed to next()
 * @param req - Express request object
 * @param res - Express response object
 * @param _next - Express next function (unused but required for error middleware signature)
 *
 * @example
 * // Usage in Express app
 * app.use(errorMiddleware);
 *
 * // In route handlers, throw AppError for expected errors:
 * throw createError.badRequest('Invalid user ID');
 *
 * // Or pass to next() for unexpected errors:
 * try {
 *   await riskyOperation();
 * } catch (error) {
 *   next(error);
 * }
 */
export const errorMiddleware = (
  err: unknown,
  req: Request,
  res: Response,
  _next: NextFunction
): void => {
  const isAppError = err instanceof AppError;
  const safeError = convertToError(err);
  const traceId = req.traceId || (isAppError ? err.traceId : randomUUID());
  let logLevel: 'error' | 'warn' = 'error';

  if (isAppError) {
    const errorResponse = {
      error: {
        code: err.code,
        message: ErrorCleanupPatterns.sanitizeMessage(err.message || UNKNOWN_ERROR_FALLBACK),
        status: err.statusCode,
        traceId: err.traceId,
        timestamp: err.timestamp,
        details: (err as AppError & { validationErrors?: unknown }).validationErrors,
      },
    };
    if (err.statusCode < 500) {
      logLevel = 'warn';
    }
    res.status(err.statusCode).json(errorResponse);
  } else {
    const sanitizedMessage = ErrorCleanupPatterns.sanitizeMessage(
      safeError.message || UNKNOWN_ERROR_FALLBACK
    );
    const errorResponse = {
      error: {
        code: ErrorCode.INTERNAL_ERROR,
        message:
          config.NODE_ENV === 'production' ? 'Internal server error' : sanitizedMessage,
        status: 500,
        traceId,
        timestamp: new Date().toISOString(),
      },
    };
    res.status(500).json(errorResponse);
  }

  const errorLog = {
    traceId,
    error: {
      name: safeError.name,
      message: ErrorCleanupPatterns.sanitizeMessage(
        safeError.message || UNKNOWN_ERROR_FALLBACK
      ),
      code: isAppError ? err.code : ErrorCode.INTERNAL_ERROR,
      stack: config.NODE_ENV !== 'production' ? safeError.stack : undefined,
    },
    request: {
      method: req.method,
      url: req.url,
      userAgent:
        typeof (req as Request & { get?: Request['get'] }).get === 'function'
          ? req.get('user-agent')
          : req.headers?.['user-agent'],
      ip: req.ip,
    },
    timestamp: new Date().toISOString(),
  };

  if (logLevel === 'error') {
    console.error('Application error:', errorLog);
  } else {
    console.warn('Client error:', errorLog);
  }
};

/**
 * Middleware to handle requests to undefined routes (404 Not Found).
 *
 * This middleware should be registered AFTER all valid routes but BEFORE
 * the error handling middleware. It catches any requests that don't match
 * defined routes and returns a standardized 404 response.
 *
 * Response format:
 * ```json
 * {
 *   "error": {
 *     "code": "NOT_FOUND",
 *     "message": "Route GET /undefined-path not found",
 *     "traceId": "uuid-v4",
 *     "timestamp": "2025-12-01T00:00:00.000Z"
 *   }
 * }
 * ```
 *
 * @param req - Express request object
 * @param res - Express response object
 * @param _next - Express next function (unused, responds directly)
 *
 * @example
 * // Correct middleware ordering in Express app:
 * app.use('/api', apiRoutes);           // 1. Define routes first
 * app.use(notFoundMiddleware);           // 2. Catch undefined routes
 * app.use(errorMiddleware);              // 3. Handle errors last
 *
 * @example
 * // Response for GET /undefined-route:
 * // HTTP 404
 * // {
 * //   "error": {
 * //     "code": "NOT_FOUND",
 * //     "message": "Route GET /undefined-route not found",
 * //     "traceId": "a1b2c3d4-...",
 * //     "timestamp": "2025-12-01T10:00:00.000Z"
 * //   }
 * // }
 */
export const notFoundMiddleware = (req: Request, res: Response, _next: NextFunction): void => {
  const error = createError.notFound(`Route ${req.method} ${req.url} not found`);
  const traceId = req.traceId || randomUUID();

  res.status(404).json({
    error: {
      code: error.code,
      message: error.message,
      traceId,
      timestamp: new Date().toISOString(),
    },
  });
};

export default errorMiddleware;
